# Extracao ML de RG/CPF/CNH

Este projeto agora suporta um extrator `ML hibrido` para melhorar leitura de documentos em imagens com:
- angulo ruim,
- perspectiva deformada,
- baixa qualidade de captura,
- frente e verso em arquivos separados.

## 1) Ativar no app

Defina variaveis de ambiente antes de abrir o aplicativo:

```bash
export EXTRACTION_PROVIDER=ml
export ML_DOC_MODEL_PATH=app/models/doc_classifier.joblib
```

Se o modelo nao existir, o extrator continua funcionando com heuristicas.

## 2) Dependencias opcionais

```bash
pip install -r requirements-ml.txt
```

Sem essas dependencias, o app volta para OCR local basico automaticamente.

## 3) Estrutura do banco de treino

Organize as imagens assim:

```text
dataset_docs/
  RG/
    FRENTE/
      *.jpg
    VERSO/
      *.jpg
  CPF/
    FRENTE/
      *.jpg
    VERSO/
      *.jpg
  CNH/
    FRENTE/
      *.jpg
    VERSO/
      *.jpg
```

Recomendacao:
- usar muitos exemplos reais do seu fluxo interno (boa/ruim iluminacao, camera torta, corte parcial),
- manter rotulo correto de tipo e lado,
- nao versionar imagens sensiveis no Git.

## 4) Pipeline de treino

1. Gerar augmentations (rotacao/perspectiva/ruido):

```bash
python Scripts/ml/augment_dataset.py \
  --input-root dataset_docs \
  --output-root dataset_docs_aug \
  --copies 4
```

2. Converter imagens em dataset OCR (`jsonl`):

```bash
python Scripts/ml/build_training_dataset.py \
  --input-root dataset_docs_aug \
  --output-jsonl app/models/doc_samples.jsonl
```

3. Treinar classificador de tipo/lado:

```bash
python Scripts/ml/train_doc_classifier.py \
  --dataset-jsonl app/models/doc_samples.jsonl \
  --output-model app/models/doc_classifier.joblib
```

## 5) O que o extrator ML faz

- corrige inclinacao da imagem (deskew),
- tenta corrigir perspectiva (warp por contorno dominante),
- cria multiplas variacoes da imagem,
- roda OCR e escolhe o melhor texto,
- classifica tipo (`RG`, `CPF`, `CNH`) e lado (`FRENTE`, `VERSO`),
- faz merge dos campos extraidos de varios arquivos com pontuacao por confianca,
- extrai campos comuns e de CNH (`cnh_numero`, `cnh_data_expedicao`, `cnh_uf`).

## 6) Seguranca operacional

- nao publique documentos reais,
- nao inclua dumps operacionais em commits,
- mantenha o dataset de treino em area controlada da intranet.
