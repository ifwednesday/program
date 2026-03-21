def only_digits(value: str) -> str:
    return "".join(ch for ch in (value or "") if ch.isdigit())


def validar_cpf(cpf: str) -> bool:
    """Valida CPF usando algoritmo de dígitos verificadores"""
    digits = only_digits(cpf)
    
    # CPF deve ter 11 dígitos
    if len(digits) != 11:
        return False
    
    # CPF não pode ser sequência de números iguais
    if digits == digits[0] * 11:
        return False
    
    # Validar primeiro dígito verificador
    soma = sum(int(digits[i]) * (10 - i) for i in range(9))
    resto = soma % 11
    digito1 = 0 if resto < 2 else 11 - resto
    
    if int(digits[9]) != digito1:
        return False
    
    # Validar segundo dígito verificador
    soma = sum(int(digits[i]) * (11 - i) for i in range(10))
    resto = soma % 11
    digito2 = 0 if resto < 2 else 11 - resto
    
    if int(digits[10]) != digito2:
        return False
    
    return True


def format_cpf(value: str) -> str:
    """Formata CPF para o padrão 000.000.000-00"""
    digits = only_digits(value)
    if len(digits) != 11:
        return value or ""
    return f"{digits[0:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:11]}"


def format_cep(value: str) -> str:
    """Formata CEP para o padrão 00000-000"""
    digits = only_digits(value)
    if len(digits) != 8:
        return value or ""
    return f"{digits[0:5]}-{digits[5:8]}"


def format_date(value: str) -> str:
    """Formata data para o padrão 00/00/0000"""
    digits = only_digits(value)
    if len(digits) == 8:
        return f"{digits[0:2]}/{digits[2:4]}/{digits[4:8]}"
    return value or ""


def auto_format_cpf(event) -> None:
    """Formata CPF automaticamente durante a digitação e valida"""
    widget = event.widget
    current_value = widget.get()
    digits = only_digits(current_value)

    if len(digits) <= 11:
        formatted = format_cpf(digits)
        if formatted != current_value:
            widget.delete(0, "end")
            widget.insert(0, formatted)
        
        # Validação visual - borda vermelha se inválido e completo (apenas CustomTkinter)
        try:
            if len(digits) == 11:
                if validar_cpf(digits):
                    widget.configure(border_color="#4a4a4a")  # Cor padrão
                else:
                    widget.configure(border_color="#d32f2f")  # Vermelho para inválido
            else:
                widget.configure(border_color="#4a4a4a")  # Cor padrão enquanto incompleto
        except Exception:
            # Widget não suporta border_color (tkinter padrão), ignora validação visual
            pass


def auto_format_date(event) -> None:
    """Formata data automaticamente durante a digitação"""
    widget = event.widget
    current_value = widget.get()
    digits = only_digits(current_value)

    if len(digits) <= 8:
        formatted = format_date(digits)
        if formatted != current_value:
            widget.delete(0, "end")
            widget.insert(0, formatted)
