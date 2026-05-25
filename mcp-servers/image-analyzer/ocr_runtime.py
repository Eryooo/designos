"""Local OCR runtime helpers for image-analyzer.

This module intentionally uses stdlib-only dependencies so it can also power
preflight probes outside the repo virtualenv.
"""

from __future__ import annotations

import base64
import csv
import json
import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

_OCR_PROBE_PNG_BASE64 = """
iVBORw0KGgoAAAANSUhEUgAAAeAAAAC0CAIAAADD3miXAAAH5ElEQVR4nO3dTWhUVx/A4ZtEDSOo
0+qqFV1IURRDk0FhEq0TvyIq7nTlwiJ2URSkYCwIWi00xFekIAVracWlpUVBF47xE/wAhbQNmHQr
ZlURx12N0Vvaed8hJGm7eCf2n87zrO6cOedyQPh5OZlk6tI0TQCIp/6f3gAA4xNogKAEGiAogQYI
SqABghJogKAEGiAogQYISqABghJogKAEGiAogQYISqABghJogKAEGiAogQYISqABghJogKAEGiAo
gQYISqABghJogKAEGiAogQYISqABaiDQ2Wx21Mjp06dzuVw+n8/lcmfOnCkPnjp1avny5a2trRs3
bhwcHBy1NpPJtLe3/8U9AWrElIm7dbFY/Prrr69evZrNZkul0ubNm99+++00Tc+dO3f79u2pU6d2
d3fv3LmzWCyOXNXY2Dg8PHzjxo1CoTBxewOo6SOO//yh/AiczWaPHj3a3d197NixI0eOTJ06NUmS
Dz/8MJPJvHz5ctTCw4cPHzp0aOI2BlDrgR4YGGhubq68bGlp6e/vf/DgQVNTU3lkxowZ58+fb2ho
GLVw9erVSZJcv3594vYGEN/r+yFhmqZ1dXXDw8Pll8ePHy8UCosWLRp3sodogAkM9OLFi3t7eysv
e3t7lyxZ8s477/T19SVJ8tFHH50/f/7hw4fjri0UCg0NDdeuXfMvBNSsCQz0vn37Ojs7nz17liRJ
qVTav39/Z2fnBx98cPDgwRcvXiRJ8sUXX4w936jwEA3UuGp+imNoaGjFihXl67a2tu7u7sHBwfb2
9sbGxqGhoT179qxZsyZN04GBgaamprfeemv79u1TpvzpBt57771p06Y9f/68ijsEmETq0jT9p/cA
wDj8JiFAUAINEJRAAwQl0ABBCTRAUAINEJRAAwQl0ABBCTRAUAINEJRAAwQl0ABBCTRAUAINEJRA
A9RAoHt7e9evX9/e3r5u3bpHjx6Vv8y78m7levr06YVCYdWqVc3NzRcuXEiSJJPJbNu2rTJz+/bt
mUxm5Kpz584V/jBlypTyxXfffVfFnQP8y/9g/7vvvnvx4sW5c+d+//3333777dmzZ7PZbKlUKr9b
ua5c/PTTT1u2bHn48GE2m50/f35vb29DQ0Oapq2trQMDA6Mmj7oJwL9eNZ+gf/nll19//TVJki1b
tuzevftv5zc1NVW+8qqlpeX+/ftJkvz4449NTU1V3BXAJFXNQH/22WcrV67cuXPnrVu3Vq5c+bfz
r1279vnnn5evOzo6isVikiTFYrGjo6OKuwKYpKoZ6B07dvT3969YsWLv3r2ffPLJn00bGhoqFAr5
fL6jo+PEiRPlwfXr11+5cqVc7bVr11ZxVwC1HujHjx/fuXPnjTfeeP/9969cuXLy5Mnf715f//Ll
yyRJhoeHK6cZ06ZNu3Hjxt27d3/44Yd79+6VB9988836+vryjxZnzpxZrV0BTF5VC3RdXd22bdvK
hX3y5Mm8efOSJFm2bFlPT0/54GLZsmWjlsyePXvBggWVlxs2bDhw4IDHZ4Cy/z7V/v/mzJlz6tSp
rVu3ZjKZhoaGb775JkmSEydO7Nq1q6urK0mSr776auQRR3397/83fPnll5U7bNq06cCBA319fdXa
EsCkVs2P2QFQRX6TECAogQYISqABghJogKAEGiAogQYISqABghJogKAEGiAogQYISqABghJogKAE
GiAogQYISqABaiDQ06dPL/zP8ePHKyOrVq1qaWm5efPmuCOnT5/O5XL5fD6Xy505c2bkrUZOA6g5
afXMmjXrz0b6+vqWLl06duTSpUttbW1Pnz5N0/Tp06dtbW09PT3jLgSoNdX8RpVsNlsqlcYdSdN0
zpw5T548GTXS3Nz86aef5vP58vw7d+4cOnSop6dn7MJqbRJgsnhNZ9CXL19evXr12JGBgYHm5ubK
YEtLS39//18vBKgRVfvS2Mq3wZavu7q68vl8eeTFixc///zzgwcPKnMqI7lcbuQdfn+kr6sbO62K
mwSYLF7TEcfRo0dfvXr18ccfjxq5evXq4cOHW1tby/Nv37595MiRYrE4dmG1NgkwWbymI45169bd
u3dv7Mi+ffs6OzufPXuWJEmpVNq/f39nZ+dfLwSoERN1xJHP57u6uipvLVy4sK+v79WrV6NG1q5d
Ozg42N7e3tjYODQ0tGfPnjVr1oy8Z2Vhfb2PbAO1pZpHHABUkcdSgKAEGiAogQYISqABghJogKAE
GiAogQYISqABghJogKAEGiAogQYISqABghJogKAEGiAogQYISqABghJogKAEGiAogQYISqABghJo
gKAEGiAogQYISqABghJogKAEGiAogQYISqABghJogKAEGiAogQYISqABghJogKAEGiAogQYISqAB
ghJogKAEGiAogQYISqABghJogKAEGiAogQYISqABghJogKAEGiAogQYISqABghJogKAEGiAogQYI
SqABghJogKAEGiAogQYISqABghJogKAEGiAogQYISqABghJogKAEGiAogQYISqABghJogKAEGiAo
gQYISqABghJogKAEGiAogQYISqABghJogKAEGiAogQYISqABghJogKAEGiAogQYISqABghJogKAE
GiAogQYISqABghJogKAEGiAogQYISqABghJogKAEGiAogQYISqABghJogKAEGiAogQYISqABghJo
gCSm3wB+n7LSCpdlOgAAAABJRU5ErkJggg==
""".strip()


