import os
import chromadb
import chainlit as cl
from openai import OpenAI
from dotenv import load_dotenv
from chromadb.config import Settings

# =========================
# PROMPT DO ASSISTENTE
# =========================

SYSTEM_PROMPT = """
Você é um assistente amigavel.

Regras:

1. Use linguagem simples, amigável e cotidiana.
2. Considere que algumas palavras possuem significados especiais dentro da família.
3. Quando receber perguntas sobre apelidos, pessoas da família ou brincadeiras internas, utilize o contexto familiar.
4. Responda de forma natural e descontraída.
5. Caso não saiba algo, diga que não possui essa informação.
6. Nunca invente fatos sobre a família.
7. Priorize as respostas da base local quando elas existirem.
8. Se a pergunta não estiver na base local, responda usando seu conhecimento geral.
9. Considere que existe um vocabulário próprio da família com apelidos e referências internas.
10. Mantenha respostas curtas e objetivas.
"""

# =========================
# CARREGA VARIÁVEIS
# =========================

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)


# =========================
# BASE FAMILIAR (Chroma)
# =========================

chroma_client = chromadb.PersistentClient(
    path="./chroma_data",
    settings=Settings(anonymized_telemetry=False)
)
collection = chroma_client.get_or_create_collection("frases")

LIMIAR_MATCH_DIRETO = 0.50
MODELO = "nvidia/nemotron-3-super-120b-a12b:free"


def buscar_contexto(pergunta: str, n_resultados: int = 3):
    resultados = collection.query(
        query_texts=[pergunta],
        n_results=n_resultados
    )
    documentos = resultados["documents"][0]
    distancias = resultados["distances"][0]
    metadados = resultados["metadatas"][0]
    return documentos, distancias, metadados


def chamar_modelo(mensagens, tentativas=2):
    """Chama o modelo com retry simples em caso de sobrecarga do provedor."""
    for tentativa in range(tentativas):
        resposta = client.chat.completions.create(
            model=MODELO,
            temperature=0.2,
            messages=mensagens,
            extra_body={
                "reasoning": {
                    "exclude": True
                }
            }
        )

        if resposta.choices:
            return resposta.choices[0].message.content

        # Sem choices: veio erro do provedor (ex: sobrecarga, rate limit)
        erro_info = getattr(resposta, "error", None)
        print(f"Tentativa {tentativa + 1} falhou. Erro do provedor:", erro_info)

    return "O modelo está sobrecarregado no momento, tenta de novo em alguns segundos 🙏"


# =========================
# CHAT
# =========================

@cl.on_message
async def main(message: cl.Message):

    texto = message.content

    documentos, distancias, metadados = buscar_contexto(texto)

    # Match direto e forte na base local
    if distancias and distancias[0] <= LIMIAR_MATCH_DIRETO:
        await cl.Message(content=documentos[0]).send()
        return

    contexto_familiar = "\n".join(
        [f"{metadados[i]['gatilho']}: {documentos[i]}" for i in range(len(documentos))]
    )

    mensagens = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "system", "content": f"Base familiar (trechos mais relevantes encontrados):\n{contexto_familiar}"},
        {"role": "user", "content": message.content}
    ]

    texto_final = chamar_modelo(mensagens)

    await cl.Message(content=texto_final).send()