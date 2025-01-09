import logging
import os
import tkinter as tk
from tkinter import messagebox, scrolledtext, simpledialog, Toplevel, Listbox, Button, Entry, Label, END
from datetime import datetime
import json
from openai import OpenAI
from tkinter import ttk

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
        self.geometry("700x600")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.current_project = None
        self.log_file = None

        self.create_widgets()

    def create_widgets(self):
        self.project_frame = tk.Frame(self)
        self.project_frame.pack(pady=10)

        self.project_label = tk.Label(self.project_frame, text="Projeto Atual: Nenhum", font=("Arial", 12, "bold"))
        self.project_label.pack(side=tk.LEFT, padx=5)

        self.select_button = tk.Button(self.project_frame, text="Selecionar Projeto", command=self.open_select_project_window)
        self.select_button.pack(side=tk.LEFT, padx=5)

        self.create_button = tk.Button(self.project_frame, text="Criar Novo Projeto", command=self.open_create_project_window)
        self.create_button.pack(side=tk.LEFT, padx=5)

        self.chat_area = scrolledtext.ScrolledText(self, state='disabled', wrap=tk.WORD, font=("Arial", 11))
        self.chat_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.entry_frame = tk.Frame(self)
        self.entry_frame.pack(pady=5, padx=10, fill=tk.X)

        self.message_entry = tk.Entry(self.entry_frame, font=("Arial", 11))
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,5))
        self.message_entry.bind("<Return>", self.send_message)

        self.send_button = tk.Button(self.entry_frame, text="Enviar", command=self.send_message)
        self.send_button.pack(side=tk.RIGHT)

    def open_select_project_window(self):
        projects = self.get_projects()
        if not projects:
            messagebox.showinfo("Info", "Nenhum projeto disponível. Crie um novo projeto primeiro.")
            return

        select_window = Toplevel(self)
        select_window.title("Selecionar Projeto")
        select_window.geometry("300x400")

        label = Label(select_window, text="Selecione um Projeto:", font=("Arial", 12))
        label.pack(pady=10)

        listbox = Listbox(select_window, selectmode=tk.SINGLE, font=("Arial", 11))
        listbox.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

        for project in projects:
            listbox.insert(END, project)

        def on_select():
            selected = listbox.curselection()
            if selected:
                project = listbox.get(selected[0])
                self.load_project(project)
                select_window.destroy()
            else:
                messagebox.showwarning("Aviso", "Selecione um projeto.")

        select_btn = Button(select_window, text="Selecionar", command=on_select)
        select_btn.pack(pady=10)

    def open_create_project_window(self):
        create_window = Toplevel(self)
        create_window.title("Criar Novo Projeto")
        create_window.geometry("300x200")

        label = Label(create_window, text="Digite o nome do novo projeto:", font=("Arial", 12))
        label.pack(pady=20)

        entry = Entry(create_window, font=("Arial", 11))
        entry.pack(padx=20, pady=5, fill=tk.X)

        def create():
            project = entry.get().strip()
            if not project:
                messagebox.showerror("Erro", "Nome do projeto não pode ser vazio.")
                return
            projects = self.get_projects()
            if project in projects:
                messagebox.showerror("Erro", "Projeto já existe.")
                return
            os.makedirs("projetos", exist_ok=True)
            log_path = os.path.join("projetos", f"{project}.json")
            with open(log_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "created_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "conversation": []
                }, f, ensure_ascii=False, indent=4)
            self.load_project(project)
            messagebox.showinfo("Sucesso", f"Projeto '{project}' criado com sucesso.")
            create_window.destroy()

        create_btn = Button(create_window, text="Criar", command=create)
        create_btn.pack(pady=20)

    def get_projects(self):
        if not os.path.exists("projetos"):
            return []
        return [f[:-5] for f in os.listdir("projetos") if f.endswith(".json")]

    def load_project(self, project):
        self.current_project = project
        self.log_file = os.path.join("projetos", f"{project}.json")
        self.project_label.config(text=f"Projeto Atual: {project}")
        self.chat_area.config(state='normal')
        self.chat_area.delete(1.0, tk.END)
        if os.path.exists(self.log_file):
            with open(self.log_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for msg in data.get("conversation", []):
                    sender = "Você" if msg['role'] == "user" else "Assistente"
                    self.chat_area.insert(tk.END, f"{sender}: {msg['content']}\n")
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
        self.message_entry.delete(0, END)

        self.after(100, lambda: self.get_response(user_message))

    def display_message(self, sender, message):
        self.chat_area.config(state='normal')
        self.chat_area.insert(tk.END, f"{sender}: {message}\n")
        self.chat_area.config(state='disabled')
        self.chat_area.yview(tk.END)

    def log_conversation(self, role, message):
        if self.log_file:
            with open(self.log_file, 'r+', encoding='utf-8') as f:
                data = json.load(f)
                data["conversation"].append({"role": role, "content": message, "timestamp": datetime.now().isoformat()})
                f.seek(0)
                json.dump(data, f, ensure_ascii=False, indent=4)

    def get_conversation_history(self):
        messages = []
        if self.log_file and os.path.exists(self.log_file):
            with open(self.log_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for msg in data.get("conversation", []):
                    messages.append({"role": msg["role"], "content": msg["content"]})
        return messages

    def get_response(self, user_message):
        messages = self.get_conversation_history()

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