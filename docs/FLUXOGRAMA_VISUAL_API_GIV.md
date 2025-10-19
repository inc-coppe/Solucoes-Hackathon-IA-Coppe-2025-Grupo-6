# 🎨 Fluxograma Visual - API GIV Completa

**Versão**: 1.0.2  
**Data**: Janeiro 2025

---

## 🔄 **FLUXO PRINCIPAL**

```
                    ┌─────────────────────────────────┐
                    │        CLIENTE/FRONTEND         │
                    └─────────────────────────────────┘
                                    │
                                    ▼
                    ┌─────────────────────────────────┐
                    │      API REST GIV COMPLETA      │
                    │   FastAPI + Machine Learning    │
                    └─────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
        ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
        │  AUTENTICAÇÃO   │ │   DASHBOARD     │ │   MACHINE       │
        │                 │ │                 │ │   LEARNING      │
        │ POST /auth/login│ │ GET /kpis       │ │ POST /ml/pred   │
        │ JWT Token       │ │ GET /dados      │ │ Random Forest   │
        └─────────────────┘ └─────────────────┘ └─────────────────┘
                                    │
                                    ▼
                    ┌─────────────────────────────────┐
                    │        DADOS PARQUET            │
                    │  • Solicitacao (28 arquivos)   │
                    │  • Procedimento (1 arquivo)    │
                    │  • Marcacao (56 arquivos)      │
                    │  • Oferta (23 arquivos)        │
                    └─────────────────────────────────┘
```

---

## 🔐 **FLUXO DE AUTENTICAÇÃO**

```
┌─────────────┐    POST /auth/login    ┌─────────────┐
│   CLIENTE   │ ──────────────────────► │   API GIV   │
└─────────────┘                         └─────────────┘
        │                                       │
        │                                       ▼
        │                               ┌─────────────┐
        │                               │ VALIDAR     │
        │                               │ CREDENCIAIS │
        │                               └─────────────┘
        │                                       │
        │                                       ▼
        │                               ┌─────────────┐
        │                               │ GERAR JWT   │
        │                               │ (30 min)    │
        │                               └─────────────┘
        │                                       │
        │                                       ▼
        │                               ┌─────────────┐
        │                               │ RETURN      │
        │                               │ TOKEN       │
        │                               └─────────────┘
        │                                       │
        │                                       ▼
        │                               ┌─────────────┐
        │                               │ ENDPOINTS   │
        │                               │ PROTEGIDOS  │
        │                               └─────────────┘
        │                                       │
        ▼                                       ▼
┌─────────────┐                         ┌─────────────┐
│ REQUISIÇÕES │ ◄─────────────────────── │ AUTHORIZATION│
│ COM TOKEN   │    Bearer <token>       │ HEADER      │
└─────────────┘                         └─────────────┘
```

---

## 📊 **FLUXO DE DADOS**

```
┌─────────────────────────────────────────────────────────────┐
│                    ARQUIVOS PARQUET                         │
│  solicitacao-*.parquet  │  procedimento-*.parquet          │
│  marcacao-*.parquet     │  oferta_programada-*.parquet     │
│  profissional_historico-*.parquet                           │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                  CARREGAMENTO INICIAL                      │
│  • glob.glob() - encontrar arquivos                        │
│  • pl.concat() - concatenar dados                          │
│  • join() - unir tabelas                                   │
│  • cache - armazenar em memória                            │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                  PROCESSAMENTO POR ENDPOINT                │
└─────────────────────────────────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        ▼                       ▼                       ▼
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│   DASHBOARD │         │ CONSULTAS   │         │     ML      │
│             │         │             │         │             │
│ • KPIs      │         │ • Filtros   │         │ • Features  │
│ • Métricas  │         │ • Paginação │         │ • Treino    │
│ • Análises  │         │ • Ordenação │         │ • Predição  │
└─────────────┘         └─────────────┘         └─────────────┘
        │                       │                       │
        └───────────────────────┼───────────────────────┘
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                    RESPOSTA JSON                            │
│  • status: "sucesso"                                       │
│  • dados: [...]                                            │
│  • metadados: {total, filtros, paginação}                  │
│  • timestamp: ISO 8601                                     │
└─────────────────────────────────────────────────────────────┘
```

---

## 🤖 **FLUXO DE MACHINE LEARNING**

