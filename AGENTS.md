# SEAPMNX Agent Memory

## Contexto tecnico
- Stack principal: Next.js 16 (App Router), React 19, TypeScript, Prisma, SQLite local.
- Diretorios-chave:
  - `src/app`: rotas, UI e acoes server.
  - `prisma`: schema e seed.
  - `public`: assets estaticos.
  - `docs`: documentacao operacional.
- Ambiente alvo de operacao: intranet/local, com opcao sem internet.

## Regras de seguranca
- Projeto confidencial e restrito.
- Nunca expor segredos de `.env`, tokens, chaves ou dados sensiveis em logs/documentacao.
- Em producao sem HTTPS interno, validar `SESSION_COOKIE_SECURE="false"` apenas quando necessario.
- Nao commitar `.env` real, dumps, backups e artefatos com dados operacionais.

## Padrao de interface
- Manter identidade visual liquid/glass ja adotada nas telas.
- Evitar regressao visual entre abas (dashboard, escalas, policiais, relatorios, parametros, usuarios).
- Tooltips precisam ficar legiveis e sem corte por overflow.

## Comandos operacionais
- Instalar dependencias: `npm install`
- Desenvolvimento: `npm run dev`
- Dev com cache limpo: `npm run dev:clean`
- Lint: `npm run lint`
- Typecheck: `npm run typecheck`
- Validacao completa: `npm run check`
- Sincronizar banco local: `npm run db:push`
- Popular banco local: `npm run db:seed`
- Build de producao: `npm run build`
- Subir producao: `npm run start`

## Codex MCP/Memory
- Bootstrap de MCP para este repo: `npm run codex:setup`
- Listar MCP ativos: `npm run codex:mcp:list`
- Memoria MCP persistente: `~/.codex/memory/seapmnx-memory.jsonl`
