"""Gera versões aumentadas (ângulo, perspectiva, ruído) para treino de OCR documental."""

from __future__ import annotations

import argparse
import random
from pathlib import Path
from typing import Iterable, List

try:
    import cv2  # type: ignore
except Exception as exc:  # noqa: BLE001
    raise SystemExit(
        "OpenCV não disponível. Instale com: pip install opencv-python"
    ) from exc

try:
    import numpy as np  # type: ignore
except Exception as exc:  # noqa: BLE001
    raise SystemExit("Numpy não disponível. Instale com: pip install numpy") from exc


SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input-root",
        required=True,
        type=Path,
        help="Raiz do dataset original: <tipo>/<lado>/*.jpg",
    )
    parser.add_argument(
        "--output-root",
        required=True,
        type=Path,
        help="Raiz do dataset aumentado (mesma estrutura).",
    )
    parser.add_argument(
        "--copies",
        type=int,
        default=4,
        help="Quantidade de cópias aumentadas por imagem.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Seed pseudoaleatória para reprodutibilidade.",
    )
    return parser.parse_args()


def iter_images(root: Path) -> Iterable[Path]:
    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
            yield path


def rotate_bound(image, angle: float):
    h, w = image.shape[:2]
    center = (w / 2.0, h / 2.0)
    matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    cos = abs(matrix[0, 0])
    sin = abs(matrix[0, 1])

    new_w = int((h * sin) + (w * cos))
    new_h = int((h * cos) + (w * sin))

    matrix[0, 2] += (new_w / 2) - center[0]
    matrix[1, 2] += (new_h / 2) - center[1]

    return cv2.warpAffine(
        image,
        matrix,
        (new_w, new_h),
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_REPLICATE,
    )


def random_perspective(image):
    h, w = image.shape[:2]
    max_shift = 0.06
    dx = int(w * max_shift)
    dy = int(h * max_shift)

    src = np.float32([[0, 0], [w - 1, 0], [w - 1, h - 1], [0, h - 1]])
    dst = np.float32(
        [
            [random.randint(0, dx), random.randint(0, dy)],
            [w - 1 - random.randint(0, dx), random.randint(0, dy)],
            [w - 1 - random.randint(0, dx), h - 1 - random.randint(0, dy)],
            [random.randint(0, dx), h - 1 - random.randint(0, dy)],
        ]
    )

    matrix = cv2.getPerspectiveTransform(src, dst)
    return cv2.warpPerspective(
        image,
        matrix,
        (w, h),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_REPLICATE,
    )


def random_brightness_contrast(image):
    alpha = random.uniform(0.75, 1.35)
    beta = random.randint(-30, 30)
    adjusted = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
    return adjusted


def random_blur_noise(image):
    output = image.copy()
    if random.random() < 0.6:
        kernel = random.choice([3, 5])
        output = cv2.GaussianBlur(output, (kernel, kernel), 0)

    if random.random() < 0.7:
        sigma = random.uniform(3.0, 16.0)
        noise = np.random.normal(0, sigma, output.shape).astype(np.float32)
        output = np.clip(output.astype(np.float32) + noise, 0, 255).astype(np.uint8)

    return output


def augment(image, copies: int) -> List:
    outputs: List = []
    for _ in range(max(0, copies)):
        work = image.copy()
        work = rotate_bound(work, random.uniform(-18.0, 18.0))
        work = random_perspective(work)
        work = random_brightness_contrast(work)
        work = random_blur_noise(work)
        outputs.append(work)
    return outputs


def main() -> None:
    args = parse_args()
    random.seed(args.seed)
    np.random.seed(args.seed)

    input_root = args.input_root.expanduser().resolve()
    output_root = args.output_root.expanduser().resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    if not input_root.exists():
        raise SystemExit(f"Diretório de entrada inexistente: {input_root}")

    total_original = 0
    total_generated = 0

    for image_path in iter_images(input_root):
        rel = image_path.relative_to(input_root)
        destination_dir = (output_root / rel.parent).resolve()
        destination_dir.mkdir(parents=True, exist_ok=True)

        image = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
        if image is None:
            continue

        total_original += 1

        copy_path = destination_dir / image_path.name
        cv2.imwrite(str(copy_path), image)

        for index, generated in enumerate(augment(image, args.copies), start=1):
            generated_path = (
                destination_dir / f"{image_path.stem}_aug{index}{image_path.suffix}"
            )
            cv2.imwrite(str(generated_path), generated)
            total_generated += 1

    print(f"Imagens originais processadas: {total_original}")
    print(f"Imagens aumentadas geradas: {total_generated}")
    print(f"Saída: {output_root}")


if __name__ == "__main__":
    main()
