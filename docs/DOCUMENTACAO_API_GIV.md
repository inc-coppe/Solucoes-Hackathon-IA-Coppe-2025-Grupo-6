# 🏥 API REST - Gestão Inteligente de Vagas (GIV)

**Versão**: 1.0.0  
**Data**: Janeiro 2025  
**Autor**: Sistema GIV  
**Baseado em**: `dashboard_final.py`

---

## 📋 **VISÃO GERAL**

A **API REST - Gestão Inteligente de Vagas (GIV)** é uma API completa desenvolvida em FastAPI que fornece acesso programático a todas as funcionalidades do sistema de gestão de vagas hospitalares. A API inclui autenticação JWT, Machine Learning para predições, endpoints para dashboard, relatórios e análises preditivas.

### **Características Principais**
- ✅ **Autenticação JWT** - Segurança completa
- ✅ **Machine Learning** - Random Forest para predições
- ✅ **Cache Inteligente** - Performance otimizada
- ✅ **Documentação Interativa** - Swagger UI e ReDoc
- ✅ **Filtros Avançados** - Consultas flexíveis
- ✅ **Relatórios Dinâmicos** - Análises em tempo real
- ✅ **Paginação** - Controle de volume de dados

---

## 🚀 **INSTALAÇÃO E CONFIGURAÇÃO**

### **1. Instalar Dependências**
```bash
pip install -r requirements_api_giv.txt
```

### **2. Executar a API**
```bash
python api_giv_completa.py
```

### **3. Acessar Documentação**
- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc
- **Página Inicial**: http://127.0.0.1:8000/

---

## 🔐 **AUTENTICAÇÃO**

### **Usuários Válidos**
| Usuário | Senha | Descrição |
|---------|-------|-----------|
| `admin` | `admin123` | Administrador |
| `tou` | `hackathon2025` | Usuário TOU |
| `api_user` | `api123` | Usuário API |
| `gestor` | `gestor456` | Gestor |

### **Obter Token JWT**
```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=admin&password=admin123
```

**Resposta:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": "admin"
}
```

### **Usar Token nas Requisições**
```http
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

---

## 📊 **ENDPOINTS PRINCIPAIS**

### **🏠 Página Inicial**
```http
GET /
```
**Descrição**: Página inicial com links para documentação e endpoints principais.

---

### **📈 Dashboard e KPIs**

#### **KPIs do Dashboard**
```http
GET /api/v1/dashboard/kpis?risco=VERMELHO&especialidade=Cardiologia
```
**Parâmetros**:
- `risco` (opcional): Lista de níveis de risco
- `especialidade` (opcional): Lista de especialidades

**Resposta**:
```json
{
  "status": "sucesso",
  "filtros_aplicados": {
    "risco": ["VERMELHO"],
    "especialidade": ["Cardiologia"]
  },
  "kpis": {
    "total_solicitacoes": 1250,
    "total_sistema": 50000,
    "taxa_confirmacao": 85.5,
    "risco_critico": 25.3,
    "sem_agendamento": 15.2,
    "sem_agendamento_total": 190
  },
  "timestamp": "2025-01-15T10:30:00"
}
```

#### **Dados do Dashboard**
```http
GET /api/v1/dashboard/dados?limit=1000&risco=AMARELO,VERMELHO
```
**Parâmetros**:
- `limit` (opcional): Limite de registros (padrão: 1000, máx: 10000)
- `risco`, `especialidade`: Filtros

**Resposta**:
```json
{
  "status": "sucesso",
  "filtros_aplicados": {
    "risco": ["AMARELO", "VERMELHO"]
  },
  "total_registros": 2500,
  "registros_retornados": 1000,
  "limit": 1000,
  "dados": [
    {
      "solicitacao_id": "123456789",
      "data_solicitacao": "2025-01-15T10:30:00",
      "solicitacao_risco": "VERMELHO",
      "procedimento_especialidade": "Cardiologia",
      "paciente_faixa_etaria": "60-74",
      "solicitacao_status": "AGENDAMENTO / CONFIRMADO"
    }
  ]
}
```

