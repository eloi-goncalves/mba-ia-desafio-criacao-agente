# Execution Plan — Phase 03: API, Runner/App e confirmações

> **Meta-plano (Camada 1).** Orienta *como* expor o assistente por uma API que
> segue o contrato oficial e implementa a confirmação de ações e a persistência
> de sessão. **Não é** artefato oficial e **não substitui** o enunciado
> ([`docs/README.md`](../../README.md)). Em conflito, o enunciado vence.

## Objetivo do Meta-Plano

Orientar a construção da API que integra os agentes da Phase 02 ao `Runner`/`App`
do ADK, seguindo **exatamente** o contrato de rotas, e implementando a Garantia 1
(confirmação) e a Garantia 3 (persistência no reinício).

## Objetivo da Execução

- API respondendo em `http://localhost:8000` com o contrato exato.
- Fluxo de confirmação de ações que gera cobrança/acesso, com retomada correta.
- Persistência de sessões e dados que sobrevive ao reinício.

## Contexto Acadêmico

Requisito 7 ("A API") e Garantias 1 e 3. A correção é feita **pelo contrato**;
qualquer divergência de caminho, campo, formato ou código de status reprova os
passos correspondentes.

## Contexto Técnico

- Depende das Phases 01 (armazenamento/sessão persistente) e 02 (agentes/tools).
- Framework web livre (curso usa FastAPI). Padrão `async`.
- O `Runner`/`App` do ADK executa o assistente e gerencia a retomada após
  confirmação.

## Instruções Oficiais que Devem Ser Respeitadas

### Contrato da API (exato)

- `POST /sessoes` → body `{"apartamento": "101"}` → `201` `{"session_id": "..."}`.
- `POST /sessoes/{session_id}/mensagens` → body `{"texto": "..."}` → `200`
  `{"resposta": "...", "confirmacoes_pendentes": [...]}`.
  - `resposta` pode ser string vazia quando a execução parou esperando confirmação.
  - `confirmacoes_pendentes` lista **todas** as pendentes da sessão naquele
    momento; lista vazia quando não há nenhuma. Cada item: `id`, `acao`,
    `detalhes` (nomes internos de `detalhes` são livres, mas devem conter os dados
    da ação — ex.: área e data; nome e data).
- `POST /sessoes/{session_id}/confirmacoes` → body `{"id": "...", "confirmado":
  true|false}` → `200` (mesmo formato de `mensagens`) ou `409` quando não existe
  confirmação pendente com esse `id` nesta sessão.
- `GET /sessoes/{session_id}/eventos` → `200` lista com **todos** os eventos
  gravados na sessão, em ordem, com conteúdo completo.
- Rotas de verificação (leem os dados direto, sem passar pelo modelo):
  - `GET /apartamentos/{numero}/reservas` → `200` lista de
    `{"codigo", "area", "data"}`.
  - `GET /apartamentos/{numero}/visitantes` → `200` lista de `{"nome", "data"}`.
- Rotas com `{session_id}` respondem `404` quando a sessão não existe.
- Todas as rotas recebem e devolvem JSON; datas no formato `AAAA-MM-DD`.

### Garantia 1 (confirmação)

- Ação que gera cobrança (reservar área com taxa > 0) ou libera acesso (autorizar
  visitante) fica **pendente** até resposta pela rota de confirmações.
- Aprovar executa **uma única vez**; negar não muda nada.
- Ação sem cobrança e sem acesso (ex.: reservar área de taxa 0, cancelar reserva)
  **não** pede confirmação.
- A confirmação vem do **sistema**, não da conversa ("já confirmo aqui" não vale).
- A rota de confirmações só aceita um `id` **pendente naquela sessão**; qualquer
  outro `id`, inclusive de confirmação já respondida, recebe `409` e nada executa.

### Garantia 3 (persistência)

- Reiniciar a API não apaga conversas nem dados. Após reinício, a mesma sessão
  continua: eventos anteriores presentes e novas mensagens funcionam. Reservas e
  visitantes gravados antes continuam valendo.

### Dica oficial (armadilha silenciosa)

