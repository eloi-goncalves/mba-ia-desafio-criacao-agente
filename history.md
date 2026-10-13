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

## 2026-10-13 — Phase 02: Agentes ADK e tools

- **Fase:** Phase 02 (agentes + tools) — execução.
- **Entendimento:** arquitetura multiagente com o apartamento vindo da sessão
  (Garantia 2) e regulamento consultado sob demanda (Garantia 4).
- **Objetivo:** agente principal + 3 especialistas e tools que leem/gravam pelo
  storage.
- **Execução:**
  - `app/tools.py`: tools de reservas (consultar, disponibilidade, reservar,
    cancelar), visitantes (consultar, autorizar) e regulamento. Apartamento lido
    do `state` (`tool_context.state['apartamento']`). Confirmação via
    `tool_context.request_confirmation(hint, payload)` para reserva com taxa e
    para autorizar visitante (Garantia 1).
  - `app/regulamento.py`: recuperador que divide o regulamento por artigo e
    retorna apenas o trecho relevante (Garantia 4).
  - `app/agentes.py`: `coordenador` (principal, sem regulamento nas instruções) +
    `especialista_reservas`, `especialista_visitantes`, `especialista_regulamento`
    (via `sub_agents`). Modelo Gemini configurável (`GEMINI_MODEL`).
- **Arquivos modificados:** `app/config.py`, `.env.example`, `app/regulamento.py`,
  `app/tools.py`, `app/agentes.py`, `tests/test_regulamento.py`,
  `tests/test_tools.py`, `tests/test_agentes.py`.
- **Testes:** `uv run pytest -q` → 23 passaram (fundação + tools + regulamento +
  topologia dos agentes). Piscina aos domingos retorna "20h"; principal sem
  regulamento nas instruções; apartamento sempre da sessão; confirmação pendente
  não grava.
- **Validação:** API da confirmação do ADK 2.2.0 inspecionada
  (`ToolContext.request_confirmation`, `requested_tool_confirmations`,
  `tool_confirmation`). Execução end-to-end do modelo exige `GOOGLE_API_KEY`
  (fornecida pelo avaliador) — as partes determinísticas são cobertas por testes.
- **Commits:** sugerido abaixo.
- **Evidências:** `23 passed`; inspeção da API do ADK.
- **Problemas:** sem `GOOGLE_API_KEY` no ambiente; validação com o modelo fica para
  quem tiver a chave. Aviso de depreciação `BaseAgentConfig` (interno do ADK).
- **Bloqueios:** nenhum para a implementação; validação com modelo depende de chave.
- **Decisões:** 3 especialistas por domínio (reservas, visitantes, regulamento)
  via `sub_agents`; confirmação manual com `payload` para popular `detalhes`.
- **Próximos passos:** Phase 03 (API, Runner/App, confirmações, persistência).
- **status:** `executada`

> Sugestão de commit (pt-BR, Conventional Commits):
> `feat: agentes ADK (principal + 3 especialistas) e tools com confirmação e regulamento sob demanda`

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
