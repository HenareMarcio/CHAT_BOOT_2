import json
import chromadb

# Lê o dicionário do arquivo JSON
with open("frases.json", "r", encoding="utf-8") as f:
    dados = json.load(f)

print(f"Encontradas {len(dados)} entradas no arquivo.")

client = chromadb.PersistentClient(path="./chroma_data")
collection = client.get_or_create_collection("frases")

palavras = list(dados.keys())
descricoes = list(dados.values())

collection.add(
    documents=descricoes,
    metadatas=[{"gatilho": p} for p in palavras],
    ids=[f"frase_{i}" for i in range(len(descricoes))]
)

print(f"{len(descricoes)} entradas adicionadas ao ChromaDB com sucesso.")