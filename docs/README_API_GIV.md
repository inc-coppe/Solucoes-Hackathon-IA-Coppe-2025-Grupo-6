# 🏥 API REST - Gestão Inteligente de Vagas (GIV)

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Uma API REST completa para gestão de vagas hospitalares com Machine Learning integrado, baseada no `dashboard_final.py`.

## 🚀 **Início Rápido**

### **1. Instalação**
```bash
# Instalar dependências
pip install -r requirements_api_giv.txt

# Executar API
python api_giv_completa.py
```

### **2. Acesso**
- **API**: http://127.0.0.1:8000
- **Documentação**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

### **3. Login**
```bash
# Obter token JWT
curl -X POST "http://127.0.0.1:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

## 📋 **Funcionalidades**

### ✅ **Implementadas**
- 🔐 **Autenticação JWT** - Segurança completa
- 📊 **Dashboard KPIs** - Métricas em tempo real
- 🤖 **Machine Learning** - Random Forest para predições
- 🔍 **Consultas Avançadas** - Filtros flexíveis
- 📈 **Análises Preditivas** - Impacto de não agendar
- 📋 **Relatórios** - Resumos e estatísticas
- 💾 **Cache Inteligente** - Performance otimizada
- 📚 **Documentação Interativa** - Swagger UI

### 🎯 **Endpoints Principais**

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/auth/login` | POST | Login e token JWT |
| `/api/v1/dashboard/kpis` | GET | KPIs do dashboard |
| `/api/v1/analise/predicao` | GET | Análise preditiva ML |
| `/api/v1/solicitacoes` | GET | Listar solicitações |
| `/api/v1/relatorios/resumo` | GET | Relatório resumido |
| `/api/v1/ml/predicao` | POST | Predição ML personalizada |

## 🔧 **Configuração**

### **Usuários Padrão**
| Usuário | Senha | Descrição |
|---------|-------|-----------|
| `admin` | `admin123` | Administrador |
| `tou` | `hackathon2025` | Usuário TOU |
| `api_user` | `api123` | Usuário API |
| `gestor` | `gestor456` | Gestor |

### **Variáveis de Ambiente**
```bash
export GIV_SECRET_KEY="sua-chave-secreta"
export GIV_ACCESS_TOKEN_EXPIRE=30
export GIV_HOST="0.0.0.0"
export GIV_PORT=8000
```

## 📊 **Exemplos de Uso**

### **Python**
```python
import requests

# Login
response = requests.post("http://127.0.0.1:8000/auth/login", 
                        data={"username": "admin", "password": "admin123"})
token = response.json()["access_token"]

# KPIs
headers = {"Authorization": f"Bearer {token}"}
kpis = requests.get("http://127.0.0.1:8000/api/v1/dashboard/kpis", headers=headers)
print(kpis.json())
```

### **JavaScript**
```javascript
// Login
const loginResponse = await fetch('/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  body: 'username=admin&password=admin123'
});
const { access_token } = await loginResponse.json();

// KPIs
const kpisResponse = await fetch('/api/v1/dashboard/kpis', {
  headers: { 'Authorization': `Bearer ${access_token}` }
});
const kpis = await kpisResponse.json();
```

### **cURL**
```bash
# Login
TOKEN=$(curl -s -X POST "http://127.0.0.1:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123" | jq -r '.access_token')

# KPIs
curl -H "Authorization: Bearer $TOKEN" \
  "http://127.0.0.1:8000/api/v1/dashboard/kpis"
```

## 🤖 **Machine Learning**

### **Modelo**
- **Algoritmo**: Random Forest Classifier
- **Features**: Risco, Especialidade, Idade, Tempo de Espera
- **Performance**: ~85% de acurácia
- **Treinamento**: Automático na primeira predição

### **Predição**
```python
dados = {
    "solicitacao_risco": "VERMELHO",
    "procedimento_especialidade": "Cardiologia",
    "paciente_faixa_etaria": "60-74"
}

response = requests.post("http://127.0.0.1:8000/api/v1/ml/predicao", 
                        headers=headers, json=dados)
predicao = response.json()
```

## 📈 **Performance**

### **Limites**
- **Dados**: Máximo 10.000 registros por requisição
- **Timeout**: 30 segundos por requisição
- **Rate Limit**: 100 req/min por usuário

### **Cache**
- **Dados**: Cache automático após primeira carga
- **Tamanho**: ~500MB em memória
- **Duração**: Até reinicialização

## 🛠️ **Desenvolvimento**

### **Estrutura do Projeto**
```
├── api_giv_completa.py          # API principal
├── requirements_api_giv.txt     # Dependências
├── DOCUMENTACAO_API_GIV.md      # Documentação completa
├── exemplo_uso_api.py           # Exemplos de uso
├── INICIAR_API_GIV.bat          # Script de inicialização
└── README_API_GIV.md            # Este arquivo
```

### **Executar Testes**
```bash
# Exemplo de uso
python exemplo_uso_api.py

# Teste de saúde
curl http://127.0.0.1:8000/health
```

## 📚 **Documentação**

- **Completa**: [DOCUMENTACAO_API_GIV.md](DOCUMENTACAO_API_GIV.md)
- **Interativa**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc
- **Schema**: http://127.0.0.1:8000/openapi.json

## 🔍 **Troubleshooting**

### **Problemas Comuns**

#### **Erro 401 - Não Autorizado**
```json
{"detail": "Token inválido"}
```
**Solução**: Verificar se o token JWT está correto e não expirado.

#### **Erro 500 - Dados Não Encontrados**
```json
{"detail": "Arquivos de solicitacao nao encontrados"}
```
**Solução**: Verificar se os arquivos Parquet estão na pasta `db/`.

#### **Modelo ML Não Treinado**
**Solução**: Fazer uma requisição para `/api/v1/ml/predicao` para treinar automaticamente.

## 🎯 **Roadmap**

### **Próximas Versões**
- **v1.1**: Cache Redis, Rate Limiting
- **v1.2**: Webhooks, Notificações
- **v1.3**: Exportação de dados (Excel, PDF)
- **v2.0**: Interface web completa

## 📞 **Suporte**

- **Issues**: [GitHub Issues](https://github.com/seu-repo/issues)
- **Documentação**: [DOCUMENTACAO_API_GIV.md](DOCUMENTACAO_API_GIV.md)
- **Exemplos**: [exemplo_uso_api.py](exemplo_uso_api.py)

## 📄 **Licença**

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

**Desenvolvido com ❤️ pela Equipe GIV**

**Versão**: 1.0.0 | **Data**: Janeiro 2025