---

### **🤖 Análise Preditiva**

#### **Análise Preditiva com ML**
```http
GET /api/v1/analise/predicao?risco=VERMELHO&especialidade=Cardiologia
```
**Resposta**:
```json
{
  "status": "sucesso",
  "filtros_aplicados": {
    "risco": ["VERMELHO"],
    "especialidade": ["Cardiologia"]
  },
  "total_sem_agendamento": 150,
  "predicao": {
    "total_sem_agendamento": 150,
    "alto_risco_ml": 45,
    "medio_risco_ml": 60,
    "baixo_risco_ml": 45,
    "agravamento_30_dias": 41,
    "agravamento_60_dias": 30,
    "agravamento_90_dias": 5,
    "custo_estimado_30_dias": 205000,
    "custo_estimado_total": 380000,
    "internacoes_projetadas": 23,
    "usa_ml": true,
    "algoritmo": "Random Forest Classifier",
    "num_arvores": 100,
    "modelo_metricas": {
      "acuracia": 0.85,
      "precisao": 0.82,
      "recall": 0.78,
      "f1_score": 0.80
    }
  }
}
```

---

### **🔍 Consultas e Filtros**

#### **Listar Solicitações**
```http
GET /api/v1/solicitacoes?risco=VERMELHO&limit=100&offset=0
```
**Parâmetros**:
- `risco` (opcional): Filtro por nível de risco
- `especialidade` (opcional): Filtro por especialidade
- `status` (opcional): Filtro por status
- `limit` (opcional): Limite de registros (padrão: 100, máx: 5000)
- `offset` (opcional): Deslocamento para paginação (padrão: 0)

**Resposta**:
```json
{
  "status": "sucesso",
  "filtros_aplicados": {
    "risco": "VERMELHO"
  },
  "paginacao": {
    "total": 500,
    "limit": 100,
    "offset": 0,
    "retornados": 100
  },
  "dados": [...]
}
```

#### **Listar Procedimentos**
```http
GET /api/v1/procedimentos?especialidade=Cardiologia&tipo=CONSULTA
```
**Parâmetros**:
- `especialidade` (opcional): Filtro por especialidade
- `tipo` (opcional): Filtro por tipo de procedimento

**Resposta**:
```json
{
  "status": "sucesso",
  "filtros_aplicados": {
    "especialidade": "Cardiologia",
    "tipo": "CONSULTA"
  },
  "total_procedimentos": 25,
  "dados": [
    {
      "procedimento_sisreg_id": "0703716",
      "procedimento": "CONSULTA CARDIOLOGIA CLINICA",
      "procedimento_especialidade": "Cardiologia",
      "procedimento_tipo": "CONSULTA"
    }
  ]
}
```

---

### **📋 Relatórios**

#### **Relatório Resumido**
```http
GET /api/v1/relatorios/resumo
```
**Resposta**:
```json
{
  "status": "sucesso",
  "resumo": {
    "total_solicitacoes": 50000,
    "confirmados": 42500,
    "nao_confirmados": 7500,
    "taxa_confirmacao": 85.0
  },
  "distribuicao_risco": [
    {"solicitacao_risco": "AZUL", "count": 25000},
    {"solicitacao_risco": "VERDE", "count": 15000},
    {"solicitacao_risco": "AMARELO", "count": 8000},
    {"solicitacao_risco": "VERMELHO", "count": 2000}
  ],
  "top_especialidades": [
    {"procedimento_especialidade": "Cardiologia", "count": 8500},
    {"procedimento_especialidade": "Neurologia", "count": 7200}
  ],
  "top_status": [
    {"solicitacao_status": "AGENDAMENTO / CONFIRMADO", "count": 30000},
    {"solicitacao_status": "SOLICITAÇÃO / PENDENTE", "count": 15000}
  ]
}
```

---

### **🤖 Machine Learning**

