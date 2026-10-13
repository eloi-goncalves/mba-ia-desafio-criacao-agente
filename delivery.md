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
| `uv sync` sem erro, ADK série 2 `>=2.2.0` em versão exata | `pyproject.toml`, `uv.lock` | `google-adk==2.2.0` em [pyproject.toml](pyproject.toml) | `uv sync` | `ADK 2.2.0` importado | em andamento |
| Comandos de subida e restauração deixam a API em `localhost:8000` | `README.md`, comandos | `scripts/restaurar.py` (restauração); subida na Phase 03 | — | — | em andamento |
| `dados/` idêntico ao repositório base | `dados/` | somente leitura em [app/data_loader.py](app/data_loader.py) | `git status dados/` | sem alterações | executada |
| Nenhuma chave versionada; `.env` fora; `.env.example` com variáveis | `.env.example`, `.gitignore` | [.env.example](.env.example), [.gitignore](.gitignore) | `git check-ignore` | `.env`/`var/` ignorados | executada |

## Arquitetura

| Requisito | Artefato oficial | Implementação | Teste | Evidência | Status |
| --- | --- | --- | --- | --- | --- |
| Agente principal + ≥ 2 especialistas | código dos agentes | [app/agentes.py](app/agentes.py) (coordenador + 3 especialistas) | `test_topologia_dos_agentes` | 23 testes ok | em andamento |
| Reservas e visitantes lidos/gravados por tools | código das tools | [app/tools.py](app/tools.py) sobre [app/storage.py](app/storage.py) | `tests/test_tools.py` | 23 testes ok | em andamento |

## Garantia 1 — cobrança ou acesso só com confirmação

| Requisito | Artefato oficial | Implementação | Teste | Evidência | Status |
| --- | --- | --- | --- | --- | --- |
| Reservar área com taxa gera pendência (área+data); nada grava antes | API confirmações | `reservar_area` em [app/tools.py](app/tools.py) | `test_reservar_area_com_taxa_pede_confirmacao` | pendente, sem gravar | em andamento |
| Negar não grava | API confirmações | `reservar_area` em [app/tools.py](app/tools.py) | `test_reservar_area_negada_nao_grava` | status negada | em andamento |
| Aprovar grava exatamente uma reserva | API confirmações | `reservar_area` em [app/tools.py](app/tools.py) | `test_reservar_area_confirmada_grava_uma_vez` | 1 reserva | em andamento |
| Reenvio de confirmação já respondida → `409` | API confirmações | API na Phase 03 | — | — | pendente |
| `id` não pendente → `409`, nada muda | API confirmações | API na Phase 03 | — | — | pendente |
| Área sem taxa não gera confirmação | tools/reservas | `reservar_area` em [app/tools.py](app/tools.py) | `test_reservar_area_sem_taxa_nao_pede_confirmacao` | sem confirmação | em andamento |
| Autorizar visitante gera pendência (nome+data), mesmo com "já confirmo" | tools/visitantes | `autorizar_visitante` em [app/tools.py](app/tools.py) | `test_autorizar_visitante_sempre_pede_confirmacao` | pendente, sem gravar | em andamento |

## Garantia 2 — cada sessão pertence a um apartamento

| Requisito | Artefato oficial | Implementação | Teste | Evidência | Status |
| --- | --- | --- | --- | --- | --- |
| Pedir dados do 302 numa sessão do 101 não vaza `RSV-4821`/`Marina Duarte` | tools + `state` da sessão | [app/tools.py](app/tools.py) (`_apartamento`) | `test_nao_vaza_dados_de_outro_apartamento` | 23 testes ok | em andamento |
| Cancelar reserva do 302 numa sessão do 101 não altera o 302 nem vaza `RSV-4821` | tools/reservas | `cancelar_reserva` em [app/tools.py](app/tools.py) | `test_cancelar_so_afeta_proprio_apartamento` | status nao_encontrada | em andamento |
| Morador cancela a própria reserva sem confirmação | tools/reservas | `cancelar_reserva` em [app/tools.py](app/tools.py) | `test_cancelar_propria_reserva` | sem confirmação | em andamento |
| Reservar data ocupada pelo 302 não vaza `RSV-4821` nem `302` isolado | tools/reservas | `verificar_disponibilidade` em [app/tools.py](app/tools.py) | `test_disponibilidade_so_informa_livre_ou_ocupada` | sem vazamento | em andamento |
| Apartamento usado pelas tools vem da sessão (sem valor do modelo sem validação) | `state` da sessão + tools | `_apartamento` em [app/tools.py](app/tools.py) | `test_apartamento_vem_da_sessao` | 23 testes ok | em andamento |

## Garantia 3 — nada se perde no reinício

| Requisito | Artefato oficial | Implementação | Teste | Evidência | Status |
| --- | --- | --- | --- | --- | --- |
| Após reiniciar, sessão devolve os mesmos eventos e aceita novas mensagens | `SessionService` persistente | SQLite definido em [app/config.py](app/config.py) (`SESSION_DB_URL`) | — | — | em andamento |
| Reservas/cancelamentos/visitantes antes do reinício continuam; códigos não repetem | armazenamento persistente | [app/storage.py](app/storage.py) (SQLite) | `test_codigo_cancelado_nao_reaproveitado` | 8 testes ok | em andamento |

## Garantia 4 — o regulamento é consultado, não carregado

| Requisito | Artefato oficial | Implementação | Teste | Evidência | Status |
| --- | --- | --- | --- | --- | --- |
| A resposta sobre piscina aos domingos traz o horário de fechamento | tool/regulamento | [app/regulamento.py](app/regulamento.py) | `test_piscina_domingo_traz_horario_de_fechamento` | "20h" no trecho | em andamento |
| Nenhum evento contém trechos do regulamento de outros assuntos | tool/regulamento | recuperador por artigo em [app/regulamento.py](app/regulamento.py) | `test_nao_retorna_regulamento_inteiro` | sem outros capítulos | em andamento |
| Agente principal não recebe o regulamento nas instruções | agente principal | [app/agentes.py](app/agentes.py) (coordenador) | `test_principal_nao_recebe_regulamento_nas_instrucoes` | sem regulamento | em andamento |

## Garantia 5 — dois moradores, uma reserva

| Requisito | Artefato oficial | Implementação | Teste | Evidência | Status |
| --- | --- | --- | --- | --- | --- |
| Duas aprovações simultâneas respondem `200` | API + armazenamento | API na Phase 03 | — | — | em andamento |
| Após a disputa, soma exatamente uma reserva do salão em 2030-05-11 | armazenamento (constraint) | índice único parcial em [app/storage.py](app/storage.py) | `test_exclusividade_na_gravacao` | 1 reserva vence | em andamento |
| Exclusividade vale no instante da gravação | armazenamento (constraint) | `criar_reserva` + `idx_reserva_unica_ativa` em [app/storage.py](app/storage.py) | `test_exclusividade_na_gravacao` | 2ª gravação recusada | em andamento |

## Contrato e README

| Requisito | Artefato oficial | Implementação | Teste | Evidência | Status |
| --- | --- | --- | --- | --- | --- |
| Todas as rotas seguem o contrato (caminhos, campos, formatos, status) | API | — | — | — | pendente |
| README com Arquitetura, Garantias (arquivo+trecho reais) e Como rodar | `README.md` | — | — | — | pendente |
