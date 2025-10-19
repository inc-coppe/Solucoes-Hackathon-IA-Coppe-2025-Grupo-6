# 🔄 Fluxograma - API REST GIV Completa

**Versão**: 1.0.2  
**Data**: Janeiro 2025  
**API**: Gestão Inteligente de Vagas (GIV)

---

## 🎯 **VISÃO GERAL DO FLUXO**

```
┌─────────────────────────────────────────────────────────────────┐
│                    API REST - GIV COMPLETA                      │
│                Gestão Inteligente de Vagas                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        INICIALIZAÇÃO                            │
│  • FastAPI App                                                  │
│  • Configuração JWT                                             │
│  • Modelo ML (Random Forest)                                    │
│  • Cache de Dados                                               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      CARREGAMENTO DE DADOS                      │
│  • Arquivos Parquet (db/*.parquet)                              │
│  • Join: Solicitação + Procedimento                             │
│  • Cache Inteligente                                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        ENDPOINTS DISPONÍVEIS                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔐 **FLUXO DE AUTENTICAÇÃO**

```
┌─────────────────┐    POST /auth/login    ┌─────────────────┐
│                 │ ─────────────────────► │                 │
│   CLIENTE       │                        │   API GIV       │
│                 │ ◄───────────────────── │                 │
└─────────────────┘    JWT Token (30min)   └─────────────────┘
         │                                           │
         │                                           ▼
         │                               ┌─────────────────┐
         │                               │                 │
         │                               │ VALIDAÇÃO JWT   │
         │                               │ • Verificar     │
         │                               │ • Decodificar   │
         │                               │ • Extrair User  │
         │                               │                 │
         │                               └─────────────────┘
         │                                           │
         ▼                                           ▼
┌─────────────────┐                         ┌─────────────────┐
│                 │                         │                 │
│ REQUISIÇÕES     │ ◄────────────────────── │ ENDPOINTS       │
│ AUTORIZADAS     │    Authorization:       │ PROTEGIDOS      │
│                 │    Bearer <token>       │                 │
└─────────────────┘                         └─────────────────┘
```

---

## 📊 **FLUXO DE DADOS E PROCESSAMENTO**

```
┌─────────────────────────────────────────────────────────────────┐
│                        ENTRADA DE DADOS                         │
│  • Filtros (risco, especialidade, status)                       │
│  • Parâmetros de paginação (limit, offset)                      │
│  • Dados para predição ML                                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      PROCESSAMENTO                              │
│  • Aplicar filtros                                              │
│  • Carregar dados do cache                                      │
│  • Executar consultas Polars                                    │
│  • Preparar features para ML                                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    MACHINE LEARNING                             │
│  • Treinar modelo (se necessário)                               │
│  • Fazer predições                                              │
│  • Calcular métricas                                            │
│  • Feature importance                                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FORMATAÇÃO E RESPOSTA                      │
│  • Formatar dados                                               │
│  • Aplicar paginação                                            │
│  • Gerar JSON response                                          │
│  • Incluir metadados                                            │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔗 **FLUXO DETALHADO POR CATEGORIA**

### **1. AUTENTICAÇÃO**
```
POST /auth/login
    │
    ▼
┌─────────────────┐
│ VALIDAR CREDS   │
│ • admin/admin123│
│ • tou/hackathon │
│ • api_user/api  │
│ • gestor/gestor │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ GERAR JWT       │
│ • 30 min exp    │
│ • HS256 alg     │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ RETURN TOKEN    │
└─────────────────┘
```

### **2. DASHBOARD E KPIs**
```
GET /api/v1/dashboard/kpis
    │
    ▼
┌─────────────────┐
│ VERIFICAR JWT   │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ APLICAR FILTROS │
│ • risco         │
│ • especialidade │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ CALCULAR KPIs   │
│ • total_solic   │
│ • taxa_conf     │
│ • risco_critico │
│ • sem_agend     │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ RETURN KPIs     │
└─────────────────┘
```

