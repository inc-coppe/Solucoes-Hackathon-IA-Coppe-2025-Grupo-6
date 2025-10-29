# 🏥 Gestão Inteligente de Vagas (GIV-Saúde)

Sistema completo de **gestão hospitalar** com **API REST**, **Dashboard Web** e **Machine Learning** para predição de agravamentos de pacientes.

![Fluxograma_API_Hackathon](Fluxograma_API_Hackathon-2025-10-12-144504.png "Fluxograma API Hackathon")

## 📚 **DOCUMENTAÇÃO COMPLETA**

Toda a documentação está organizada na pasta **[`docs/`](./docs/README.md)**:

- 🔄 **Fluxogramas e Arquitetura**
- 📊 **Análises Comparativas** 
- 🗄️ **Documentação de Dados**
- 🚀 **Documentação da API GIV-Saúde**
- 🔐 **Segurança**

**👉 [ACESSE A DOCUMENTAÇÃO COMPLETA](./docs/README.md)**

---

## 🎯 **FUNCIONALIDADES PRINCIPAIS**

### 🚀 **API REST Completa**
- **FastAPI** com 13 endpoints especializados
- **Autenticação JWT** com 4 usuários
- **Machine Learning** integrado (Random Forest)
- **Cache inteligente** para performance
- **Documentação automática** (Swagger UI)

### 📊 **Dashboard Web**
- **Interface moderna** com formatação brasileira
- **Gráficos interativos** com Plotly
- **KPIs em tempo real**
- **Filtros avançados**

### 🤖 **Machine Learning**
- **Predição de agravamentos** de pacientes
- **Modelo Random Forest** treinado
- **Métricas de performance**
- **Feature importance**

---

## 🧩 **Pré-requisitos**

### **Python 3.8+**
```bash
python --version
```

### **Dependências Principais**
```bash
# API GIV-Saúde Completa (FastAPI)
pip install -r requirements_api_GIV-Saúde.txt

# Dashboard Web (FastAPI)
pip install -r requirements_otimizado.txt

# API Básica (Flask - legado)
pip install -r requirements.txt
```

### **Bibliotecas Principais**
- **FastAPI** - Framework web moderno (API GIV-Saúde e Dashboard)
- **Polars** - Processamento eficiente de dados Parquet
- **Plotly** - Gráficos interativos
- **Scikit-learn** - Machine Learning (Random Forest)
- **PyJWT** - Autenticação JWT
- **Uvicorn** - Servidor ASGI para FastAPI

---

## 🔐 **Configuração de Segurança**

**IMPORTANTE**: Configure as variáveis de ambiente antes de executar:

```bash
# Copie o arquivo de exemplo
cp config.env.example config.env

# Edite o arquivo config.env e configure suas chaves secretas
GIV-Saúde_SECRET_KEY=sua-chave-secreta-forte-aqui
APP_SECRET_KEY=sua-chave-secreta-app-aqui
GIV-Saúde_ACCESS_TOKEN_EXPIRE=30
```

**⚠️ NUNCA** commite arquivos `.env` ou `config.env` com chaves reais!

---

## 🚀 **Como Executar**

### **1. 🚀 API GIV-Saúde Completa (FastAPI - Recomendado)**

```bash
# Executar diretamente
python api_GIV-Saúde_completa.py

# Ou usar o script de inicialização
INICIAR_API_GIV-Saúde.bat
```

**Tecnologia:** FastAPI + Uvicorn  
**Acesso:**
- **API**: http://127.0.0.1:8000
- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

### **2. 📊 Dashboard Web (FastAPI)**

```bash
# Dashboard otimizado
python dashboard_final.py

# Ou usar o script
INICIAR_OTIMIZADO.bat
```

**Tecnologia:** FastAPI + Uvicorn  
**Acesso:**
- **Dashboard**: http://127.0.0.1:8000

### **3. 🔧 API Básica (Flask - Legado)**

```bash
# API Flask básica (versão antiga)
python app.py
```

**Tecnologia:** Flask  
**Acesso:**
- **API**: http://127.0.0.1:5000

---

## 📂 **Estrutura do Projeto**

```
📁 projeto-GIV-Saúde/
├── 📁 docs/                    # 📚 Documentação completa
│   ├── 📄 README.md           # Índice da documentação
│   ├── 📄 SEGURANCA.md        # Guia de segurança
│   └── 📄 *.md                # Documentação específica
├── 📁 db/                      # 🗄️ Dados Parquet
│   ├── 📄 *.parquet           # Arquivos de dados
│   └── 📄 DOCUMENTACAO_CAMPOS_TABELAS.md
├── 📁 static/                  # 🎨 Arquivos estáticos
├── 📄 api_GIV-Saúde_completa.py     # 🚀 API REST FastAPI (principal)
├── 📄 dashboard_final.py      # 📊 Dashboard FastAPI
├── 📄 modelo_ml_saude.py      # 🤖 Modelo de ML
├── 📄 app.py                  # 🔧 API Flask (legado)
├── 📄 config.env.example      # 🔐 Template de configuração
└── 📄 *.bat                   # 🚀 Scripts de inicialização
```

