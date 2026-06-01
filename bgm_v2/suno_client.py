"""Thin Suno client with retry, polling, dual-candidate download, hash cache."""
from __future__ import annotations
import hashlib
import json
import time
from pathlib import Path
from typing import List, Optional

import requests

from .config import Config
from .http_util import SESSION


class SunoError(RuntimeError):
    pass


class SunoClient:
    def __init__(self, config: Optional[Config] = None):
        self.cfg = config or Config()
        self.cfg.ensure_dirs()

    # ---- public ----------------------------------------------------------

    def generate(self, payload: dict, *, cache: bool = True) -> List[Path]:
        """Submit a Suno generation, poll till complete, return paths of all clips.

        Suno typically returns 2 clips per call. We download both.
        """
        key = self._payload_hash(payload)
        cached = self._cache_lookup(key)
        if cached and cache:
            print(f"[suno] cache hit -> {[str(p.name) for p in cached]}")
            return cached

        last_err: Optional[Exception] = None
        for attempt in range(1, self.cfg.suno_max_retries + 1):
            try:
                clip_ids = self._submit(payload)
                print(f"[suno] attempt {attempt} clip_ids={clip_ids}")
                files = self._wait_and_download(clip_ids, key)
                if files:
                    self._cache_store(key, files, payload)
                    return files
            except Exception as e:
                last_err = e
                wait = 4 ** attempt
                print(f"[suno] attempt {attempt} failed: {e}; sleeping {wait}s")
                time.sleep(wait)
        raise SunoError(f"All retries failed: {last_err}")

    # ---- internals -------------------------------------------------------

    def _submit(self, payload: dict) -> List[str]:
        url = f"{self.cfg.suno_api_base}/generate"
        headers = {
            "Authorization": f"Bearer {self.cfg.suno_api_key}",
            "Content-Type": "application/json",
        }
        r = SESSION.post(url, headers=headers, json=payload, timeout=60)
        if r.status_code != 200:
            raise SunoError(f"submit {r.status_code}: {r.text[:300]}")
        data = r.json()
        clips = data.get("clips") or data.get("data") or []
        ids = [c["id"] for c in clips if c.get("id")]
        if not ids:
            raise SunoError(f"no clip ids in response: {str(data)[:300]}")
        return ids

    def _wait_and_download(self, clip_ids: List[str], cache_key: str) -> List[Path]:
        deadline = time.time() + self.cfg.suno_poll_timeout_s
        done: dict[str, str] = {}  # clip_id -> audio_url
        while time.time() < deadline and len(done) < len(clip_ids):
            for cid in clip_ids:
                if cid in done:
                    continue
                feed = self._feed(cid)
                for entry in feed:
                    if entry.get("id") == cid:
                        status = entry.get("status")
                        if status == "complete" and entry.get("audio_url"):
                            done[cid] = entry["audio_url"]
                        elif status == "failed":
                            raise SunoError(f"clip {cid} failed: {entry}")
                        break
            if len(done) < len(clip_ids):
                time.sleep(self.cfg.suno_poll_interval_s)

        if not done:
            raise SunoError("timeout waiting for any clip")

        paths: List[Path] = []
        for i, cid in enumerate(clip_ids):
            if cid not in done:
                continue
            p = self.cfg.cache_dir / f"{cache_key}__cand{i}__{cid}.mp3"
            self._download(done[cid], p)
            paths.append(p)
        return paths

    def _feed(self, clip_id: str) -> list:
        """Poll a single clip. Network errors return [] so the outer poll loop
        keeps retrying without burning a fresh Suno generation."""
        try:
            r = SESSION.get(
                f"{self.cfg.suno_api_base}/feed/{clip_id}",
                headers={"Authorization": f"Bearer {self.cfg.suno_api_key}"},
                timeout=30,
            )
        except requests.exceptions.RequestException as e:
            print(f"[suno] feed {clip_id[:8]} network err: {type(e).__name__}; will retry next tick")
            return []
        if r.status_code != 200:
            return []
        try:
            data = r.json()
        except ValueError:
            return []
        return data if isinstance(data, list) else data.get("data", [])

    def _download(self, url: str, dest: Path) -> None:
        r = SESSION.get(url, stream=True, timeout=120)
        r.raise_for_status()
        dest.parent.mkdir(parents=True, exist_ok=True)
        with dest.open("wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

    # ---- cache -----------------------------------------------------------

    def _payload_hash(self, payload: dict) -> str:
        canon = json.dumps(payload, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(canon.encode("utf-8")).hexdigest()[:16]

    def _cache_lookup(self, key: str) -> List[Path]:
        files = sorted(self.cfg.cache_dir.glob(f"{key}__cand*.mp3"))
        return files

    def _cache_store(self, key: str, files: List[Path], payload: dict) -> None:
        meta = self.cfg.cache_dir / f"{key}__payload.json"
        meta.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