### **3. ANÁLISE PREDITIVA**
```
GET /api/v1/analise/predicao
    │
    ▼
┌─────────────────┐
│ VERIFICAR JWT   │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ FILTRAR SEM     │
│ AGENDAMENTO     │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ TREINAR MODELO  │
│ (se necessário) │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ FAZER PREDIÇÕES │
│ • Random Forest │
│ • Probabilidades│
│ • Agravamentos  │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│CALCULAR MÉTRICAS│
│ • Custos        │
│ • Internações   │
│ • Timeline      │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ RETURN PREDIÇÃO │
└─────────────────┘
```

### **4. CONSULTAS E FILTROS**
```
GET /api/v1/solicitacoes
    │
    ▼
┌─────────────────┐
│ VERIFICAR JWT   │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ APLICAR FILTROS │
│ • risco         │
│ • especialidade │
│ • status        │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ PAGINAÇÃO       │
│ • limit         │
│ • offset        │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ RETURN DADOS    │
└─────────────────┘
```

### **5. MACHINE LEARNING**
```
POST /api/v1/ml/predicao
    │
    ▼
┌─────────────────┐
│ VERIFICAR JWT   │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ VALIDAR DADOS   │
│ • risco         │
│ • especialidade │
│ • faixa_etaria  │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│PREPARAR FEATURES│
│ • risco_numerico│
│ • tempo_espera  │
│ • idade_aprox   │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ FAZER PREDIÇÃO  │
│ • prob_agrav    │
│ • classificação │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ RETURN RESULTADO│
└─────────────────┘
```

---

## 📈 **FLUXO DE DADOS COMPLETO**

```
┌─────────────────────────────────────────────────────────────────┐
│                        ARQUIVOS PARQUET                         │
│  • solicitacao-*.parquet (28 arquivos)                          │
│  • procedimento-*.parquet (1 arquivo)                           │
│  • marcacao-*.parquet (56 arquivos)                             │
│  • oferta_programada-*.parquet (23 arquivos)                    │
│  • profissional_historico-*.parquet (16 arquivos)               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      CARREGAMENTO INICIAL                       │
│  • glob.glob() para encontrar arquivos                          │
│  • pl.concat() para concatenar                                  │
│  • Join: solicitacao + procedimento                             │
│  • Cache em _dados_cache                                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      PROCESSAMENTO POR                          │
│                        ENDPOINT                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────┐ │
│  │   KPIs      │  │  PREDIÇÃO   │  │ CONSULTAS   │  │   ML    │ │
│  │             │  │             │  │             │  │         │ │
│  │ • Filtros   │  │ • ML Model  │  │ • Filtros   │  │• Train  │ │
│  │ • Cálculos  │  │ • Features  │  │ • Paginação │  │• Pred   │ │
│  │ • Métricas  │  │ • Agravam.  │  │ • Ordenação │  │• Metrics│ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      RESPOSTA JSON                              │
│  • status: "sucesso"                                            │
│  • dados: [...]                                                 │
│  • metadados: {total, filtros, paginação}                       │
│  • timestamp: ISO 8601                                          │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 **FLUXO DE ERROS E TRATAMENTO**

```
┌─────────────────────────────────────────────────────────────────┐
│                        TRATAMENTO DE ERROS                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────┐ │
│  │ 401 UNAUTH  │  │ 400 BAD REQ │  │404 NOT FOUND│  │ 500 ERR │ │
│  │             │  │             │  │             │  │         │ │
│  │ • Token     │  │ • Params    │  │ • Resource  │  │ • Server│ │
│  │   inválido  │  │   inválidos │  │   não exis. │  │   error │ │
│  │ • Expirado  │  │ • Dados     │  │ • File      │  │ • ML    │ │
│  │ • Ausente   │  │   inválidos │  │   not found │  │   error │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      RESPOSTA DE ERRO                           │
│  • HTTPException com código                                     │
│  • Mensagem detalhada                                           │
│  • Logs para debugging                                          │
│  • Headers apropriados                                          │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🚀 **FLUXO DE INICIALIZAÇÃO**

