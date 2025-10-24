"""Constantes e valores padrão da aplicação"""

# Estados civis
ESTADOS_CIVIS_MASCULINO = ["solteiro", "casado", "divorciado", "viúvo"]
ESTADOS_CIVIS_FEMININO = ["solteira", "casada", "divorciada", "viúva"]
ESTADOS_CIVIS_TODOS = ESTADOS_CIVIS_FEMININO + ESTADOS_CIVIS_MASCULINO

# Tratamentos
TRATAMENTOS = ["Sr.", "Sra.", "Dr.", "Dra."]

# Nacionalidades
NACIONALIDADES_MASCULINO = ["brasileiro"]
NACIONALIDADES_FEMININO = ["brasileira"]

# Gêneros (terminações)
GENEROS = ["o", "a"]

# Regimes de casamento
REGIMES_CASAMENTO = [
    "comunhão parcial de bens",
    "comunhão universal de bens",
    "separação total de bens",
    "participação final nos aquestos",
]

# Unidades de área
UNIDADES_AREA = ["m²", "hectares", "alqueires"]

# Tipos de imóvel
TIPOS_IMOVEL = [
    "lote de terras",
    "casa",
    "apartamento",
    "terreno",
    "chácara",
    "fazenda",
    "sala comercial",
    "galpão",
]

# Zonas
ZONAS = ["zona urbana", "zona rural"]

# Estados do Brasil
ESTADOS_BRASIL = [
    ("AC", "Acre"),
    ("AL", "Alagoas"),
    ("AP", "Amapá"),
    ("AM", "Amazonas"),
    ("BA", "Bahia"),
    ("CE", "Ceará"),
    ("DF", "Distrito Federal"),
    ("ES", "Espírito Santo"),
    ("GO", "Goiás"),
    ("MA", "Maranhão"),
    ("MT", "Mato Grosso"),
    ("MS", "Mato Grosso do Sul"),
    ("MG", "Minas Gerais"),
    ("PA", "Pará"),
    ("PB", "Paraíba"),
    ("PR", "Paraná"),
    ("PE", "Pernambuco"),
    ("PI", "Piauí"),
    ("RJ", "Rio de Janeiro"),
    ("RN", "Rio Grande do Norte"),
    ("RS", "Rio Grande do Sul"),
    ("RO", "Rondônia"),
    ("RR", "Roraima"),
    ("SC", "Santa Catarina"),
    ("SP", "São Paulo"),
    ("SE", "Sergipe"),
    ("TO", "Tocantins"),
]

UF_BR_SIGLAS = [uf[0] for uf in ESTADOS_BRASIL]
UF_BR_NOMES = [uf[1] for uf in ESTADOS_BRASIL]

# Cores para UI
COLORS = {
    "primary": "#1f6aa5",
    "primary_hover": "#1a5a8a",
    "secondary": "#2d2d2d",
    "background": "#1a1a1a",
    "surface": "#3a3a3a",
    "border": "#4a4a4a",
    "border_hover": "#5a5a5a",
    "text": "#ffffff",
    "text_secondary": "#b3b3b3",
    "success": "#2e7d32",
    "success_hover": "#256428",
    "warning": "#f57c00",
    "warning_hover": "#db6e00",
    "error": "#d32f2f",
    "error_hover": "#b71c1c",
    "valid": "#4a4a4a",
    "invalid": "#d32f2f",
}

# Fontes
FONTS = {
    "default": ("Segoe UI", 11),
    "bold": ("Segoe UI", 11, "bold"),
    "title": ("Segoe UI", 14, "bold"),
    "small": ("Segoe UI", 10),
}

