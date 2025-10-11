# Hackathon - Guia Técnico

---

## 1 - BigQuery

## 🎯 Objetivo

O objetivo principal deste script é fornecer um ponto de partida claro e funcional para interagir com o BigQuery usando a biblioteca cliente oficial do Google para Python (google-cloud-bigquery).

## 📋 Pré-requisitos
Antes de executar o script, certifique-se de que você possui os seguintes pré-requisitos instalados e configurados:

- Google Cloud SDK: A ferramenta de linha de comando gcloud instalada e configurada em sua máquina. Você pode instalá-la a partir deste link (https://cloud.google.com/sdk/docs/install).

- Instale as dependências necessárias:

```bash
pip install google-cloud-bigquery
```

- Autentique-se na sua máquina:

```bash
gcloud auth application-default login
```

## 🚀 Execução

```bash
python consultar_bigquery.py
```

---

## 2 - API REST

API REST desenvolvida em **Python** com **Flask** para a Hackathon.  
Inclui autenticação **JWT** e um endpoint para a tarefa principal.



## 🧩 Pré-requisitos

Instale as dependências necessárias:

```bash
pip install Flask PyJWT
```

## 🚀 Execução

Para iniciar o servidor, execute o comando na raiz do projeto:

```bash
python api_main.py
```

O servidor estará disponível em:  
**http://127.0.0.1:5000**

## 🔗 Endpoints da API

### 1. Autenticação

Gera um token de acesso **JWT** válido por uma hora.

- **URL:** `POST /token`
- **Corpo da Requisição (JSON):**
  ```json
  {
      "login": "user_hackathon",
      "senha": "senha123"
  }
  ```
- **Resposta (200 OK):**
  ```json
  {
      "token": "seu.jwt.token.aqui"
  }
  ```

### 2. Execução da Tarefa

Processa a tarefa da Hackathon. Requer autenticação.

- **URL:** `POST /task`
- **Cabeçalhos:**

  | Chave          | Valor                    |
  |----------------|--------------------------|
  | Content-Type   | application/json          |
  | Authorization  | Bearer {seu_jwt_token}   |

- **Corpo da Requisição (JSON):**
  ```json
  {
      "dados_da_tarefa": "exemplo"
  }
  ```

- **Resposta (200 OK):**  
  Retorna o resultado do processamento.

## 🧪 Exemplo de Uso (cURL)

### 1. Obter Token

```bash
curl -X POST http://127.0.0.1:5000/token -H "Content-Type: application/json" -d '{"login": "user_hackathon", "senha": "senha123"}'
```

### 2. Executar Tarefa (substitua o token)

```bash
curl -X POST http://127.0.0.1:5000/task -H "Content-Type: application/json" -H "Authorization: Bearer seu.jwt.token.aqui" -d '{"dados_da_tarefa": "exemplo"}'
```