A retomada só funciona quando a resposta da confirmação chega ao **agente que
pediu a confirmação**, e quem escolhe esse agente é o `Runner`. Essa escolha muda
conforme a topologia dos agentes, bloqueios de transferência, a configuração de
retomada do `App` e o serviço de sessão. Testar a aprovação **com sessão
persistida e após reiniciar a API**, não só no `adk web`. A confirmação funcionou
com sessão persistida em **SQLite** quando a resposta chegou ao agente certo.

## Pré-condições

- Phases 01 e 02 concluídas.
- `SessionService` persistente definido (ex.: SQLite).

## Estado Esperado do Repositório (antes)

Agentes e tools prontos; armazenamento persistente pronto; sem camada HTTP.

## Fases Anteriores

Phases 01 e 02 concluídas.

## Fase Acadêmica a Ser Executada

Camada HTTP + `Runner`/`App` + confirmação + persistência. Garantias 1 e 3.

## Workflow Oficial

Sem workflow nomeado. Ciclo:
`investigar → decidir → planejar → implementar → testar → validar → evidenciar`.

## Skills Obrigatórias

Doc oficial do ADK: `Runner`/`App`, execução personalizada, padrão `async`,
confirmação de ações (como o cliente responde a uma confirmação pendente),
`SessionService` persistente. Doc do framework web escolhido.

## Artefatos Oficiais (criados/atualizados nesta fase)

Na execução futura (código):

- Aplicação web com as rotas do contrato.
- Integração com `Runner`/`App` do ADK.
- Camada que traduz eventos de confirmação do ADK para `confirmacoes_pendentes`
  e que injeta a resposta do morador de volta no `Runner`.
- Mapa de confirmações pendentes por sessão (para validar `id` e devolver `409`).
- Comando de subida documentado (rascunhado na Phase 01, finalizado aqui).

## Estratégia de Execução

1. **Criar sessão com apartamento no `state`.** `POST /sessoes` cria a sessão no
   `SessionService` persistente com o apartamento gravado no `state`
   (base da Garantia 2, consumida pelas tools da Phase 02).
2. **Enviar mensagem.** `POST /mensagens` roda o `Runner` de forma `async`,
   coleta a `resposta` final e todas as confirmações pendentes da sessão.
3. **Mapear confirmações.** Cada confirmação pendente recebe um `id` estável
   (preferir o id do evento/convite de confirmação do ADK) e expõe `acao` e
   `detalhes` com os dados da ação.
4. **Responder confirmação.** `POST /confirmacoes` valida que o `id` está
   **pendente nessa sessão**; se não estiver (inexistente ou já respondido),
   retorna `409` sem executar nada. Se estiver, injeta a resposta no `Runner`
   para o **agente que pediu** e retoma a execução (aprovar executa uma vez;
   negar não grava nada).
5. **Eventos.** `GET /eventos` devolve todos os eventos da sessão, em ordem,
   lendo do `SessionService` persistente. `404` se a sessão não existir.
6. **Rotas de verificação.** Leem reservas/visitantes direto do armazenamento,
   sem passar pelo modelo.
7. **Persistência (Garantia 3).** Usar `SessionService` persistente (ex.: SQLite)
   e armazenamento persistente de dados, de modo que reiniciar a API preserve
   eventos e dados.

## Passo a Passo

1. Investigar na doc/código do ADK **como um cliente responde a uma confirmação
   pendente** e como o `Runner` escolhe o agente de retomada; ajustar topologia e
   configuração de retomada do `App` conforme necessário.
2. Implementar `POST /sessoes` (cria sessão persistente com apartamento no `state`).
3. Implementar `POST /sessoes/{id}/mensagens` (executa o `Runner`, monta a
   resposta e `confirmacoes_pendentes`).
4. Implementar `POST /sessoes/{id}/confirmacoes` (valida `id`/sessão, `409` quando
   não pendente, retoma e executa uma única vez).
5. Implementar `GET /sessoes/{id}/eventos` (todos os eventos; `404` se não existe).
6. Implementar `GET /apartamentos/{numero}/reservas` e
   `GET /apartamentos/{numero}/visitantes`.
7. Finalizar e documentar o **comando de subida** (API em `localhost:8000`).
8. Testar o fluxo de confirmação **com sessão persistida** e **após reiniciar**.