@dataclass(frozen=True, slots=True)
class OCRLine:
    text: str
    confidence: float


@dataclass(frozen=True, slots=True)
class OCRResult:
    backend: str | None
    lines: tuple[OCRLine, ...]
    raw_text: str
    error: str | None = None


@dataclass(frozen=True, slots=True)
class OCRProbeResult:
    available: bool
    backend: str | None
    error: str | None = None


def probe_ocr_backend() -> OCRProbeResult:
    """Probe available OCR backends with a bundled sample image."""
    with tempfile.TemporaryDirectory(prefix="designos-ocr-probe-") as tmp:
        sample_path = Path(tmp) / "probe.png"
        sample_path.write_bytes(base64.b64decode(_OCR_PROBE_PNG_BASE64))

        errors: list[str] = []
        for backend in ("tesseract", "vision_swift"):
            result = _run_backend(sample_path, backend=backend)
            if result.backend and result.lines:
                return OCRProbeResult(available=True, backend=result.backend)
            if result.error:
                errors.append(f"{backend}: {result.error}")
        return OCRProbeResult(
            available=False,
            backend=None,
            error="; ".join(errors) if errors else "no local OCR backend available",
        )


def run_ocr(image_path: Path, *, preferred_backend: str | None = None) -> OCRResult:
    """Run OCR against a single image using the first working backend."""
    backends: list[str] = []
    if preferred_backend:
        backends.append(preferred_backend)
    for backend_name in ("tesseract", "vision_swift"):
        if backend_name not in backends:
            backends.append(backend_name)
    for backend in backends:
        result = _run_backend(image_path, backend=backend)
        if result.backend and result.lines:
            return result
        if result.backend and result.raw_text.strip():
            return result
    return OCRResult(
        backend=None,
        lines=(),
        raw_text="",
        error="no local OCR backend available or OCR extraction failed",
    )


