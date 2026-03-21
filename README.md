# Qualificador

Aplicação desktop em Python para geração de qualificações e trechos padronizados em documentos jurídicos.

O projeto combina formulários estruturados, templates JSON e extração assistida de dados a partir de PDF e imagem. O foco é reduzir retrabalho operacional sem perder previsibilidade na saída gerada.

## Visão geral

O aplicativo atende aos seguintes fluxos:

- modelo simples de pessoa física
- certidão
- casados
- imóveis
- extração assistida para preenchimento das abas acima

Comportamentos centrais da aplicação:

- preserva os dados digitados ao alternar entre abas
- gera texto a partir de templates JSON versionáveis
- reaproveita campos compartilhados entre fluxos compatíveis
- mantém histórico local dos documentos gerados
- oferece atalhos de teclado e ações de limpeza pela interface

## Recursos

- interface desktop com Tkinter e CustomTkinter
- geração de texto para múltiplos cenários jurídicos
- suporte a extração local com leitura direta de PDF e OCR
- integração opcional com provedor remoto de extração
- pipeline opcional de pré-processamento e classificação local
- empacotamento para distribuição com PyInstaller

## Requisitos

- Python 3.10 ou superior
- Tk 8.6 ou superior
- dependências listadas em `requirements.txt`

Observação para macOS:

- evite `/usr/bin/python3` do Command Line Tools em versões recentes do sistema
- esse runtime costuma vir com Tk 8.5 e pode abortar ao abrir a interface

## Instalação

```bash
git clone <url-do-repositorio>
cd <pasta-do-projeto>

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Execução local

```bash
python main.py
```

## Build

```bash
python build.py
```

O binário gerado fica em `dist/Qualificador.exe` no Windows e em `dist/Qualificador` nos ambientes compatíveis usados para validação local.

## Extração de dados

### Modo padrão

O modo padrão usa processamento local:

- leitura estruturada de PDF quando possível
- OCR local para arquivos convertidos em imagem
- fallback automático entre estratégias disponíveis

### Provedor remoto opcional

Para usar o provedor remoto:

```bash
export GEMINI_API_KEY=...
export EXTRACTION_PROVIDER=gemini
```

### Pipeline local opcional

Para cenários com imagem difícil, orientação ruim ou OCR inconsistente, existe um pipeline local opcional de pré-processamento e classificação:

```bash
pip install -r requirements-ml.txt
export EXTRACTION_PROVIDER=ml
```

Se houver um classificador treinado, o caminho pode ser informado por variável de ambiente:

```bash
export ML_DOC_MODEL_PATH=app/models/doc_classifier.joblib
```

Documentação complementar:

- [docs/ml-extracao-documentos.md](docs/ml-extracao-documentos.md)

## Configuração

O arquivo `config.json` centraliza parâmetros de execução, como:

- valores padrão de formulários
- dimensões iniciais da janela
- política de histórico
- nível de log

## Qualidade

Verificações recomendadas:

```bash
black .
isort .
./.venv/bin/python -m flake8 app main.py build.py
./.venv/bin/python -m mypy app main.py build.py
./.venv/bin/python -m py_compile main.py build.py $(rg --files app -g '*.py')
```

## Estrutura do repositório

```text
.
├── app/
│   ├── constants/
│   ├── extractors/
│   ├── tabs/
│   ├── ui_builders/
│   ├── config.py
│   ├── extraction.py
│   ├── gui_tk.py
│   ├── handlers.py
│   ├── history.py
│   ├── logger.py
│   ├── ml_extraction.py
│   ├── shortcuts.py
│   ├── styles.py
│   ├── template_engine.py
│   └── validators.py
├── docs/
├── Scripts/ml/
├── templates/
├── .github/workflows/
├── build.py
├── config.json
├── main.py
├── pyproject.toml
├── requirements.txt
└── requirements-ml.txt
```

## Release

O pipeline de release está em `.github/workflows/build-release.yml` e executa:

- checkout do código
- preparação do Python
- instalação de dependências
- build com `python build.py`
- publicação dos artefatos na release

## Licença

Este repositório utiliza licença de uso pessoal não comercial.

Consulte:

- [LICENSE](LICENSE)
- [COMMERCIAL_LICENSE.md](COMMERCIAL_LICENSE.md)
