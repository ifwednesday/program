"""Serviços de extração de texto e campos para documentos PDF/imagem."""

from __future__ import annotations

import base64
import io
import json
import mimetypes
import os
import re
import shutil
import unicodedata
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Protocol, Sequence, Tuple

try:
    from pypdf import PdfReader  # type: ignore
except Exception:  # noqa: BLE001
    try:
        from PyPDF2 import PdfReader  # type: ignore
    except Exception:  # noqa: BLE001
        PdfReader = None  # type: ignore[assignment]

try:
    from PIL import Image, ImageEnhance, ImageOps  # type: ignore
except Exception:  # noqa: BLE001
    Image = None  # type: ignore[assignment]
    ImageEnhance = None  # type: ignore[assignment]
    ImageOps = None  # type: ignore[assignment]

try:
    import pytesseract  # type: ignore
except Exception:  # noqa: BLE001
    pytesseract = None  # type: ignore[assignment]

try:
    import fitz  # type: ignore
except Exception:  # noqa: BLE001
    fitz = None  # type: ignore[assignment]

if pytesseract is not None:
    candidate_paths = [
        os.environ.get("TESSERACT_CMD", ""),
        shutil.which("tesseract") or "",
        str(Path.home() / "miniforge3" / "bin" / "tesseract"),
        str(Path("/opt/homebrew/bin/tesseract")),
        str(Path("/usr/local/bin/tesseract")),
        str(Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe")),
    ]
    for candidate in candidate_paths:
        if candidate and Path(candidate).exists():
            try:
                pytesseract.pytesseract.tesseract_cmd = candidate
            except Exception:  # noqa: BLE001
                pass
            break


@dataclass
class ExtractionResult:
    raw_text: str
    fields: Dict[str, str]
    warnings: List[str]


class ExtractorProtocol(Protocol):
    def extract_from_files(self, files: Sequence[Path]) -> ExtractionResult: ...


class DocumentExtractor:
    SUPPORTED_IMAGES = {
        ".bmp",
        ".gif",
        ".heic",
        ".heif",
        ".jfif",
        ".jpeg",
        ".jpg",
        ".png",
        ".tif",
        ".tiff",
        ".webp",
    }

    def extract_from_files(self, files: Sequence[Path]) -> ExtractionResult:
        blocks: List[str] = []
        warnings: List[str] = []

        for file_path in files:
            if not file_path.exists():
                warnings.append(f"Arquivo não encontrado: {file_path.name}")
                continue

            text, file_warnings = self._extract_single(file_path)
            warnings.extend(file_warnings)
            if text.strip():
                blocks.append(f"===== {file_path.name} =====\n{text.strip()}")

        raw_text = "\n\n".join(blocks).strip()
        fields = self.parse_fields(raw_text) if raw_text else {}
        return ExtractionResult(raw_text=raw_text, fields=fields, warnings=warnings)

    def _extract_single(self, file_path: Path) -> Tuple[str, List[str]]:
        suffix = file_path.suffix.lower()
        if suffix == ".pdf":
            return self._extract_pdf_text(file_path)
        if suffix in self.SUPPORTED_IMAGES:
            return self._extract_image_text(file_path)
        return "", [f"Formato não suportado: {file_path.name}"]

    def _extract_pdf_text(self, file_path: Path) -> Tuple[str, List[str]]:
        if PdfReader is None:
            return "", ["Biblioteca de PDF indisponível (instale 'pypdf' ou 'PyPDF2')."]

        warnings: List[str] = []
        chunks: List[str] = []
        try:
            reader = PdfReader(str(file_path))
            for page in reader.pages:
                try:
                    content = page.extract_text() or ""
                except Exception:  # noqa: BLE001
                    content = ""
                if content.strip():
                    chunks.append(content)
        except Exception as exc:  # noqa: BLE001
            return "", [f"Falha ao ler PDF {file_path.name}: {exc}"]

        text = self._normalize_extracted_text("\n".join(chunks).strip())
        # Alguns PDFs têm texto parcial ou inexistente mesmo sendo visualmente nítidos.
        # Neste caso, tenta OCR por página para recuperar conteúdo.
        char_count = len(re.sub(r"\s+", "", text))
        if char_count < 80:
            ocr_text, ocr_warnings = self._extract_pdf_ocr_text(file_path)
            warnings.extend(ocr_warnings)
            if len(re.sub(r"\s+", "", ocr_text)) > char_count:
                text = ocr_text.strip()

        if not text:
            warnings.append(f"Não foi possível extrair texto do PDF: {file_path.name}.")
        return text, warnings

    def _extract_image_text(self, file_path: Path) -> Tuple[str, List[str]]:
        if Image is None:
            return "", ["Biblioteca 'Pillow' não disponível para leitura de imagens."]
        if pytesseract is None:
            return "", ["Biblioteca 'pytesseract' não disponível para OCR de imagens."]

        try:
            with Image.open(file_path) as img:
                img = img.convert("RGB")
                text, warnings = self._ocr_pil_image(img)
                return self._normalize_extracted_text(text.strip()), warnings
        except Exception as exc:  # noqa: BLE001
            return "", [f"Falha no OCR da imagem {file_path.name}: {exc}"]

    def _extract_pdf_ocr_text(self, file_path: Path) -> Tuple[str, List[str]]:
        if fitz is None:
            return (
                "",
                [
                    (
                        "PDF sem texto selecionável e OCR de PDF indisponível "
                        "(instale 'pymupdf')."
                    )
                ],
            )
        if Image is None:
            return "", ["Biblioteca 'Pillow' não disponível para OCR de PDF."]
        if pytesseract is None:
            return "", ["Biblioteca 'pytesseract' não disponível para OCR de PDF."]

        warnings: List[str] = []
        chunks: List[str] = []
        try:
            with fitz.open(str(file_path)) as doc:
                for page_number, page in enumerate(doc, start=1):
                    try:
                        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
                        img_bytes = pix.tobytes("png")
                        with Image.open(io.BytesIO(img_bytes)) as img:
                            text, ocr_warnings = self._ocr_pil_image(img.convert("RGB"))
                        if text.strip():
                            chunks.append(text.strip())
                        warnings.extend(
                            f"{file_path.name} - página {page_number}: {item}"
                            for item in ocr_warnings
                        )
                    except Exception as exc:  # noqa: BLE001
                        warnings.append(
                            f"Falha no OCR da página {page_number} de {file_path.name}: {exc}"
                        )
        except Exception as exc:  # noqa: BLE001
            return "", [f"Falha ao abrir PDF para OCR ({file_path.name}): {exc}"]

        text = self._normalize_extracted_text("\n".join(chunks).strip())
        if text:
            warnings.append(
                f"PDF {file_path.name}: conteúdo obtido por OCR (documento escaneado)."
            )
        return text, warnings

    def _ocr_pil_image(self, image_obj) -> Tuple[str, List[str]]:
        if pytesseract is None:
            return "", ["pytesseract indisponível."]
        candidates: List[Tuple[str, int]] = []
        warnings: List[str] = []

        for prepared in self._preprocess_for_ocr(image_obj):
            for config in ("--oem 1 --psm 6", "--oem 1 --psm 11", "--oem 1 --psm 4"):
                text = ""
                try:
                    text = pytesseract.image_to_string(
                        prepared,
                        lang="por+eng",
                        config=config,
                    )
                except Exception:
                    try:
                        text = pytesseract.image_to_string(prepared, config=config)
                        warnings.append(
                            "Idioma OCR 'por+eng' indisponível; usado OCR padrão do Tesseract."
                        )
                    except Exception as exc:  # noqa: BLE001
                        warnings.append(f"OCR falhou ({config}): {exc}")
                        continue
                if text.strip():
                    candidates.append((text, self._score_ocr_text(text)))

        if not candidates:
            return "", warnings or ["Falha no OCR."]

        best_text = max(candidates, key=lambda item: item[1])[0]
        return best_text, warnings

    def parse_fields(self, text: str) -> Dict[str, str]:
        cleaned = self._normalize_extracted_text(self._normalize(text))
        fields: Dict[str, str] = {}

        fields["nome"] = self._find_first(
            cleaned,
            (
                r"(?:^|\n)\s*nome(?:\s+completo)?\s*[:\-]\s*([^\n]{3,120})",
                r"(?:^|\n)\s*outorgante\s*[:\-]\s*([^\n]{3,120})",
                r"(?:^|\n)\s*registro\s+civil\s+([A-ZÁÀÂÃÉÊÍÓÔÕÚÇ ]{6,})",
            ),
        )
        fields["nome_pai"] = self._find_first(
            cleaned,
            (
                r"(?:^|\n)\s*(?:nome\s+do\s+pai|pai)\s*[:\-]\s*([^\n]{3,120})",
                r"filiaç[ãa]o\s*[:\-].*?\bpai\s*[:\-]\s*([^\n;]+)",
            ),
        )
        fields["nome_mae"] = self._find_first(
            cleaned,
            (
                r"(?:^|\n)\s*(?:nome\s+da\s+m[ãa]e|m[ãa]e)\s*[:\-]\s*([^\n]{3,120})",
                r"filiaç[ãa]o\s*[:\-].*?\bm[ãa]e\s*[:\-]\s*([^\n;]+)",
            ),
        )
        if not fields.get("nome_pai") or not fields.get("nome_mae"):
            pai, mae = self._extract_filiation(cleaned)
            if pai and not fields.get("nome_pai"):
                fields["nome_pai"] = pai
            if mae and not fields.get("nome_mae"):
                fields["nome_mae"] = mae

        fields["sexo"] = self._extract_sex(cleaned)
        fields["naturalidade"] = self._find_first(
            cleaned,
            (
                r"(?:^|\n)\s*naturalidade\s*[:\-]\s*([^\n]{2,120})",
                r"(?:^|\n)\s*natural\s+de\s*[:\-]?\s*([^\n]{2,120})",
            ),
        )
        fields["data_nascimento"] = self._find_first(
            cleaned,
            (
                r"(?:data\s+de\s+nascimento|nascimento)\s*[:\-]\s*([0-3]?\d[\/\-][01]?\d[\/\-]\d{2,4})",
                r"\bnascid[oa]?\s*(?:em|aos)?\s*([0-3]?\d[\/\-][01]?\d[\/\-]\d{2,4})",
            ),
        )
        if not fields.get("data_nascimento"):
            fields["data_nascimento"] = self._extract_date_by_words(cleaned)
        fields["profissao"] = self._find_first(
            cleaned, (r"(?:^|\n)\s*profiss[ãa]o\s*[:\-]\s*([^\n]{2,120})",)
        )
        fields["logradouro"] = self._find_first(
            cleaned,
            (
                r"(?:^|\n)\s*(?:logradouro|endere[cç]o)\s*[:\-]\s*([^\n]{3,160})",
                r"(?:^|\n)\s*(rua|avenida|av\.|travessa|alameda)\s+([^\n]{3,160})",
            ),
            join_groups=True,
        )
        fields["numero"] = self._find_first(
            cleaned, (r"(?:^|\n)\s*n[úu]mero\s*[:\-]\s*([^\n]{1,20})",)
        )
        fields["bairro"] = self._find_first(
            cleaned, (r"(?:^|\n)\s*bairro\s*[:\-]\s*([^\n]{2,120})",)
        )
        fields["cidade"] = self._find_first(
            cleaned,
            (
                r"(?:^|\n)\s*(?:cidade|munic[íi]pio)\s*[:\-]\s*([^\n]{2,120})",
                r"(?:^|\n)\s*localidade\s*[:\-]\s*([^\n]{2,120})",
            ),
        )
        fields["email"] = self._find_email(cleaned)
        fields["cep"] = self._find_first(
            cleaned,
            (
                r"(?:^|\n)\s*cep\s*[:\-]?\s*(\d{5}-?\d{3})\b",
                r"(?:\bcep\b)[^\n]{0,15}(\d{5}-?\d{3})",
            ),
        )

        cpf_digits = self._extract_cpf_digits(cleaned)
        if cpf_digits:
            fields["cpf"] = self._format_cpf_digits(cpf_digits)
        fields["cnpj"] = self._find_first(
            cleaned, (r"\b(\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2})\b",)
        )
        fields["razao_social"] = self._find_first(
            cleaned,
            (r"(?:^|\n)\s*(?:raz[ãa]o\s+social|empresa)\s*[:\-]\s*([^\n]{3,160})",),
        )
        fields["nire"] = self._find_first(
            cleaned, (r"(?:^|\n)\s*nire\s*[:\-]?\s*([^\n]{3,60})",)
        )
        fields["loteamento"] = self._find_first(
            cleaned, (r"(?:^|\n)\s*loteamento\s*[:\-]\s*([^\n]{2,120})",)
        )
        if not fields.get("naturalidade"):
            fields["naturalidade"] = self._find_first(
                cleaned,
                (r"c\.?\s*nasc[^,\n;]*[,;\s]\s*([A-ZÁÀÂÃÉÊÍÓÔÕÚÇ]{3,}(?:-[A-Z]{2}))",),
            )

        rg_num, orgao_rg, uf_rg = self._extract_rg_parts(
            cleaned,
            cpf_digits=cpf_digits,
        )
        fields["rg"] = rg_num
        fields["orgao_rg"] = orgao_rg
        fields["uf_rg"] = uf_rg

        if fields.get("nome"):
            fields["nome"] = self._clean_person_name(fields["nome"])
        if fields.get("nome_pai"):
            fields["nome_pai"] = self._clean_person_name(fields["nome_pai"])
        if fields.get("nome_mae"):
            fields["nome_mae"] = self._clean_person_name(fields["nome_mae"])

        return {key: value for key, value in fields.items() if value}

    @staticmethod
    def _normalize(text: str) -> str:
        text = text.replace("\r", "\n")
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    def _find_first(
        self,
        text: str,
        patterns: Iterable[str],
        join_groups: bool = False,
    ) -> str:
        for pattern in patterns:
            match = re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE)
            if not match:
                continue
            if join_groups and match.lastindex and match.lastindex > 1:
                candidate = " ".join(
                    part for part in match.groups(default="") if part.strip()
                )
            else:
                candidate = match.group(1) if match.lastindex else match.group(0)
            value = self._clean_value(candidate)
            if value:
                return value
        return ""

    @staticmethod
    def _find_email(text: str) -> str:
        match = re.search(
            r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)",
            text,
            flags=re.IGNORECASE,
        )
        return match.group(1).strip() if match else ""

    def _extract_rg_parts(
        self, text: str, cpf_digits: str = ""
    ) -> Tuple[str, str, str]:
        match = re.search(
            r"(?:^|\n)\s*(?:registro\s*geral|rg)(?:\s*n[ºo.]*)?\s*[:\-]?\s*([0-9.\-xX]{5,20})"
            r"(?:\s*/\s*([A-Za-z]{2,6}))?"
            r"(?:\s*[-/]\s*([A-Za-z]{2}))?",
            text,
            flags=re.IGNORECASE | re.MULTILINE,
        )
        if match:
            rg = self._clean_value(match.group(1))
            rg_digits = self._ocr_to_digits(rg)
            if rg_digits:
                rg = rg_digits
            orgao = self._clean_value(match.group(2) or "SSP").upper()
            uf = self._clean_value(match.group(3) or "").upper()
            return rg, orgao or "SSP", uf

        rg_fallback = self._extract_rg_digits(text, cpf_digits=cpf_digits)
        orgao = self._find_first(
            text,
            (
                r"(?:org[aã]o\s+expedidor|expedidor|org[aã]o)\s*[:\-]?\s*(SSP|SESP|DETRAN|PC|SDS|IFP)",
                r"\b(SSP|SESP|DETRAN|PC|SDS|IFP)\b",
            ),
        ).upper()
        uf = self._find_first(
            text,
            (
                r"(?:\buf\b|/|-)\s*(AC|AL|AP|AM|BA|CE|DF|ES|GO|MA|MT|MS|MG|PA|PB|PR|PE|PI|RJ|RN|RS|RO|RR|SC|SP|SE|TO)\b",
                r"(?:registro\s*geral|registrogeral|rg)[^\n]{0,35}\b(AC|AL|AP|AM|BA|CE|DF|ES|GO|MA|MT|MS|MG|PA|PB|PR|PE|PI|RJ|RN|RS|RO|RR|SC|SP|SE|TO)\b",
            ),
        )
        return rg_fallback, (orgao or "SSP"), uf.upper()

    def _extract_filiation(self, text: str) -> Tuple[str, str]:
        # Caso 1: "filiação: PAI e MÃE"
        inline = re.search(
            r"filiaç[ãa]o\s*[:\-]?\s*(.+?)\s+\be\b\s+(?:d[ao]s?\s+)?(.+)",
            text,
            flags=re.IGNORECASE,
        )
        if inline:
            pai = self._clean_person_name(self._clean_value(inline.group(1)))
            mae = self._clean_person_name(self._clean_value(inline.group(2)))
            if pai and mae:
                return pai, mae

        # Caso 2: "filho(a) de PAI e da MÃE"
        filho_de = re.search(
            r"filh[oa]\s+de\s+(.+?)\s+\be\b\s+(?:d[ao]s?\s+)?(.+)",
            text,
            flags=re.IGNORECASE,
        )
        if filho_de:
            pai = self._clean_person_name(self._clean_value(filho_de.group(1)))
            mae = self._clean_person_name(self._clean_value(filho_de.group(2)))
            if pai and mae:
                return pai, mae

        # Caso 3: "FILIAÇÃO" em uma linha e nomes nas duas linhas seguintes.
        lines = [self._clean_value(line) for line in text.splitlines()]
        for index, line in enumerate(lines):
            if "filiacao" not in self._ascii_lower(line):
                continue
            next_lines = lines[index + 1 : index + 4]
            name_candidates = [
                self._clean_person_name(item)
                for item in next_lines
                if self._looks_like_name_line(item)
            ]
            if len(name_candidates) >= 2:
                return name_candidates[0], name_candidates[1]

        return "", ""

    def _extract_sex(self, text: str) -> str:
        value = self._find_first(
            text,
            (
                r"(?:^|\n)\s*sexo\s*[:\-]?\s*(masculino|feminino|m|f)\b",
                r"(?:^|\n)\s*sex\s*[:\-]?\s*(masculino|feminino|m|f)\b",
                r"\bsexo\s+([mf])\b",
            ),
        )
        normalized = self._ascii_lower(value)
        if normalized in {"m", "masculino"}:
            return "MASCULINO"
        if normalized in {"f", "feminino"}:
            return "FEMININO"
        return ""

    def _looks_like_name_line(self, value: str) -> bool:
        cleaned = self._clean_value(value)
        if not cleaned:
            return False
        if re.search(r"\d", cleaned):
            return False
        ascii_line = self._ascii_lower(cleaned)
        forbidden = (
            "cpf",
            "rg",
            "nascimento",
            "naturalidade",
            "ctps",
            "cnh",
            "eleitor",
            "cep",
            "endereco",
            "bairro",
            "cidade",
        )
        if any(key in ascii_line for key in forbidden):
            return False
        words = cleaned.split()
        return len(words) >= 2 and any(len(word) > 2 for word in words)

    def _extract_date_by_words(self, text: str) -> str:
        months = {
            "janeiro": "01",
            "fevereiro": "02",
            "marco": "03",
            "abril": "04",
            "maio": "05",
            "junho": "06",
            "julho": "07",
            "agosto": "08",
            "setembro": "09",
            "outubro": "10",
            "novembro": "11",
            "dezembro": "12",
        }
        normalized = self._ascii_lower(text)
        match = re.search(
            r"\b([0-3]?\d)\s+de\s+([a-z]+)\s+de\s+(\d{4})\b",
            normalized,
            flags=re.IGNORECASE,
        )
        if not match:
            return ""
        day = match.group(1).zfill(2)
        month = months.get(match.group(2).lower(), "")
        year = match.group(3)
        if not month:
            return ""
        return f"{day}/{month}/{year}"

    def _normalize_extracted_text(self, text: str) -> str:
        if not text:
            return ""
        lines = [line.strip() for line in text.splitlines()]
        cleaned_lines: List[str] = []
        previous_relevant = False
        skip_patterns = (
            r"^\[\d+\]\s*photoscan",
            r"^photoscan do google fotos$",
            r"^valida em todo o territorio nacional$",
        )

        for line in lines:
            if not line:
                continue
            line_ascii = self._ascii_lower(line)
            if any(re.search(pattern, line_ascii) for pattern in skip_patterns):
                continue
            line = re.sub(r"[^\w\s\-/.:,ºª()]+", " ", line, flags=re.UNICODE)
            line = re.sub(r"\s{2,}", " ", line).strip()
            line = self._sanitize_relevant_line(line)
            if not line:
                continue
            line_relevant = self._is_relevant_line(line)
            keep_as_continuation = (
                previous_relevant
                and bool(re.search(r"\d{5,}", line))
                and bool(re.search(r"\b[0-3]?\d[/-][01]?\d[/-]\d{2,4}\b", line))
            )
            if line and (line_relevant or keep_as_continuation):
                cleaned_lines.append(line)
            previous_relevant = line_relevant

        deduped: List[str] = []
        seen: set[str] = set()
        for line in cleaned_lines:
            key = self._ascii_lower(line)
            if key in seen:
                continue
            seen.add(key)
            deduped.append(line)

        return "\n".join(deduped).strip()

    def _sanitize_relevant_line(self, line: str) -> str:
        line = self._clean_value(line)
        if not line:
            return ""

        line = re.sub(r"(?i)\bregistrogeral\b", "REGISTRO GERAL", line)
        line = re.sub(r"(?i)\bdatadeexpedicao\b", "DATA DE EXPEDICAO", line)
        ascii_line = self._ascii_lower(line)

        if "registro civil" in ascii_line:
            match = re.search(r"(?i)\bregistro\s*civil\b\s*(.+)", line)
            if match:
                name = self._clean_person_name(match.group(1))
                return f"REGISTRO CIVIL {name}" if name else "REGISTRO CIVIL"
            return "REGISTRO CIVIL"

        if "registro geral" in ascii_line and "data de expedicao" in ascii_line:
            return "REGISTRO GERAL DATA DE EXPEDICAO"

        if "sexo" in ascii_line:
            sex_match = re.search(
                r"(?i)\bsexo\b\s*[:\-]?\s*(masculino|feminino|m|f)\b", line
            )
            if sex_match:
                sex_value = self._ascii_lower(sex_match.group(1))
                if sex_value in {"m", "masculino"}:
                    return "SEXO MASCULINO"
                if sex_value in {"f", "feminino"}:
                    return "SEXO FEMININO"
            return "SEXO"

        if "cpf" in ascii_line:
            segment = re.split(r"(?i)\bcpf\b", line, maxsplit=1)
            tail = segment[1] if len(segment) > 1 else line

            # Prioriza CPF válido para não inventar número incorreto.
            for candidate in self._extract_numeric_candidates(
                tail, min_len=11, max_len=11
            ):
                if self._is_valid_cpf(candidate):
                    return f"CPF {self._format_cpf_digits(candidate)}"

            # Mantém o melhor candidato bruto visível para revisão manual.
            fallback = self._extract_numeric_candidates(tail, min_len=10, max_len=11)
            if fallback:
                return f"CPF {fallback[0]}"
            return "CPF"

        if re.search(r"(?i)\bc\.?\s*nasc\b", line):
            naturalidade_match = re.search(
                r"\b([A-Za-zÀ-ÖØ-öø-ÿ]{3,}(?:\s+[A-Za-zÀ-ÖØ-öø-ÿ]{2,}){0,3}-[A-Za-z]{2})\b",
                line,
            )
            if naturalidade_match:
                naturalidade = self._clean_value(naturalidade_match.group(1)).upper()
                return f"C.NASC {naturalidade}"

        if "ctps" in ascii_line:
            ctps_num = ""
            serie = ""
            uf = ""
            m_ctps = re.search(
                r"(?i)\bctps\b[^0-9A-Za-z]{0,4}([0-9A-Za-z.\-/]{4,20})", line
            )
            if m_ctps:
                ctps_num = self._ocr_to_digits(m_ctps.group(1))
            m_serie = re.search(
                r"(?i)\bs[ée]rie\b[^0-9A-Za-z]{0,4}([0-9A-Za-z.\-/]{1,10})", line
            )
            if m_serie:
                serie = self._ocr_to_digits(m_serie.group(1))
            m_uf = re.search(
                r"(?i)\buf\b[^A-Za-z]{0,3}(AC|AL|AP|AM|BA|CE|DF|ES|GO|MA|MT|MS|MG|PA|PB|PR|PE|PI|RJ|RN|RS|RO|RR|SC|SP|SE|TO)\b",
                line,
            )
            if m_uf:
                uf = m_uf.group(1).upper()

            parts = ["CTPS"]
            if ctps_num:
                parts.append(ctps_num)
            if serie:
                parts.append(f"SÉRIE {serie}")
            if uf:
                parts.append(f"UF {uf}")
            return " ".join(parts)

        if "eleitor" in ascii_line:
            m_eleitor = re.search(
                r"(?i)(?:t\.?\s*eleitor|titulo\s*eleitor)[^0-9A-Za-z]{0,4}([0-9A-Za-z.\-/]{8,24})",
                line,
            )
            if m_eleitor:
                titulo = self._ocr_to_digits(m_eleitor.group(1))
                if titulo:
                    return f"T.ELEITOR {titulo}"
            return "T.ELEITOR"

        date_match = re.search(r"\b[0-3]?\d[/-][01]?\d[/-]\d{2,4}\b", line)
        if date_match and re.search(r"\d{6,10}", line):
            rg_candidates = self._extract_numeric_candidates(
                line, min_len=6, max_len=10
            )
            rg_num = ""
            for candidate in rg_candidates:
                if len(candidate) == 8 and candidate.startswith(("19", "20")):
                    continue
                rg_num = candidate
                break
            if rg_num:
                return f"{rg_num} {date_match.group(0)}"

        return self._trim_common_ocr_tail(line)

    def _trim_common_ocr_tail(self, line: str) -> str:
        tokens = line.split()
        while tokens:
            token = tokens[-1].strip(".,;:-")
            if not token:
                tokens.pop()
                continue
            if re.search(r"\d", token):
                break
            if len(token) >= 4:
                break
            if token.isupper() and len(token) == 2:
                break
            if len(token) <= 2 and token.isalpha():
                tokens.pop()
                continue
            if token.islower() and len(token) <= 3:
                tokens.pop()
                continue
            break

        if not tokens:
            return ""
        return " ".join(tokens).strip()

    def _preprocess_for_ocr(self, image_obj) -> List:
        if Image is None:
            return [image_obj]
        variants = [image_obj]

        if ImageOps is not None:
            gray = ImageOps.grayscale(image_obj)
            variants.append(gray)
            if ImageEnhance is not None:
                contrast = ImageEnhance.Contrast(gray).enhance(2.2)
                variants.append(contrast)
                sharp = ImageEnhance.Sharpness(contrast).enhance(1.8)
                variants.append(sharp)
                lut = [0] * 166 + [255] * 90
                bw = sharp.point(lut)
                variants.append(bw)
        return variants

    def _score_ocr_text(self, text: str) -> int:
        plain = self._ascii_lower(text)
        score = len(re.sub(r"\s+", "", plain))
        keyword_weights = {
            "cpf": 120,
            "registro geral": 80,
            "rg": 70,
            "registro civil": 70,
            "nome": 40,
            "nascimento": 40,
            "mae": 35,
            "pai": 35,
            "cidade": 30,
        }
        for key, weight in keyword_weights.items():
            if key in plain:
                score += weight
        if re.search(r"\d{3}\.?\d{3}\.?\d{3}-?\d{2}", plain):
            score += 140
        if re.search(r"\d{1,2}[/-]\d{1,2}[/-]\d{2,4}", plain):
            score += 90
        if re.search(r"\bregistro civil\b", plain):
            score += 130
        if re.search(r"\bphoto ?scan\b", plain):
            score -= 120
        return score

    def _is_relevant_line(self, line: str) -> bool:
        ascii_line = self._ascii_lower(line)
        if "photoscan" in ascii_line or "google fotos" in ascii_line:
            return False
        tokens = re.findall(r"[a-z0-9]+", ascii_line)
        if len(tokens) >= 6:
            short_alpha = sum(
                1 for token in tokens if token.isalpha() and len(token) <= 2
            )
            has_strong_keyword = any(
                keyword in ascii_line
                for keyword in (
                    "cpf",
                    "registro",
                    "c.nasc",
                    "ctps",
                    "eleitor",
                    "cnh",
                    "cnpj",
                )
            )
            if short_alpha / len(tokens) > 0.55 and not has_strong_keyword:
                return False
        keywords = (
            "cpf",
            "rg",
            "registro geral",
            "registrogeral",
            "registro civil",
            "c.nasc",
            "nascimento",
            "nome",
            "pai",
            "mae",
            "filiacao",
            "sexo",
            "orgao expedidor",
            "naturalidade",
            "natural de",
            "cidade",
            "bairro",
            "logradouro",
            "endereco",
            "cep",
            "cnh",
            "titulo eleitor",
            "t.eleitor",
            "ctps",
            "nire",
            "cnpj",
        )
        if any(keyword in ascii_line for keyword in keywords):
            return True
        if re.search(r"\b[A-Za-z]{3,}-[A-Za-z]{2}\b", line):
            return True
        if re.search(r"\b[0-3]?\d[/-][01]?\d[/-]\d{2,4}\b", ascii_line):
            return True
        if re.search(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b", ascii_line):
            return True
        if re.search(r"\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b", ascii_line):
            return True
        if re.search(r"\b[0-3]?\d\s+de\s+[a-z]+\s+de\s+\d{4}\b", ascii_line):
            return True
        return False

    def _extract_digits_near_keyword(
        self, text: str, keyword_pattern: str, min_len: int, max_len: int
    ) -> str:
        lines = text.splitlines()
        for index, line in enumerate(lines):
            if not re.search(keyword_pattern, line, flags=re.IGNORECASE):
                continue
            segments = [line]
            if index + 1 < len(lines):
                segments.append(lines[index + 1])
            for segment in segments:
                candidates = self._extract_numeric_candidates(
                    segment, min_len=min_len, max_len=max_len
                )
                if candidates:
                    return candidates[0]
        return ""

    def _extract_cpf_digits(self, text: str) -> str:
        # 1) Primeiro tenta CPF já bem formado no texto.
        for match in re.finditer(r"\b(\d{3}\.?\d{3}\.?\d{3}-?\d{2})\b", text):
            digits = self._ocr_to_digits(match.group(1))
            if self._is_valid_cpf(digits):
                return digits

        # 2) Depois tenta ao redor da palavra "CPF".
        lines = text.splitlines()
        for index, line in enumerate(lines):
            if "cpf" not in self._ascii_lower(line):
                continue
            segments = [line]
            if index + 1 < len(lines):
                segments.append(lines[index + 1])
            for segment in segments:
                for candidate in self._extract_numeric_candidates(
                    segment, min_len=10, max_len=11
                ):
                    if len(candidate) == 11 and self._is_valid_cpf(candidate):
                        return candidate
                # OCR costuma quebrar CPF em mais de um token.
                token_digits = [
                    self._ocr_to_digits(token)
                    for token in re.findall(r"[0-9A-Za-z.\-/]+", segment)
                ]
                token_digits = [token for token in token_digits if token]
                for start in range(len(token_digits)):
                    merged = ""
                    for end in range(start, min(start + 4, len(token_digits))):
                        merged += token_digits[end]
                        if len(merged) > 11:
                            break
                        if len(merged) == 11 and self._is_valid_cpf(merged):
                            return merged

        return ""

    def _extract_rg_digits(self, text: str, cpf_digits: str = "") -> str:
        lines = text.splitlines()
        rg_candidates: List[str] = []
        for index, line in enumerate(lines):
            line_ascii = self._ascii_lower(line)
            if not (
                "registrogeral" in line_ascii
                or "registro geral" in line_ascii
                or re.search(r"\brg\b", line_ascii)
            ):
                continue
            segments = [line]
            if index + 1 < len(lines):
                segments.append(lines[index + 1])
            for segment in segments:
                for candidate in self._extract_numeric_candidates(
                    segment, min_len=5, max_len=10
                ):
                    if cpf_digits and candidate == cpf_digits:
                        continue
                    # descarta provável data compactada
                    if len(candidate) == 8 and candidate.startswith(("19", "20")):
                        continue
                    rg_candidates.append(candidate)
        if not rg_candidates:
            return ""
        # Prioriza comprimentos comuns de RG (7-9 dígitos)
        rg_candidates.sort(key=lambda value: (abs(len(value) - 8), -len(value)))
        return rg_candidates[0]

    def _extract_numeric_candidates(
        self, text: str, min_len: int, max_len: int
    ) -> List[str]:
        raw_tokens = re.findall(r"[0-9A-Za-z./\-]+", text)
        out: List[str] = []
        for token in raw_tokens:
            if not re.search(r"\d", token):
                continue
            digits = self._ocr_to_digits(token)
            if min_len <= len(digits) <= max_len:
                out.append(digits)
        return out

    @staticmethod
    def _ocr_to_digits(value: str) -> str:
        trans = str.maketrans(
            {
                "O": "0",
                "o": "0",
                "Q": "0",
                "D": "0",
                "I": "1",
                "l": "1",
                "S": "5",
                "s": "5",
                "B": "8",
                "G": "6",
                "Z": "2",
            }
        )
        converted = (value or "").translate(trans)
        return re.sub(r"\D", "", converted)

    @staticmethod
    def _format_cpf_digits(digits: str) -> str:
        if len(digits) != 11:
            return digits
        return f"{digits[0:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:11]}"

    @staticmethod
    def _is_valid_cpf(digits: str) -> bool:
        if len(digits) != 11:
            return False
        if digits == digits[0] * 11:
            return False
        nums = [int(ch) for ch in digits]
        sum1 = sum(num * weight for num, weight in zip(nums[:9], range(10, 1, -1)))
        d1 = (sum1 * 10) % 11
        d1 = 0 if d1 == 10 else d1
        if d1 != nums[9]:
            return False
        sum2 = sum(num * weight for num, weight in zip(nums[:10], range(11, 1, -1)))
        d2 = (sum2 * 10) % 11
        d2 = 0 if d2 == 10 else d2
        return d2 == nums[10]

    def _clean_person_name(self, value: str) -> str:
        text = self._clean_value(value)
        text = re.sub(r"[^A-Za-zÀ-ÖØ-öø-ÿ' -]", " ", text)
        text = re.sub(r"\s{2,}", " ", text).strip()

        stop_tokens = {
            "CPF",
            "RG",
            "C",
            "NASC",
            "LIV",
            "FLS",
            "DATA",
            "CERT",
            "MILITAR",
            "DNI",
            "CNS",
            "NIS",
            "PIS",
            "PASEP",
            "CTPS",
            "CNH",
            "ELEITOR",
        }

        tokens = []
        for token in text.split():
            upper = token.upper().strip(".:,;-")
            if upper in stop_tokens:
                break
            if token.islower():
                break
            if len(upper) == 1:
                continue
            tokens.append(token)

        while tokens and len(tokens[-1]) <= 2:
            tokens.pop()
        if len(tokens) > 6:
            tokens = tokens[:6]
        return " ".join(tokens).strip()

    @staticmethod
    def _ascii_lower(value: str) -> str:
        normalized = unicodedata.normalize("NFKD", value or "")
        encoded = normalized.encode("ascii", "ignore").decode("ascii")
        return encoded.lower()

    @staticmethod
    def _clean_value(value: str) -> str:
        value = (value or "").strip()
        value = re.sub(r"\s+", " ", value)
        value = value.strip(" ;,.-")
        return value


class GeminiDocumentExtractor:
    """Extrator remoto com Gemini API (fallback local em falhas)."""

    _TARGET_KEYS = (
        "nome",
        "nome_pai",
        "nome_mae",
        "sexo",
        "cpf",
        "uf_rg",
        "orgao_rg",
        "data_nascimento",
        "naturalidade",
        "rg",
    )
    _SUPPORTED_SUFFIXES = DocumentExtractor.SUPPORTED_IMAGES.union({".pdf"})

    def __init__(
        self,
        api_key: str,
        model: str = "",
        timeout_seconds: int = 90,
    ) -> None:
        self.api_key = (api_key or "").strip()
        self.model = (
            model or os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
        ).strip()
        self.timeout_seconds = timeout_seconds
        self.local_extractor = DocumentExtractor()

    def extract_from_files(self, files: Sequence[Path]) -> ExtractionResult:
        blocks: List[str] = []
        warnings: List[str] = []
        merged_fields: Dict[str, str] = {}

        for file_path in files:
            if not file_path.exists():
                warnings.append(f"Arquivo não encontrado: {file_path.name}")
                continue

            fields, text, file_warnings = self._extract_single(file_path)
            warnings.extend(file_warnings)
            if text.strip():
                blocks.append(f"===== {file_path.name} =====\n{text.strip()}")
            for key in self._TARGET_KEYS:
                value = str(fields.get(key, "")).strip()
                if value and not merged_fields.get(key):
                    merged_fields[key] = value

        raw_text = "\n\n".join(blocks).strip()
        return ExtractionResult(
            raw_text=raw_text, fields=merged_fields, warnings=warnings
        )

    def _extract_single(self, file_path: Path) -> Tuple[Dict[str, str], str, List[str]]:
        suffix = file_path.suffix.lower()
        if suffix not in self._SUPPORTED_SUFFIXES:
            return {}, "", [f"Formato não suportado: {file_path.name}"]

        try:
            content = file_path.read_bytes()
        except Exception as exc:  # noqa: BLE001
            return {}, "", [f"Falha ao ler arquivo {file_path.name}: {exc}"]

        # Inline data no Gemini tem limite de tamanho; em excesso, cai no local.
        if len(content) > 18 * 1024 * 1024:
            local_fields, local_text, local_warnings = self._extract_local(file_path)
            local_warnings.insert(
                0,
                (
                    f"{file_path.name}: arquivo grande para Gemini inline "
                    "(>18MB); usado extrator local."
                ),
            )
            return local_fields, local_text, local_warnings

        mime_type = self._guess_mime_type(file_path)
        try:
            fields, model_raw_text = self._extract_with_gemini(content, mime_type)
        except Exception as exc:  # noqa: BLE001
            local_fields, local_text, local_warnings = self._extract_local(file_path)
            local_warnings.insert(
                0,
                f"{file_path.name}: Gemini indisponível ({exc}); usado extrator local.",
            )
            return local_fields, local_text, local_warnings

        fields = self._normalize_gemini_fields(fields)
        missing_keys = [key for key in self._TARGET_KEYS if not fields.get(key)]
        if missing_keys:
            local_fields, _, _ = self._extract_local(file_path)
            for key in missing_keys:
                local_value = str(local_fields.get(key, "")).strip()
                if local_value:
                    fields[key] = local_value

        normalized_lines = [
            f"{key}: {fields[key]}" for key in self._TARGET_KEYS if fields.get(key)
        ]
        text_output = "\n".join(normalized_lines)
        if not text_output:
            local_fields, local_text, local_warnings = self._extract_local(file_path)
            local_warnings.insert(
                0,
                f"{file_path.name}: Gemini não retornou campos válidos; usado extrator local.",
            )
            return local_fields, local_text, local_warnings

        _ = model_raw_text
        return fields, text_output, []

    def _extract_local(self, file_path: Path) -> Tuple[Dict[str, str], str, List[str]]:
        text, warnings = self.local_extractor._extract_single(file_path)
        parsed = self.local_extractor.parse_fields(text) if text else {}
        local_fields = {
            key: str(parsed.get(key, "")).strip() for key in self._TARGET_KEYS
        }
        local_fields = {k: v for k, v in local_fields.items() if v}
        return local_fields, text, warnings

    def _extract_with_gemini(
        self,
        content: bytes,
        mime_type: str,
    ) -> Tuple[Dict[str, str], str]:
        prompt = (
            "Extraia somente os campos em JSON estrito.\n"
            "Não invente valores. Se não achar, retorne string vazia.\n"
            "Use chaves exatas: "
            "nome, nome_pai, nome_mae, sexo, cpf, rg, orgao_rg, uf_rg, data_nascimento, naturalidade.\n"
            "Regras:\n"
            "- sexo: MASCULINO ou FEMININO.\n"
            "- se vier em letra única, converta: M->MASCULINO, F->FEMININO.\n"
            "- cpf: no formato 000.000.000-00 (ou vazio se ilegível).\n"
            "- data_nascimento: formato DD/MM/AAAA.\n"
            "- rg: somente dígitos.\n"
            "- orgao_rg: sigla curta (ex.: SSP, PC, DETRAN).\n"
            "- uf_rg: UF do órgão expedidor com 2 letras (ex.: MT, SP).\n"
            "- quando houver FILIACAO/FILIAÇÃO, separar nome_pai e nome_mae corretamente.\n"
            "- NÃO use CPF no campo rg.\n"
            "Retorne apenas o objeto JSON."
        )
        request_payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {"text": prompt},
                        {
                            "inline_data": {
                                "mime_type": mime_type,
                                "data": base64.b64encode(content).decode("ascii"),
                            }
                        },
                    ],
                }
            ],
            "generationConfig": {
                "temperature": 0,
                "responseMimeType": "application/json",
            },
        }

        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
            f"?key={self.api_key}"
        )
        body = json.dumps(request_payload).encode("utf-8")
        request = urllib.request.Request(
            url,
            data=body,
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(
                request, timeout=self.timeout_seconds
            ) as response:
                payload = response.read().decode("utf-8", errors="ignore")
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="ignore")
            raise RuntimeError(f"HTTP {exc.code}: {detail[:280]}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"erro de conexão: {exc.reason}") from exc

        data = json.loads(payload)
        parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
        raw_text = ""
        if isinstance(parts, list):
            for part in parts:
                if isinstance(part, dict) and isinstance(part.get("text"), str):
                    raw_text = part["text"]
                    if raw_text.strip():
                        break

        if not raw_text.strip():
            prompt_feedback = data.get("promptFeedback", {})
            if prompt_feedback:
                raise RuntimeError(
                    f"resposta bloqueada: {json.dumps(prompt_feedback, ensure_ascii=False)}"
                )
            raise RuntimeError("resposta vazia da API.")

        parsed = self._parse_json_object(raw_text)
        return parsed, raw_text

    def _parse_json_object(self, raw: str) -> Dict[str, str]:
        text = (raw or "").strip()
        if not text:
            return {}
        parsed: object
        try:
            parsed = json.loads(text)
        except Exception:
            match = re.search(r"\{.*\}", text, flags=re.DOTALL)
            if not match:
                return {}
            try:
                parsed = json.loads(match.group(0))
            except Exception:
                return {}
        if not isinstance(parsed, dict):
            return {}
        out: Dict[str, str] = {}
        for key in self._TARGET_KEYS:
            value = parsed.get(key, "")
            out[key] = str(value).strip() if value is not None else ""
        return out

    def _normalize_gemini_fields(self, fields: Dict[str, str]) -> Dict[str, str]:
        out: Dict[str, str] = {}
        for key in self._TARGET_KEYS:
            value = self.local_extractor._clean_value(str(fields.get(key, "")))
            if not value:
                continue

            if key in {"nome", "nome_pai", "nome_mae"}:
                value = self.local_extractor._clean_person_name(value).upper()
            elif key == "sexo":
                ascii_value = self.local_extractor._ascii_lower(value)
                if ascii_value in {"m", "masculino"}:
                    value = "MASCULINO"
                elif ascii_value in {"f", "feminino"}:
                    value = "FEMININO"
                else:
                    value = ""
            elif key == "cpf":
                value = self._normalize_cpf(value)
            elif key == "rg":
                value = self.local_extractor._ocr_to_digits(value)
            elif key == "orgao_rg":
                value = re.sub(r"[^A-Za-z]", "", value).upper()
                if len(value) > 8:
                    value = value[:8]
            elif key == "uf_rg":
                value = self._normalize_uf(value)
            elif key == "data_nascimento":
                value = self._normalize_date(value)
            elif key == "naturalidade":
                value = re.sub(r"\s{2,}", " ", value).strip()

            if value:
                out[key] = value

        # Se houver RG e órgão vazio, mantém padrão notarial.
        if out.get("rg") and not out.get("orgao_rg"):
            out["orgao_rg"] = "SSP"
        return out

    def _normalize_cpf(self, value: str) -> str:
        formatted_match = re.search(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b", value)
        digits = ""
        if formatted_match:
            digits = self.local_extractor._ocr_to_digits(formatted_match.group(0))
        if not digits:
            digits = self.local_extractor._ocr_to_digits(value)
        if len(digits) < 11:
            return ""
        if len(digits) > 11:
            digits = digits[:11]
        return self.local_extractor._format_cpf_digits(digits)

    def _normalize_uf(self, value: str) -> str:
        uf_match = re.search(
            r"\b(AC|AL|AP|AM|BA|CE|DF|ES|GO|MA|MT|MS|MG|PA|PB|PR|PE|PI|RJ|RN|RS|RO|RR|SC|SP|SE|TO)\b",
            value.upper(),
        )
        if uf_match:
            return uf_match.group(1)
        letters = re.sub(r"[^A-Za-z]", "", value).upper()
        if len(letters) >= 2:
            return letters[-2:]
        return ""

    def _normalize_date(self, value: str) -> str:
        match = re.search(r"\b([0-3]?\d)[/\-.]([01]?\d)[/\-.](\d{2,4})\b", value)
        if not match:
            return ""
        day = int(match.group(1))
        month = int(match.group(2))
        year_raw = match.group(3)
        year = (
            int(year_raw) + 2000
            if len(year_raw) == 2 and int(year_raw) <= 30
            else int(year_raw)
        )
        if len(year_raw) == 2 and int(year_raw) > 30:
            year = int(year_raw) + 1900
        if day < 1 or day > 31 or month < 1 or month > 12:
            return ""
        return f"{day:02d}/{month:02d}/{year:04d}"

    @staticmethod
    def _guess_mime_type(file_path: Path) -> str:
        suffix = file_path.suffix.lower()
        explicit = {
            ".pdf": "application/pdf",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".bmp": "image/bmp",
            ".gif": "image/gif",
            ".webp": "image/webp",
            ".tif": "image/tiff",
            ".tiff": "image/tiff",
            ".heic": "image/heic",
            ".heif": "image/heif",
        }
        if suffix in explicit:
            return explicit[suffix]
        guessed, _ = mimetypes.guess_type(file_path.name)
        return guessed or "application/octet-stream"


def create_document_extractor() -> Tuple[ExtractorProtocol, List[str]]:
    """
    Define provedor de extração.

    Variáveis:
    - EXTRACTION_PROVIDER=gemini|local|auto (default: auto)
    - GEMINI_API_KEY=...
    - GEMINI_MODEL=gemini-2.5-flash (opcional)
    """
    provider = os.environ.get("EXTRACTION_PROVIDER", "auto").strip().lower()
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    warnings: List[str] = []

    if provider in {"gemini", "auto"} and api_key:
        return GeminiDocumentExtractor(api_key=api_key), warnings

    if provider == "gemini" and not api_key:
        warnings.append(
            "EXTRACTION_PROVIDER=gemini está ativo, mas GEMINI_API_KEY não foi definido; usado extrator local."
        )

    return DocumentExtractor(), warnings
