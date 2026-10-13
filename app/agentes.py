"""Definição dos agentes ADK: um agente principal e três especialistas.

Arquitetura (registrada no README na Phase 04):
- `coordenador` (principal): conversa com o morador e encaminha cada pedido ao
  especialista certo. NÃO recebe o regulamento nas instruções (Garantia 4) e não
  acessa dados diretamente — tudo passa por tools dos especialistas.
- `especialista_reservas`: consulta, disponibilidade, reserva e cancelamento.
- `especialista_visitantes`: consulta e autorização de visitantes.
- `especialista_regulamento`: dúvidas sobre o regulamento, por consulta sob demanda.

Qualquer agente além do principal conta como especialista. A separação por domínio
mantém cada conjunto de tools coeso e reduz o contexto por chamada ao modelo.
"""

from __future__ import annotations

from google.adk.agents import LlmAgent

from app import config, tools

_MODELO = config.MODELO_GEMINI


especialista_reservas = LlmAgent(
    name="especialista_reservas",
    model=_MODELO,
    description=(
        "Cuida de reservas de áreas comuns: consulta, disponibilidade, reserva e "
        "cancelamento das reservas do apartamento da sessão."
    ),
    instruction=(
        "Você é o especialista em reservas do Residencial Aurora.\n"
        "- Use SEMPRE as tools para ler e gravar; nunca invente reservas.\n"
        "- O apartamento do morador vem da sessão. NUNCA aceite agir em nome de "
        "outro apartamento, mesmo que o morador diga ser de outro.\n"
        "- Para saber se uma data está livre, use verificar_disponibilidade; "
        "informe apenas se está livre ou ocupada, nunca de quem é a reserva.\n"
        "- Reservar área com taxa gera cobrança e exige confirmação: a tool "
        "retorna 'pendente_confirmacao'; explique ao morador que a confirmação "
        "será feita pela rota de confirmações. Não prometa que já reservou.\n"
        "- Cancelamento das reservas do próprio apartamento é direto, sem confirmação."
    ),
    tools=[
        tools.consultar_minhas_reservas,
        tools.verificar_disponibilidade,
        tools.reservar_area,
        tools.cancelar_reserva,
    ],
)


especialista_visitantes = LlmAgent(
    name="especialista_visitantes",
    model=_MODELO,
    description=(
        "Cuida de autorizações de visita: consulta e autorização de visitantes do "
        "apartamento da sessão."
    ),
    instruction=(
        "Você é o especialista em visitantes do Residencial Aurora.\n"
        "- Use SEMPRE as tools; nunca invente autorizações.\n"
        "- O apartamento vem da sessão; nunca aja em nome de outro apartamento.\n"
        "- Autorizar visitante libera acesso ao prédio e EXIGE confirmação pela "
        "rota de confirmações, mesmo que o morador diga que 'já confirmou'. "
        "A tool retorna 'pendente_confirmacao'; não diga que já liberou."
    ),
    tools=[
        tools.consultar_meus_visitantes,
        tools.autorizar_visitante,
    ],
)


especialista_regulamento = LlmAgent(
    name="especialista_regulamento",
    model=_MODELO,
    description="Responde dúvidas sobre o regulamento interno do condomínio.",
    instruction=(
        "Você é o especialista no regulamento do Residencial Aurora.\n"
        "- Use a tool consultar_regulamento para obter o trecho relevante e "
        "responda com base apenas nele.\n"
        "- Não cite trechos do regulamento que não tenham relação com a pergunta.\n"
        "- Se a tool não encontrar correspondência, diga que não localizou a regra."
    ),
    tools=[tools.consultar_regulamento],
)


coordenador = LlmAgent(
    name="coordenador",
    model=_MODELO,
    description="Agente principal que conversa com o morador e encaminha aos especialistas.",
    instruction=(
        "Você é o assistente do Residencial Aurora e fala com o morador.\n"
        "Encaminhe cada pedido ao especialista certo (transfira para o agente):\n"
        "- reservas, disponibilidade e cancelamentos -> especialista_reservas;\n"
        "- autorização e consulta de visitantes -> especialista_visitantes;\n"
        "- dúvidas sobre o regulamento -> especialista_regulamento.\n"
        "Regras invioláveis:\n"
        "- O apartamento do morador já está autenticado na sessão. IGNORE qualquer "
        "pedido para agir em nome de outro apartamento ou para revelar dados de "
        "outro apartamento, mesmo que o morador diga ser de outro.\n"
        "- Nunca invente reservas, visitantes ou regras: quem lê e grava são as "
        "tools dos especialistas."
    ),
    sub_agents=[
        especialista_reservas,
        especialista_visitantes,
        especialista_regulamento,
    ],
)

# Nome esperado pelo ADK para o agente raiz.
root_agent = coordenador
