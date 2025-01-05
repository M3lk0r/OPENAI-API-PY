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
            "Melhore o codigo a seguir segurindo novas bibliotecas, recebendo e devolvendo a mensagem por interface grafica, utilizando um log de toda a conversa em arquivo de texto \n"
            "tbem aproveitadendo esse aquivo de texto para gerar uma memoria para a utilização da api, e tudo isso separando por projetos como se cada um fosse um chat diferente"
            "import os\n"
            "import logging\n"
            "from openai import OpenAI\n\n"
            "logging.basicConfig(level=logging.INFO)\n\n"
            "MODEL = \"o1-mini\"\n\n"
            "try:\n"
            "    api_key = os.getenv(\"OPENAI_API_KEY\")\n"
            "    if not api_key:\n"
            "        raise ValueError(\"Chave da API não encontrada. Certifique-se de configurá-la como variável do sistema.\")\n"
            "    client = OpenAI(api_key=api_key)\n"
            "except Exception as e:\n"
            "    logging.error(f\"Erro ao inicializar o cliente OpenAI: {e}\")\n"
            "    exit(1)\n\n"
            "def create_chat_completion(messages):\n"
            "    try:\n"
            "        chat_completion = client.chat.completions.create(\n"
            "            model=MODEL,\n"
            "            messages=messages,\n"
            "        )\n"
            "        return chat_completion\n"
            "    except Exception as e:\n"
            "        logging.error(f\"Erro ao criar a chat completion: {e}\")\n"
            "        return None\n\n"
            "messages = [\n"
            "    {\n"
            "        \"role\": \"user\",\n"
            "        \"content\": (\n"
            "            \"mensagem\"\n"
            "        )\n"
            "    },\n"
            "]\n\n"
            "chat_completion = create_chat_completion(messages)\n"
            "if chat_completion:\n"
            "    response = chat_completion.choices[0].message.content\n"
            "    print(response)\n"
            "else:\n"
            "    logging.error(\"Não foi possível obter uma resposta do modelo.\")"
        )
    },
]

chat_completion = create_chat_completion(messages)
if chat_completion:
    response = chat_completion.choices[0].message.content
    print(response)
else:
    logging.error("Não foi possível obter uma resposta do modelo.")
