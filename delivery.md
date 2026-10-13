# delivery.md — Rastreabilidade das entregas

Rastreabilidade: **Requisito → Artefato oficial → Implementação → Teste →
Evidência → Status**.

`Status` permitido: `pendente` | `em andamento` | `executada`.

> `delivery.md` e [`history.md`](history.md) **não substituem** o enunciado
> oficial ([`docs/README.md`](docs/README.md)) nem o `README.md` de entrega. Os
> ponteiros de "Implementação", "Teste" e "Evidência" devem ser preenchidos
> durante a execução futura, apontando **arquivos e trechos que existem**.

Mapa de execução (meta-planos → entregas):
[`docs/instructions/prompts_plans/README.md`](docs/instructions/prompts_plans/README.md).

## Execução e entrega

| Requisito (critério de aceite) | Artefato oficial | Implementação | Teste | Evidência | Status |
| --- | --- | --- | --- | --- | --- |
| `uv sync` sem erro, ADK série 2 `>=2.2.0` em versão exata | `pyproject.toml`, `uv.lock` | — | — | — | pendente |
| Comandos de subida e restauração deixam a API em `localhost:8000` | `README.md`, comandos | — | — | — | pendente |
| `dados/` idêntico ao repositório base | `dados/` | — | — | — | pendente |
| Nenhuma chave versionada; `.env` fora; `.env.example` com variáveis | `.env.example`, `.gitignore` | — | — | — | pendente |

## Arquitetura

| Requisito | Artefato oficial | Implementação | Teste | Evidência | Status |
| --- | --- | --- | --- | --- | --- |
| Agente principal + ≥ 2 especialistas | código dos agentes | — | — | — | pendente |
| Reservas e visitantes lidos/gravados por tools | código das tools | — | — | — | pendente |

## Garantia 1 — cobrança ou acesso só com confirmação

| Requisito | Artefato oficial | Implementação | Teste | Evidência | Status |
| --- | --- | --- | --- | --- | --- |
| Reservar área com taxa gera pendência (área+data); nada grava antes | API confirmações | — | — | — | pendente |
| Negar não grava | API confirmações | — | — | — | pendente |
| Aprovar grava exatamente uma reserva | API confirmações | — | — | — | pendente |
| Reenvio de confirmação já respondida → `409` | API confirmações | — | — | — | pendente |
| `id` não pendente → `409`, nada muda | API confirmações | — | — | — | pendente |
| Área sem taxa não gera confirmação | tools/reservas | — | — | — | pendente |
| Autorizar visitante gera pendência (nome+data), mesmo com "já confirmo" | tools/visitantes | — | — | — | pendente |

## Garantia 2 — cada sessão pertence a um apartamento

| Requisito | Artefato oficial | Implementação | Teste | Evidência | Status |
| --- | --- | --- | --- | --- | --- |
| Pedir dados do 302 numa sessão do 101 não vaza `RSV-4821`/`Marina Duarte` | tools + `state` da sessão | — | — | — | pendente |
| Cancelar reserva do 302 numa sessão do 101 não altera o 302 nem vaza `RSV-4821` | tools/reservas | — | — | — | pendente |
| Morador cancela a própria reserva sem confirmação | tools/reservas | — | — | — | pendente |
| Reservar data ocupada pelo 302 não vaza `RSV-4821` nem `302` isolado | tools/reservas | — | — | — | pendente |
| Apartamento usado pelas tools vem da sessão (sem valor do modelo sem validação) | `state` da sessão + tools | — | — | — | pendente |

## Garantia 3 — nada se perde no reinício

| Requisito | Artefato oficial | Implementação | Teste | Evidência | Status |
| --- | --- | --- | --- | --- | --- |
| Após reiniciar, sessão devolve os mesmos eventos e aceita novas mensagens | `SessionService` persistente | — | — | — | pendente |
| Reservas/cancelamentos/visitantes antes do reinício continuam; códigos não repetem | armazenamento persistente | — | — | — | pendente |

## Garantia 4 — o regulamento é consultado, não carregado

| Requisito | Artefato oficial | Implementação | Teste | Evidência | Status |
| --- | --- | --- | --- | --- | --- |
| Resposta sobre piscina aos domingos traz o horário de fechamento | tool/regulamento | — | — | — | pendente |
| Nenhum evento contém trechos do regulamento de outros assuntos | tool/regulamento | — | — | — | pendente |
| Agente principal não recebe o regulamento nas instruções | agente principal | — | — | — | pendente |

## Garantia 5 — dois moradores, uma reserva

| Requisito | Artefato oficial | Implementação | Teste | Evidência | Status |
| --- | --- | --- | --- | --- | --- |
| Duas aprovações simultâneas respondem `200` | API + armazenamento | — | — | — | pendente |
| Após a disputa, soma exatamente uma reserva do salão em 2030-05-11 | armazenamento (constraint) | — | — | — | pendente |
| Exclusividade vale no instante da gravação | armazenamento (constraint) | — | — | — | pendente |

## Contrato e README

| Requisito | Artefato oficial | Implementação | Teste | Evidência | Status |
| --- | --- | --- | --- | --- | --- |
| Todas as rotas seguem o contrato (caminhos, campos, formatos, status) | API | — | — | — | pendente |
| README com Arquitetura, Garantias (arquivo+trecho reais) e Como rodar | `README.md` | — | — | — | pendente |
