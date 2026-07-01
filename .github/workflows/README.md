# GitHub Actions Workflows

## build-release.yml

Workflow automatizado para build e publicação do executável Qualificador.

### Quando é executado:

1. **Automaticamente**: push em `master`, push de tag `v*`, pull request para `master`, ou publicação de release no GitHub
2. **Manualmente**: Via interface do GitHub Actions (aba Actions)

### O que faz:

1. ✅ Faz checkout do código
2. 🐍 Configura Python 3.11
3. 📦 Instala as dependências do `requirements.txt`
4. 🔨 Executa o `build.py` para criar o executável
5. ✔️ Verifica se o `.exe` foi criado corretamente
6. 🚀 Publica o executável na release do GitHub

### Como usar:

#### Opção 1: Criar uma Release (Recomendado)

1. Vá até a página do seu repositório no GitHub
2. Clique em **"Releases"** (barra lateral direita)
3. Clique em **"Draft a new release"**
4. Preencha:
   - **Tag version**: ex: `v1.0.0`, `v1.1.0`, etc.
   - **Release title**: ex: "Qualificador v1.0.0"
   - **Description**: descreva as mudanças da versão
5. Clique em **"Publish release"**
6. O workflow será executado automaticamente
7. Após alguns minutos, o executável estará disponível para download na release

#### Opção 2: Executar Manualmente (Para Testes)

1. Vá até a aba **"Actions"** no GitHub
2. Selecione **"Build and Release"** na lista de workflows
3. Clique em **"Run workflow"**
4. Selecione a branch e clique em **"Run workflow"**
5. Após a execução, o executável estará disponível como artefato por 7 dias

### Requisitos:

- O repositório deve estar no GitHub
- Não precisa configurar secrets (usa o token automático do GitHub)
- O workflow roda em Windows (necessário para gerar o .exe)

### Estrutura de arquivos publicados:

Quando uma release é publicada, os seguintes arquivos são anexados:
- `Qualificador.exe` - O executável principal
- `config.json` - Arquivo de configuração padrão
- `LICENSE` - Licença de Uso Pessoal Não-Comercial
- `COMMERCIAL_LICENSE.md` - Informações sobre licenciamento comercial

### Troubleshooting:

Se o workflow falhar, verifique:
1. Todas as dependências estão no `requirements.txt`
2. O `build.py` funciona localmente
3. Os logs do workflow na aba Actions do GitHub

