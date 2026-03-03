"""Extrator remoto (Gemini) com fallback para OCR local."""

from __future__ import annotations

import base64
import json
import mimetypes
import os
import re
import urllib.error
import urllib.request
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

from .local import DocumentExtractor, ExtractionResult


class GeminiDocumentExtractor:
    """Extrator remoto com Gemini API (fallback local em falhas)."""

    _TARGET_KEYS = (
        "nome",
        "nome_pai",
        "nome_mae",
        "sexo",
        "cpf",
        "cnh_numero",
        "cnh_data_expedicao",
        "cnh_uf",
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
            "nome, nome_pai, nome_mae, sexo, cpf, rg, orgao_rg, uf_rg, data_nascimento, naturalidade, cnh_numero, cnh_data_expedicao, cnh_uf.\n"
            "Regras:\n"
            "- sexo: MASCULINO ou FEMININO.\n"
            "- se vier em letra única, converta: M->MASCULINO, F->FEMININO.\n"
            "- cpf: no formato 000.000.000-00 (ou vazio se ilegível).\n"
            "- data_nascimento: formato DD/MM/AAAA.\n"
            "- cnh_numero: somente dígitos (preferencialmente 11).\n"
            "- cnh_data_expedicao: formato DD/MM/AAAA.\n"
            "- cnh_uf: UF com 2 letras (AC..TO).\n"
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
            elif key == "cnh_numero":
                value = self.local_extractor._ocr_to_digits(value)
                if len(value) < 9:
                    value = ""
                elif len(value) > 11:
                    value = value[:11]
            elif key == "cnh_data_expedicao":
                value = self._normalize_date(value)
            elif key == "cnh_uf":
                value = self._normalize_uf(value)
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