---

## 🔗 **Endpoints da API GIV-Saúde**

### **🔐 Autenticação**
- `POST /auth/login` - Login e token JWT

### **📊 Dashboard**
- `GET /api/v1/dashboard/kpis` - KPIs do dashboard
- `GET /api/v1/dashboard/dados` - Dados do dashboard
- `GET /api/v1/analise/predicao` - Análise preditiva

### **🔍 Consultas**
- `GET /api/v1/solicitacoes` - Listar solicitações
- `GET /api/v1/procedimentos` - Listar procedimentos
- `GET /api/v1/relatorios/resumo` - Relatório resumido

### **🤖 Machine Learning**
- `GET /api/v1/ml/modelo/info` - Informações do modelo
- `POST /api/v1/ml/predicao` - Fazer predição

### **⚙️ Utilitários**
- `GET /api/v1/status` - Status da API
- `GET /health` - Health check
- `GET /api/v1/filtros/opcoes` - Opções de filtros

---

## 🧪 **Exemplos de Uso**

### **1. 🔐 Login na API GIV-Saúde (FastAPI)**

```bash
curl -X POST "http://127.0.0.1:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

### **2. 📊 Obter KPIs**

```bash
curl -H "Authorization: Bearer SEU_TOKEN_JWT" \
  "http://127.0.0.1:8000/api/v1/dashboard/kpis"
```

### **3. 🤖 Fazer Predição ML**

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/ml/predicao" \
  -H "Authorization: Bearer SEU_TOKEN_JWT" \
  -H "Content-Type: application/json" \
  -d '{"risco": "VERMELHO", "especialidade": "CARDIOLOGIA", "faixa_etaria": "ADULTO"}'
```

---

## 👥 **Usuários Disponíveis**

| Usuário | Senha | Descrição |
|---------|-------|-----------|
| `admin` | `admin123` | Administrador |
| `tou` | `hackathon2025` | Usuário TOU |
| `api_user` | `api123` | Usuário API |
| `gestor` | `gestor456` | Gestor |

---

## 📊 **Dados do Sistema**

### **📁 Arquivos Parquet (130+ arquivos)**
- **Solicitações**: 28 arquivos
- **Procedimentos**: 1 arquivo
- **Marcações**: 56 arquivos
- **Ofertas Programadas**: 23 arquivos
- **Histórico Profissional**: 16 arquivos

### **📈 Métricas do Sistema**
- **Total de Registros**: Milhares de solicitações
- **Especialidades**: 50+ especialidades médicas
- **Tipos de Risco**: VERMELHO, AMARELO, VERDE, AZUL
- **Modelo ML**: 85%+ de acurácia

---

## 🔧 **Configurações Avançadas**

### **Variáveis de Ambiente**
```bash
# Configurações de segurança
GIV-Saúde_SECRET_KEY=sua-chave-secreta-forte
APP_SECRET_KEY=sua-chave-secreta-app
GIV-Saúde_ACCESS_TOKEN_EXPIRE=30

# Configurações de ambiente
ENVIRONMENT=development
LOG_LEVEL=INFO
```

### **Cache e Performance**
- **Cache inteligente** para dados Parquet
- **Processamento otimizado** com Polars
- **ML treinamento automático** na primeira predição
- **Suporte assíncrono** para operações

---

## 🆘 **Suporte e Troubleshooting**

### **Problemas Comuns**

1. **Erro de autenticação**: Verificar token JWT válido
2. **Dados não carregam**: Verificar arquivos Parquet na pasta `db/`
3. **ML não funciona**: Verificar dependências do scikit-learn
4. **Porta ocupada**: Mudar porta no código ou finalizar processo

### **Logs e Debug**
```bash
# Executar com logs detalhados
python api_GIV-Saúde_completa.py --log-level debug
```

---

## 🧾 **Licença**

Este projeto é de uso interno da **Hackathon IA Coppe 2025** e destina-se a fins educacionais e de demonstração.

---

## 🎯 **Status do Projeto**

- ✅ **API REST FastAPI** - Implementada e funcionando (13 endpoints)
- ✅ **Dashboard FastAPI** - Interface moderna com ML integrado
- ✅ **Machine Learning** - Random Forest treinado e funcional
- ✅ **Documentação** - Completa e organizada na pasta `docs/`
- ✅ **Segurança** - Vulnerabilidades corrigidas (GitGuardian)
- ✅ **Git** - Repositório atualizado e sincronizado
- ✅ **Flask Legado** - API básica mantida para compatibilidade

### **Tecnologias Principais:**
- **FastAPI** - Framework web moderno (API principal e Dashboard)
- **Flask** - Framework legado (API básica)
- **Polars** - Processamento de dados Parquet
- **Scikit-learn** - Machine Learning
- **Uvicorn** - Servidor ASGI para FastAPI

**Versão**: 1.0.2  
**Última Atualização**: Janeiro 2025
