import wave, struct, os
from openai import OpenAI
from pvrecorder import PvRecorder
from playsound import playsound
from IPython.display import Image, display
import logging

logging.basicConfig(level=logging.INFO)

MODEL = "o1-mini"

client = OpenAI()

def create_chat_completion(messages):
    try:
        chat_completion = client.chat.completions.create(
            model=MODEL,
            messages=messages,
        )
        return chat_completion
    except Exception as e:
        logging.error(f"Error creating chat completion: {e}")
        return None

def handle_error(e):
    logging.error(f"Error: {e}")

messages = [
    #{"role": "user", "content": "preciso criar um site q tenha como ser instalado no celular com um webapp, me de todas a orientações e codigos necessarios, a função dele será para votação com 6 opções por categoria, após a pessoa votar deve ser direcionada para próxima categoria, os votos so podem ser realizados apor a pessoa realizar um login via conta google, caso n tenha cadastro ele será feito automaticamente tudo isso para usuários normais, mas um lugar para administradores deve ser feito onde sera possível tirar relatórios e adicionar algumas usuários pre cadastrados ou n via email a grupos distinto a fim de tirar relatórios, uma pagina apresentando um gráfico do ganhador de cada categoria bem no estilo the game awards o site deve ser acessado por dispositivos moveis e desktops a linguagem de programação ou banco de dados deve ser escolhida para que compra todos os requisitos, lembrando que devera hospedar imagens, texto e vídeos, tendo uma preferencia por python, ele sera hospedado em um IIS um diretório para os arquivos estáticos deve ser criado tbem"},
    {"role": "user", "content": "Tenho um ambiente com Proxmox VE no qual realizo deploys utilizando pipelines do Azure DevOps. Minha infraestrutura inclui servidores Ubuntu e Windows Server 2025. Desejo utilizar Docker e Kubernetes para integrar e gerenciar contêineres no meu cluster Proxmox VE. Atualmente, meu cluster não possui alta disponibilidade (HA) e é composto por dois nós. Já tenho dois servidores configurados com Ubuntu 24.04 e a possibilidade de criar mais servidores, inclusive com Windows Server, caso necessário. Minha infraestrutura de rede no cluster conta com três redes configuradas: Produção: onde estão localizados os servidores principais; DMZ: destinada à comunicação com serviços externos; Gerência: utilizada para o acesso e administração dos nós do cluster. Preciso de um guia detalhado, passo a passo, para configurar e gerenciar contêineres utilizando Kubernetes nesse ambiente. Caso seja uma boa prática, posso criar novas redes para atender às demandas específicas do cluster."},
]

chat_completion = create_chat_completion(messages).choices[0].message.content

print (chat_completion)