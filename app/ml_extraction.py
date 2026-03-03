"""Extrator híbrido com pré-processamento de imagem e classificação de documento."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

try:
    import cv2  # type: ignore
except Exception:  # noqa: BLE001
    cv2 = None  # type: ignore[assignment]

try:
    import joblib  # type: ignore
except Exception:  # noqa: BLE001
    joblib = None  # type: ignore[assignment]

try:
    import numpy as np  # type: ignore
except Exception:  # noqa: BLE001
    np = None  # type: ignore[assignment]

try:
    from PIL import Image  # type: ignore
except Exception:  # noqa: BLE001
    Image = None  # type: ignore[assignment]

try:
    from .extraction import DocumentExtractor, ExtractionResult
except ImportError:
    from extraction import DocumentExtractor, ExtractionResult  # type: ignore

_UFS = {
    "AC",
    "AL",
    "AP",
    "AM",
    "BA",
    "CE",
    "DF",
    "ES",
    "GO",
    "MA",
    "MT",
    "MS",
    "MG",
    "PA",
    "PB",
    "PR",
    "PE",
    "PI",
    "RJ",
    "RN",
    "RS",
    "RO",
    "RR",
    "SC",
    "SP",
    "SE",
    "TO",
}


@dataclass
class _PerFileExtraction:
    file_name: str
    text: str
    fields: Dict[str, str]
    score: int
    doc_type: str
    doc_side: str
    warnings: List[str]


class _DocumentTypeSideClassifier:
    """Classificador opcional de tipo/lado baseado em texto OCR."""

    def __init__(self, model_path: Path) -> None:
        self.model_path = model_path
        self.type_model = None
        self.side_model = None
        self.warnings: List[str] = []
        self._load()

    def _load(self) -> None:
        if joblib is None:
            self.warnings.append(
                "Biblioteca 'joblib' ausente: classificação ML desativada; usando heurísticas."
            )
            return

        if not self.model_path.exists():
            self.warnings.append(
                f"Modelo ML não encontrado em {self.model_path}; usando heurísticas."
            )
            return

        try:
            payload = joblib.load(self.model_path)
        except Exception as exc:  # noqa: BLE001
            self.warnings.append(
                f"Falha ao carregar modelo ML ({self.model_path.name}): {exc}"
            )
            return

        if isinstance(payload, dict):
            self.type_model = payload.get("type_model")
            self.side_model = payload.get("side_model")

        if self.type_model is None or self.side_model is None:
            self.warnings.append(
                "Artefato ML inválido (esperado: type_model/side_model); usando heurísticas."
            )

    def predict(self, text: str, file_name: str = "") -> Tuple[str, str]:
        doc_type = "DESCONHECIDO"
        doc_side = "NAO_IDENTIFICADO"

        if self.type_model is not None and text.strip():
            try:
                predicted = self.type_model.predict([text])[0]
                doc_type = str(predicted).strip().upper() or doc_type
            except Exception:
                pass

        if self.side_model is not None and text.strip():
            try:
                predicted = self.side_model.predict([text])[0]
                doc_side = str(predicted).strip().upper() or doc_side
            except Exception:
                pass

        if doc_type in {"", "DESCONHECIDO"}:
            doc_type = self._heuristic_doc_type(text, file_name)
        if doc_side in {"", "NAO_IDENTIFICADO"}:
            doc_side = self._heuristic_doc_side(text, file_name)

        return doc_type, doc_side

    @staticmethod
    def _heuristic_doc_type(text: str, file_name: str = "") -> str:
        base = f"{file_name}\n{text}".lower()
        if any(
            marker in base
            for marker in (
                "carteira nacional de habilitacao",
                "permissao para dirigir",
                "detran",
                "categoria",
                "acc",
                "cnh",
            )
        ):
            return "CNH"
        if "registro geral" in base or re.search(r"\brg\b", base):
            return "RG"
        if "cadastro de pessoa fisica" in base or re.search(r"\bcpf\b", base):
            return "CPF"
        return "DESCONHECIDO"

    @staticmethod
    def _heuristic_doc_side(text: str, file_name: str = "") -> str:
        base = f"{file_name}\n{text}".lower()

        if any(marker in base for marker in ("_frente", "frente.", " frente ")):
            return "FRENTE"
        if any(marker in base for marker in ("_verso", "verso.", " verso ")):
            return "VERSO"

        front_score = 0
        back_score = 0

        front_tokens = (
            "registro geral",
            "nome",
            "data de nascimento",
            "cpf",
            "categoria",
            "validade",
            "1a habilitacao",
        )
        back_tokens = (
            "filiacao",
            "observacoes",
            "assinatura",
            "orgao expedidor",
            "expedicao",
            "local",
        )

        for token in front_tokens:
            if token in base:
                front_score += 1
        for token in back_tokens:
            if token in base:
                back_score += 1

        if front_score == back_score == 0:
            return "NAO_IDENTIFICADO"
        return "FRENTE" if front_score >= back_score else "VERSO"


class MLHybridDocumentExtractor:
    """Extrator local com técnicas de visão computacional para imagens difíceis."""

    SUPPORTED_IMAGES = DocumentExtractor.SUPPORTED_IMAGES

    def __init__(
        self,
        model_path: str = "app/models/doc_classifier.joblib",
    ) -> None:
        self.local_extractor = DocumentExtractor()
        self.model_path = Path(model_path)
        self.classifier = _DocumentTypeSideClassifier(self.model_path)
        self._setup_warnings: List[str] = list(self.classifier.warnings)

        if Image is None:
            self._setup_warnings.append(
                "Biblioteca Pillow indisponível para pipeline ML; usando OCR local básico."
            )
        if cv2 is None or np is None:
            self._setup_warnings.append(
                "OpenCV/Numpy indisponíveis; correção de ângulo/perspectiva desativada."
            )

    def get_setup_warnings(self) -> List[str]:
        return list(self._setup_warnings)

    def extract_from_files(self, files: Sequence[Path]) -> ExtractionResult:
        blocks: List[str] = []
        warnings: List[str] = self.get_setup_warnings()

        merged_fields: Dict[str, str] = {}
        field_scores: Dict[str, int] = {}

        for file_path in files:
            if not file_path.exists():
                warnings.append(f"Arquivo não encontrado: {file_path.name}")
                continue

            result = self._extract_single(file_path)
            warnings.extend(result.warnings)

            if result.text.strip():
                header = (
                    f"===== {result.file_name} "
                    f"({result.doc_type}/{result.doc_side}) ====="
                )
                blocks.append(f"{header}\n{result.text.strip()}")

            self._merge_fields(
                out=merged_fields,
                out_scores=field_scores,
                incoming=result.fields,
                extraction_score=result.score,
                doc_side=result.doc_side,
            )

        raw_text = "\n\n".join(blocks).strip()
        return ExtractionResult(
            raw_text=raw_text, fields=merged_fields, warnings=warnings
        )

    def _extract_single(self, file_path: Path) -> _PerFileExtraction:
        suffix = file_path.suffix.lower()
        if suffix == ".pdf":
            return self._extract_pdf(file_path)
        if suffix in self.SUPPORTED_IMAGES:
            return self._extract_image(file_path)
        return _PerFileExtraction(
            file_name=file_path.name,
            text="",
            fields={},
            score=0,
            doc_type="DESCONHECIDO",
            doc_side="NAO_IDENTIFICADO",
            warnings=[f"Formato não suportado: {file_path.name}"],
        )

    def _extract_pdf(self, file_path: Path) -> _PerFileExtraction:
        text, warnings = self.local_extractor._extract_single(file_path)
        text = self.local_extractor._normalize_extracted_text(text)

        fields = self.local_extractor.parse_fields(text) if text else {}
        fields.update(self._extract_cnh_fields(text))
        score = self.local_extractor._score_ocr_text(text)
        doc_type, doc_side = self.classifier.predict(text, file_name=file_path.name)

        return _PerFileExtraction(
            file_name=file_path.name,
            text=text,
            fields=fields,
            score=score,
            doc_type=doc_type,
            doc_side=doc_side,
            warnings=warnings,
        )

    def _extract_image(self, file_path: Path) -> _PerFileExtraction:
        if Image is None:
            text, warnings = self.local_extractor._extract_single(file_path)
            fields = self.local_extractor.parse_fields(text) if text else {}
            fields.update(self._extract_cnh_fields(text))
            score = self.local_extractor._score_ocr_text(text)
            doc_type, doc_side = self.classifier.predict(text, file_name=file_path.name)
            return _PerFileExtraction(
                file_name=file_path.name,
                text=text,
                fields=fields,
                score=score,
                doc_type=doc_type,
                doc_side=doc_side,
                warnings=warnings,
            )

        warnings: List[str] = []
        try:
            with Image.open(file_path) as source_image:
                rgb_image = source_image.convert("RGB")
                variants = self._prepare_variants(rgb_image)
        except Exception as exc:  # noqa: BLE001
            return _PerFileExtraction(
                file_name=file_path.name,
                text="",
                fields={},
                score=0,
                doc_type="DESCONHECIDO",
                doc_side="NAO_IDENTIFICADO",
                warnings=[f"Falha ao processar imagem {file_path.name}: {exc}"],
            )

        best_text = ""
        best_score = -1
        for variant in variants:
            text, ocr_warnings = self.local_extractor._ocr_pil_image(variant)
            warnings.extend(ocr_warnings)
            normalized = self.local_extractor._normalize_extracted_text(text)
            score = self.local_extractor._score_ocr_text(normalized)
            if score > best_score:
                best_score = score
                best_text = normalized

        if best_score < 0:
            best_score = 0

        fields = self.local_extractor.parse_fields(best_text) if best_text else {}
        fields.update(self._extract_cnh_fields(best_text))

        doc_type, doc_side = self.classifier.predict(
            best_text, file_name=file_path.name
        )
        best_score += self._document_bonus(doc_type, doc_side, best_text)

        return _PerFileExtraction(
            file_name=file_path.name,
            text=best_text,
            fields=fields,
            score=best_score,
            doc_type=doc_type,
            doc_side=doc_side,
            warnings=warnings,
        )

    def _prepare_variants(self, image_obj) -> List:
        variants = [image_obj]
        if cv2 is None or np is None:
            return variants

        try:
            bgr = cv2.cvtColor(np.array(image_obj), cv2.COLOR_RGB2BGR)
        except Exception:
            return variants

        cv_variants = [bgr]

        deskewed = self._deskew_image(bgr)
        cv_variants.append(deskewed)

        warped = self._try_perspective_warp(deskewed)
        cv_variants.append(warped)

        for angle in (-12, -6, 6, 12):
            cv_variants.append(self._rotate_bound(warped, angle))

        seen_signatures: set[Tuple[int, int, int]] = set()
        output = [image_obj]
        for item in cv_variants:
            if item is None or not hasattr(item, "shape"):
                continue
            shape = getattr(item, "shape", None)
            if shape is None or len(shape) < 2:
                continue
            signature = (
                int(shape[0]),
                int(shape[1]),
                int(shape[2] if len(shape) > 2 else 1),
            )
            if signature in seen_signatures:
                continue
            seen_signatures.add(signature)
            try:
                rgb = cv2.cvtColor(item, cv2.COLOR_BGR2RGB)
                output.append(Image.fromarray(rgb))
            except Exception:
                continue

        return output

    def _deskew_image(self, image):
        if cv2 is None or np is None:
            return image

        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (5, 5), 0)
            _, thresh = cv2.threshold(
                gray,
                0,
                255,
                cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU,
            )
            coords = np.column_stack(np.where(thresh > 0))
            if coords.size == 0:
                return image
            angle = cv2.minAreaRect(coords)[-1]
            if angle < -45:
                angle = -(90 + angle)
            else:
                angle = -angle
            if abs(float(angle)) < 0.7 or abs(float(angle)) > 25:
                return image
            return self._rotate_bound(image, float(angle))
        except Exception:
            return image

    def _try_perspective_warp(self, image):
        if cv2 is None or np is None:
            return image

        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray, (5, 5), 0)
            edges = cv2.Canny(blur, 60, 180)
            contours, _ = cv2.findContours(
                edges,
                cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE,
            )
            if not contours:
                return image

            image_area = image.shape[0] * image.shape[1]
            contours = sorted(contours, key=cv2.contourArea, reverse=True)[:8]

            for contour in contours:
                area = cv2.contourArea(contour)
                if area < image_area * 0.20:
                    continue
                perimeter = cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)
                if len(approx) != 4:
                    continue
                points = approx.reshape(4, 2).astype("float32")
                ordered = self._order_points(points)
                return self._warp_from_points(image, ordered)
        except Exception:
            return image

        return image

    @staticmethod
    def _rotate_bound(image, angle: float):
        if cv2 is None:
            return image
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

    @staticmethod
    def _order_points(points):
        if np is None:
            return points
        rect = np.zeros((4, 2), dtype="float32")
        s = points.sum(axis=1)
        rect[0] = points[np.argmin(s)]
        rect[2] = points[np.argmax(s)]

        diff = np.diff(points, axis=1)
        rect[1] = points[np.argmin(diff)]
        rect[3] = points[np.argmax(diff)]
        return rect

    @staticmethod
    def _warp_from_points(image, points):
        if cv2 is None or np is None:
            return image

        tl, tr, br, bl = points
        width_top = ((tr[0] - tl[0]) ** 2 + (tr[1] - tl[1]) ** 2) ** 0.5
        width_bottom = ((br[0] - bl[0]) ** 2 + (br[1] - bl[1]) ** 2) ** 0.5
        max_width = int(max(width_top, width_bottom))

        height_right = ((tr[0] - br[0]) ** 2 + (tr[1] - br[1]) ** 2) ** 0.5
        height_left = ((tl[0] - bl[0]) ** 2 + (tl[1] - bl[1]) ** 2) ** 0.5
        max_height = int(max(height_right, height_left))

        if max_width < 20 or max_height < 20:
            return image

        destination = np.array(
            [
                [0, 0],
                [max_width - 1, 0],
                [max_width - 1, max_height - 1],
                [0, max_height - 1],
            ],
            dtype="float32",
        )

        matrix = cv2.getPerspectiveTransform(points, destination)
        warped = cv2.warpPerspective(image, matrix, (max_width, max_height))
        return warped

    def _extract_cnh_fields(self, text: str) -> Dict[str, str]:
        fields: Dict[str, str] = {}
        if not text:
            return fields

        cnh_number = self._extract_cnh_number(text)
        cnh_date = self._extract_cnh_issue_date(text)
        cnh_uf = self._extract_cnh_uf(text)

        if cnh_number:
            fields["cnh_numero"] = cnh_number
        if cnh_date:
            fields["cnh_data_expedicao"] = cnh_date
        if cnh_uf:
            fields["cnh_uf"] = cnh_uf

        return fields

    def _extract_cnh_number(self, text: str) -> str:
        lines = text.splitlines()
        candidates: List[str] = []
        for index, line in enumerate(lines):
            if not re.search(r"(?i)\b(cnh|habilita[cç][aã]o|permiss[aã]o)\b", line):
                continue
            segments = [line]
            if index + 1 < len(lines):
                segments.append(lines[index + 1])
            for segment in segments:
                for candidate in self.local_extractor._extract_numeric_candidates(
                    segment,
                    min_len=9,
                    max_len=11,
                ):
                    candidates.append(candidate)

        if not candidates:
            return ""

        candidates.sort(
            key=lambda value: (0 if len(value) == 11 else 1, abs(len(value) - 11))
        )
        return candidates[0]

    @staticmethod
    def _extract_cnh_issue_date(text: str) -> str:
        match = re.search(
            r"(?i)(?:data\s+de\s+expedi[cç][aã]o|expedi[cç][aã]o|emiss[aã]o)\s*[:\-]?\s*([0-3]?\d[\/\-.][01]?\d[\/\-.]\d{2,4})",
            text,
        )
        if not match:
            return ""
        value = match.group(1)
        date_match = re.search(r"\b([0-3]?\d)[\/\-.]([01]?\d)[\/\-.](\d{2,4})\b", value)
        if not date_match:
            return ""
        day = int(date_match.group(1))
        month = int(date_match.group(2))
        year_raw = date_match.group(3)
        year = int(year_raw)
        if len(year_raw) == 2:
            year += 2000 if year <= 30 else 1900
        if day < 1 or day > 31 or month < 1 or month > 12:
            return ""
        return f"{day:02d}/{month:02d}/{year:04d}"

    @staticmethod
    def _extract_cnh_uf(text: str) -> str:
        patterns = (
            r"(?i)\b(?:detran|cnh)\b[^\n]{0,28}\b(AC|AL|AP|AM|BA|CE|DF|ES|GO|MA|MT|MS|MG|PA|PB|PR|PE|PI|RJ|RN|RS|RO|RR|SC|SP|SE|TO)\b",
            r"(?i)\buf\s*[:\-]?\s*(AC|AL|AP|AM|BA|CE|DF|ES|GO|MA|MT|MS|MG|PA|PB|PR|PE|PI|RJ|RN|RS|RO|RR|SC|SP|SE|TO)\b",
        )
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).upper()
        return ""

    def _document_bonus(self, doc_type: str, doc_side: str, text: str) -> int:
        score = 0
        if doc_type in {"RG", "CPF", "CNH"}:
            score += 40
        if doc_side in {"FRENTE", "VERSO"}:
            score += 25
        if re.search(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b", text):
            score += 20
        return score

    def _merge_fields(
        self,
        out: Dict[str, str],
        out_scores: Dict[str, int],
        incoming: Dict[str, str],
        extraction_score: int,
        doc_side: str,
    ) -> None:
        for key, raw_value in incoming.items():
            value = self.local_extractor._clean_value(str(raw_value or ""))
            if not value:
                continue

            score = extraction_score + self._field_score(key, value, doc_side)
            previous = out_scores.get(key, -(10**9))
            if score > previous:
                out[key] = value
                out_scores[key] = score

    def _field_score(self, key: str, value: str, doc_side: str) -> int:
        score = len(value)
        digits = self.local_extractor._ocr_to_digits(value)

        if key == "cpf":
            if self.local_extractor._is_valid_cpf(digits):
                score += 260
            elif len(digits) == 11:
                score += 120
        elif key == "rg":
            if 5 <= len(digits) <= 12:
                score += 140
        elif key in {"nome", "nome_pai", "nome_mae"}:
            score += min(len(value), 80)
        elif key in {"data_nascimento", "cnh_data_expedicao"}:
            if re.search(r"\b[0-3]?\d/[01]?\d/\d{4}\b", value):
                score += 130
        elif key == "cnh_numero":
            if 9 <= len(digits) <= 11:
                score += 150
        elif key == "cnh_uf" and value.upper() in _UFS:
            score += 90

        side = (doc_side or "").upper()
        if (
            key in {"nome", "cpf", "rg", "cnh_numero", "data_nascimento"}
            and side == "FRENTE"
        ):
            score += 30
        if (
            key in {"nome_pai", "nome_mae", "orgao_rg", "uf_rg", "cnh_data_expedicao"}
            and side == "VERSO"
        ):
            score += 25

        return score