#### **Informações do Modelo**
```http
GET /api/v1/ml/modelo/info
```
**Resposta**:
```json
{
  "status": "sucesso",
  "modelo": {
    "treinado": true,
    "algoritmo": "Random Forest Classifier",
    "parametros": {
      "n_estimators": 100,
      "max_depth": 10,
      "min_samples_split": 20,
      "min_samples_leaf": 10
    },
    "metricas": {
      "acuracia": 0.85,
      "precisao": 0.82,
      "recall": 0.78,
      "f1_score": 0.80,
      "total_treino": 40000,
      "total_teste": 10000
    },
    "feature_importance": {
      "features": ["risco_numerico", "tempo_espera_dias", "especialidade_codigo"],
      "importances": [0.45, 0.30, 0.25]
    }
  },
  "features": [
    "solicitacao_risco",
    "procedimento_especialidade",
    "paciente_faixa_etaria",
    "tempo_espera_dias",
    "status_critico"
  ]
}
```

#### **Predição ML Personalizada**
```http
POST /api/v1/ml/predicao
Content-Type: application/json

{
  "solicitacao_risco": "VERMELHO",
  "procedimento_especialidade": "Cardiologia",
  "paciente_faixa_etaria": "60-74",
  "solicitacao_status": "PENDENTE"
}
```
**Resposta**:
```json
{
  "status": "sucesso",
  "entrada": {
    "solicitacao_risco": "VERMELHO",
    "procedimento_especialidade": "Cardiologia",
    "paciente_faixa_etaria": "60-74"
  },
  "predicao": {
    "probabilidade_agravamento": 0.85,
    "predicao_agravamento": 1,
    "classificacao": "Alto Risco"
  }
}
```

---

### **🔧 Utilitários**

#### **Opções de Filtros**
```http
GET /api/v1/filtros/opcoes
```
**Resposta**:
```json
{
  "status": "sucesso",
  "filtros": {
    "riscos": ["AZUL", "VERDE", "AMARELO", "VERMELHO"],
    "especialidades": [
      "Cardiologia",
      "Neurologia",
      "Ortopedia",
      "Pediatria"
    ],
    "status": [
      "AGENDAMENTO / CONFIRMADO",
      "SOLICITAÇÃO / PENDENTE",
      "AGENDAMENTO / FALTA"
    ]
  }
}
```

#### **Status da API**
```http
GET /api/v1/status
```
**Resposta**:
```json
{
  "status": "OK",
  "versao": "1.0.0",
  "nome": "API REST - Gestão Inteligente de Vagas (GIV)",
  "total_registros": 50000,
  "timestamp": "2025-01-15T10:30:00",
  "modelo_ml_treinado": true,
  "cache_ativado": true
}
```

#### **Health Check**
```http
GET /health
```
**Resposta**:
```json
{
  "status": "healthy",
  "timestamp": "2025-01-15T10:30:00",
  "version": "1.0.0"
}
```

---

## 🎯 **CÓDIGOS DE STATUS HTTP**

| Código | Descrição |
|--------|-----------|
| `200` | Sucesso |
| `400` | Erro de validação |
| `401` | Não autorizado |
| `403` | Acesso negado |
| `404` | Não encontrado |
| `422` | Erro de validação de dados |
| `500` | Erro interno do servidor |

---

## 🔍 **EXEMPLOS DE USO**

### **1. Obter KPIs com Filtros**
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/dashboard/kpis?risco=VERMELHO&especialidade=Cardiologia" \
  -H "Authorization: Bearer SEU_TOKEN_JWT"
```

### **2. Fazer Predição ML**
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/ml/predicao" \
  -H "Authorization: Bearer SEU_TOKEN_JWT" \
  -H "Content-Type: application/json" \
  -d '{
    "solicitacao_risco": "VERMELHO",
    "procedimento_especialidade": "Cardiologia",
    "paciente_faixa_etaria": "60-74"
  }'
```

### **3. Listar Solicitações com Paginação**
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/solicitacoes?risco=AMARELO&limit=50&offset=100" \
  -H "Authorization: Bearer SEU_TOKEN_JWT"
```

### **4. Gerar Relatório Resumido**
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/relatorios/resumo" \
  -H "Authorization: Bearer SEU_TOKEN_JWT"
```

