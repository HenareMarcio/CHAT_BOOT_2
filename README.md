# CHAT_BOOT_2 — Chatbot Familiar com RAG

Chatbot conversacional que responde perguntas sobre apelidos, brincadeiras internas e referências da família, usando busca semântica local (RAG) combinada com um modelo de linguagem via OpenRouter.

## Como funciona

1. Uma base de apelidos e descrições (`frases.json`) é indexada no **ChromaDB**, um banco de dados vetorial que roda localmente e persiste os dados em disco.
2. Quando o usuário manda uma mensagem no chat, o sistema busca no Chroma as entradas mais **semanticamente parecidas** com a pergunta (não precisa ser a palavra exata).
3. Se a correspondência for muito próxima, o bot responde direto com a informação da base.
4. Se não houver uma correspondência forte, o bot manda as informações mais relevantes encontradas como contexto para um modelo de IA (via OpenRouter), que gera uma resposta natural.

## Stack utilizada

- **[Chainlit](https://chainlit.io/)** — interface de chat
- **[ChromaDB](https://www.trychroma.com/)** — banco de dados vetorial local, com persistência em disco
- **[OpenRouter](https://openrouter.ai/)** — gateway de acesso a modelos de IA (usando o modelo `nvidia/nemotron-3-super-120b-a12b:free`)
- **Python 3.12**

## Estrutura do projeto

```
CHAT_BOOT_2/
├── app.py           # aplicação principal (Chainlit + busca no Chroma + chamada à IA)
├── ingest.py        # script para carregar/atualizar a base de frases no ChromaDB
├── frases.json       # base de apelidos e descrições da família
├── chroma_data/       # banco vetorial persistido (gerado automaticamente, não versionado)
├── .env               # chave da API do OpenRouter (não versionado)
└── .gitignore
```

## Pré-requisitos

- Python 3.12 instalado
- Uma chave de API do [OpenRouter](https://openrouter.ai/keys)

## Instalação

**1. Clone o repositório**
```bash
git clone https://github.com/HenareMarcio/CHAT_BOOT_2.git
cd CHAT_BOOT_2
```

**2. Crie e ative um ambiente virtual**
```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**3. Instale as dependências**
```powershell
pip install chromadb chainlit openai python-dotenv
```

**4. Configure sua chave da API**

Crie um arquivo `.env` na raiz do projeto com o conteúdo:
```
OPENROUTER_API_KEY=sua_chave_aqui
```

**5. Edite a base de frases (opcional)**

Adicione ou modifique entradas no `frases.json`, no formato:
```json
{
  "apelido": "Descrição de quem é ou o que significa."
}
```

**6. Popule o banco vetorial**
```powershell
python ingest.py
```
Rode esse comando sempre que atualizar o `frases.json`, para reindexar as mudanças.

## Executando

```powershell
chainlit run app.py -w
```

A interface abre automaticamente em `http://localhost:8000`. O parâmetro `-w` ativa o auto-reload ao editar o código.

## Ajustes possíveis

- **`LIMIAR_MATCH_DIRETO`** (em `app.py`): controla a sensibilidade da busca no Chroma. Um valor mais baixo faz o bot responder direto da base com mais frequência; um valor mais alto manda mais perguntas para a IA decidir.
- **`MODELO`** (em `app.py`): troque pelo identificador de outro modelo disponível no OpenRouter, caso o modelo gratuito atual esteja instável ou sobrecarregado.

## Notas

- O modelo gratuito usado pode retornar erros de sobrecarga (`503`) em horários de pico; o `app.py` já tenta novamente automaticamente antes de exibir uma mensagem de erro ao usuário.
- A pasta `chroma_data/` não é versionada no Git — ao clonar o projeto em outra máquina, rode `python ingest.py` para recriar o banco local.
