import logging
import os
import tkinter as tk
from tkinter import messagebox, scrolledtext, Toplevel, Listbox, Button, Entry, Label, END
from datetime import datetime
import yaml
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

class ChatApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Aplicação de Chat OpenAI")
        self.geometry("700x600")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.current_project = None
        self.log_file = None
        self.current_model = None

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

        self.message_entry = tk.Text(self.entry_frame, font=("Arial", 11), height=4)
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,5))
        self.message_entry.bind("<Return>", self.handle_enter)
        self.message_entry.bind("<Shift-Return>", self.handle_shift_enter)

        self.send_button = tk.Button(self.entry_frame, text="Enviar", command=self.send_message)
        self.send_button.pack(side=tk.RIGHT)

    def handle_enter(self, event):
        """Envia a mensagem ao pressionar Enter (sem Shift)."""
        if not event.state & 0x1:
            self.send_message()
            return "break"

    def handle_shift_enter(self, event):
        """Adiciona uma nova linha ao pressionar Shift+Enter."""
        self.message_entry.insert(tk.INSERT, "\n")
        return "break"

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
        create_window.geometry("400x400")
        create_window.resizable(False, False)

        create_window.columnconfigure(1, weight=1)
        create_window.rowconfigure(3, weight=1)

        label = Label(create_window, text="Nome do Projeto:", font=("Arial", 12))
        label.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)

        entry = Entry(create_window, font=("Arial", 11))
        entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        model_label = Label(create_window, text="Selecionar Modelo:", font=("Arial", 12))
        model_label.grid(row=1, column=0, padx=10, pady=10, sticky=tk.NW)

        model_listbox = Listbox(create_window, selectmode=tk.SINGLE, font=("Arial", 11), height=10)
        model_listbox.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        scrollbar = tk.Scrollbar(create_window, orient=tk.VERTICAL, command=model_listbox.yview)
        model_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=1, column=2, sticky='ns', pady=10)

        models = self.get_available_models()
        if not models:
            messagebox.showerror("Erro", "Não foi possível carregar os modelos disponíveis.")
            create_window.destroy()
            return

        for model in models:
            model_listbox.insert(END, model)

        button_frame = tk.Frame(create_window)
        button_frame.grid(row=2, column=0, columnspan=3, pady=20)

        create_btn = Button(button_frame, text="Criar", command=lambda: self.create_project(entry, model_listbox, create_window))
        create_btn.pack(side=tk.LEFT, padx=10)

        cancel_btn = Button(button_frame, text="Cancelar", command=create_window.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=10)

    def create_project(self, entry, model_listbox, window):
        project = entry.get().strip()
        if not project:
            messagebox.showerror("Erro", "Nome do projeto não pode ser vazio.")
            return
        projects = self.get_projects()
        if project in projects:
            messagebox.showerror("Erro", "Projeto já existe.")
            return

        selected_model_index = model_listbox.curselection()
        if not selected_model_index:
            messagebox.showerror("Erro", "Selecione um modelo.")
            return
        selected_model = model_listbox.get(selected_model_index[0])

        os.makedirs("projetos", exist_ok=True)
        log_path = os.path.join("projetos", f"{project}.yaml")
        try:
            with open(log_path, 'w', encoding='utf-8') as f:
                yaml.dump({
                    "created_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "model": selected_model,
                    "conversation": []
                }, f, allow_unicode=True)
            self.load_project(project)
            messagebox.showinfo("Sucesso", f"Projeto '{project}' criado com sucesso.")
            window.destroy()
            logging.info(f"Projeto '{project}' criado.")
        except Exception as e:
            logging.error(f"Erro ao criar projeto: {e}")
            messagebox.showerror("Erro", f"Falha ao criar projeto: {e}")

    def get_available_models(self):
        """Retorna uma lista de modelos disponíveis na API OpenAI."""
        try:
            models = client.models.list()
            return [model.id for model in models.data]
        except Exception as e:
            logging.error(f"Erro ao obter modelos: {e}")
            return []

    def get_projects(self):
        if not os.path.exists("projetos"):
            return []
        return [f[:-5] for f in os.listdir("projetos") if f.endswith(".yaml")]

    def load_project(self, project):
        self.current_project = project
        self.log_file = os.path.join("projetos", f"{project}.yaml")
        if os.path.exists(self.log_file):
            with open(self.log_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                self.current_model = data.get("model", "Nenhum modelo selecionado")
                self.project_label.config(text=f"Projeto Atual: {project} | Modelo: {self.current_model}")
                self.chat_area.config(state='normal')
                self.chat_area.delete(1.0, tk.END)
                for msg in data.get("conversation", []):
                    sender = "Você" if msg['role'] == "user" else "Assistente"
                    self.display_message(sender, msg['content'], msg['role'])
        self.chat_area.config(state='disabled')
        logging.info(f"Projeto '{project}' carregado.")

    def send_message(self, event=None):
        if not self.current_project:
            messagebox.showwarning("Aviso", "Selecione ou crie um projeto primeiro.")
            return
        user_message = self.message_entry.get("1.0", tk.END).strip()
        if not user_message:
            return
        self.display_message("Você", user_message, "user")
        self.log_conversation("user", user_message)
        self.message_entry.delete("1.0", tk.END)

        self.send_button.config(state='disabled')

        self.display_message("Assistente", "Assistente está digitando...", "assistant_loading")

        self.after(100, lambda: self.get_response(user_message))

    def display_message(self, sender, message, role):
        self.chat_area.config(state='normal')

        self.chat_area.tag_config("user", foreground="blue", font=("Arial", 11, "bold"))
        self.chat_area.tag_config("assistant_loading", foreground="gray", font=("Arial", 11, "italic"))
        self.chat_area.tag_config("assistant", foreground="green", font=("Arial", 11))
        self.chat_area.tag_config("bold", font=("Arial", 11, "bold"))
        self.chat_area.tag_config("code", background="#f0f0f0", font=("Courier", 10))
        self.chat_area.tag_config("header", font=("Arial", 14, "bold"))

        if role == "user":
            self.chat_area.insert(tk.END, f"{sender}: ", "user")
        elif role == "assistant_loading":
            self.chat_area.insert(tk.END, f"{sender}: ", "assistant_loading")
        else:
            self.chat_area.insert(tk.END, f"{sender}: ", "assistant")

        lines = message.split("\n")
        in_code_block = False
        for line in lines:
            if line.strip().startswith("```"):
                in_code_block = not in_code_block
                if in_code_block:
                    self.chat_area.insert(tk.END, "\n", "code")
                continue

            if in_code_block:
                self.chat_area.insert(tk.END, f"{line}\n", "code")
            else:
                if line.startswith("##"):
                    self.chat_area.insert(tk.END, f"{line[2:].strip()}\n", "header")
                elif "**" in line:
                    parts = line.split("**")
                    for i, part in enumerate(parts):
                        if i % 2 == 1:
                            self.chat_area.insert(tk.END, part, "bold")
                        else:
                            self.chat_area.insert(tk.END, part)
                    self.chat_area.insert(tk.END, "\n")
                else:
                    self.chat_area.insert(tk.END, f"{line}\n")

        self.chat_area.config(state='disabled')
        self.chat_area.yview(tk.END)    

    def log_conversation(self, role, message):
        if self.log_file:
            with open(self.log_file, 'r+', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                data["conversation"].append({"role": role, "content": message, "timestamp": datetime.now().isoformat()})
                f.seek(0)
                yaml.dump(data, f, allow_unicode=True)

    def get_conversation_history(self):
        messages = []
        if self.log_file and os.path.exists(self.log_file):
            with open(self.log_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                for msg in data.get("conversation", []):
                    messages.append({"role": msg["role"], "content": msg["content"]})
        return messages

    def get_response(self, user_message):
        messages = self.get_conversation_history()

        try:
            completion = client.chat.completions.create(
                model=self.current_model,
                messages=messages
            )

            assistant_message = completion.choices[0].message.content.strip()
            self.remove_loading_message()

            self.display_message("Assistente", assistant_message, "assistant")
            self.log_conversation("assistant", assistant_message)
            logging.info("Resposta recebida da API.")
        except Exception as e:
            self.remove_loading_message()

            logging.error(f"Erro ao obter resposta da API: {e}")
            messagebox.showerror("Erro", f"Falha ao obter resposta da API: {e}")
        finally:
            self.send_button.config(state='normal')

    def remove_loading_message(self):
        self.chat_area.config(state='normal')
        content = self.chat_area.get("1.0", tk.END)
        if "Assistente: Assistente está digitando..." in content:
            self.chat_area.delete("end-2l", "end-1c")
        self.chat_area.config(state='disabled')

    def on_closing(self):
        if messagebox.askokcancel("Sair", "Deseja sair da aplicação?"):
            self.destroy()

if __name__ == "__main__":
    app = ChatApplication()
    app.mainloop()