```
┌─────────────────────────────────────────────────────────────┐
│                   DADOS DE ENTRADA                         │
│  • solicitation_risco                                      │
│  • procedimento_especialidade                              │
│  • paciente_faixa_etaria                                   │
│  • data_solicitacao                                        │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                 FEATURE ENGINEERING                        │
│  • risco_numerico (VERMELHO=4, AMARELO=3, etc.)           │
│  • tempo_espera_dias                                       │
│  • idade_aproximada                                        │
│  • especialidade_codigo                                    │
│  • status_critico                                          │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                   TREINAMENTO DO MODELO                    │
│  • Random Forest Classifier                                │
│  • 100 árvores de decisão                                  │
│  • Split treino/teste (80/20)                              │
│  • Métricas: acurácia, precisão, recall, F1-score         │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                     PREDIÇÕES                              │
│  • Probabilidade de agravamento                            │
│  • Classificação (Alto/Médio/Baixo Risco)                 │
│  • Projeções temporais (30/60/90 dias)                    │
│  • Estimativas de custo                                    │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 **FLUXO DE ENDPOINTS**

```
┌─────────────────────────────────────────────────────────────┐
│                    ENDPOINTS PÚBLICOS                      │
│  GET /                - Página inicial                     │
│  POST /auth/login     - Login JWT                          │
│  GET /api/v1/status   - Status da API                      │
│  GET /health          - Health check                       │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                   ENDPOINTS PROTEGIDOS                     │
│  (Requerem JWT Token)                                      │
└─────────────────────────────────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        ▼                       ▼                       ▼
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│ DASHBOARD   │         │ CONSULTAS   │         │     ML      │
│             │         │             │         │             │
│ /kpis       │         │ /solicitacoes│         │ /modelo/info│
│ /dados      │         │ /procedimentos│         │ /predicao   │
│ /predicao   │         │ /relatorios │         │ /filtros    │
└─────────────┘         └─────────────┘         └─────────────┘
```

---

## ⚡ **FLUXO DE PERFORMANCE**

```
┌─────────────────────────────────────────────────────────────┐
│                    CACHE INTELIGENTE                       │
│  • _dados_cache - dados em memória                         │
│  • Carregamento único na inicialização                     │
│  • Reutilização em todas as requisições                    │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                 PROCESSAMENTO OTIMIZADO                    │
│  • Polars - processamento eficiente                        │
│  • Filtros aplicados antes do processamento                │
│  • Paginação para controlar volume                         │
│  • Join otimizado entre tabelas                            │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                    RESPOSTA RÁPIDA                         │
│  • JSON estruturado                                        │
│  • Metadados incluídos                                     │
│  • Timestamp para cache                                    │
│  • Status codes apropriados                                │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 **FLUXO DE INICIALIZAÇÃO**

```
┌─────────────────────────────────────────────────────────────┐
│                    INICIALIZAÇÃO DA API                    │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│ 1. CONFIGURAR FASTAPI                                       │
│    • title: "API REST - Gestão Inteligente de Vagas"      │
│    • version: "1.0.2"                                      │
│    • docs_url: "/docs"                                     │
│    • redoc_url: "/redoc"                                   │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. CONFIGURAR JWT                                           │
│    • SECRET_KEY: "chave-secreta-giv-api-2025"              │
│    • ALGORITHM: "HS256"                                     │
│    • EXPIRE: 30 minutos                                     │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. INICIALIZAR MODELO ML                                    │
│    • ModeloPredicaoAgravamento()                            │
│    • Random Forest Classifier                               │
│    • modelo_global.treinado = False                         │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. CARREGAR DADOS                                           │
│    • carregar_dados()                                       │
│    • Cache em _dados_cache                                  │
│    • Join de tabelas                                        │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. INICIAR SERVIDOR                                         │
│    • uvicorn.run()                                          │
│    • host: "127.0.0.1"                                      │
│    • port: 8000                                             │
│    • log_level: "info"                                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 📈 **RESUMO DO FLUXO**

### **CARACTERÍSTICAS PRINCIPAIS**
- ✅ **13 Endpoints** organizados
- ✅ **JWT Authentication** 
- ✅ **Machine Learning** integrado
- ✅ **Cache inteligente**
- ✅ **Filtros avançados**
- ✅ **Documentação automática**

### **FLUXO GERAL**
1. **Inicialização** → Configuração e dados
2. **Autenticação** → JWT para endpoints protegidos  
3. **Processamento** → Filtros, consultas e ML
4. **Resposta** → JSON estruturado

### **PERFORMANCE**
- **Cache**: Dados carregados uma vez
- **ML**: Treinamento automático
- **Polars**: Processamento eficiente
- **Async**: Operações assíncronas

---

**Fluxograma Visual criado em**: Janeiro 2025  
**Versão da API**: 1.0.2  
**Status**: ✅ COMPLETO

