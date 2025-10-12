# --- Estágio 1: Builder ---
# Usamos um estágio de build para instalar as dependências de forma isolada.
FROM python:3.9-slim as builder

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copia o arquivo de dependências e instala
# Isso otimiza o cache do Docker. As dependências só serão reinstaladas se o requirements.txt mudar.
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# --- Estágio 2: Final ---
# Usamos uma imagem Python limpa para a versão final, resultando em uma imagem menor e mais segura.
FROM python:3.9-slim

# Define o diretório de trabalho
WORKDIR /app

# Copia as dependências já instaladas do estágio 'builder'
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages

# Copia o código da sua aplicação para dentro do contêiner
COPY . .

# Expõe a porta que a aplicação irá rodar.
# Esta porta deve ser a mesma que você configurou no seu ECS Task Definition.
EXPOSE 8000

# Comando para iniciar a aplicação quando o contêiner for executado.
# Substitua 'main:app' se o seu arquivo principal ou variável da app forem diferentes.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