## Regras de Investigação

- Confirmar o formato real dos eventos de confirmação do ADK antes de mapear
  `confirmacoes_pendentes`.
- Confirmar como re-entrar no `Runner` com a resposta da confirmação.
- Validar empiricamente a dica oficial (retomada com sessão persistida e reinício).

## Regras de Implementação

- Seguir o contrato **ao pé da letra** (caminhos, campos, formatos, status).
- `409` nunca executa a ação.
- Aprovação executa **exatamente uma vez** (idempotência do lado da confirmação;
  a unicidade de reserva vem na Phase 04/Garantia 5).
- Rotas de verificação nunca passam pelo modelo.
- Nenhuma ação de cobrança/acesso grava antes da aprovação.

## Regras de Git

- `git status`/`git diff` antes e depois; sem operações destrutivas sem
  autorização; commits pequenos (pt-BR, Conventional Commits).

## Testes

- Integração por rota, cobrindo os passos 2–13 do fluxo do avaliador:
  - criação de sessão (`201`);
  - reserva de área com taxa gera `confirmacoes_pendentes` com área e data, sem
    gravar antes da resposta; negar não grava; aprovar grava **uma** reserva;
  - reenvio do mesmo `id` já respondido → `409`, sem duplicar;
  - `id` inexistente → `409`, sem alterar;
  - reserva de área sem taxa (quadra) não gera confirmação;
  - autorizar visitante gera confirmação (mesmo com "já confirmo aqui") e só grava
    após aprovação;
  - `GET /eventos` em ordem e completo; `404` para sessão inexistente;
  - persistência: reiniciar a API preserva eventos e dados; nova mensagem aumenta
    a contagem de eventos.

## Validação

- Rodar o fluxo do avaliador (passos 1–13) via chamadas HTTP reais.
- Conferir efeitos pelas rotas de verificação e por `GET /eventos`.
- **Validar a confirmação após reinício da API com sessão persistida** (dica
  oficial).

## Evidências

- Logs/saída das chamadas HTTP de cada passo do fluxo.
- Demonstração do `409` em reenvio e em `id` inexistente.
- Contagem de eventos antes e depois do reinício.
- Saída dos testes de integração.

## Critérios de Aceitação

- [ ] Todas as rotas seguem o contrato (caminhos, campos, formatos, status).
- [ ] Reservar área com taxa gera confirmação com área e data; nada grava antes.
- [ ] Negar não grava; aprovar grava exatamente uma reserva.
- [ ] Reenvio de confirmação já respondida → `409`, sem reexecutar.
- [ ] `id` não pendente → `409`, sem alterar nada.
- [ ] Reservar área sem taxa não gera confirmação.
- [ ] Autorizar visitante gera confirmação mesmo com "já confirmo aqui"; só grava
      após aprovação.
- [ ] `GET /eventos` completo e em ordem; `404` para sessão inexistente.
- [ ] Após reiniciar, a sessão devolve os mesmos eventos e aceita novas mensagens;
      dados gravados antes continuam valendo.

## Tratamento de Bloqueios

Marcar `pendente` se:

- a resposta da confirmação não chegar ao agente que pediu (retomada silenciosa
  falha) e a causa não puder ser resolvida com ajuste de topologia/retomada;
- o `SessionService` persistente escolhido não suportar confirmação;
- o contrato não puder ser atendido exatamente com as APIs disponíveis.

## Atualização do Histórico

Registrar em [`history.md`](../../../history.md) a execução, a configuração que
fez a retomada funcionar (topologia, `App`, `SessionService`) e os resultados.

## Atualização do Delivery

Atualizar em [`delivery.md`](../../../delivery.md) as linhas de "Contrato", da
Garantia 1 e da Garantia 3.

## Definition of Done

API no contrato exato; confirmação funcionando com sessão persistida e após
reinício; persistência de eventos e dados comprovada; testes de integração
passando. Garantia 5 (concorrência) e Garantia 4 (regulamento) finalizadas na
Phase 04.

## Condições para Interromper a Execução

- Retomada da confirmação falha de forma não resolvível.
- Qualquer desvio inevitável do contrato oficial.
- Persistência de sessão não sobrevive ao reinício.
