# Qualificador

Sistema desktop para geração de qualificações de partes em documentos jurídicos.

Versão atual: `2.2.2`

## 📋 Descrição

O Qualificador é uma aplicação desktop desenvolvida em Python que facilita a criação de qualificações completas de partes (pessoas físicas, jurídicas, casais, imóveis, etc.) utilizando templates pré-configurados.

## ✨ Funcionalidades

- 🆔 Qualificação de pessoas físicas (com ou sem CNH)
- 👰 Qualificação de casais (com ou sem CNH)
- 📄 Qualificação de certidões
- 🏢 Qualificação de empresas
- 🏠 Qualificação de imóveis
- 📝 Sistema de templates personalizáveis
- 💾 Histórico de qualificações recentes
- 🧹 Limpeza de cache por botão na interface
- ⌨️ Atalhos de teclado para produtividade
- 🎨 Interface moderna e intuitiva

## 🚀 Download

Faça o download da versão mais recente na [página de Releases](../../releases).

Arquivos disponíveis para download:
- `Qualificador.exe` - Executável principal
- `config.json` - Arquivo de configuração (opcional)
- `LICENSE` - Licença do projeto

## 💻 Uso

1. Baixe o arquivo `Qualificador.exe` da última release
2. Execute o arquivo (não precisa instalação)
3. Selecione a aba correspondente ao tipo de qualificação
4. Preencha os campos necessários
5. Clique em "Copiar" para copiar a qualificação formatada
6. Use "Limpar cache" na barra inferior quando quiser limpar caches temporários

## 🛠️ Desenvolvimento

### Requisitos

- Python 3.10+ (recomendado 3.11 ou 3.12)
- Dependências listadas em `requirements.txt`

> **Importante (macOS 26+)**: não use `/usr/bin/python3` (Command Line Tools, Tk 8.5).
> Esse runtime pode abortar ao abrir a interface Tk.
> Use Python instalado via python.org (ou outro distribuidor com Tk 8.6).

### Instalação para desenvolvimento

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/qualificador.git
cd qualificador

# Crie um ambiente virtual
python -m venv env

# Ative o ambiente virtual
# Windows:
env\Scripts\activate
# Linux/Mac:
source env/bin/activate

# Instale as dependências
pip install -r requirements.txt
```

### Executar em modo de desenvolvimento

```bash
python main.py
```

### Build do executável

```bash
python build.py
```

O executável será gerado em `dist/Qualificador.exe`.

### Ferramentas de desenvolvimento

O projeto utiliza:
- **Black**: Formatação de código
- **isort**: Organização de imports
- **Flake8**: Linting
- **MyPy**: Type checking

```bash
# Formatar código
black .

# Organizar imports
isort .

# Verificar linting
flake8 .

# Verificar tipos
mypy .
```

### Extração ML (opcional)

Para extração mais robusta de RG/CPF/CNH com imagens inclinadas (frente/verso), use o modo ML:

```bash
pip install -r requirements-ml.txt
export EXTRACTION_PROVIDER=ml
```

Guia completo de dataset/treino: `docs/ml-extracao-documentos.md`.

## 📁 Estrutura do Projeto

```
qualificador/
├── app/                    # Código fonte principal
│   ├── constants/          # Constantes e dados estáticos
│   ├── tabs/               # Implementação das abas
│   ├── ui_builders/        # Construtores de interface
│   ├── config.py           # Configurações
│   ├── gui_tk.py           # Interface principal
│   ├── handlers.py         # Handlers de eventos
│   ├── history.py          # Gestão de histórico
│   ├── logger.py           # Sistema de logs
│   ├── shortcuts.py        # Atalhos de teclado
│   ├── styles.py           # Estilos visuais
│   ├── template_engine.py  # Engine de templates
│   └── validators.py       # Validadores de dados
├── templates/              # Templates de qualificação
├── .github/                # Workflows do GitHub Actions
├── main.py                 # Ponto de entrada
├── build.py                # Script de build
├── config.json             # Configuração padrão
└── requirements.txt        # Dependências Python
```

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para:

1. Fazer um fork do projeto
2. Criar uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abrir um Pull Request

## 📝 Licença

Este projeto utiliza uma **Licença de Uso Pessoal Não-Comercial**:

- ✅ **Uso pessoal**: GRATUITO para indivíduos
- ✅ **Profissionais autônomos**: Podem usar para seu próprio trabalho
- ❌ **Empresas/Organizações**: REQUEREM licença comercial paga
- ❌ **Uso comercial**: PROIBIDO sem licença apropriada

**Para uso comercial/empresarial**, entre em contato através das [issues](../../issues) do projeto para obter uma licença comercial.

Veja o arquivo [LICENSE](LICENSE) para todos os termos e condições detalhados.

## 📞 Contato

Para dúvidas, sugestões ou reportar problemas, abra uma [issue](../../issues) no GitHub.

---

**Desenvolvido com ❤️ em Python**

