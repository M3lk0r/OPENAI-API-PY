from openai import OpenAI
import logging
import os
import tkinter as tk
from tkinter import simpledialog, messagebox, scrolledtext
from datetime import datetime

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler("app.log"),
                        logging.StreamHandler()
                    ])

API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    messagebox.showerror("Erro", "Chave da API não encontrada. Configure a variável 'OPENAI_API_KEY'.")
    logging.error("Chave da API não encontrada.")
    exit(1)

client = OpenAI(api_key=API_KEY)

MODEL = "o1-mini"

class ChatApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Aplicação de Chat OpenAI")
        self.geometry("600x500")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.current_project = None
        self.log_file = None

        self.project_frame = tk.Frame(self)
        self.project_frame.pack(pady=10)

        self.project_label = tk.Label(self.project_frame, text="Projeto Atual: Nenhum")
        self.project_label.pack(side=tk.LEFT, padx=5)

        self.select_button = tk.Button(self.project_frame, text="Selecionar Projeto", command=self.select_project)
        self.select_button.pack(side=tk.LEFT, padx=5)

        self.create_button = tk.Button(self.project_frame, text="Criar Novo Projeto", command=self.create_project)
        self.create_button.pack(side=tk.LEFT, padx=5)

        self.chat_area = scrolledtext.ScrolledText(self, state='disabled', wrap=tk.WORD)
        self.chat_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.entry_frame = tk.Frame(self)
        self.entry_frame.pack(pady=5, padx=10, fill=tk.X)

        self.message_entry = tk.Entry(self.entry_frame)
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,5))
        self.message_entry.bind("<Return>", self.send_message)

        self.send_button = tk.Button(self.entry_frame, text="Enviar", command=self.send_message)
        self.send_button.pack(side=tk.RIGHT)

    def select_project(self):
        projects = self.get_projects()
        if not projects:
            messagebox.showinfo("Info", "Nenhum projeto disponível. Crie um novo projeto primeiro.")
            return
        project = simpledialog.askstring("Selecionar Projeto", f"Projetos disponíveis:\n{', '.join(projects)}\n\nDigite o nome do projeto:")
        if project in projects:
            self.load_project(project)
        else:
            messagebox.showerror("Erro", f"Projeto '{project}' não encontrado.")

    def create_project(self):
        project = simpledialog.askstring("Criar Projeto", "Digite o nome do novo projeto:")
        if project:
            projects = self.get_projects()
            if project in projects:
                messagebox.showerror("Erro", "Projeto já existe.")
                return
            os.makedirs("projetos", exist_ok=True)
            log_path = os.path.join("projetos", f"{project}.txt")
            with open(log_path, 'w') as f:
                f.write(f"--- Conversa iniciada em {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n")
            self.load_project(project)
            messagebox.showinfo("Sucesso", f"Projeto '{project}' criado com sucesso.")

    def get_projects(self):
        if not os.path.exists("projetos"):
            return []
        return [f[:-4] for f in os.listdir("projetos") if f.endswith(".txt")]

    def load_project(self, project):
        self.current_project = project
        self.log_file = os.path.join("projetos", f"{project}.txt")
        self.project_label.config(text=f"Projeto Atual: {project}")
        self.chat_area.config(state='normal')
        self.chat_area.delete(1.0, tk.END)
        if os.path.exists(self.log_file):
            with open(self.log_file, 'r', encoding='utf-8') as f:
                conversation = f.read()
                self.chat_area.insert(tk.END, conversation + "\n")
        self.chat_area.config(state='disabled')
        logging.info(f"Projeto '{project}' carregado.")

    def send_message(self, event=None):
        if not self.current_project:
            messagebox.showwarning("Aviso", "Selecione ou crie um projeto primeiro.")
            return
        user_message = self.message_entry.get().strip()
        if not user_message:
            return
        self.display_message("Você", user_message)
        self.log_conversation("user", user_message)
        self.message_entry.delete(0, tk.END)

        self.after(100, lambda: self.get_response(user_message))

    def display_message(self, sender, message):
        self.chat_area.config(state='normal')
        self.chat_area.insert(tk.END, f"{sender}: {message}\n")
        self.chat_area.config(state='disabled')
        self.chat_area.yview(tk.END)

    def log_conversation(self, role, message):
        if self.log_file:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(f"{role.capitalize()}: {message}\n")

    def get_conversation_history(self):
        messages = []
        if self.log_file and os.path.exists(self.log_file):
            with open(self.log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if ": " in line:
                        role, content = line.strip().split(": ", 1)
                        if role.lower() == "user":
                            messages.append({"role": "user", "content": content})
                        elif role.lower() == "assistant":
                            messages.append({"role": "assistant", "content": content})
        return messages

    def get_response(self, user_message):
        messages = self.get_conversation_history()
        messages.append({"role": "user", "content": user_message})

        try:
            completion = client.chat.completions.create(
                model=MODEL,
                messages=messages
            )

            assistant_message = completion.choices[0].message.content.strip()
            self.display_message("Assistente", assistant_message)
            self.log_conversation("assistant", assistant_message)
            logging.info("Resposta recebida da API.")
        except Exception as e:
            logging.error(f"Erro ao obter resposta da API: {e}")
            messagebox.showerror("Erro", f"Falha ao obter resposta da API: {e}")

    def on_closing(self):
        if messagebox.askokcancel("Sair", "Deseja sair da aplicação?"):
            self.destroy()

if __name__ == "__main__":
    app = ChatApplication()
    app.mainloop()