```
┌─────────────────────────────────────────────────────────────────┐
│                    INICIALIZAÇÃO DA API                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 1. CONFIGURAR FASTAPI                                           │
│    • title, description, version                                │
│    • docs_url="/docs"                                           │
│    • redoc_url="/redoc"                                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. CONFIGURAR JWT                                               │
│    • SECRET_KEY                                                 │
│    • ALGORITHM = "HS256"                                        │
│    • ACCESS_TOKEN_EXPIRE_MINUTES = 30                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. INICIALIZAR MODELO ML                                        │
│    • ModeloPredicaoAgravamento()                                │
│    • modelo_global.treinado = False                             │
│    • Configurar Random Forest                                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. CARREGAR DADOS                                               │
│    • carregar_dados()                                           │
│    • Cache inteligente                                          │
│    • Join de tabelas                                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. INICIAR SERVIDOR                                             │
│    • uvicorn.run()                                              │
│    • host="127.0.0.1"                                           │
│    • port=8000                                                  │
│    • log_level="info"                                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📊 **ENDPOINTS E FLUXOS**

### **ENDPOINTS PRINCIPAIS**

| Endpoint | Método | Fluxo | Autenticação |
|----------|--------|-------|--------------|
| `/` | GET | Página inicial | ❌ |
| `/auth/login` | POST | Login JWT | ❌ |
| `/api/v1/status` | GET | Status da API | ❌ |
| `/health` | GET | Health check | ❌ |
| `/api/v1/dashboard/kpis` | GET | KPIs dashboard | ✅ |
| `/api/v1/dashboard/dados` | GET | Dados dashboard | ✅ |
| `/api/v1/analise/predicao` | GET | Análise preditiva | ✅ |
| `/api/v1/solicitacoes` | GET | Listar solicitações | ✅ |
| `/api/v1/procedimentos` | GET | Listar procedimentos | ✅ |
| `/api/v1/relatorios/resumo` | GET | Relatório resumido | ✅ |
| `/api/v1/ml/modelo/info` | GET | Info modelo ML | ✅ |
| `/api/v1/ml/predicao` | POST | Predição ML | ✅ |
| `/api/v1/filtros/opcoes` | GET | Opções filtros | ✅ |

### **FLUXO DE AUTENTICAÇÃO POR ENDPOINT**

```
┌─────────────────────────────────────────────────────────────────┐
│                    ENDPOINTS PÚBLICOS                           │
│  • GET /                                                        │
│  • POST /auth/login                                             │
│  • GET /api/v1/status                                           │
│  • GET /health                                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ENDPOINTS PROTEGIDOS                         │
│  • Verificar JWT Token                                          │
│  • Extrair username                                             │
│  • Validar expiração                                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────────────┐
│  ┌─────────────┐  ┌───────────────┐  ┌─────────────┐  ┌──────────┐ │
│  │ DASHBOARD   │  │ CONSULTAS     │  │    ML       │  │ RELAT.   │ │
│  │             │  │               │  │             │  │          │ │
│  │ • KPIs      │  │• Solicitações │  │ • Predição  │  │ • Resumo │ │
│  │ • Dados     │  │• Procedimentos│  │ • Modelo    │  │ • Stats  │ │
│  │ • Predição  │  │• Filtros      │  │ • Métricas  │  │ • Análise│ │
│  └─────────────┘  └───────────────┘  └─────────────┘  └──────────┘ │
└────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 **RESUMO DO FLUXO**

### **CARACTERÍSTICAS PRINCIPAIS**
- ✅ **13 Endpoints** organizados por categoria
- ✅ **Autenticação JWT** com 4 usuários
- ✅ **Machine Learning** integrado (Random Forest)
- ✅ **Cache inteligente** para performance
- ✅ **Filtros avançados** e paginação
- ✅ **Tratamento de erros** robusto
- ✅ **Documentação automática** (Swagger UI)

### **FLUXO GERAL**
1. **Inicialização** → Configuração e carregamento de dados
2. **Autenticação** → JWT token para endpoints protegidos
3. **Processamento** → Filtros, consultas e ML
4. **Resposta** → JSON estruturado com metadados

### **PERFORMANCE**
- **Cache**: Dados carregados uma vez
- **ML**: Treinamento automático na primeira predição
- **Polars**: Processamento eficiente de dados
- **Async**: Suporte a operações assíncronas

---

**Fluxograma criado em**: Janeiro 2025  
**Versão da API**: 1.0.2  
**Status**: ✅ COMPLETO

