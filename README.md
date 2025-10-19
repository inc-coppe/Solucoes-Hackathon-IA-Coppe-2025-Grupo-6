# 🏥 Gestão Inteligente de Vagas (GIV)

Sistema completo de **gestão hospitalar** com **API REST**, **Dashboard Web** e **Machine Learning** para predição de agravamentos de pacientes.

![Fluxograma_API_Hackathon](Fluxograma_API_Hackathon-2025-10-12-144504.png "Fluxograma API Hackathon")

## 📚 **DOCUMENTAÇÃO COMPLETA**

Toda a documentação está organizada na pasta **[`docs/`](./docs/README.md)**:

- 🔄 **Fluxogramas e Arquitetura**
- 📊 **Análises Comparativas** 
- 🗄️ **Documentação de Dados**
- 🚀 **Documentação da API GIV**
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
# API GIV Completa
pip install -r requirements_api_giv.txt

# Dashboard (alternativo)
pip install -r requirements_otimizado.txt

# API Básica (legado)
pip install -r requirements.txt
```

### **Bibliotecas Principais**
- **FastAPI** - Framework web moderno
- **Polars** - Processamento eficiente de dados
- **Plotly** - Gráficos interativos
- **Scikit-learn** - Machine Learning
- **PyJWT** - Autenticação JWT

---

## 🔐 **Configuração de Segurança**

**IMPORTANTE**: Configure as variáveis de ambiente antes de executar:

```bash
# Copie o arquivo de exemplo
cp config.env.example config.env

# Edite o arquivo config.env e configure suas chaves secretas
GIV_SECRET_KEY=sua-chave-secreta-forte-aqui
APP_SECRET_KEY=sua-chave-secreta-app-aqui
GIV_ACCESS_TOKEN_EXPIRE=30
```

**⚠️ NUNCA** commite arquivos `.env` ou `config.env` com chaves reais!

---

## 🚀 **Como Executar**

### **1. 🚀 API GIV Completa (Recomendado)**

```bash
# Executar diretamente
python api_giv_completa.py

# Ou usar o script de inicialização
INICIAR_API_GIV.bat
```

**Acesso:**
- **API**: http://127.0.0.1:8000
- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

### **2. 📊 Dashboard Web**

```bash
# Dashboard otimizado
python dashboard_final.py

# Ou usar o script
INICIAR_OTIMIZADO.bat
```

**Acesso:**
- **Dashboard**: http://127.0.0.1:8000

### **3. 🔧 API Básica (Legado)**

```bash
# API Flask básica
python app.py
```

**Acesso:**
- **API**: http://127.0.0.1:5000

---

## 📂 **Estrutura do Projeto**

```
📁 projeto-giv/
├── 📁 docs/                    # 📚 Documentação completa
│   ├── 📄 README.md           # Índice da documentação
│   ├── 📄 SEGURANCA.md        # Guia de segurança
│   └── 📄 *.md                # Documentação específica
├── 📁 db/                      # 🗄️ Dados Parquet
│   ├── 📄 *.parquet           # Arquivos de dados
│   └── 📄 DOCUMENTACAO_CAMPOS_TABELAS.md
├── 📁 static/                  # 🎨 Arquivos estáticos
├── 📄 api_giv_completa.py     # 🚀 API REST principal
├── 📄 dashboard_final.py      # 📊 Dashboard web
├── 📄 modelo_ml_saude.py      # 🤖 Modelo de ML
├── 📄 app.py                  # 🔧 API básica (legado)
├── 📄 config.env.example      # 🔐 Template de configuração
└── 📄 *.bat                   # 🚀 Scripts de inicialização
```

---

## 🔗 **Endpoints da API GIV**

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

### **1. 🔐 Login na API GIV**

```bash
curl -X POST "http://127.0.0.1:8000/auth/service" \
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
GIV_SECRET_KEY=sua-chave-secreta-forte
APP_SECRET_KEY=sua-chave-secreta-app
GIV_ACCESS_TOKEN_EXPIRE=30

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
python api_giv_completa.py --log-level debug
```

---

## 🧾 **Licença**

Este projeto é de uso interno da **Hackathon IA Coppe 2025** e destina-se a fins educacionais e de demonstração.

---

## 🎯 **Status do Projeto**

- ✅ **API REST Completa** - Implementada e funcionando
- ✅ **Dashboard Web** - Interface moderna com ML
- ✅ **Machine Learning** - Modelo treinado e funcional
- ✅ **Documentação** - Completa e organizada
- ✅ **Segurança** - Vulnerabilidades corrigidas
- ✅ **Git** - Repositório atualizado e sincronizado

**Versão**: 1.0.2  
**Última Atualização**: Outubro 2025