# Meta-planos de execução — índice

Este diretório contém **meta-planos** (prompts/planos operacionais) destinados a
orientar **agentes de IA futuros** na execução do desafio acadêmico
"Regra é regra: o assistente virtual do Residencial Aurora".

> IMPORTANTE — distinção entre as duas camadas
>
> - **Camada 1 (estes documentos):** ensinam *como* um agente deve executar o
>   desafio. São orientação, não entrega.
> - **Camada 2 (execução futura):** a implementação real do desafio, guiada pelo
>   documento oficial [`docs/README.md`](../../README.md).
>
> Os meta-planos **não substituem, não alteram e não reinterpretam** o enunciado
> oficial. Em qualquer conflito, **o enunciado oficial vence**.

## Autoridade oficial

O documento de autoridade é o enunciado do desafio, presente em dois locais
idênticos neste repositório:

- [`README.md`](../../../README.md) (raiz)
- [`docs/README.md`](../../README.md)

Antes de qualquer execução, o agente executor **deve ler o enunciado oficial
integralmente**, incluindo a seção **"Dicas finais"** e os **Critérios de aceite**.

## Observações sobre o estado real do repositório (verificado em 2026-10-13)

O prompt-mestre que originou estes meta-planos usava, como exemplo genérico,
caminhos e um workflow que **não existem** neste repositório. Os meta-planos
foram adaptados à realidade verificada:

- O projeto real é `mba-ia-desafio-criacao-agente` (não "greenfield-project").
- O enunciado oficial está em `docs/README.md` (não em
  `docs/instructions/readme.md`).
- **Não existe** um workflow oficial do tipo
  `research → plan-context → plan-validate → plan-resolve → plan-build → implement`.
- **Não existem** skills oficiais versionadas no repositório.
- **Não existem** fases acadêmicas pré-definidas nem fases concluídas: o
  repositório é *greenfield* (só o enunciado e os dados em `dados/`).
- O repositório é um fork (`eloi-goncalves/mba-ia-desafio-criacao-agente`) na
  branch `main`, com um único commit inicial (`chore: enunciado e dados do
  desafio`).

Como o enunciado **não impõe** um workflow nem uma divisão em fases, a divisão
em quatro meta-planos abaixo é uma **decomposição recomendada** (orientação), e
não um requisito oficial. O agente executor pode ajustá-la desde que entregue
tudo o que o enunciado exige.

## Decomposição recomendada

| Meta-plano | Foco | Garantias cobertas |
| --- | --- | --- |
| [`execution_plan_phase#01.md`](execution_plan_phase%2301.md) | Fundação: projeto `uv`, estrutura, carregamento dos dados, armazenamento persistente, `.env.example`, comandos de subida e restauração | Base das Garantias 3 e 5 |
| [`execution_plan_phase#02.md`](execution_plan_phase%2302.md) | Agentes ADK (principal + especialistas), tools de reservas/visitantes/regulamento, `state` da sessão com o apartamento | Garantias 2 e 4 (base) |
| [`execution_plan_phase#03.md`](execution_plan_phase%2303.md) | API FastAPI, `Runner`/`App`, contrato de rotas, confirmação de ações, persistência de sessão | Garantias 1 e 3 |
| [`execution_plan_phase#04.md`](execution_plan_phase%2304.md) | Garantias finais: concorrência/idempotência, regulamento sob demanda, reforço anti-injeção, validação do fluxo do avaliador, README final | Garantias 4, 5 e revisão de 1–3 |

## Rastreabilidade

Durante a execução futura, o agente deve manter atualizados, na raiz do
repositório:

- [`history.md`](../../../history.md) — histórico global de execução.
- [`delivery.md`](../../../delivery.md) — rastreabilidade requisito → artefato →
  implementação → teste → evidência → status.

## Precedência de informações (em caso de conflito)

1. Enunciado oficial do desafio (`docs/README.md` / `README.md`).
2. Seção "Dicas finais" e Critérios de aceite do enunciado.
3. Documentação oficial do Google ADK.
4. Código já existente no repositório.
5. Estes meta-planos.
6. Convenções genéricas.
7. Suposições do agente (evitar; preferir investigar).
