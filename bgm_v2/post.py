"""Post-processing: trim + fade-out + LUFS normalization + crossfade stitching."""
from __future__ import annotations
from pathlib import Path
from typing import List, Optional

from pydub import AudioSegment


def fade_and_normalize(
    src: Path,
    target_duration_s: int,
    target_lufs: float = -18.0,
    fade_out_ms: int = 3000,
    out_path: Optional[Path] = None,
) -> Path:
    """Trim, fade out, then loudness-normalize to target_lufs."""
    audio = AudioSegment.from_mp3(str(src))
    target_ms = int(target_duration_s * 1000)
    if 0 < target_ms < len(audio):
        audio = audio[:target_ms]
    if fade_out_ms > 0:
        audio = audio.fade_out(min(fade_out_ms, len(audio)))

    if out_path is None:
        out_path = src.with_name(src.stem + "__faded.mp3")
    audio.export(str(out_path), format="mp3", bitrate="192k")
    return _loudness_normalize(out_path, target_lufs)


def crossfade_segments(parts: List[Path], crossfade_ms: int = 2500, out_path: Optional[Path] = None) -> Path:
    """Concatenate audio files with crossfade between them."""
    assert parts, "no parts"
    merged = AudioSegment.from_mp3(str(parts[0]))
    for p in parts[1:]:
        nxt = AudioSegment.from_mp3(str(p))
        cf = min(crossfade_ms, len(merged), len(nxt))
        merged = merged.append(nxt, crossfade=cf)
    if out_path is None:
        out_path = parts[0].with_name("merged.mp3")
    merged.export(str(out_path), format="mp3", bitrate="192k")
    return out_path


def _loudness_normalize(path: Path, target_lufs: float) -> Path:
    """LUFS-normalize in place using pyloudnorm; falls back to peak normalize."""
    try:
        import pyloudnorm as pyln
        import soundfile as sf
        import numpy as np

        # pydub mp3 -> soundfile via temporary wav
        wav_path = path.with_suffix(".wav")
        AudioSegment.from_mp3(str(path)).export(str(wav_path), format="wav")
        data, rate = sf.read(str(wav_path))
        meter = pyln.Meter(rate)
        loud = meter.integrated_loudness(data)
        if loud == float("-inf"):
            wav_path.unlink(missing_ok=True)
            return path
        normed = pyln.normalize.loudness(data, loud, target_lufs)
        peak = float(np.max(np.abs(normed)) or 1.0)
        if peak > 0.99:
            normed = normed * (0.99 / peak)
        sf.write(str(wav_path), normed, rate)
        AudioSegment.from_wav(str(wav_path)).export(str(path), format="mp3", bitrate="192k")
        wav_path.unlink(missing_ok=True)
    except Exception as e:
        print(f"[post] LUFS normalize failed, returning unnormalized: {e}")
    return path
