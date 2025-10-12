# Hackathon - Guia Técnico

---

## 1 - Streamlit + LLM da AWS

## 📋 Pré-requisitos

- Instale as dependências necessárias:

```bash
pip install streamlit
```

## 🚀 Execução

```bash
streamlit run streamlit_aws_bedrock.py
```

---

## 2 - LLM da AWS

## 📋 Pré-requisitos
- AWS CLI: https://awscli.amazonaws.com/AWSCLIV2.msi.

Verificação: Abra um novo Prompt de Comando

```bash
aws --version
```

- Instale as dependências necessárias:

```bash
pip install boto3
```

- Autentique-se na sua máquina:

As Chaves de acesso podem ser retiradas em https://us-east-1.console.aws.amazon.com/iam/home?region=us-west-2#/users/details/programador-cli?section=security_credentials.

```bash
aws configure
```

## 🚀 Execução

```bash
python aws_bedrock.py
```

---

## 3 - BigQuery

## 🎯 Objetivo

O objetivo principal deste script é fornecer um ponto de partida claro e funcional para interagir com o BigQuery usando a biblioteca cliente oficial do Google para Python (google-cloud-bigquery).

## 📋 Pré-requisitos
Antes de executar o script, certifique-se de que você possui os seguintes pré-requisitos instalados e configurados:

- Google Cloud SDK: A ferramenta de linha de comando gcloud instalada e configurada em sua máquina. Você pode instalá-la a partir deste link (https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe?hl=pt-br).

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
python bigquery_consulta.py
```

---

## 4 - API REST

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
python api_class.py
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
