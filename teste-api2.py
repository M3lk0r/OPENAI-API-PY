import os
import logging
from openai import OpenAI

logging.basicConfig(level=logging.INFO)

MODEL = "o1-mini"

try:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("Chave da API não encontrada. Certifique-se de configurá-la como variável do sistema.")
    client = OpenAI(api_key=api_key)
except Exception as e:
    logging.error(f"Erro ao inicializar o cliente OpenAI: {e}")
    exit(1)

def create_chat_completion(messages):
    try:
        chat_completion = client.chat.completions.create(
            model=MODEL,
            messages=messages,
        )
        return chat_completion
    except Exception as e:
        logging.error(f"Erro ao criar a chat completion: {e}")
        return None

messages = [
    {
        "role": "user",
        "content": (
            "Me de uma explicação de como utilizar a api da openia, de dando os modelos do o1 disponiveis, como funciona a parte de messages de forma sucinta e resumida, tbem preciso saber como funciona o armazenamento de memoria caso eu eu envie uma mensagem relacionada a algo que ja foi enviado anteriormes"
        )
    },
]

chat_completion = create_chat_completion(messages)
if chat_completion:
    response = chat_completion.choices[0].message.content
    print(response)
else:
    logging.error("Não foi possível obter uma resposta do modelo.")
