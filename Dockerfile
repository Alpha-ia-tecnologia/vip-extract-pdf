FROM python:3.12

# Define o diretório de trabalho
WORKDIR /code

# Copia e instala as dependências
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copia o restante do código
COPY ./src /code/app

# Comando para iniciar o servidor FastAPI com Uvicorn
CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "8000"]
