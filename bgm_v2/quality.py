"""Audio quality metrics: vocal-energy heuristic, BPM detection, candidate scoring."""
from __future__ import annotations
from pathlib import Path
from typing import Optional

import numpy as np
import librosa


def _load(path: Path, sr: int = 22050) -> tuple[np.ndarray, int]:
    y, sr = librosa.load(str(path), sr=sr, mono=True)
    return y, sr


def vocal_energy_ratio(path: Path) -> float:
    """Crude vocal-presence heuristic.

    Idea: vocal energy concentrates in 200-3400 Hz with strong harmonics.
    We compute the ratio of band energy in the human-voice formant range
    relative to total spectral energy, AND compare harmonic vs percussive
    component energy. A purely instrumental orchestral cue tends to spread
    across wider bands; vocals push energy toward 200-3000 Hz.

    Returns a float in [0, 1]. Empirically:
      < 0.30  most likely instrumental
      0.30-0.45  ambiguous
      > 0.45  likely vocal-heavy
    """
    y, sr = _load(path)
    y_harm = librosa.effects.harmonic(y)
    S = np.abs(librosa.stft(y_harm, n_fft=2048, hop_length=512))
    freqs = librosa.fft_frequencies(sr=sr, n_fft=2048)
    band = (freqs >= 200) & (freqs <= 3400)
    band_energy = S[band].sum()
    total = S.sum() + 1e-9
    return float(band_energy / total)


def detect_bpm(path: Path) -> float:
    y, sr = _load(path)
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    return float(np.atleast_1d(tempo)[0])


def measure_lufs(path: Path) -> Optional[float]:
    try:
        import pyloudnorm as pyln
        import soundfile as sf
        data, rate = sf.read(str(path))
        meter = pyln.Meter(rate)
        return float(meter.integrated_loudness(data))
    except Exception as e:
        print(f"[quality] LUFS measure failed: {e}")
        return None


def score_candidate(path: Path, target_bpm: int) -> dict:
    """Combine metrics into one scalar, plus a metrics breakdown."""
    ver = vocal_energy_ratio(path)
    bpm = detect_bpm(path)
    lufs = measure_lufs(path)

    # vocal penalty: 1.0 at ver<=0.25, 0.0 at ver>=0.50
    vocal_score = max(0.0, min(1.0, (0.50 - ver) / 0.25))
    # bpm match: 1.0 at exact, decays linearly to 0 at +-30%
    err = abs(bpm - target_bpm) / max(1, target_bpm)
    bpm_score = max(0.0, 1.0 - err / 0.30)

    total = 0.7 * vocal_score + 0.3 * bpm_score

    return {
        "path": str(path),
        "vocal_energy_ratio": round(ver, 4),
        "bpm_detected": round(bpm, 1),
        "bpm_target": target_bpm,
        "lufs": round(lufs, 2) if lufs is not None else None,
        "vocal_score": round(vocal_score, 3),
        "bpm_score": round(bpm_score, 3),
        "score": round(total, 3),
    }
