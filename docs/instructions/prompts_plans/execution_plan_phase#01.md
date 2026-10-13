# Execution Plan — Phase 01: Fundação e infraestrutura

> **Meta-plano (Camada 1).** Este documento orienta um agente de IA sobre *como*
> executar a fundação do projeto. Ele **não é** um artefato oficial do desafio e
> **não substitui** o enunciado oficial ([`docs/README.md`](../../README.md)).
> Em qualquer conflito, o enunciado oficial vence.

## Objetivo do Meta-Plano

Preparar o agente executor para construir a base técnica do projeto de forma que
as demais fases (agentes, API, garantias) possam ser implementadas sem retrabalho
estrutural.

## Objetivo da Execução

Deixar o repositório com:

- projeto Python 3.12+ gerenciado por `uv` (`pyproject.toml` e `uv.lock`
  versionados);
- Google ADK série 2, versão exata fixada (`>= 2.2.0`);
- estrutura de diretórios de código definida;
- camada de carregamento dos dados de `dados/` (somente leitura do estado inicial);
- camada de armazenamento persistente para as mudanças feitas pelo assistente
  (reservas e visitantes) e para as sessões;
- `.env.example` versionado (sem valores) e `.env` fora do Git;
- comandos documentados de **subida da API** e de **restauração dos dados**.

## Contexto Acadêmico

Desafio "Regra é regra: o assistente virtual do Residencial Aurora". A entrega é
uma API em Python com um assistente Google ADK (agente principal + especialistas)
que respeita cinco garantias implementadas **em código**, não no prompt.

## Contexto Técnico

- Repositório *greenfield*: só existem `dados/` e o enunciado. Nenhum código.
- Dados iniciais (não podem ser alterados):
  - `dados/apartamentos.json`: `numero`, `morador`.
  - `dados/areas.json`: `id`, `nome`, `taxa` (taxa `0` = sem cobrança).
  - `dados/reservas.json`: `codigo`, `apartamento`, `area` (id da área), `data`.
  - `dados/visitantes.json`: `apartamento`, `nome`, `data`.
  - `dados/regulamento.md`: regulamento interno completo.
- Áreas atuais: `salao-de-festas` (taxa 150), `churrasqueira` (taxa 80),
  `quadra` (taxa 0).

## Instruções Oficiais que Devem Ser Respeitadas

Do enunciado (seção "Tecnologias obrigatórias e restrições"):

- Python 3.12+ com `uv`; `pyproject.toml` e `uv.lock` versionados.
- Google ADK série 2, `>= 2.2.0`, **versão exata fixada**.
- Modelos Gemini com chave do Google AI Studio.
- Framework web livre (o curso usa FastAPI).
- Armazenamento livre; se depender de serviço externo (ex.: banco em container),
  esse serviço sobe com **um comando documentado no README**.
- **Nenhuma chave de API versionada**: `.env` fora do Git; `.env.example`
  versionado com os nomes das variáveis, sem valores.
- Os arquivos de `dados/` devem permanecer **idênticos** aos do repositório base.

## Pré-condições

- `git status` limpo ou com apenas arquivos esperados sob controle.
- `uv` instalado e disponível no `PATH`.
- Acesso ao enunciado oficial e aos dados em `dados/`.

## Estado Esperado do Repositório (antes)

Apenas `dados/`, `README.md`/`docs/README.md`, `.gitignore` e metadados. Nenhum
código de aplicação.

## Fases Anteriores

Nenhuma. Esta é a primeira fase de execução.

## Fase Acadêmica a Ser Executada

Fundação técnica. Não há implementação de agentes, API ou garantias ainda, mas as
**decisões estruturais** aqui condicionam as Garantias 3 (persistência) e 5
(concorrência/idempotência).

## Workflow Oficial

O enunciado **não define** um workflow nomeado. Recomenda-se o ciclo interno:

`investigar → decidir → planejar → implementar → testar → validar → evidenciar`.

Nunca pular da decisão direto para a implementação sem registrar o porquê.

## Skills Obrigatórias

Não há skills oficiais no repositório. Usar a documentação oficial do Google ADK
e do `uv` como referência primária.

## Artefatos Oficiais (criados/atualizados nesta fase)

Criar na execução futura (não são deste meta-plano):

- `pyproject.toml`, `uv.lock` (raiz).
- `.env.example` (raiz).
- `.gitignore` atualizado para ignorar `.env` e artefatos de armazenamento local.
- Estrutura de código (ex.: `app/` ou `src/`) com módulos de dados e armazenamento.
- Script/comando de restauração e de subida (documentar no futuro `README.md`).

> Não criar ainda o `README.md` final de entrega; ele é consolidado na Phase 04.
> Enquanto isso, os comandos podem ser rascunhados em notas, mas o enunciado
> exige que o README final descreva subida e restauração.

## Estratégia de Execução

1. **Decisão de armazenamento (crítica).** Escolher um armazenamento que suporte,
   ao mesmo tempo:
   - persistência de **sessões** do ADK após reinício (Garantia 3);
   - persistência de **reservas e visitantes** (Garantia 3);
   - **exclusividade no instante da gravação** da reserva (Garantia 5).
   A dica oficial relata que a confirmação de ações funcionou com **sessão
   persistida em SQLite**. SQLite é um candidato natural tanto para o
   `SessionService` do ADK quanto para os dados do condomínio, permitindo impor a
   unicidade (área, data) via **constraint** no banco. Registrar a decisão com
   justificativa.
