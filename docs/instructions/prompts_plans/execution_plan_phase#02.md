# Execution Plan — Phase 02: Agentes ADK e tools

> **Meta-plano (Camada 1).** Orienta *como* construir a arquitetura de agentes e
> as tools. **Não é** artefato oficial e **não substitui** o enunciado oficial
> ([`docs/README.md`](../../README.md)). Em conflito, o enunciado vence.

## Objetivo do Meta-Plano

Orientar a construção do assistente ADK (agente principal + especialistas) e das
tools que leem e gravam reservas, visitantes e consultam o regulamento, de modo
que as regras críticas fiquem **no código** e o apartamento venha **da sessão**.

## Objetivo da Execução

- Agente principal que distribui o trabalho a **no mínimo dois especialistas**.
- Tools que leem e gravam reservas e visitantes acessando o armazenamento da
  Phase 01 — nunca algo que o modelo "lembra" ou inventa.
- `state` da sessão guardando o **apartamento autenticado**, usado pelas tools.
- Base das Garantias 2 (sessão pertence a um apartamento) e 4 (regulamento sob
  demanda).

## Contexto Acadêmico

Requisito 1 do enunciado: "Um assistente, vários especialistas". Conta como
especialista qualquer agente além do principal, seja qual for a forma de
acioná-lo. A quantidade, o papel e a forma de acionamento de cada um são decisões
do executor, **registradas no README com o motivo**.

## Contexto Técnico

- Depende da Phase 01 (armazenamento e carregamento prontos).
- Modelos Gemini (chave do Google AI Studio). O modelo de cada agente é escolha
  do executor; consultar modelos e limites atuais no Google AI Studio.
- Ordem de grandeza: o fluxo do avaliador faz dezenas de chamadas ao modelo.

## Instruções Oficiais que Devem Ser Respeitadas

- **Requisito 1:** agente principal + ≥ 2 especialistas; reservas e visitantes
  lidos/gravados por **tools**.
- **Garantia 2:** o apartamento é definido uma única vez na criação da sessão e
  **vem da sessão**, nunca de um valor que o modelo escolhe sem validação.
  Nenhuma tool pode aceitar um apartamento escolhido pelo modelo sem validar
  contra o da sessão. Nada do que o morador escreve pode alterar/trazer dados de
  outro apartamento. Checar se uma data está livre pode olhar a agenda da área,
  mas só pode chegar à conversa "livre/ocupada", nunca de quem é a reserva.
- **Garantia 4:** o agente principal **não recebe o regulamento nas instruções**;
  o regulamento é consultado sob demanda e nenhum evento pode conter trechos de
  capítulos que tratam de outros assuntos.

## Pré-condições

- Phase 01 concluída: `uv sync` ok, armazenamento e carregamento funcionando.
- Chave do Google AI Studio disponível em `.env` local (não versionada).

## Estado Esperado do Repositório (antes)

Fundação pronta, sem agentes nem tools. Sem API ainda (Phase 03).

## Fases Anteriores

Phase 01 (fundação) concluída.

## Fase Acadêmica a Ser Executada

Arquitetura multiagente e tools. Garantias 2 e 4 **começam** aqui; a validação
completa por API ocorre na Phase 03/04.

## Workflow Oficial

Não há workflow nomeado no enunciado. Seguir o ciclo:
`investigar → decidir → planejar → implementar → testar → validar → evidenciar`.

## Skills Obrigatórias

Documentação oficial do Google ADK (agentes, subagents, tools, boas práticas de
tools, modos de execução, confirmação de tools, `state` da sessão).

## Artefatos Oficiais (criados/atualizados nesta fase)

Na execução futura (código):

- Definição do **agente principal** (sem regulamento nas instruções).
- Definição dos **especialistas** (ex.: reservas, visitantes, regulamento).
- **Tools** de reservas (consultar, reservar, cancelar), visitantes (autorizar,
  listar) e regulamento (consulta sob demanda).
- Leitura do apartamento a partir do `state` da sessão (helper único reutilizado
  por todas as tools).

> As decisões de quantos especialistas, papéis e acionamento devem ser anotadas
> para consolidação na seção **Arquitetura** do README (Phase 04).

## Estratégia de Execução

1. **Apartamento vem da sessão.** Criar um ponto único que lê o apartamento do
   `state` da sessão. Nenhuma tool deve receber `apartamento` como argumento
   livre do modelo; se receber por necessidade de assinatura, deve **ignorar** o
   valor do modelo e usar o da sessão (ou validar estritamente contra ele).
2. **Especialistas por domínio.** Sugestão (não obrigatória): um especialista de
   **reservas** (consultar disponibilidade, reservar, cancelar), um de
   **visitantes** (autorizar/listar) e um de **regulamento** (consulta sob
   demanda). O agente principal roteia. Mínimo exigido: dois especialistas.
3. **Tools acessam o armazenamento, não a memória do modelo.** Toda leitura e
   escrita de reservas/visitantes passa pelas tools da Phase 01.
