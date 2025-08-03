#!/usr/bin/env python3
"""Export a YOLO .pt checkpoint to ONNX for deployment.

This script prefers the Ultralytics Python API and falls back to the
`yolo export` CLI if the API is not available. It exposes common export
parameters and prints the ONNX output path on success.

Usage examples:
  python export_yolo_to_onnx.py \
      --model monkeyocr/model_weight/Structure/doclayout_yolo_docstructbench_imgsz1280_2501.pt \
      --imgsz 1280 \
      --opset 12 \
      --dynamic \
      --simplify

  python export_yolo_to_onnx.py \
      --model best.pt \
      --imgsz 1280 1280 \
      --opset 13 \
      --device 0
"""

from __future__ import annotations

import argparse
import pathlib
import shlex
import subprocess
import sys
from typing import List, Optional, Tuple, Union


def parse_image_size(values: List[str]) -> Union[int, Tuple[int, int]]:
    """Parse image size argument to either an int or an (h, w) tuple.

    Accepts one value (square) or two values (height width). Raises
    ValueError otherwise.
    """
    if len(values) == 1:
        return int(values[0])
    if len(values) == 2:
        height, width = int(values[0]), int(values[1])
        return height, width
    raise ValueError("--imgsz must be one or two integers: H [W]")


def try_ultralytics_export(
    model_path: str,
    imgsz: Union[int, Tuple[int, int]],
    opset: int,
    dynamic: bool,
    half: bool,
    simplify: bool,
    device: str,
    output: Optional[str],
) -> Optional[pathlib.Path]:
    """Attempt export via Ultralytics Python API. Return ONNX path or None.

    The API returns a path-like object in newer versions; handle common cases.
    """
    try:
        from ultralytics import YOLO  # type: ignore
    except Exception:
        return None

    model = YOLO(model_path)
    export_result = model.export(
        format="onnx",
        imgsz=imgsz,
        opset=opset,
        dynamic=dynamic,
        half=half,
        simplify=simplify,
        device=device,
    )

    # Ultralytics may return a Path or a list of files; normalize.
    onnx_path: Optional[pathlib.Path] = None
    if isinstance(export_result, (str, pathlib.Path)):
        onnx_path = pathlib.Path(export_result)
    elif isinstance(export_result, (list, tuple)) and export_result:
        onnx_path = pathlib.Path(str(export_result[0]))

    if onnx_path is None:
        # Attempt to infer output in the same directory as model
        candidate = pathlib.Path(model_path).with_suffix(".onnx")
        if candidate.exists():
            onnx_path = candidate

    if onnx_path and output:
        dst = pathlib.Path(output)
        dst.parent.mkdir(parents=True, exist_ok=True)
        onnx_path.replace(dst)
        return dst
    return onnx_path


def run_cli_export(
    model_path: str,
    imgsz: Union[int, Tuple[int, int]],
    opset: int,
    dynamic: bool,
    half: bool,
    simplify: bool,
    device: str,
    output: Optional[str],
) -> pathlib.Path:
    """Fallback to the `yolo export` CLI. Return the ONNX path.

    This requires the `ultralytics` CLI to be installed and available.
    """
    # Compose CLI image size
    if isinstance(imgsz, tuple):
        imgsz_value = f"{imgsz[0]} {imgsz[1]}"
    else:
        imgsz_value = str(imgsz)

    args = {
        "model": model_path,
        "format": "onnx",
        "opset": str(opset),
        "imgsz": imgsz_value,
        "dynamic": str(dynamic).lower(),
        "half": str(half).lower(),
        "simplify": str(simplify).lower(),
        "device": device,
    }

    cli_parts = [
        sys.executable,
        "-m",
        "ultralytics",
        "export",
    ] + [f"{k}={v}" for k, v in args.items()]

    command = " ".join(shlex.quote(p) for p in cli_parts)
    completed = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)

    # Heuristic for output path: prefer explicit output if given; else derive.
    candidate = pathlib.Path(model_path).with_suffix(".onnx")
    if output:
        dst = pathlib.Path(output)
        if candidate.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            candidate.replace(dst)
            return dst
        # If CLI saved elsewhere, try to locate any .onnx in cwd
        onnx_files = list(pathlib.Path.cwd().glob("*.onnx"))
        if onnx_files:
            onnx_files[0].replace(dst)
            return dst
        raise FileNotFoundError("Export succeeded but ONNX file was not found; please specify --output")
    # Without explicit output, prefer model_path.with_suffix('.onnx')
    if candidate.exists():
        return candidate
    # Otherwise, pick the newest ONNX in cwd
    onnx_files = sorted(pathlib.Path.cwd().glob("*.onnx"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not onnx_files:
        raise FileNotFoundError("Export succeeded but ONNX file was not found")
    return onnx_files[0]


def main() -> None:
    """Parse arguments and perform export to ONNX.

    Prints the absolute path to the produced ONNX file on success and exits 0.
    """
    parser = argparse.ArgumentParser(description="Export YOLO .pt checkpoint to ONNX")
    parser.add_argument("--model", required=True, help="Path to YOLO .pt checkpoint")
    parser.add_argument(
        "--imgsz",
        nargs="+",
        default=["1280"],
        help="Image size: one int (square) or two ints (H W). Default: 1280",
    )
    parser.add_argument("--opset", type=int, default=12, help="ONNX opset version. Default: 12")
    parser.add_argument("--dynamic", action="store_true", help="Enable dynamic input shapes")
    parser.add_argument("--half", action="store_true", help="Export with FP16 where possible")
    parser.add_argument("--simplify", action="store_true", help="Run onnxsim simplification")
    parser.add_argument("--device", default="cpu", help="Device for export, e.g., 'cpu', '0' for GPU")
    parser.add_argument("--output", default=None, help="Optional output .onnx path")

    args = parser.parse_args()

    model_path = pathlib.Path(args.model)
    if not model_path.exists():
        raise FileNotFoundError(f"Model checkpoint not found: {model_path}")

    image_size = parse_image_size(args.imgsz)

    # Try Python API first
    onnx_path = try_ultralytics_export(
        model_path=str(model_path),
        imgsz=image_size,
        opset=args.opset,
        dynamic=bool(args.dynamic),
        half=bool(args.half),
        simplify=bool(args.simplify),
        device=str(args.device),
        output=args.output,
    )

    if onnx_path is None:
        # Fallback to CLI
        onnx_path = run_cli_export(
            model_path=str(model_path),
            imgsz=image_size,
            opset=args.opset,
            dynamic=bool(args.dynamic),
            half=bool(args.half),
            simplify=bool(args.simplify),
            device=str(args.device),
            output=args.output,
        )

    print(str(onnx_path.resolve()))


if __name__ == "__main__":
    main()


