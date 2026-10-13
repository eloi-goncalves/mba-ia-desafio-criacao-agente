# Residencial Aurora — assistente virtual (Google ADK)

Assistente de chat para os moradores do Residencial Aurora, construído com
**Google ADK** (série 2, versão fixa `2.2.0`) e exposto por uma **API FastAPI**.
Pelo chat, o morador reserva áreas comuns, cancela as próprias reservas, autoriza
visitantes e tira dúvidas sobre o regulamento. O modelo conduz a conversa, mas as
**regras críticas moram no código** — nenhuma mensagem fura as regras do condomínio.

> O enunciado original do desafio está preservado em
> [`docs/README.md`](docs/README.md).

## Arquitetura

O assistente é um sistema multiagente: um **agente principal** que conversa com o
morador e encaminha cada pedido a **especialistas** por domínio. Toda leitura e
gravação de reservas e visitantes passa por **tools** que acessam o armazenamento
— nunca por algo que o modelo "lembra" ou inventa. Os agentes estão em
[`app/agentes.py`](app/agentes.py) e as tools em [`app/tools.py`](app/tools.py).

| Agente | Responsabilidade | Como é acionado |
| --- | --- | --- |
| `coordenador` (principal) | Conversa com o morador e roteia o pedido. Não acessa dados nem recebe o regulamento. | Recebe a mensagem e transfere para o especialista. |
| `especialista_reservas` | Consulta, disponibilidade, reserva e cancelamento. | Transferência a partir do coordenador (`sub_agents`). |
| `especialista_visitantes` | Consulta e autorização de visitantes. | Transferência a partir do coordenador. |
| `especialista_regulamento` | Dúvidas sobre o regulamento, por consulta sob demanda. | Transferência a partir do coordenador. |

**Por quê:** separar por domínio mantém cada conjunto de tools coeso, reduz o
contexto enviado ao modelo em cada chamada e isola as regras críticas nas tools.
São três especialistas (acima do mínimo de dois) porque reservas, visitantes e
regulamento têm responsabilidades e dados bem distintos.

Fluxo de uma mensagem (camada HTTP em [`app/api.py`](app/api.py), execução em
[`app/runtime.py`](app/runtime.py)):

```
POST /sessoes {apartamento}      -> cria sessão persistente; grava o apartamento no state
POST .../mensagens {texto}       -> Runner executa; devolve resposta + confirmacoes_pendentes
POST .../confirmacoes {id, ...}  -> responde à confirmação; retoma a tool original
GET  .../eventos                 -> todos os eventos da sessão, em ordem
GET  /apartamentos/{n}/reservas  -> verificação direta (sem passar pelo modelo)
GET  /apartamentos/{n}/visitantes
```

## Garantias

Cada garantia é imposta em código e não depende do que o modelo decide.

### Garantia 1 — cobrança ou acesso só com confirmação

Ações que geram cobrança (reservar área com taxa > 0) ou liberam acesso (autorizar
visitante) chamam `tool_context.request_confirmation(...)` e ficam pendentes até a
resposta pela rota de confirmações. Em [`app/tools.py`](app/tools.py),
`reservar_area` e `autorizar_visitante`:

```python
confirmacao = tool_context.tool_confirmation
if confirmacao is None:
    tool_context.request_confirmation(hint=..., payload={"acao": ..., ...})
    return {"status": "pendente_confirmacao", ...}
if not confirmacao.confirmed:
    return {"status": "negada", ...}
# só aqui grava
```

A confirmação vem do **sistema**, não da conversa: dizer "já confirmo aqui" não
executa nada. A rota `POST /sessoes/{id}/confirmacoes` em
[`app/api.py`](app/api.py) só aceita um `id` que esteja **pendente naquela
sessão** — as pendências são derivadas dos eventos em
[`app/runtime.py`](app/runtime.py) (`confirmacoes_pendentes`), então qualquer
outro `id`, inclusive um já respondido, recebe `409` e nada executa.

### Garantia 2 — cada sessão pertence a um apartamento

O apartamento é gravado no `state` da sessão na criação
([`app/runtime.py`](app/runtime.py), `criar_sessao`) e é a **única** fonte usada
pelas tools. Em [`app/tools.py`](app/tools.py), `_apartamento(tool_context)` lê
`tool_context.state["apartamento"]`; nenhuma tool aceita um apartamento escolhido
pelo modelo. A disponibilidade (`verificar_disponibilidade`) devolve apenas
"livre"/"ocupada", sem revelar de quem é a reserva. Assim, nada que o morador
escreva altera ou traz dados de outro apartamento.

### Garantia 3 — nada se perde no reinício

As sessões usam `DatabaseSessionService` sobre SQLite
([`app/runtime.py`](app/runtime.py), `SESSION_DB_URL` em
[`app/config.py`](app/config.py)) e os dados do condomínio ficam em SQLite
([`app/storage.py`](app/storage.py)). Reiniciar a API preserva eventos e dados.

### Garantia 4 — o regulamento é consultado, não carregado

O agente principal **não recebe o regulamento nas instruções**
([`app/agentes.py`](app/agentes.py)). O especialista usa a tool
`consultar_regulamento`, que em [`app/regulamento.py`](app/regulamento.py) divide
o texto por artigo e devolve **apenas o trecho relevante** — nenhum evento carrega
capítulos de outros assuntos.

### Garantia 5 — dois moradores, uma reserva

A exclusividade vale **no instante da gravação**: um índice único parcial garante
no máximo uma reserva ativa por (área, data), em [`app/storage.py`](app/storage.py):

```sql
CREATE UNIQUE INDEX idx_reserva_unica_ativa
    ON reservas (area, data) WHERE ativa = 1;
```

`criar_reserva` grava dentro de `BEGIN IMMEDIATE` e trata a violação de unicidade
como recusa normal (retorna `None`, sem erro de servidor). Em uma disputa, uma
reserva vence e a outra é recusada. Os códigos de reserva nunca se repetem
(reservas canceladas permanecem com `ativa = 0`, então seus códigos não são
reaproveitados).

## Como rodar

### Pré-requisitos

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- Uma chave do Google AI Studio (modelos Gemini)

### Variáveis de ambiente

Copie o exemplo e preencha sua chave (o `.env` não é versionado):

```bash
cp .env.example .env
# edite .env e preencha GOOGLE_API_KEY
```

Variáveis de [`.env.example`](.env.example):

- `GOOGLE_API_KEY` — chave do Google AI Studio.
- `GOOGLE_GENAI_USE_VERTEXAI` — mantenha `FALSE` (usa o AI Studio).
- `GEMINI_MODEL` — modelo Gemini dos agentes (padrão `gemini-2.0-flash`).

### Instalar

```bash
uv sync
```

### Restaurar os dados iniciais

Repõe reservas e visitantes ao estado de `dados/*.json` (não apaga as sessões):

```bash
uv run python -m scripts.restaurar
```

### Subir a API

```bash
uv run uvicorn app.api:app --port 8000
```

A API responde em `http://localhost:8000`.

### Testes

```bash
uv run pytest -q
```

Para começar totalmente do zero (incluindo sessões), remova o diretório `var/`.
