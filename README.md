# Hackathon API REST - Guia Técnico

API REST desenvolvida em **Python** com **Flask** para a Hackathon.  
Inclui autenticação **JWT** e um endpoint para a tarefa principal.

---

## 🧩 Pré-requisitos

Instale as dependências necessárias:

```bash
pip install Flask PyJWT
```

---

## 🚀 Execução

Para iniciar o servidor, execute o comando na raiz do projeto:

```bash
python api_main.py
```

O servidor estará disponível em:  
**http://127.0.0.1:5000**

---

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

---

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

---

## 🧪 Exemplo de Uso (cURL)

### 1. Obter Token

```bash
curl -X POST http://127.0.0.1:5000/token -H "Content-Type: application/json" -d '{"login": "user_hackathon", "senha": "senha123"}'
```

### 2. Executar Tarefa (substitua o token)

```bash
curl -X POST http://127.0.0.1:5000/task -H "Content-Type: application/json" -H "Authorization: Bearer seu.jwt.token.aqui" -d '{"dados_da_tarefa": "exemplo"}'
```

---

📂 **Seções do Guia:**
- Pré-requisitos  
- Execução  
- Endpoints da API  
  - Autenticação  
  - Execução da Tarefa  
- Exemplo de Uso (cURL)
