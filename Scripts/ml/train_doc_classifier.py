"""Treina classificador de tipo/lado do documento a partir de dataset JSONL."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Tuple

try:
    import joblib  # type: ignore
except Exception as exc:  # noqa: BLE001
    raise SystemExit("joblib indisponível. Instale com: pip install joblib") from exc

try:
    from sklearn.feature_extraction.text import TfidfVectorizer  # type: ignore
    from sklearn.metrics import accuracy_score  # type: ignore
    from sklearn.model_selection import train_test_split  # type: ignore
    from sklearn.pipeline import Pipeline  # type: ignore
    from sklearn.svm import LinearSVC  # type: ignore
except Exception as exc:  # noqa: BLE001
    raise SystemExit(
        "scikit-learn indisponível. Instale com: pip install scikit-learn"
    ) from exc


MIN_SAMPLES = 40


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dataset-jsonl",
        required=True,
        type=Path,
        help="Arquivo JSONL com campos: text, doc_type, doc_side.",
    )
    parser.add_argument(
        "--output-model",
        default=Path("app/models/doc_classifier.joblib"),
        type=Path,
        help="Caminho do artefato .joblib.",
    )
    parser.add_argument(
        "--test-size",
        type=float,
        default=0.2,
        help="Percentual para validação holdout.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Seed para split reprodutível.",
    )
    return parser.parse_args()


def load_rows(path: Path) -> Tuple[List[str], List[str], List[str]]:
    texts: List[str] = []
    types: List[str] = []
    sides: List[str] = []

    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except Exception:
                continue

            text = str(row.get("text", "")).strip()
            doc_type = str(row.get("doc_type", "")).strip().upper()
            doc_side = str(row.get("doc_side", "")).strip().upper()
            if not text or not doc_type or not doc_side:
                continue

            texts.append(text)
            types.append(doc_type)
            sides.append(doc_side)

    return texts, types, sides


def build_pipeline() -> Pipeline:
    return Pipeline(
        [
            (
                "tfidf",
                TfidfVectorizer(
                    lowercase=True,
                    ngram_range=(1, 3),
                    min_df=2,
                    max_features=40000,
                ),
            ),
            ("clf", LinearSVC()),
        ]
    )


def main() -> None:
    args = parse_args()
    dataset_path = args.dataset_jsonl.expanduser().resolve()
    output_model = args.output_model.expanduser().resolve()

    if not dataset_path.exists():
        raise SystemExit(f"Dataset JSONL inexistente: {dataset_path}")

    texts, types, sides = load_rows(dataset_path)
    if len(texts) < MIN_SAMPLES:
        raise SystemExit(
            f"Amostras insuficientes ({len(texts)}). Necessário pelo menos {MIN_SAMPLES}."
        )

    indices = list(range(len(texts)))
    train_idx, test_idx = train_test_split(
        indices,
        test_size=args.test_size,
        random_state=args.seed,
        stratify=types,
    )

    x_train = [texts[index] for index in train_idx]
    x_test = [texts[index] for index in test_idx]
    y_type_train = [types[index] for index in train_idx]
    y_type_test = [types[index] for index in test_idx]
    y_side_train = [sides[index] for index in train_idx]
    y_side_test = [sides[index] for index in test_idx]

    type_model = build_pipeline()
    side_model = build_pipeline()

    type_model.fit(x_train, y_type_train)
    side_model.fit(x_train, y_side_train)

    pred_type = type_model.predict(x_test)
    pred_side = side_model.predict(x_test)

    type_accuracy = accuracy_score(y_type_test, pred_type)
    side_accuracy = accuracy_score(y_side_test, pred_side)

    payload = {
        "type_model": type_model,
        "side_model": side_model,
        "metadata": {
            "samples": len(texts),
            "test_size": args.test_size,
            "seed": args.seed,
            "type_accuracy": float(type_accuracy),
            "side_accuracy": float(side_accuracy),
            "trained_at": datetime.now(timezone.utc).isoformat(),
            "source": str(dataset_path),
        },
    }

    output_model.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(payload, output_model)

    print(f"Amostras: {len(texts)}")
    print(f"Acurácia tipo: {type_accuracy:.4f}")
    print(f"Acurácia lado: {side_accuracy:.4f}")
    print(f"Modelo salvo em: {output_model}")


if __name__ == "__main__":
    main()
