# TESTE-API-PY

Criaver variavel de ambiente para chave da API (Windows)

[System.Environment]::SetEnvironmentVariable('OPENAI_API_KEY', 'valor', [System.EnvironmentVariableTarget]::Machine)
$env:OPENAI_API_KEY = "sua_chave_aqui"

Criar venv

python -m venv venv

Ativar venv

py .\venv\Scripts\activate

Instalar requerimentos do projeto

pip install -r requirements.txt
