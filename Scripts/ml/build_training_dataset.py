"""Constrói dataset JSONL para treino do classificador de tipo/lado a partir de imagens."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable, List, Tuple

try:
    from PIL import Image, ImageEnhance, ImageOps  # type: ignore
except Exception as exc:  # noqa: BLE001
    raise SystemExit("Pillow indisponível. Instale com: pip install Pillow") from exc

try:
    import pytesseract  # type: ignore
except Exception as exc:  # noqa: BLE001
    raise SystemExit(
        "pytesseract indisponível. Instale com: pip install pytesseract"
    ) from exc

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input-root",
        required=True,
        type=Path,
        help="Dataset em estrutura: <tipo>/<lado>/*.jpg",
    )
    parser.add_argument(
        "--output-jsonl",
        required=True,
        type=Path,
        help="Arquivo JSONL de saída.",
    )
    parser.add_argument(
        "--lang",
        default="por+eng",
        help="Idioma do OCR para o Tesseract.",
    )
    return parser.parse_args()


def iter_images(root: Path) -> Iterable[Path]:
    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
            yield path


def infer_labels(root: Path, image_path: Path) -> Tuple[str, str]:
    rel = image_path.relative_to(root)
    parts = rel.parts
    if len(parts) < 3:
        raise ValueError(
            "Estrutura inválida. Use: <input-root>/<doc_type>/<doc_side>/<arquivo>"
        )
    doc_type = parts[0].upper()
    doc_side = parts[1].upper()
    return doc_type, doc_side


def preprocess_variants(image_obj):
    variants = [image_obj]
    gray = ImageOps.grayscale(image_obj)
    variants.append(gray)
    contrast = ImageEnhance.Contrast(gray).enhance(2.1)
    variants.append(contrast)
    sharp = ImageEnhance.Sharpness(contrast).enhance(1.6)
    variants.append(sharp)
    threshold = sharp.point([0] * 150 + [255] * 106)
    variants.append(threshold)
    return variants


def ocr_best_text(image_obj, lang: str) -> str:
    best_text = ""
    best_score = -1
    configs = ("--oem 1 --psm 6", "--oem 1 --psm 11", "--oem 1 --psm 4")

    for variant in preprocess_variants(image_obj):
        for config in configs:
            text = ""
            try:
                text = pytesseract.image_to_string(variant, lang=lang, config=config)
            except Exception:
                try:
                    text = pytesseract.image_to_string(variant, config=config)
                except Exception:
                    continue

            cleaned = " ".join((text or "").split())
            if not cleaned:
                continue
            score = len(cleaned)
            if "cpf" in cleaned.lower():
                score += 50
            if "registro geral" in cleaned.lower() or "rg" in cleaned.lower():
                score += 35
            if "cnh" in cleaned.lower() or "habilitacao" in cleaned.lower():
                score += 35

            if score > best_score:
                best_score = score
                best_text = cleaned

    return best_text


def main() -> None:
    args = parse_args()
    input_root = args.input_root.expanduser().resolve()
    output_jsonl = args.output_jsonl.expanduser().resolve()

    if not input_root.exists():
        raise SystemExit(f"Diretório de entrada inexistente: {input_root}")

    output_jsonl.parent.mkdir(parents=True, exist_ok=True)

    rows: List[dict] = []

    for image_path in iter_images(input_root):
        try:
            doc_type, doc_side = infer_labels(input_root, image_path)
        except ValueError:
            continue

        try:
            with Image.open(image_path) as img:
                text = ocr_best_text(img.convert("RGB"), lang=args.lang)
        except Exception:
            continue

        if not text:
            continue

        rows.append(
            {
                "file_path": str(image_path),
                "doc_type": doc_type,
                "doc_side": doc_side,
                "text": text,
            }
        )

    with output_jsonl.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"Amostras válidas: {len(rows)}")
    print(f"JSONL gerado em: {output_jsonl}")


if __name__ == "__main__":
    main()
