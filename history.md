# history.md — Histórico global de execução

Histórico cronológico das execuções relevantes deste projeto. Cada entrada deve
registrar, em português: data, fase, entendimento, objetivo, execução, arquivos
modificados, testes, validação, commits, evidências, problemas, bloqueios,
decisões, próximos passos e `status`.

`status` permitido: `pendente` | `executada`.

> Nota: `history.md` e [`delivery.md`](delivery.md) fazem parte do sistema de
> rastreabilidade desta iniciativa e **não substituem** o enunciado oficial
> ([`docs/README.md`](docs/README.md)) nem o `README.md` de entrega.

---

## 2026-10-13 — Meta-planejamento (Camada 1)

- **Fase:** Meta-planejamento (não é execução do desafio).
- **Entendimento:** o repositório é *greenfield* (apenas `dados/` e o enunciado,
  duplicado em `README.md` e `docs/README.md`). Desafio: assistente Google ADK do
  Residencial Aurora, exposto por API, com cinco garantias em código. Não existem
  no repositório: workflow nomeado, skills oficiais, fases pré-definidas nem
  código. Git: branch `main`, commit único (`chore: enunciado e dados do
  desafio`), fork `eloi-goncalves/mba-ia-desafio-criacao-agente`.
- **Objetivo:** produzir a camada de meta-planejamento para orientar agentes
  futuros, sem implementar o desafio.
- **Execução:** criados os meta-planos em
  `docs/instructions/prompts_plans/` (`README.md` índice +
  `execution_plan_phase#01..04.md`) e os arquivos de rastreabilidade
  `history.md` e `delivery.md` na raiz.
- **Arquivos modificados:**
  - `docs/instructions/prompts_plans/README.md`
  - `docs/instructions/prompts_plans/execution_plan_phase#01.md`
  - `docs/instructions/prompts_plans/execution_plan_phase#02.md`
  - `docs/instructions/prompts_plans/execution_plan_phase#03.md`
  - `docs/instructions/prompts_plans/execution_plan_phase#04.md`
  - `history.md`
  - `delivery.md`
- **Testes:** não aplicável (nenhum código de produção alterado).
- **Validação:** revisão de conformidade dos meta-planos contra o enunciado
  oficial (ver índice em `docs/instructions/prompts_plans/README.md`).
- **Commits:** sugerido abaixo (ainda não executado automaticamente).
- **Evidências:** arquivos listados acima presentes no repositório.
- **Problemas:** o prompt-mestre usava caminhos/workflow genéricos inexistentes
  neste repositório (`mba-ia-greenfield-project`, `docs/instructions/readme.md`,
  `research → plan-context → ...`, "Phase 03 videos"). Adaptado à realidade.
- **Bloqueios:** nenhum.
- **Decisões:** decomposição em 4 meta-planos (fundação; agentes/tools; API/
  confirmações/persistência; garantias finais/validação/README), por ser a forma
  que melhor orienta a execução futura.
- **Próximos passos:** executar `execution_plan_phase#01.md` (fundação do projeto).
- **status:** `executada`

> Sugestão de commit (pt-BR, Conventional Commits):
> `docs: adicionar meta-planos de execução e rastreabilidade (history/delivery)`

---

## 2026-10-13 — Phase 01: Fundação e infraestrutura

- **Fase:** Phase 01 (fundação) — execução.
- **Entendimento:** base técnica do projeto, habilitando Garantias 3
  (persistência) e 5 (exclusividade na gravação).
- **Objetivo:** projeto `uv`, ADK fixo, carregamento dos dados, armazenamento
  persistente, `.env.example`, comando de restauração.
- **Execução:**
  - `uv` instalado (0.13.0); `pyproject.toml` com `google-adk==2.2.0` (versão do
    curso, citada na dica como testada), `fastapi`, `uvicorn[standard]`,
    `python-dotenv`; `uv.lock` gerado; `uv sync` sem erro.
  - Pacote `app/`: `config.py` (caminhos/ambiente), `data_loader.py` (leitura
    somente-leitura de `dados/`), `storage.py` (SQLite com índice único parcial
    para exclusividade de reserva ativa por área+data).
  - `scripts/restaurar.py` (comando de restauração).
  - `.env.example` (sem valores) e `.gitignore` atualizado (`var/`, `*.db`).
- **Arquivos modificados:** `pyproject.toml`, `uv.lock`, `.env.example`,
  `.gitignore`, `app/*.py`, `scripts/*.py`, `tests/test_fundacao.py`.
- **Testes:** `uv run pytest -q` → 8 passaram (carregamento, disponibilidade sem
  vazamento, código único, exclusividade na gravação, cancelamento só do próprio
  apartamento, código cancelado não reaproveitado, autorização de visitante).
- **Validação:** ADK 2.2.0 importado; `dados/` intacto; `.env` e `var/` ignorados.
- **Commits:** sugerido abaixo.
- **Evidências:** saída de `uv sync`; `8 passed in 0.12s`; `git check-ignore` ok.
- **Problemas:** `uv` não vinha instalado (instalado via script oficial); o
  `.gitignore` inicial não cobria `var/`/`*.db` (corrigido).
- **Bloqueios:** nenhum. (Execução end-to-end do modelo exige `GOOGLE_API_KEY`,
  que será necessária nas fases com agentes; a fundação é testável sem chave.)
- **Decisões:** SQLite como armazenamento (sessão persistente do ADK + dados do
  condomínio); exclusividade via índice único parcial `WHERE ativa = 1`.
- **Próximos passos:** Phase 02 (agentes ADK + tools).
- **status:** `executada`

> Sugestão de commit (pt-BR, Conventional Commits):
> `feat: fundação do projeto (uv, ADK 2.2.0, carregamento de dados e storage SQLite)`

---

## Modelo para novas entradas

```
## AAAA-MM-DD — <Fase>

- Fase:
- Entendimento:
- Objetivo:
- Execução:
- Arquivos modificados:
- Testes:
- Validação:
- Commits:
- Evidências:
- Problemas:
- Bloqueios:
- Decisões:
- Próximos passos:
- status: pendente | executada
```
