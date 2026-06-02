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
        """Submit a music task (yunwu / suno-api schema). Returns [taskBatchId].

        我们的 BGM 是描述驱动的纯器乐，用灵感模式(gpt_description_prompt)，不传歌词。
        """
        url = f"{self.cfg.suno_api_base}/submit/music"
        headers = {
            "Authorization": f"Bearer {self.cfg.suno_api_key}",
            "Content-Type": "application/json",
        }
        desc = payload.get("gpt_description_prompt") or payload.get("prompt") or ""
        body = {
            "gpt_description_prompt": desc,
            "prompt": "",
            "make_instrumental": bool(payload.get("make_instrumental", True)),
            "mv": payload.get("mv") or self.cfg.suno_model,
        }
        if payload.get("tags"):
            body["tags"] = payload["tags"]
        if payload.get("title"):
            body["title"] = payload["title"]

        r = SESSION.post(url, headers=headers, json=body, timeout=60)
        if r.status_code != 200:
            raise SunoError(f"submit {r.status_code}: {r.text[:300]}")
        data = r.json()
        d = data.get("data")
        if isinstance(d, str):
            task_id = d
        elif isinstance(d, dict):
            task_id = d.get("taskBatchId") or d.get("task_id")
        else:
            task_id = None
        if not task_id:
            raise SunoError(f"no task id in response: {str(data)[:300]}")
        return [str(task_id)]

    def _wait_and_download(self, task_ids: List[str], cache_key: str) -> List[Path]:
        """Poll the batch task until clips complete, download all candidates."""
        task_id = task_ids[0]
        deadline = time.time() + self.cfg.suno_poll_timeout_s
        items: list = []
        while time.time() < deadline:
            data = self._fetch(task_id)
            items = data.get("items") or []
            if any(self._clip_status(it) == 40 for it in items):
                raise SunoError(f"clip failed: {items}")
            if items and all(self._clip_status(it) >= 30 and self._clip_url(it) for it in items):
                break
            if str(data.get("taskStatus", "")).lower() in ("success", "complete", "completed", "finished"):
                break
            time.sleep(self.cfg.suno_poll_interval_s)

        # 优先取完整(status>=30)的候选，否则退而取任何已有音频地址的
        ready = [it for it in items if self._clip_status(it) >= 30 and self._clip_url(it)]
        if not ready:
            ready = [it for it in items if self._clip_url(it)]
        if not ready:
            raise SunoError("no audio produced before timeout")

        paths: List[Path] = []
        for i, it in enumerate(ready):
            clip_id = it.get("clipId") or it.get("id") or str(i)
            p = self.cfg.cache_dir / f"{cache_key}__cand{i}__{clip_id}.mp3"
            self._download(self._clip_url(it), p)
            paths.append(p)
        return paths

    @staticmethod
    def _clip_url(it: dict) -> str:
        return it.get("cld2AudioUrl") or it.get("audioUrl") or it.get("audio_url") or ""

    @staticmethod
    def _clip_status(it: dict) -> int:
        try:
            return int(it.get("status") or 0)
        except (TypeError, ValueError):
            return 0

    def _fetch(self, task_id: str) -> dict:
        """Poll a batch task. Network errors return {} so the outer poll loop
        keeps retrying without burning a fresh Suno generation."""
        try:
            r = SESSION.get(
                f"{self.cfg.suno_api_base}/fetch/{task_id}",
                headers={"Authorization": f"Bearer {self.cfg.suno_api_key}"},
                timeout=30,
            )
        except requests.exceptions.RequestException as e:
            print(f"[suno] fetch {task_id[:8]} network err: {type(e).__name__}; will retry next tick")
            return {}
        if r.status_code != 200:
            return {}
        try:
            data = r.json()
        except ValueError:
            return {}
        return data.get("data") or {}

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
