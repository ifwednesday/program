import logging
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox
from typing import Dict

logger = logging.getLogger(__name__)

try:
    from .config import get_config
    from .history import get_history_manager
    from .template_engine import render_template
    from .validators import (
        format_cep,
        format_cnpj,
        format_cpf,
        format_date,
        only_digits,
        validar_cnpj,
        validar_cpf,
    )
except ImportError:
    from config import get_config  # type: ignore
    from history import get_history_manager  # type: ignore
    from template_engine import render_template  # type: ignore
    from validators import (  # type: ignore
        format_cep,
        format_cnpj,
        format_cpf,
        format_date,
        only_digits,
        validar_cnpj,
        validar_cpf,
    )


class EventHandlers:
    def __init__(self, app):
        self.app = app
        self.history = get_history_manager()
        self.config = get_config()

    def values_from_inputs(self) -> Dict[str, str]:
        data = {
            k: (v.get() if isinstance(v, (tk.StringVar, tk.BooleanVar)) else v)
            for k, v in self.app.vars.items()
        }
        nome = (data.get("nome") or "").strip()
        if self.app.vars["nome_caps"].get():
            nome = nome.upper()
        data["nome"] = nome

        # Aplicar formatação automática para campos específicos
        data["cpf"] = format_cpf(data.get("cpf", ""))
        data["cep"] = format_cep(data.get("cep", ""))

        # Formatar datas
        for date_field in [
            "data_nascimento",
            "data_registro",
            "data_certidao",
            "cnh_data_expedicao",
            "cert_data",
        ]:
            if date_field in data:
                data[date_field] = format_date(data.get(date_field, ""))

        # Formatar CNPJ se existir
        if "cnpj" in data:
            data["cnpj"] = format_cnpj(data.get("cnpj", ""))

        data["tratamento"] = data.get("tratamento") or "Sr."
        genero = (data.get("genero_terminacao") or "o").lower()
        data["genero_terminacao"] = genero
        data["sufixo_a"] = "" if genero == "o" else "a"
        return data

    def reset_all_vars(self) -> None:
        defaults = {
            "nacionalidade": "brasileiro",
            "estado_civil": "solteiro",
            "orgao_rg": "SSP",
            "uf_rg": "MT",
            "cnh_uf": "MT",
            "profissao": "do lar",
            "logradouro": "Rua Campo Novo",
            "numero": "56",
            "bairro": "Sant'Ana",
            "cidade": "Nova Xavantina-MT",
            "cep": "78690-000",
            "email": "não declarado",
            "genero_terminacao": "o",
            "tratamento": "Sr.",
            # Campos casados pessoa 1
            "tratamento1": "Sr.",
            "genero_terminacao1": "o",
            "orgao_rg1": "SSP",
            "uf_rg1": "MT",
            "cnh_uf1": "MT",
            "profissao1": "do lar",
            "email1": "não declarado",
            # Campos casados pessoa 2
            "tratamento2": "Sra.",
            "genero_terminacao2": "a",
            "orgao_rg2": "SSP",
            "uf_rg2": "MT",
            "cnh_uf2": "MT",
            "profissao2": "do lar",
            "email2": "não declarado",
            # Endereço casados
            "logradouro_casados": "Rua Campo Novo",
            "numero_casados": "56",
            "bairro_casados": "Sant'Ana",
            "cidade_casados": "Nova Xavantina-MT",
            "cep_casados": "78690-000",
            # Empresa
            "logradouro_empresa": "Rua Campo Novo",
            "numero_empresa": "56",
            "bairro_empresa": "Sant'Ana",
            "cidade_empresa": "Nova Xavantina-MT",
            "cep_empresa": "78690-000",
            "email_empresa": "não declarado",
            "email_pessoal": "não declarado",
            # Imóvel
            "cidade_imovel": "Nova Xavantina",
        }
        for key, var in self.app.vars.items():
            if isinstance(var, tk.StringVar):
                var.set(defaults.get(key, ""))
            elif isinstance(var, tk.BooleanVar):
                var.set(key == "nome_caps")

    def on_generate_modelo(self) -> None:
        try:
            data = self.values_from_inputs()
            
            # Validar CPF se fornecido
            cpf = data.get("cpf", "")
            if cpf and len(only_digits(cpf)) == 11:
                if not validar_cpf(cpf):
                    logger.warning(f"CPF inválido fornecido: {cpf}")
                    messagebox.showwarning(
                        "Atenção",
                        "O CPF digitado é inválido. Verifique os dígitos.",
                    )
            
            if self.app.cnh_enabled.get():
                data.setdefault("cnh_uf", "MT")
                data.setdefault("cnh_numero", "")
                data.setdefault("cnh_data_expedicao", "")
                try:
                    output = render_template(self.app.template_text_cnh, data, strict=False)
                    template_used = "modelo_cnh"
                except KeyError as e:
                    logger.error(f"Campo obrigatório faltando no template CNH: {e}")
                    messagebox.showerror("Erro", f"Campo obrigatório faltando: {e}")
                    return
                except ValueError as e:
                    logger.error(f"Valor inválido no template CNH: {e}")
                    messagebox.showerror("Erro", f"Valor inválido: {e}")
                    return
                except Exception as e:
                    logger.exception("Erro inesperado ao gerar texto CNH")
                    messagebox.showerror("Erro", f"Erro ao gerar texto (CNH): {e}")
                    return
            else:
                try:
                    output = render_template(self.app.template_text, data, strict=False)
                    template_used = "modelo_padrao"
                except KeyError as e:
                    logger.error(f"Campo obrigatório faltando no template: {e}")
                    messagebox.showerror("Erro", f"Campo obrigatório faltando: {e}")
                    return
                except ValueError as e:
                    logger.error(f"Valor inválido no template: {e}")
                    messagebox.showerror("Erro", f"Valor inválido: {e}")
                    return
                except Exception as e:
                    logger.exception("Erro inesperado ao gerar texto")
                    messagebox.showerror("Erro", f"Erro ao gerar texto: {e}")
                    return

            self.app.preview.configure(state=tk.NORMAL)
            self.app.preview.delete("1.0", tk.END)
            self.app.preview.insert("1.0", output)
            self.app.preview.configure(state=tk.DISABLED)
            self.app.btn_copy.configure(state=tk.NORMAL)
            self.app.btn_save.configure(state=tk.NORMAL)
            self.app.status.configure(text="Texto gerado")
            
            # Adicionar ao histórico
            if self.config.get("historico.enabled", True):
                try:
                    self.history.add(template_used, data)
                    logger.info(f"Documento adicionado ao histórico: {data.get('nome', 'N/A')}")
                except Exception as e:
                    logger.error(f"Erro ao salvar no histórico: {e}")
                    
        except Exception as e:
            logger.exception("Erro crítico ao gerar modelo")
            messagebox.showerror("Erro", f"Erro crítico: {e}")

    def on_copy_modelo(self) -> None:
        text = self.app.preview.get("1.0", tk.END).strip()
        if not text:
            return
        try:
            self.app.clipboard_clear()
            self.app.clipboard_append(text)
            self.app.status.configure(text="Copiado para a área de transferência")
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Erro", f"Não foi possível copiar: {exc}")

    def on_save_modelo(self) -> None:
        text = self.app.preview.get("1.0", tk.END).strip()
        if not text:
            messagebox.showinfo("Salvar", "Nada para salvar")
            return
        nome = (self.app.vars["nome"].get() or "").strip().replace(" ", "_")
        cpf_digits = only_digits(self.app.vars["cpf"].get() or "")
        if self.app.cnh_enabled.get():
            default_name = (
                f"qualificacao_cnh_{nome or 'pessoa'}_{cpf_digits or 'cpf'}.txt"
            )
        else:
            default_name = f"qualificacao_{nome or 'pessoa'}_{cpf_digits or 'cpf'}.txt"
        file_path = filedialog.asksaveasfilename(
            title="Salvar como",
            defaultextension=".txt",
            initialdir=str(self.app.base_dir),
            initialfile=default_name,
            filetypes=(("Texto", "*.txt"), ("Todos os arquivos", "*.*")),
        )
        if file_path:
            try:
                Path(file_path).write_text(text, encoding="utf-8")
                self.app.status.configure(text=f"Arquivo salvo em {file_path}")
            except Exception as exc:  # noqa: BLE001
                messagebox.showerror("Erro", f"Erro ao salvar: {exc}")

    def on_clear_modelo(self) -> None:
        self.reset_all_vars()
        self.app.preview.configure(state=tk.NORMAL)
        self.app.preview.delete("1.0", tk.END)
        self.app.preview.configure(state=tk.DISABLED)
        self.app.btn_copy.configure(state=tk.DISABLED)
        self.app.btn_save.configure(state=tk.DISABLED)
        self.app.status.configure(text="Campos limpos")

    def on_generate_cert(self) -> None:
        data = self.values_from_inputs()
        data.setdefault("cert_matricula", "")
        data.setdefault("cert_data", "")
        
        # Verificar se CNH está ativado
        cnh_enabled = self.app.cnh_enabled_certidao.get()
        
        try:
            if cnh_enabled:
                data.setdefault("cnh_uf", "MT")
                data.setdefault("cnh_numero", "")
                data.setdefault("cnh_data_expedicao", "")
                output = render_template(self.app.template_text_cert_cnh, data, strict=False)
            else:
                output = render_template(self.app.template_text_cert, data, strict=False)
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Erro", f"Erro ao gerar texto (Certidão): {exc}")
            return
        self.app.preview3.configure(state=tk.NORMAL)
        self.app.preview3.delete("1.0", tk.END)
        self.app.preview3.insert("1.0", output)
        self.app.preview3.configure(state=tk.DISABLED)
        self.app.btn_copy3.configure(state=tk.NORMAL)
        self.app.btn_save3.configure(state=tk.NORMAL)
        self.app.status.configure(text="Texto (Certidão) gerado")

    def on_copy_cert(self) -> None:
        text = self.app.preview3.get("1.0", tk.END).strip()
        if not text:
            return
        try:
            self.app.clipboard_clear()
            self.app.clipboard_append(text)
            self.app.status.configure(
                text="Copiado (Certidão) para a área de transferência"
            )
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Erro", f"Não foi possível copiar (Certidão): {exc}")

    def on_save_cert(self) -> None:
        text = self.app.preview3.get("1.0", tk.END).strip()
        if not text:
            messagebox.showinfo("Salvar", "Nada para salvar")
            return
        nome = (self.app.vars["nome"].get() or "").strip().replace(" ", "_")
        cpf_digits = only_digits(self.app.vars["cpf"].get() or "")
        default_name = (
            f"qualificacao_certidao_{nome or 'pessoa'}_{cpf_digits or 'cpf'}.txt"
        )
        file_path = filedialog.asksaveasfilename(
            title="Salvar como",
            defaultextension=".txt",
            initialdir=str(self.app.base_dir),
            initialfile=default_name,
            filetypes=(("Texto", "*.txt"), ("Todos os arquivos", "*.*")),
        )
        if file_path:
            try:
                Path(file_path).write_text(text, encoding="utf-8")
                self.app.status.configure(text=f"Arquivo salvo em {file_path}")
            except Exception as exc:  # noqa: BLE001
                messagebox.showerror("Erro", f"Erro ao salvar: {exc}")

    def on_clear_cert(self) -> None:
        self.reset_all_vars()
        self.app.preview3.configure(state=tk.NORMAL)
        self.app.preview3.delete("1.0", tk.END)
        self.app.preview3.configure(state=tk.DISABLED)
        self.app.btn_copy3.configure(state=tk.DISABLED)
        self.app.btn_save3.configure(state=tk.DISABLED)
        self.app.status.configure(text="Campos limpos")

    def on_generate_casados(self) -> None:
        data = self.values_from_inputs()

        # Aplicar maiúsculas nos nomes
        if self.app.vars["nome_caps1"].get():
            data["nome1"] = (data.get("nome1") or "").upper()
        if self.app.vars["nome_caps2"].get():
            data["nome2"] = (data.get("nome2") or "").upper()

        # Calcular sufixos e artigos para o template
        genero1 = data.get("genero_terminacao1", "o")
        genero2 = data.get("genero_terminacao2", "a")
        data["sufixo_a1"] = "" if genero1 == "o" else "a"
        data["sufixo_a2"] = "" if genero2 == "o" else "a"
        data["conjuge_artigo"] = "a sua esposa" if genero2 == "a" else "o seu esposo"

        # Verificar quais pessoas têm CNH ativada
        cnh1_enabled = self.app.cnh_enabled1.get()
        cnh2_enabled = self.app.cnh_enabled2.get()

        # Gerar texto dinamicamente baseado nos switches CNH
        try:
            output = self._generate_casados_text(data, cnh1_enabled, cnh2_enabled)
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Erro", f"Erro ao gerar texto (Casados): {exc}")
            return

        self.app.preview_casados.configure(state=tk.NORMAL)
        self.app.preview_casados.delete("1.0", tk.END)
        self.app.preview_casados.insert("1.0", output)
        self.app.preview_casados.configure(state=tk.DISABLED)
        self.app.btn_copy_casados.configure(state=tk.NORMAL)
        self.app.btn_save_casados.configure(state=tk.NORMAL)
        self.app.status.configure(text="Texto (Casados) gerado")

    def _generate_casados_text(
        self, data: Dict, cnh1_enabled: bool, cnh2_enabled: bool
    ) -> str:
        """Gera texto para casados baseado nos switches CNH"""
        
        # Verificar se deve usar o modelo alternativo
        use_alternativo = getattr(
            self.app, "casados_modelo_alternativo", tk.BooleanVar(value=False)
        ).get()
        
        if use_alternativo:
            return self._generate_casados_text_alternativo(data, cnh1_enabled, cnh2_enabled)

        # Gerar texto da pessoa 1
        pessoa1_text = self._generate_pessoa_text(data, 1, cnh1_enabled)

        # Gerar texto da pessoa 2
        pessoa2_text = self._generate_pessoa_text(data, 2, cnh2_enabled)

        # Texto final
        conjuge_artigo = data.get("conjuge_artigo", "a sua esposa")
        regime_casamento = data.get("regime_casamento", "")
        cert_matricula = data.get("cert_casamento_matricula", "")
        logradouro = data.get("logradouro", "")
        numero = data.get("numero", "")
        bairro = data.get("bairro", "")
        cidade = data.get("cidade", "")
        cep = data.get("cep", "")

        return (
            f"{pessoa1_text}; e {conjuge_artigo} {pessoa2_text}; brasileiros, "
            f"casados sob o regime da {regime_casamento}, "
            f"na vigência da Lei n.º 6.515/77 "
            f"(conforme Certidão de Casamento lavrada sob a Matrícula n.º "
            f"{cert_matricula}, "
            f"expedidas nestas Notas), residentes e domiciliados à {logradouro}, "
            f"n.º {numero}, {bairro}, na cidade de {cidade} – CEP: {cep}"
        )
    
    def _generate_casados_text_alternativo(
        self, data: Dict, cnh1_enabled: bool, cnh2_enabled: bool
    ) -> str:
        """Gera texto para casados no formato alternativo"""
        
        # Obter dados da pessoa 1
        tratamento1 = data.get("tratamento1", "Sr.")
        nome1 = data.get("nome1", "")
        genero1 = data.get("genero_terminacao1", "o")
        nacionalidade1 = "brasileiro" if genero1 == "o" else "brasileira"
        naturalidade1 = data.get("naturalidade1", "")
        data_nascimento1 = data.get("data_nascimento1", "")
        nome_pai1 = data.get("nome_pai1", "")
        nome_mae1 = data.get("nome_mae1", "")
        sufixo_a1 = "" if genero1 == "o" else "a"
        rg1 = data.get("rg1", "")
        orgao_rg1 = data.get("orgao_rg1", "SSP")
        uf_rg1 = data.get("uf_rg1", "MT")
        cpf1 = data.get("cpf1", "")
        profissao1 = data.get("profissao1", "")
        email1 = data.get("email1", "")
        
        # Obter dados da pessoa 2
        tratamento2 = data.get("tratamento2", "Sra.")
        nome2 = data.get("nome2", "")
        genero2 = data.get("genero_terminacao2", "a")
        nacionalidade2 = "brasileiro" if genero2 == "o" else "brasileira"
        naturalidade2 = data.get("naturalidade2", "")
        data_nascimento2 = data.get("data_nascimento2", "")
        nome_pai2 = data.get("nome_pai2", "")
        nome_mae2 = data.get("nome_mae2", "")
        sufixo_a2 = "" if genero2 == "o" else "a"
        rg2 = data.get("rg2", "")
        orgao_rg2 = data.get("orgao_rg2", "SSP")
        uf_rg2 = data.get("uf_rg2", "MT")
        cpf2 = data.get("cpf2", "")
        profissao2 = data.get("profissao2", "")
        email2 = data.get("email2", "")
        
        # Dados do casamento
        regime_casamento = data.get("regime_casamento", "")
        cert_matricula = data.get("cert_casamento_matricula", "")
        # Usar campos de endereço - o formulário usa as mesmas chaves do modelo base
        logradouro = data.get("logradouro", "")
        numero = data.get("numero", "")
        bairro = data.get("bairro", "")
        cidade = data.get("cidade", "")
        cep = data.get("cep", "")
        
        # Gerar texto da pessoa 1
        if cnh1_enabled:
            cnh_uf1 = data.get("cnh_uf1", "MT")
            cnh_numero1 = data.get("cnh_numero1", "")
            cnh_data1 = data.get("cnh_data_expedicao1", "")
            pessoa1_text = (
                f"{tratamento1} {nome1}, {nacionalidade1}, natural de {naturalidade1}, "
                f"nascid{genero1} aos {data_nascimento1}, "
                f"filh{genero1} de {nome_pai1} e da Sra. {nome_mae1}, "
                f"portador{sufixo_a1} da CNH-{cnh_uf1} n.º {cnh_numero1}, "
                f"expedida em {cnh_data1}, onde consta o RG n.º "
                f"{rg1}/{orgao_rg1}-{uf_rg1}, "
                f"inscrit{genero1} no CPF/MF sob o n.º {cpf1}, {profissao1} "
                f"– com endereço eletrônico: {email1}"
            )
        else:
            pessoa1_text = (
                f"{tratamento1} {nome1}, {nacionalidade1}, natural de {naturalidade1}, "
                f"nascid{genero1} aos {data_nascimento1}, "
                f"filh{genero1} de {nome_pai1} e da Sra. {nome_mae1}, "
                f"portador{sufixo_a1} da CI/RG n.º {rg1}/{orgao_rg1}-{uf_rg1}, "
                f"inscrit{genero1} no CPF/MF sob o n.º {cpf1}, {profissao1} "
                f"– com endereço eletrônico: {email1}"
            )
        
        # Gerar texto da pessoa 2
        if cnh2_enabled:
            cnh_uf2 = data.get("cnh_uf2", "MT")
            cnh_numero2 = data.get("cnh_numero2", "")
            cnh_data2 = data.get("cnh_data_expedicao2", "")
            pessoa2_text = (
                f"{tratamento2} {nome2}, {nacionalidade2}, natural de {naturalidade2}, "
                f"nascid{genero2} aos {data_nascimento2}, "
                f"filh{genero2} de {nome_pai2} e da Sra. {nome_mae2}, "
                f"portador{sufixo_a2} da CNH-{cnh_uf2} n.º {cnh_numero2}, "
                f"expedida em {cnh_data2}, onde consta o RG n.º "
                f"{rg2}/{orgao_rg2}-{uf_rg2}, "
                f"inscrit{genero2} no CPF/MF sob o n.º {cpf2}, {profissao2} "
                f"– com endereço eletrônico: {email2}"
            )
        else:
            pessoa2_text = (
                f"{tratamento2} {nome2}, {nacionalidade2}, natural de {naturalidade2}, "
                f"nascid{genero2} aos {data_nascimento2}, "
                f"filh{genero2} de {nome_pai2} e da Sra. {nome_mae2}, "
                f"portador{sufixo_a2} da CI/RG n.º {rg2}/{orgao_rg2}-{uf_rg2}, "
                f"inscrit{genero2} no CPF/MF sob o n.º {cpf2}, {profissao2} "
                f"– com endereço eletrônico: {email2}"
            )
        
        # Determinar artigo para pessoa 2 baseado no gênero
        artigo_conjuge = "a" if genero2 == "a" else "o"
        
        # Texto final no formato alternativo
        return (
            f"{pessoa1_text}; casado sob o regime da {regime_casamento}, "
            f"na vigência da Lei n.º 6.515/77 "
            f"(conforme Certidão de Casamento lavrada sob a Matrícula n.º "
            f"{cert_matricula}, expedidas nestas Notas), com {artigo_conjuge} {pessoa2_text}; "
            f"residentes e domiciliados à {logradouro}, n.º {numero}, {bairro}, "
            f"na cidade de {cidade} – CEP: {cep}"
        )

    def _generate_pessoa_text(
        self, data: Dict, pessoa_num: int, cnh_enabled: bool
    ) -> str:
        """Gera texto para uma pessoa específica"""
        suffix = str(pessoa_num)

        tratamento = data.get(f"tratamento{suffix}", "Sr.")
        nome = data.get(f"nome{suffix}", "")
        naturalidade = data.get(f"naturalidade{suffix}", "")
        genero_terminacao = data.get(f"genero_terminacao{suffix}", "o")
        data_nascimento = data.get(f"data_nascimento{suffix}", "")
        nome_pai = data.get(f"nome_pai{suffix}", "")
        nome_mae = data.get(f"nome_mae{suffix}", "")
        sufixo_a = data.get(f"sufixo_a{suffix}", "")
        rg = data.get(f"rg{suffix}", "")
        orgao_rg = data.get(f"orgao_rg{suffix}", "SSP")
        uf_rg = data.get(f"uf_rg{suffix}", "GO")
        cpf = data.get(f"cpf{suffix}", "")
        profissao = data.get(f"profissao{suffix}", "")
        email = data.get(f"email{suffix}", "")

        if cnh_enabled:
            cnh_uf = data.get(f"cnh_uf{suffix}", "GO")
            cnh_numero = data.get(f"cnh_numero{suffix}", "")
            cnh_data = data.get(f"cnh_data_expedicao{suffix}", "")
            return (
                f"{tratamento} {nome}, natural de {naturalidade}, "
                f"nascid{genero_terminacao} aos {data_nascimento}, "
                f"filh{genero_terminacao} de {nome_pai} e da Sra. {nome_mae}, "
                f"portador{sufixo_a} da CNH-{cnh_uf} n.º {cnh_numero}, "
                f"expedida em {cnh_data}, onde consta o RG n.º "
                f"{rg}/{orgao_rg}-{uf_rg}, "
                f"inscrit{genero_terminacao} no CPF/MF sob o n.º {cpf}, {profissao} "
                f"– com endereço eletrônico: {email}"
            )
        else:
            return (
                f"{tratamento} {nome}, natural de {naturalidade}, "
                f"nascid{genero_terminacao} aos {data_nascimento}, "
                f"filh{genero_terminacao} de {nome_pai} e da Sra. {nome_mae}, "
                f"portador{sufixo_a} da CI/RG n.º "
                f"{rg}/{orgao_rg}-{uf_rg}, "
                f"inscrit{genero_terminacao} no CPF/MF sob o n.º {cpf}, {profissao} "
                f"– com endereço eletrônico: {email}"
            )

    def on_copy_casados(self) -> None:
        text = self.app.preview_casados.get("1.0", tk.END).strip()
        if not text:
            return
        try:
            self.app.clipboard_clear()
            self.app.clipboard_append(text)
            self.app.status.configure(
                text="Copiado (Casados) para a área de transferência"
            )
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Erro", f"Não foi possível copiar: {exc}")

    def on_save_casados(self) -> None:
        text = self.app.preview_casados.get("1.0", tk.END).strip()
        if not text:
            messagebox.showinfo("Salvar", "Nada para salvar")
            return
        nome1 = (self.app.vars["nome1"].get() or "").strip().replace(" ", "_")
        nome2 = (self.app.vars["nome2"].get() or "").strip().replace(" ", "_")
        cpf1_digits = only_digits(self.app.vars["cpf1"].get() or "")
        default_name = (
            f"qualificacao_casados_{nome1 or 'pessoa1'}_"
            f"{nome2 or 'pessoa2'}_{cpf1_digits or 'cpf'}.txt"
        )
        file_path = filedialog.asksaveasfilename(
            title="Salvar como",
            defaultextension=".txt",
            initialdir=str(self.app.base_dir),
            initialfile=default_name,
            filetypes=(("Texto", "*.txt"), ("Todos os arquivos", "*.*")),
        )
        if file_path:
            try:
                Path(file_path).write_text(text, encoding="utf-8")
                self.app.status.configure(text=f"Arquivo salvo em {file_path}")
            except Exception as exc:  # noqa: BLE001
                messagebox.showerror("Erro", f"Erro ao salvar: {exc}")

    def on_clear_casados(self) -> None:
        self.reset_all_vars()
        self.app.preview_casados.configure(state=tk.NORMAL)
        self.app.preview_casados.delete("1.0", tk.END)
        self.app.preview_casados.configure(state=tk.DISABLED)
        self.app.btn_copy_casados.configure(state=tk.DISABLED)
        self.app.btn_save_casados.configure(state=tk.DISABLED)
        self.app.status.configure(text="Campos limpos")

    def on_generate_empresa(self) -> None:
        try:
            data = self.values_from_inputs()

            # Validar CNPJ se fornecido
            cnpj = data.get("cnpj", "")
            if cnpj and len(only_digits(cnpj)) == 14:
                if not validar_cnpj(cnpj):
                    logger.warning(f"CNPJ inválido fornecido: {cnpj}")
                    messagebox.showwarning(
                        "Atenção",
                        "O CNPJ digitado é inválido. Verifique os dígitos.",
                    )

            # Aplicar maiúsculas no nome do representante
            if self.app.vars["nome_caps"].get():
                data["nome_representante"] = (data.get("nome_representante") or "").upper()

            # Mapear campos de endereço compartilhados para os campos específicos do template de empresa
            # O formulário da empresa agora usa as chaves compartilhadas (logradouro, numero, etc.)
            data["logradouro_empresa"] = data.get("logradouro", "")
            data["numero_empresa"] = data.get("numero", "")
            data["bairro_empresa"] = data.get("bairro", "")
            data["cidade_empresa"] = data.get("cidade", "")
            data["cep_empresa"] = data.get("cep", "")

            # Calcular sufixos e artigos para o template
            genero = data.get("genero_terminacao", "a")
            data["sufixo_a"] = "" if genero == "o" else "a"

            # Verificar se CNH está ativado
            cnh_enabled = self.app.cnh_enabled_empresa.get()

            try:
                if cnh_enabled:
                    data.setdefault("cnh_uf", "MT")
                    data.setdefault("cnh_numero", "")
                    data.setdefault("cnh_data_expedicao", "")
                    output = render_template(self.app.template_text_empresa, data, strict=False)
                else:
                    output = render_template(self.app.template_text_empresa_sem_cnh, data, strict=False)
            except KeyError as e:
                logger.error(f"Campo obrigatório faltando no template empresa: {e}")
                messagebox.showerror("Erro", f"Campo obrigatório faltando: {e}")
                return
            except ValueError as e:
                logger.error(f"Valor inválido no template empresa: {e}")
                messagebox.showerror("Erro", f"Valor inválido: {e}")
                return
            except Exception as e:
                logger.exception("Erro inesperado ao gerar texto empresa")
                messagebox.showerror("Erro", f"Erro ao gerar texto (Empresa): {e}")
                return

            self.app.preview_empresa.configure(state=tk.NORMAL)
            self.app.preview_empresa.delete("1.0", tk.END)
            self.app.preview_empresa.insert("1.0", output)
            self.app.preview_empresa.configure(state=tk.DISABLED)
            self.app.btn_copy_empresa.configure(state=tk.NORMAL)
            self.app.btn_save_empresa.configure(state=tk.NORMAL)
            self.app.status.configure(text="Texto (Empresa) gerado")
            
            # Adicionar ao histórico
            if self.config.get("historico.enabled", True):
                try:
                    self.history.add("modelo_empresa", data)
                    logger.info(f"Empresa adicionada ao histórico: {data.get('razao_social', 'N/A')}")
                except Exception as e:
                    logger.error(f"Erro ao salvar empresa no histórico: {e}")
                    
        except Exception as e:
            logger.exception("Erro crítico ao gerar documento de empresa")
            messagebox.showerror("Erro", f"Erro crítico: {e}")

    def on_copy_empresa(self) -> None:
        text = self.app.preview_empresa.get("1.0", tk.END).strip()
        if not text:
            return
        try:
            self.app.clipboard_clear()
            self.app.clipboard_append(text)
            self.app.status.configure(
                text="Copiado (Empresa) para a área de transferência"
            )
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Erro", f"Não foi possível copiar: {exc}")

    def on_save_empresa(self) -> None:
        text = self.app.preview_empresa.get("1.0", tk.END).strip()
        if not text:
            return
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[
                    ("Arquivos de texto", "*.txt"),
                    ("Todos os arquivos", "*.*"),
                ],
            )
            if filename:
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(text)
                self.app.status.configure(text=f"Arquivo salvo: {filename}")
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Erro", f"Não foi possível salvar: {exc}")

    def on_clear_empresa(self) -> None:
        # Limpar campos da empresa
        empresa_fields = [
            "razao_social",
            "cnpj",
            "junta_comercial",
            "nire",
            "logradouro_empresa",
            "numero_empresa",
            "quadra_empresa",
            "lote_empresa",
            "bairro_empresa",
            "cidade_empresa",
            "cep_empresa",
            "email_empresa",
            "numero_alteracao",
            "numero_registro",
            "data_registro",
            "uf_junta",
            "protocolo",
            "data_certidao",
            "autenticacao_eletronica",
            "cargo_representante",
            "nome_representante",
            "nacionalidade_empresa",
            "estado_civil_empresa",
            "naturalidade",
            "data_nascimento",
            "nome_pai",
            "nome_mae",
            "cnh_uf",
            "cnh_numero",
            "cnh_data_expedicao",
            "rg",
            "orgao_rg",
            "uf_rg",
            "cpf",
            "profissao",
            "endereco_pessoal",
            "email_pessoal",
        ]

        for field in empresa_fields:
            if field in self.app.vars:
                if isinstance(self.app.vars[field], tk.StringVar):
                    self.app.vars[field].set("")
                elif isinstance(self.app.vars[field], tk.BooleanVar):
                    self.app.vars[field].set(False)

        # Limpar preview
        self.app.preview_empresa.configure(state=tk.NORMAL)
        self.app.preview_empresa.delete("1.0", tk.END)
        self.app.preview_empresa.configure(state=tk.DISABLED)
        self.app.btn_copy_empresa.configure(state=tk.DISABLED)
        self.app.btn_save_empresa.configure(state=tk.DISABLED)
        self.app.status.configure(text="Campos limpos")

    def on_generate_imovel(self) -> None:
        data = self.values_from_inputs()

        try:
            output = render_template(self.app.template_text_imovel, data, strict=False)
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Erro", f"Erro ao gerar texto (Imóvel): {exc}")
            return

        self.app.preview_imovel.configure(state=tk.NORMAL)
        self.app.preview_imovel.delete("1.0", tk.END)
        self.app.preview_imovel.insert("1.0", output)
        self.app.preview_imovel.configure(state=tk.DISABLED)
        self.app.btn_copy_imovel.configure(state=tk.NORMAL)
        self.app.btn_save_imovel.configure(state=tk.NORMAL)
        self.app.status.configure(text="Texto (Imóvel) gerado")

    def on_copy_imovel(self) -> None:
        text = self.app.preview_imovel.get("1.0", tk.END).strip()
        if not text:
            return
        try:
            self.app.clipboard_clear()
            self.app.clipboard_append(text)
            self.app.status.configure(
                text="Copiado (Imóvel) para a área de transferência"
            )
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Erro", f"Não foi possível copiar: {exc}")

    def on_save_imovel(self) -> None:
        text = self.app.preview_imovel.get("1.0", tk.END).strip()
        if not text:
            return
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[
                    ("Arquivos de texto", "*.txt"),
                    ("Todos os arquivos", "*.*"),
                ],
            )
            if filename:
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(text)
                self.app.status.configure(text=f"Arquivo salvo: {filename}")
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Erro", f"Não foi possível salvar: {exc}")

    def on_clear_imovel(self) -> None:
        # Limpar campos do imóvel
        imovel_fields = [
            "quantidade_imovel",
            "tipo_imovel",
            "zona_imovel",
            "cidade_imovel",
            "estado_imovel",
            "loteamento",
            "area_valor",
            "area_unidade",
            "area_por_extenso",
            "lote",
            "lote_por_extenso",
            "quadra",
            "quadra_por_extenso",
        ]

        for field in imovel_fields:
            if field in self.app.vars:
                if isinstance(self.app.vars[field], tk.StringVar):
                    self.app.vars[field].set("")
                elif isinstance(self.app.vars[field], tk.BooleanVar):
                    self.app.vars[field].set(False)

        # Resetar valores padrão
        self.app.vars["quantidade_imovel"].set("Um (01)")
        self.app.vars["tipo_imovel"].set("lote de terras")
        self.app.vars["zona_imovel"].set("zona urbana")
        self.app.vars["cidade_imovel"].set("Nova Xavantina")
        self.app.vars["estado_imovel"].set("Mato Grosso")
        self.app.vars["area_unidade"].set("m²")

        # Limpar preview
        self.app.preview_imovel.configure(state=tk.NORMAL)
        self.app.preview_imovel.delete("1.0", tk.END)
        self.app.preview_imovel.configure(state=tk.DISABLED)
        self.app.btn_copy_imovel.configure(state=tk.DISABLED)
        self.app.btn_save_imovel.configure(state=tk.DISABLED)
        self.app.status.configure(text="Campos limpos")

    def on_exit(self) -> None:
        self.app.destroy()