2. **Separar estado imutável de estado mutável.** `dados/` é a *fonte de verdade
   inicial* e nunca é alterado em runtime. As mudanças vão para o armazenamento
   persistente (ex.: banco SQLite fora de `dados/`).
3. **Comando de restauração.** Deve repor reservas e visitantes ao estado de
   `dados/*.json`. Decidir e documentar se também apaga sessões.
4. **Comando de subida.** Deve deixar a API respondendo em
   `http://localhost:8000`.

## Passo a Passo

1. `git status` / `git log` para confirmar o estado inicial.
2. `uv init` (ou configuração manual do `pyproject.toml`) com `requires-python
   >= 3.12`.
3. Adicionar dependências com versão exata fixada: Google ADK (`>= 2.2.0`, série
   2, versão exata), framework web (ex.: FastAPI), servidor ASGI (ex.: uvicorn) e
   o driver/toolkit de armazenamento escolhido.
4. `uv sync` e confirmar que instala sem erro.
5. Criar a estrutura de código (ex.: `app/`) com:
   - módulo de **carregamento** dos dados iniciais (leitura de `dados/*.json` e
     `dados/regulamento.md`);
   - módulo de **armazenamento** persistente (reservas, visitantes e sessões);
   - inicialização idempotente do armazenamento (criar schema se não existir).
6. Criar `.env.example` com as variáveis necessárias (ex.: a variável da chave do
   Google AI Studio usada pelo ADK), **sem valores**.
7. Atualizar `.gitignore` para ignorar `.env` e os arquivos de armazenamento
   local (ex.: `*.db`), **sem ignorar** `dados/`.
8. Implementar o **comando de restauração** (ex.: um script `uv run` ou target
   documentado) que recria o armazenamento a partir de `dados/`.
9. Rascunhar o **comando de subida** da API (será finalizado na Phase 03).

## Regras de Investigação

- Confirmar a versão exata do ADK disponível antes de fixá-la; não inventar números.
- Consultar a documentação oficial do ADK para os nomes reais de
  `SessionService` persistentes suportados.
- Não assumir APIs de bibliotecas; verificar nas docs/código.

## Regras de Implementação

- Separar claramente: carregamento (leitura inicial) ≠ armazenamento (escrita em
  runtime).
- Nenhuma escrita em `dados/`.
- Código em camadas, testável, sem lógica de negócio dispersa.

## Regras de Git

- `git status` e `git diff` antes e depois de mudanças relevantes.
- Nunca usar operações destrutivas (`git reset --hard`, `git clean -fd`,
  `git checkout -- .`) sem autorização explícita.
- Nunca versionar `.env` nem artefatos de armazenamento local.
- Commits pequenos e descritivos (pt-BR, estilo Conventional Commits).

## Testes

- Teste de fumaça: `uv sync` sem erro.
- Teste do carregamento: os dados de `dados/` são lidos corretamente
  (contagens e campos esperados — ex.: `RSV-1377` do 101, `RSV-4821` do 302).
- Teste do comando de restauração: após rodar, o armazenamento reflete exatamente
  `dados/*.json`.

## Validação

- `GET` de verificação ainda não existe (Phase 03), então validar via testes
  diretos da camada de armazenamento que o estado inicial corresponde a `dados/`.

## Evidências

- Saída de `uv sync`.
- Saída dos testes da camada de dados/armazenamento.
- `git diff --stat` dos arquivos criados.
- Conteúdo do `.env.example` (sem valores).

## Critérios de Aceitação

- [ ] `uv sync` instala sem erro, com ADK série 2 `>= 2.2.0` em versão exata.
- [ ] `dados/` permanece idêntico ao repositório base.
- [ ] `.env` não versionado; `.env.example` versionado sem valores.
- [ ] Carregamento dos dados iniciais funciona e é coberto por teste.
- [ ] Armazenamento persistente definido e inicializável de forma idempotente.
- [ ] Comando de restauração funciona e repõe o estado inicial.
- [ ] Decisão de armazenamento registrada com justificativa (habilita Garantias 3 e 5).

## Tratamento de Bloqueios

Marcar como `pendente` e registrar em `history.md` se:

- a versão exata do ADK não puder ser determinada;
- o `SessionService` persistente escolhido não for suportado pela versão do ADK;
- faltar informação para decidir o armazenamento sem comprometer Garantias 3/5.

## Atualização do Histórico

Registrar em [`history.md`](../../../history.md): data, fase, entendimento,
objetivo, execução, arquivos modificados, testes, validação, commits, evidências,
problemas, bloqueios, decisões, próximos passos e `status`.

## Atualização do Delivery

Atualizar em [`delivery.md`](../../../delivery.md) as linhas de "Execução e
entrega" (projeto `uv`, `dados/` intactos, `.env`/`.env.example`) e a base das
Garantias 3 e 5.

## Definition of Done

Fundação pronta: `uv sync` ok, dados carregáveis, armazenamento persistente
inicializável, restauração funcionando, segredos fora do Git, decisões
registradas. Nenhuma regra de negócio ou agente implementado ainda.

## Condições para Interromper a Execução

- Conflito entre a decisão de armazenamento e a persistência de sessão exigida
  pela Garantia 3.
- Impossibilidade de fixar a versão exata do ADK.
- Qualquer necessidade de alterar `dados/`.