---

## 🚀 **PERFORMANCE E LIMITES**

### **Limites de Requisição**
- **Dados do Dashboard**: Máximo 10.000 registros por requisição
- **Solicitações**: Máximo 5.000 registros por requisição
- **Timeout**: 30 segundos por requisição
- **Rate Limiting**: 100 requisições por minuto por usuário

### **Cache**
- **Dados**: Cache automático após primeira carga
- **Duração**: Até reinicialização do servidor
- **Tamanho**: ~500MB em memória

### **Machine Learning**
- **Treinamento**: Automático na primeira predição
- **Performance**: ~85% de acurácia
- **Tempo de Predição**: < 1 segundo

---

## 🛠️ **CONFIGURAÇÃO AVANÇADA**

### **Variáveis de Ambiente**
```bash
# Configurações opcionais
export GIV_SECRET_KEY="sua-chave-secreta"
export GIV_ACCESS_TOKEN_EXPIRE=30
export GIV_HOST="0.0.0.0"
export GIV_PORT=8000
```

### **Configuração de Produção**
```python
# Para produção, usar:
uvicorn.run(
    app, 
    host="0.0.0.0", 
    port=8000,
    workers=4,
    log_level="warning"
)
```

---

## 📝 **LOGS E MONITORAMENTO**

### **Logs Disponíveis**
- **Inicialização**: Carregamento de dados e modelo ML
- **Requisições**: Endpoint, usuário, tempo de resposta
- **Erros**: Detalhes de erros com stack trace
- **ML**: Treinamento e predições

### **Métricas**
- **Uptime**: Tempo de funcionamento
- **Requisições**: Total por endpoint
- **Performance**: Tempo médio de resposta
- **ML**: Acurácia e métricas do modelo

---

## 🔧 **TROUBLESHOOTING**

### **Problemas Comuns**

#### **1. Erro 401 - Não Autorizado**
```json
{
  "detail": "Token inválido"
}
```
**Solução**: Verificar se o token JWT está correto e não expirado.

#### **2. Erro 500 - Erro Interno**
```json
{
  "detail": "Erro ao carregar dados: Arquivo não encontrado"
}
```
**Solução**: Verificar se os arquivos Parquet estão na pasta `db/`.

#### **3. Modelo ML Não Treinado**
```json
{
  "modelo_ml_treinado": false
}
```
**Solução**: Fazer uma requisição para `/api/v1/ml/predicao` para treinar automaticamente.

#### **4. Cache Vazio**
```json
{
  "cache_ativado": false
}
```
**Solução**: Reiniciar a API para recarregar o cache.

---

## 📚 **RECURSOS ADICIONAIS**

### **Documentação Interativa**
- **Swagger UI**: `/docs` - Interface completa para testar endpoints
- **ReDoc**: `/redoc` - Documentação alternativa
- **OpenAPI Schema**: `/openapi.json` - Schema completo da API

### **Integração com Frontend**
```javascript
// Exemplo de uso com JavaScript
const response = await fetch('/api/v1/dashboard/kpis', {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});
const data = await response.json();
```

### **Integração com Python**
```python
import requests

headers = {'Authorization': f'Bearer {token}'}
response = requests.get('http://127.0.0.1:8000/api/v1/dashboard/kpis', headers=headers)
data = response.json()
```

---

## 🎯 **ROADMAP**

### **Próximas Versões**
- **v1.1**: Cache Redis, Rate Limiting
- **v1.2**: Webhooks, Notificações
- **v1.3**: Exportação de dados (Excel, PDF)
- **v2.0**: Interface web completa

### **Funcionalidades Futuras**
- **Dashboard em Tempo Real**: WebSockets
- **Análises Avançadas**: Mais algoritmos ML
- **Relatórios Personalizados**: Construtor de relatórios
- **API GraphQL**: Alternativa ao REST

---

**Documentação gerada em**: Janeiro 2025  
**Versão da API**: 1.0.0  
**Contato**: Equipe de Desenvolvimento GIV