def _run_backend(image_path: Path, *, backend: str) -> OCRResult:
    if backend == "tesseract":
        return _run_tesseract(image_path)
    if backend == "vision_swift":
        return _run_swift_vision(image_path)
    return OCRResult(backend=None, lines=(), raw_text="", error=f"unknown backend: {backend}")


def _run_tesseract(image_path: Path) -> OCRResult:
    if shutil.which("tesseract") is None:
        return OCRResult(backend=None, lines=(), raw_text="", error="tesseract command not found")

    cmd = [
        "tesseract",
        str(image_path),
        "stdout",
        "--psm",
        "6",
        "tsv",
    ]
    try:
        proc = subprocess.run(
            cmd,
            check=False,
            capture_output=True,
            text=True,
            timeout=20,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return OCRResult(backend=None, lines=(), raw_text="", error=str(exc))
    if proc.returncode != 0:
        return OCRResult(
            backend=None,
            lines=(),
            raw_text="",
            error=(proc.stderr or proc.stdout or "tesseract failed").strip(),
        )

    lines = _parse_tesseract_tsv(proc.stdout)
    raw_text = "\n".join(line.text for line in lines)
    return OCRResult(
        backend="tesseract",
        lines=tuple(lines),
        raw_text=raw_text,
    )


def _parse_tesseract_tsv(raw_tsv: str) -> list[OCRLine]:
    rows = csv.DictReader(raw_tsv.splitlines(), delimiter="\t")
    grouped: dict[tuple[str, str, str, str], list[tuple[str, float]]] = {}
    for row in rows:
        text = (row.get("text") or "").strip()
        if not text:
            continue
        try:
            conf = float(row.get("conf") or "-1")
        except ValueError:
            conf = -1.0
        key = (
            row.get("page_num") or "0",
            row.get("block_num") or "0",
            row.get("par_num") or "0",
            row.get("line_num") or "0",
        )
        grouped.setdefault(key, []).append((text, conf))

    parsed: list[OCRLine] = []
    for key in sorted(grouped):
        parts = grouped[key]
        joined = " ".join(text for text, _conf in parts).strip()
        if not joined:
            continue
        valid = [conf for _text, conf in parts if conf >= 0]
        avg_conf = (sum(valid) / len(valid) / 100.0) if valid else 0.5
        parsed.append(OCRLine(text=joined, confidence=max(0.0, min(avg_conf, 1.0))))
    return parsed


def _run_swift_vision(image_path: Path) -> OCRResult:
    if shutil.which("swift") is None:
        return OCRResult(backend=None, lines=(), raw_text="", error="swift command not found")

    helper = Path(__file__).with_name("vision_ocr.swift")
    if not helper.exists():
        return OCRResult(backend=None, lines=(), raw_text="", error="vision_ocr.swift not found")

    home = Path(tempfile.gettempdir()) / "designos-swift-home"
    (home / ".cache" / "clang" / "ModuleCache").mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    env["HOME"] = str(home)
    env.setdefault("CLANG_MODULE_CACHE_PATH", str(home / ".cache" / "clang" / "ModuleCache"))
    cmd = ["swift", str(helper), str(image_path)]
    try:
        proc = subprocess.run(
            cmd,
            check=False,
            capture_output=True,
            text=True,
            timeout=35,
            env=env,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return OCRResult(backend=None, lines=(), raw_text="", error=str(exc))
    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "swift vision OCR failed").strip()
        return OCRResult(backend=None, lines=(), raw_text="", error=err)

    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        return OCRResult(backend=None, lines=(), raw_text="", error=f"invalid swift OCR JSON: {exc}")

    raw_lines = payload.get("lines", [])
    lines: list[OCRLine] = []
    if isinstance(raw_lines, list):
        for entry in raw_lines:
            if not isinstance(entry, dict):
                continue
            text = str(entry.get("text", "")).strip()
            if not text:
                continue
            try:
                confidence = float(entry.get("confidence", 0.5))
            except (TypeError, ValueError):
                confidence = 0.5
            lines.append(OCRLine(text=text, confidence=max(0.0, min(confidence, 1.0))))

    raw_text = str(payload.get("raw_text", "")).strip()
    if not raw_text and lines:
        raw_text = "\n".join(line.text for line in lines)
    return OCRResult(
        backend="vision_swift",
        lines=tuple(lines),
        raw_text=raw_text,
        error=None,
    )


__all__ = ["OCRLine", "OCRProbeResult", "OCRResult", "probe_ocr_backend", "run_ocr"]