4. **Disponibilidade sem vazamento (Garantia 2).** A tool de disponibilidade
   retorna apenas "livre"/"ocupada" para (área, data); nunca `codigo`,
   `apartamento` ou nome de terceiros.
5. **Regulamento sob demanda (Garantia 4).** A tool de regulamento recebe a
   dúvida, localiza o trecho relevante e devolve só a resposta necessária — não o
   capítulo inteiro, não trechos de outros assuntos. O agente principal **não**
   carrega o regulamento nas instruções.
6. **Confirmação (preparação para Garantia 1).** Marcar, já no design das tools,
   quais ações geram cobrança (reservar área com taxa > 0) ou liberam acesso
   (autorizar visitante). Essas tools serão as que exigem confirmação na Phase 03.

## Passo a Passo

1. Investigar na doc do ADK: como definir agente principal e subagents, como
   declarar tools, como ler o `state` da sessão dentro de uma tool, e o mecanismo
   de **confirmação de tools**.
2. Implementar o helper de leitura do apartamento a partir da sessão.
3. Implementar as tools de reservas (consultar disponibilidade, reservar,
   cancelar) usando o apartamento da sessão.
4. Implementar as tools de visitantes (autorizar, listar) usando o apartamento
   da sessão.
5. Implementar a tool de consulta ao regulamento (sob demanda).
6. Definir o agente principal (instruções **sem** regulamento) e os especialistas.
7. Configurar o roteamento/transferência entre agentes conforme a doc do ADK.
8. Escrever testes de unidade das tools (sem depender do modelo).

## Regras de Investigação

- Verificar na doc oficial os nomes reais de classes/parâmetros do ADK (agentes,
  tools, `state`, confirmação). Não inventar APIs.
- Confirmar como a confirmação de tools expõe os "detalhes" da ação (necessário
  para `confirmacoes_pendentes` na Phase 03).

## Regras de Implementação

- As regras críticas ficam no código das tools, não no texto do prompt.
- Nenhuma tool confia no apartamento dito pelo morador.
- A tool de disponibilidade nunca expõe identidade de reservas de terceiros.
- O agente principal nunca recebe o regulamento nas instruções.

## Regras de Git

- `git status`/`git diff` antes e depois.
- Sem operações destrutivas sem autorização.
- Commits pequenos (pt-BR, Conventional Commits).

## Testes

- Unidade por tool:
  - reservar/cancelar/consultar usam o apartamento da **sessão**, ignorando
    valores injetados;
  - cancelamento só afeta reservas do próprio apartamento;
  - disponibilidade retorna apenas livre/ocupada, sem dados de terceiros;
  - regulamento retorna a resposta sem trechos de outros assuntos.
- Teste anti-injeção na camada de tool: pedir dados do 302 numa sessão do 101
  não retorna `RSV-4821` nem `Marina Duarte`.

## Validação

- Opcional durante o desenvolvimento: usar `adk web` para observar transferências
  e chamadas de tool. A validação definitiva contra o contrato é feita via API na
  Phase 03/04.

## Evidências

- Saída dos testes de unidade das tools.
- Exemplo de chamada de tool mostrando que o apartamento usado é o da sessão.
- Demonstração de que a disponibilidade não vaza identidade.

## Critérios de Aceitação

- [ ] Existe um agente principal e **pelo menos dois** especialistas.
- [ ] Reservas e visitantes são lidos/gravados **por tools** sobre o armazenamento.
- [ ] O apartamento usado pelas tools vem da **sessão**; nenhuma tool aceita
      apartamento do modelo sem validar.
- [ ] Disponibilidade retorna só livre/ocupada, sem identidade de terceiros.
- [ ] O agente principal **não** recebe o regulamento nas instruções.
- [ ] Decisões de arquitetura anotadas para o README (Phase 04).

## Tratamento de Bloqueios

Marcar `pendente` se:

- a doc do ADK não deixar claro como ler o `state` da sessão dentro de uma tool;
- não for possível garantir, na assinatura das tools, que o apartamento venha da
  sessão;
- o mecanismo de confirmação de tools não expuser os detalhes necessários.

## Atualização do Histórico

Registrar em [`history.md`](../../../history.md) a execução, decisões de
arquitetura (quantos especialistas, papéis, acionamento) e resultados de teste.

## Atualização do Delivery

Atualizar em [`delivery.md`](../../../delivery.md) as linhas de "Arquitetura" e a
base das Garantias 2 e 4.

## Definition of Done

Agentes e tools implementados e testados em unidade; apartamento sempre vindo da
sessão; disponibilidade sem vazamento; regulamento fora das instruções do agente
principal; decisões registradas. Sem API ainda.

## Condições para Interromper a Execução

- Impossibilidade de impedir, no código, o uso de apartamento ditado pelo modelo.
- Mecanismo de confirmação do ADK incompatível com o contrato da API.
- Necessidade de carregar o regulamento inteiro nas instruções (violaria Garantia 4).
