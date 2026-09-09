# %%
from retrieval import ( #importar classe do arquivo retrieval.py
    busca, 
    model, 
    embeddings, 
    chunks
)

from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langchain.tools import (
    tool,
    BaseTool
)
from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
    BaseMessage,
    ToolMessage
)

from langchain_core.tools import BaseTool

from IPython.display import Markdown, display

#%%
def fazer_busca(query: str, k: int = 5) -> str:
    # utilizando classe criada no retrieval
    buscador = busca(
        model= model,
        vetor= embeddings,
        k= k,
        xq= query
    )

    indices = buscador.metrica(tipo= 1) #IndexFlatL2

    if indices is None or len(indices[0]) == 0:
        return 'Nenhuma informação encontrada'
     
    chunks_encontrados = [ # Recupera os chunks de texto originais a partir dos índices retornados pelo FAISS
        chunks[i]['text'] for i in indices[0] if i < len(chunks)
    ]
    
    return '\n\n---\n\n'.join(chunks_encontrados)

#%%
def traduzir_query_ingles(query: str) -> str:
    ''' Receber a query em pt e traduzir pra ingles'''

    #if isinstance(query, dict):
        #query = query.get('query', '')

    if isinstance(query, dict):
        query = list(query.values())[0]

    prompt = ChatPromptTemplate.from_template(
        'Você é um assistente especialista em busca vetorial. '
        'Traduza a seguinte pergunta do usuário para o inglês de forma clara e direta. '
        'Retorne APENAS o texto traduzido em inglês, sem explicações adicionais.\n\n'
        'Pergunta: {query}'
    )

    chain = prompt | llm # pegar a saida do objeto a esquerda e passa como entrada para a direita
    english_query = chain.invoke( # retorna um obj contendo a messagem da IA
        {'query': query}
    )

    # Extrai o texto do content (content extrai apenas o texto bruto contido dentro da msg)
    if isinstance(english_query.content, list):
        texto = ''.join([
            p if isinstance(p, str) else p.get('text', '') for p in english_query.content
        ])

    else:
        texto = str(english_query.content)

    display(
        Markdown(
            f'\n\n[Translate]\n\nQuery original: {query} \n\nTraduzida: {texto}'
        )
    )
    #print(f'\n[Translate]\nQuery original: {query} \nTraduzida: {texto}')

    return texto

#%%
@tool
def procurar_repositorio_doc(query) -> str:
    ''' Use when the question is about rules, PEPs, conventions, or official style guides for Python code.
    
    Args:
        query: The user's question, topic, or search terms regarding Python code style/guidelines.

    Returns:
        Relevant excerpts found in the official document repository.
    '''

    if isinstance(query, dict):
        query = list(query.values())[0]

    #query_ingles = traduzir_query_ingles(query)
    return (
            fazer_busca(
            query, 
            k=5
        ) +
    '[Instrução de Idioma: Sintetize as informações acima e responda em Português do Brasil.]'
    )


#%%
# Iniciando o modelo
from langchain.chat_models import init_chat_model

llm = init_chat_model(
    model = 'gemini-3.5-flash-lite',
    model_provider = 'google_genai'
)

# criar a lista de ferramentas
tools: list[BaseTool] = [procurar_repositorio_doc]

# complementar o llm com as tools
llm_tools = llm.bind_tools(tools)

# Definir o que e a forma que queremos de resposta. Não é exibido ao ausuário.
system_message = SystemMessage( #Prompt programador
    'Você é um guia de estudos que ajuda programadores, cientistas de dados e afins.\n\n'
    'Evite conversar sobre assuntos paralelos ao tópico escolhido. \n\n'
    'As respostas devem ser em portugues\n\n'
    'Você pode ser amigável e tratar o estudante conforme ele te tratar. Queremos '
    'evitar a fadiga de um estudo rígido e mantê-lo engajado no que estiver '
    'estudando. Talvez até adicionando algum curiosidade. \n\n'
    'As próximas mensagens serão de um estudante.'
)

# Criar historico de mensages
messages: list[BaseMessage] = [
    system_message
]

while True:
    input_pt = str(input('Qual a pergunta?')).lower()

    if input_pt == 'sair':
        break

    input_humano = traduzir_query_ingles(input_pt)
    msg_humano = HumanMessage(input_humano)

    messages.append(msg_humano)
    
    llm_response = llm_tools.invoke(messages) # enviar msg para o modelo
    messages.append(llm_response) # Add ao historico

    # verificar se o modelo optou por chamar a ferramentea
    if llm_response.tool_calls:
        print('\n⚙️ TOOL ACIONADA. \nO modelo está olhando a doc do repositorio.')

        # executar cada tool solicitada pelo modelo
        for tool_call in llm_response.tool_calls:

            tool_name = tool_call['name'] # nome da fonte
            tool_arg = tool_call['args'] # query

            if tool_name == 'procurar_repositorio_doc':
                resultado = procurar_repositorio_doc.invoke(tool_arg) # fazer a buscar no repositorio

                tool_message = ToolMessage( # chamar msg da tool
                    content = resultado, 
                    tool_call_id = tool_call['id']
                ) # gerar um dicionario de resposta:id da query
                messages.append(tool_message)

        # voltar a segunda chamada pra IA juntar a resposta final com o contexto de busca

        reposta_final = llm_tools.invoke(messages)            
        # Se .content for uma lista, junta o texto de cada bloco:
        if isinstance(reposta_final.content, list):
            texto_final = "".join(
                [
                    bloco.get("text", "")
                    for bloco in reposta_final.content
                    if isinstance(bloco, dict)
                ]
            )
        else:
            texto_final = reposta_final.content

        print(40*'*-')
        print('Resposta Final (com RAG):')
        print(80*' ')
        display(Markdown(texto_final))
        #print(texto_final)
        print(40*'*-')

    else:
        if isinstance(llm_response.content, list):
            texto_resposta = "".join(
                [
                    bloco.get("text", "")
                    for bloco in llm_response.content
                    if isinstance(bloco, dict)
                ]
            )
        else:
            texto_resposta = llm_response.content

        print(40*'*-')
        print('Resposta Final:')
        print(80*' ')
        display(Markdown(texto_resposta))
        print(40*'*-')
# %%