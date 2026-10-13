# Execution Plan — Phase 04: Garantias finais, validação e README

> **Meta-plano (Camada 1).** Orienta *como* fechar as garantias transversais,
> validar o fluxo completo do avaliador e produzir o README de entrega. **Não é**
> artefato oficial e **não substitui** o enunciado
> ([`docs/README.md`](../../README.md)). Em conflito, o enunciado vence.

## Objetivo do Meta-Plano

Orientar o agente a finalizar a Garantia 5 (concorrência/idempotência), fechar a
Garantia 4 (regulamento sob demanda), reforçar a Garantia 2 (anti-injeção),
validar os 15 passos do fluxo do avaliador e escrever o `README.md` de entrega.

## Objetivo da Execução

- Exclusividade de reserva (área, data) garantida **no instante da gravação**.
- Nenhum evento da sessão contém trechos do regulamento de outros assuntos.
- Reforço de que nada do que o morador escreve altera/vaza dados de outro
  apartamento.
- Fluxo do avaliador (passos 1–15) validado de ponta a ponta.
- `README.md` na raiz com as seções **Arquitetura**, **Garantias** e **Como
  rodar**, substituindo o enunciado.

## Contexto Acadêmico

Garantias 4 e 5 e revisão final das Garantias 1–3. Entregável: fork público na
`main`, com `README.md` na raiz substituindo o enunciado.

## Contexto Técnico

- Depende das Phases 01–03.
- A unicidade (área, data) deve ser imposta no armazenamento (ex.: **constraint**
  no SQLite), não apenas por conferência prévia.

## Instruções Oficiais que Devem Ser Respeitadas

- **Garantia 5:** dois moradores podem pedir a mesma área/data e aprovar ao mesmo
  tempo; uma vence, a outra é recusada **com resposta normal, sem erro de
  servidor**. Nunca podem existir duas reservas ativas para a mesma área na mesma
  data. A exclusividade vale **no instante da gravação**, não só numa conferência
  prévia.
- **Garantia 4:** o assistente responde dúvidas com base em
  `dados/regulamento.md`, mas **nenhum evento** da sessão pode conter trechos de
  capítulos que tratam de outros assuntos; o agente principal **não** recebe o
  regulamento nas instruções.
- **Garantia 2:** nada que o morador escreva faz o assistente alterar/trazer
  dados de outro apartamento (ex.: pedir dados do 302 numa sessão do 101 não traz
  `RSV-4821` nem `Marina Duarte`; reservar data já ocupada pelo 302 não vaza
  `RSV-4821` nem o número `302` isolado).
- **Regra de negócio 5:** o código da reserva é gerado pelo sistema e **nunca
  repete** nenhum código anterior, inclusive de reserva cancelada.
- **Entregável/README:** três seções obrigatórias — Arquitetura (cada agente, sua
  responsabilidade, como é acionado e por quê), Garantias (para cada uma das
  cinco, o arquivo e o trecho que a implementam e por que não depende do modelo),
  Como rodar (pré-requisitos, variáveis do `.env`, comando de subida e comando de
  restauração). A seção Garantias deve apontar **arquivos e trechos que existem**.

## Pré-condições

- Phases 01–03 concluídas; API no contrato; confirmação e persistência funcionando.

## Estado Esperado do Repositório (antes)

Assistente, tools e API completos, faltando: unicidade na gravação, validação
completa e README de entrega.

## Fases Anteriores

Phases 01, 02 e 03 concluídas.

## Fase Acadêmica a Ser Executada

Garantias 4 e 5, revisão final e entrega (README).

## Workflow Oficial

Sem workflow nomeado. Ciclo:
`investigar → decidir → planejar → implementar → testar → validar → evidenciar`.

## Skills Obrigatórias

Doc oficial do ADK (contexto/tokens com subagents) e documentação do armazenamento
escolhido sobre **idempotência/concorrência** (ex.: constraints e tratamento de
violação de unicidade no SQLite).

## Artefatos Oficiais (criados/atualizados nesta fase)

Na execução futura:

- Imposição de unicidade (área, data) no armazenamento + tratamento da violação
  como recusa normal (sem `500`).
- Geração de código de reserva única e nunca repetida.
- Ajustes finais na tool de regulamento para não vazar trechos de outros assuntos.
- `README.md` na raiz (Arquitetura, Garantias, Como rodar).

## Estratégia de Execução

1. **Garantia 5 — unicidade na gravação.** Impor uma **constraint de unicidade**
   para reservas ativas por (área, data) no armazenamento. Na gravação, capturar a
   violação e devolver recusa normal (sem erro de servidor). Isso resolve a
   corrida entre conferência e gravação. Idempotência da confirmação (Phase 03)
   impede dupla execução na mesma sessão; a constraint impede duplicidade entre
   sessões concorrentes.
2. **Código de reserva único.** Gerar código em formato livre que **nunca** repete
   códigos existentes nem de reservas canceladas (ex.: manter todos os códigos já
   usados e nunca reciclar; ou usar sequência/UUID verificado).
3. **Garantia 4 — regulamento sob demanda.** Garantir que a tool de regulamento
   devolve só o trecho pertinente, e que nenhum evento registre capítulos de
   outros assuntos. Conferir em `GET /eventos` após uma pergunta de regulamento.
4. **Garantia 2 — reforço.** Reconfirmar que pedidos cruzados de apartamento não
   vazam dados nem código de terceiros nos eventos.
5. **Validação completa.** Executar os 15 passos do fluxo do avaliador, incluindo
   a disputa concorrente do passo 14 (duas aprovações ao mesmo tempo).
6. **README de entrega.** Escrever `README.md` na raiz com as três seções,
   apontando arquivos e trechos reais.

## Passo a Passo

1. Implementar a constraint de unicidade e o tratamento de violação como recusa.
2. Implementar/validar a geração de código único e não repetido.
3. Ajustar a tool de regulamento para resposta mínima e sem vazamento.
4. Reexecutar os testes de anti-injeção (Garantia 2).
5. Executar o **fluxo do avaliador completo (passos 1–15)** via HTTP.
6. Executar a **disputa concorrente** (passo 14): duas sessões aprovando a mesma
   área/data ao mesmo tempo; conferir exatamente uma reserva e dois `200`.
7. Escrever `README.md` (Arquitetura, Garantias com arquivo+trecho reais, Como
   rodar com `.env`, subida e restauração).
8. Revisar os critérios de aceite do enunciado, um a um.

## Regras de Investigação

- Pesquisar como o armazenamento escolhido garante atomicidade/unicidade sob
  concorrência (aula de idempotência do módulo, conforme o enunciado).
- Confirmar que a violação de unicidade é capturável e traduzível em recusa normal.

## Regras de Implementação

- A exclusividade vale **no instante da gravação** (constraint), não só em
  conferência prévia.
- Violação de unicidade → resposta normal, nunca `500`.
- Código de reserva nunca reciclado.
- README aponta somente arquivos e trechos que **existem**.

## Regras de Git

- `git status`/`git diff` antes e depois; sem operações destrutivas sem
  autorização; commits pequenos (pt-BR, Conventional Commits).
- Entrega na branch `main`.

## Testes

- Concorrência: duas gravações simultâneas de (área, data) → só uma vence, a outra
  é recusada sem `500`; nunca duas reservas ativas para a mesma (área, data).
- Código de reserva: os códigos criados no fluxo são distintos entre si e de
  `RSV-1377`, `RSV-4821`, `RSV-2950`.
- Regulamento: `GET /eventos` após pergunta sobre a piscina aos domingos traz o
  horário de fechamento, e nenhum evento contém trechos de outros assuntos.
- Anti-injeção: passos 3, 4 e 10 do fluxo do avaliador.

## Validação

- Executar os **15 passos** do fluxo do avaliador e conferir cada critério de
  aceite do enunciado.
- Validar com ambiente limpo (clone, `.env` a partir de `.env.example`,
  `uv sync`, restauração, subida).

## Evidências

- Saída do fluxo do avaliador (passos 1–15), incluindo a disputa concorrente.
- `GET` de verificação mostrando exatamente uma reserva do salão em 2030-05-11
  somando os dois apartamentos (passo 14).
- `GET /eventos` evidenciando ausência de trechos de outros assuntos do regulamento.
- Trechos do `README.md` com os ponteiros de código das cinco garantias.

## Critérios de Aceitação

- [ ] Duas aprovações simultâneas para a mesma área/data respondem `200` e somam
      exatamente uma reserva (passo 14).
- [ ] A exclusividade vale no instante da gravação (constraint), não só em
      conferência prévia (passo 15).
- [ ] Códigos de reserva nunca repetem nenhum anterior (passo 13).
- [ ] Resposta sobre a piscina aos domingos traz o horário de fechamento (passo 12).
- [ ] Nenhum evento contém trechos de capítulos do regulamento de outros assuntos
      (passo 12).
- [ ] Pedidos cruzados de apartamento não vazam dados nem código de terceiros
      (passos 3, 4, 10).
- [ ] `README.md` na raiz com Arquitetura, Garantias (arquivo+trecho reais) e Como
      rodar; substitui o enunciado.
- [ ] Todos os critérios de aceite do enunciado revisados e satisfeitos.

## Tratamento de Bloqueios

Marcar `pendente` se:

- o armazenamento não garantir unicidade atômica na gravação;
- a violação de unicidade não puder virar recusa normal (ficar como `500`);
- algum evento inevitavelmente registrar trechos do regulamento de outros assuntos;
- algum passo do fluxo do avaliador falhar sem solução segura.

## Atualização do Histórico

Registrar em [`history.md`](../../../history.md) a execução das Garantias 4 e 5, o
resultado da disputa concorrente e a validação dos 15 passos.

## Atualização do Delivery

Fechar em [`delivery.md`](../../../delivery.md) todas as linhas das cinco
garantias, do contrato e do README, com evidências e `status`.

## Definition of Done

Todas as cinco garantias de pé em todos os passos do fluxo do avaliador; código de
reserva único; README de entrega completo e apontando trechos reais; todos os
critérios de aceite satisfeitos; entrega na `main`.

## Condições para Interromper a Execução

- Qualquer critério de aceite do enunciado não satisfeito sem solução segura.
- Duplicidade de reserva possível sob concorrência.
- README apontando arquivos/trechos inexistentes.
