#!/usr/bin/env python3
"""
API REST Completa - Gestão Inteligente de Vagas (GIV-Saúde)
====================================================

API REST completa baseada no dashboard_final.py com todas as funcionalidades:
- Autenticação JWT
- Carregamento de dados com cache
- Machine Learning para predições
- Endpoints para dashboard, KPIs, relatórios
- Análises preditivas
- Filtros e consultas avançadas

Autor: Sistema GIV
Versão: 1.0.2
Data: Janeiro 2025
"""

import polars as pl
import plotly.graph_objects as go
import plotly.express as px
from fastapi import FastAPI, Query, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional, Dict, Any
import glob
from datetime import datetime, timedelta
try:
    import jwt
except ImportError:
    # Fallback para PyJWT
    import PyJWT as jwt
import json
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import warnings
warnings.filterwarnings('ignore')

# ===== CONFIGURAÇÃO DA APLICAÇÃO =====
app = FastAPI(
    title="API REST - Gestão Inteligente de Vagas (GIV-Saúde)",
    description="API completa para gestão de vagas hospitalares com Machine Learning",
    version="1.0.2",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurações
import os
SECRET_KEY = os.getenv("GIV_SECRET_KEY", "chave-secreta-padrao-dev")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("GIV_ACCESS_TOKEN_EXPIRE", "30"))

# Usuários válidos
USUARIOS_VALIDOS = {
    "admin": "admin123",
    "tou": "hackathon2025",
    "api_user": "api123",
    "gestor": "gestor456"
}

# ===== MODELO DE MACHINE LEARNING =====
class ModeloPredicaoAgravamento:
    """Modelo de ML integrado para predição de agravamentos"""
    
    def __init__(self):
        self.modelo = None
        self.encoders = {}
        self.feature_importance = None
        self.metricas = {}
        self.treinado = False
        
    def preparar_features(self, df):
        """Feature Engineering otimizado"""
        df_features = df.clone()
        
        # Feature 1: Risco
        if 'solicitacao_risco' in df_features.columns:
            df_features = df_features.with_columns(
                pl.col('solicitacao_risco').fill_null("DESCONHECIDO")
            )
            risco_map = {'VERMELHO': 4, 'AMARELO': 3, 'VERDE': 2, 'AZUL': 1, 'DESCONHECIDO': 0}
            df_features = df_features.with_columns(
                pl.col('solicitacao_risco').replace(risco_map, default=0).alias('risco_numerico')
            )
        
        # Feature 2: Tempo de espera
        if 'data_solicitacao' in df_features.columns:
            hoje = datetime.now()
            df_features = df_features.with_columns(
                (hoje - pl.col('data_solicitacao')).dt.total_seconds() / 86400
                .alias('tempo_espera_dias')
            )
        else:
            np.random.seed(42)
            df_features = df_features.with_columns(
                pl.lit(np.random.randint(1, 120, len(df_features))).alias('tempo_espera_dias')
            )
        
        # Feature 3: Faixa Etária
        if 'paciente_faixa_etaria' in df_features.columns:
            df_features = df_features.with_columns(
                pl.col('paciente_faixa_etaria').str.extract(r'(\d+)', 1)
                .cast(pl.Int32, strict=False)
                .fill_null(40)
                .alias('idade_aproximada')
            )
        else:
            df_features = df_features.with_columns(pl.lit(40).alias('idade_aproximada'))
        
        # Feature 4: Especialidade
        if 'procedimento_especialidade' in df_features.columns:
            df_features = df_features.with_columns(
                pl.col('procedimento_especialidade').fill_null("DESCONHECIDA")
            )
            especialidades_unicas = df_features['procedimento_especialidade'].unique().to_list()
            esp_map = {esp: idx for idx, esp in enumerate(especialidades_unicas)}
            df_features = df_features.with_columns(
                pl.col('procedimento_especialidade').replace(esp_map).alias('especialidade_codigo')
            )
            self.encoders['especialidade'] = esp_map
        
        # Feature 5: Status crítico
        if 'solicitacao_status' in df_features.columns:
            df_features = df_features.with_columns(
                pl.col('solicitacao_status')
                .str.contains('CRITICO|URGENTE|GRAVE')
                .fill_null(False)
                .cast(pl.Int32)
                .alias('status_critico')
            )
        else:
            df_features = df_features.with_columns(pl.lit(0).alias('status_critico'))
        
        return df_features
    
    def criar_target(self, df):
        """Criar variável target baseada em regras de negócio"""
        df_target = df.clone()
        np.random.seed(42)
        
        prob_agravamento = []
        for i in range(len(df_target)):
            row = df_target.row(i, named=True)
            risco = row.get('solicitacao_risco', 'AZUL')
            tempo = row.get('tempo_espera_dias', 0)
            
            if risco == 'VERMELHO':
                prob = 0.7 + (tempo / 100) * 0.2
            elif risco == 'AMARELO':
                prob = 0.4 + (tempo / 150) * 0.2
            elif risco == 'VERDE':
                prob = 0.15 + (tempo / 200) * 0.1
            elif risco == 'AZUL':
                prob = 0.05 + (tempo / 250) * 0.05
            else:
                prob = 0.1 + (tempo / 300) * 0.05
            
            prob = min(prob + np.random.normal(0, 0.1), 1.0)
            prob = max(prob, 0.0)
            agravou = 1 if np.random.random() < prob else 0
            prob_agravamento.append(agravou)
        
        df_target = df_target.with_columns(
            pl.Series('agravamento', prob_agravamento)
        )
        return df_target
    
    def treinar(self, df):
        """Treinar modelo de ML"""
        print("🤖 INICIANDO TREINAMENTO DO MODELO DE ML")
        
        # Preparar features
        df_prep = self.preparar_features(df)
        df_prep = self.criar_target(df_prep)
        
        feature_cols = ['risco_numerico', 'tempo_espera_dias', 'idade_aproximada', 
                       'especialidade_codigo', 'status_critico']
        feature_cols_existentes = [col for col in feature_cols if col in df_prep.columns]
        
        X = df_prep.select(feature_cols_existentes).to_numpy()
        y = df_prep['agravamento'].to_numpy()
        
        # Split treino/teste
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Treinamento
        self.modelo = RandomForestClassifier(
            n_estimators=100, max_depth=10, min_samples_split=20,
            min_samples_leaf=10, random_state=42, n_jobs=-1
        )
        
        self.modelo.fit(X_train, y_train)
        
        # Avaliação
        y_pred = self.modelo.predict(X_test)
        y_pred_proba = self.modelo.predict_proba(X_test)[:, 1]
        
        acuracia = accuracy_score(y_test, y_pred)
        precisao = precision_score(y_test, y_pred, zero_division=0)
        recall = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        
        self.metricas = {
            'acuracia': acuracia, 'precisao': precisao, 'recall': recall,
            'f1_score': f1, 'total_treino': len(X_train), 'total_teste': len(X_test)
        }
        
        self.feature_importance = {
            'features': feature_cols_existentes,
            'importances': self.modelo.feature_importances_.tolist()
        }
        
        self.treinado = True
        print("✅ MODELO TREINADO COM SUCESSO!")
        
        return self.metricas
    
    def predizer_agravamentos(self, df_sem_agendamento):
        """Prediz probabilidade de agravamento"""
        if not self.treinado:
            self.treinar(df_sem_agendamento)
        
        df_pred = self.preparar_features(df_sem_agendamento)
        feature_cols = ['risco_numerico', 'tempo_espera_dias', 'idade_aproximada', 
                       'especialidade_codigo', 'status_critico']
        feature_cols_existentes = [col for col in feature_cols if col in df_pred.columns]
        
        X = df_pred.select(feature_cols_existentes).to_numpy()
        probabilidades = self.modelo.predict_proba(X)[:, 1]
        predicoes = self.modelo.predict(X)
        
        df_pred = df_pred.with_columns([
            pl.Series('probabilidade_agravamento', probabilidades),
            pl.Series('predicao_agravamento', predicoes)
        ])
        
        return df_pred
    
    def calcular_metricas_predicao(self, df_predicoes):
        """Calcula métricas de predição"""
        total = len(df_predicoes)
        
        alto_risco = df_predicoes.filter(pl.col('probabilidade_agravamento') > 0.7).height
        medio_risco = df_predicoes.filter(
            (pl.col('probabilidade_agravamento') > 0.4) & 
            (pl.col('probabilidade_agravamento') <= 0.7)
        ).height
        baixo_risco = df_predicoes.filter(pl.col('probabilidade_agravamento') <= 0.4).height
        
        agravamentos_30_dias = int(alto_risco * 0.9)
        agravamentos_60_dias = int(medio_risco * 0.5)
        agravamentos_90_dias = int(baixo_risco * 0.1)
        
        custo_unitario = 5000
        custo_30_dias = agravamentos_30_dias * custo_unitario
        custo_total = (agravamentos_30_dias + agravamentos_60_dias + agravamentos_90_dias) * custo_unitario
        
        internacoes = int((agravamentos_30_dias + agravamentos_60_dias + agravamentos_90_dias) * 0.30)
        
        df_esp = df_predicoes.group_by('procedimento_especialidade').agg([
            pl.count().alias('total'),
            pl.col('probabilidade_agravamento').mean().alias('prob_media'),
            (pl.col('probabilidade_agravamento') > 0.7).sum().alias('alto_risco_count')
        ]).sort('prob_media', descending=True).head(10)
        
        especialidades_criticas = df_esp.to_dicts() if len(df_esp) > 0 else []
        
        return {
            'total_sem_agendamento': total,
            'alto_risco_ml': alto_risco,
            'medio_risco_ml': medio_risco,
            'baixo_risco_ml': baixo_risco,
            'agravamento_30_dias': agravamentos_30_dias,
            'agravamento_60_dias': agravamentos_60_dias,
            'agravamento_90_dias': agravamentos_90_dias,
            'custo_estimado_30_dias': custo_30_dias,
            'custo_estimado_total': custo_total,
            'internacoes_projetadas': internacoes,
            'especialidades_criticas_ml': especialidades_criticas,
            'probabilidade_media': df_predicoes['probabilidade_agravamento'].mean(),
            'modelo_metricas': self.metricas
        }

# ===== INSTÂNCIAS GLOBAIS =====
modelo_global = ModeloPredicaoAgravamento()
_dados_cache = None
security = HTTPBearer()

# ===== FUNÇÕES UTILITÁRIAS =====
def carregar_dados():
    """Carrega os dados da pasta db com cache"""
    global _dados_cache
    
    if _dados_cache is not None:
        return _dados_cache
    
    try:
        print("Carregando dados da pasta db...")
        
        # Carregar solicitações
        solicitacao_files = glob.glob("db/solicitacao-*.parquet")
        if solicitacao_files:
            df_solicitacao = pl.concat([pl.read_parquet(f) for f in solicitacao_files])
            print(f"OK: {len(solicitacao_files)} arquivos de solicitacao carregados")
        else:
            raise FileNotFoundError("Arquivos de solicitacao nao encontrados")
        
        # Carregar procedimentos
        procedimento_files = glob.glob("db/procedimento-*.parquet")
        if procedimento_files:
            df_procedimento = pl.concat([pl.read_parquet(f) for f in procedimento_files])
            print(f"OK: {len(procedimento_files)} arquivo(s) de procedimento carregados")
            
            # Join
            df_completo = df_solicitacao.join(
                df_procedimento, on="procedimento_sisreg_id", how="left"
            )
        else:
            df_completo = df_solicitacao
        
        print(f"OK: Total: {len(df_completo):,} registros")
        
        _dados_cache = df_completo
        return df_completo
        
    except Exception as e:
        print(f"ERRO ao carregar dados: {e}")
        raise

def criar_token_jwt(username: str) -> str:
    """Cria token JWT para autenticação"""
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": username, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verificar_token_jwt(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verifica token JWT"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return username
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )

def analisar_predicao_sem_agendamento(df_sem_agendamento):
    """Análise preditiva do impacto de não agendar pacientes"""
    if df_sem_agendamento.is_empty():
        return None
    
    try:
        if not modelo_global.treinado:
            modelo_global.treinar(df_sem_agendamento)
        
        df_predicoes = modelo_global.predizer_agravamentos(df_sem_agendamento)
        metricas_ml = modelo_global.calcular_metricas_predicao(df_predicoes)
        
        metricas_ml["usa_ml"] = True
        metricas_ml["algoritmo"] = "Random Forest Classifier"
        metricas_ml["num_arvores"] = 100
        
        return metricas_ml
        
    except Exception as e:
        print(f"Erro no ML: {e}")
        # Fallback simples
        total = len(df_sem_agendamento)
        vermelhos = df_sem_agendamento.filter(pl.col("solicitacao_risco") == "VERMELHO").height
        amarelos = df_sem_agendamento.filter(pl.col("solicitacao_risco") == "AMARELO").height
        
        agravamento_30_dias = int(vermelhos * 0.8 + amarelos * 0.3)
        agravamento_60_dias = int(vermelhos * 0.2 + amarelos * 0.4)
        agravamento_90_dias = int(amarelos * 0.2)
        
        return {
            'total_sem_agendamento': total,
            'agravamento_30_dias': agravamento_30_dias,
            'agravamento_60_dias': agravamento_60_dias,
            'agravamento_90_dias': agravamento_90_dias,
            'custo_estimado_30_dias': agravamento_30_dias * 5000,
            'custo_estimado_total': (agravamento_30_dias + agravamento_60_dias + agravamento_90_dias) * 5000,
            'internacoes_projetadas': int((agravamento_30_dias + agravamento_60_dias + agravamento_90_dias) * 0.30),
            'usa_ml': False,
            'algoritmo': "Regras Estatísticas (fallback)"
        }

# ===== ENDPOINTS DA API =====

@app.get("/", response_class=HTMLResponse)
async def root():
    """Página inicial da API"""
    return """
    <html>
        <head>
            <title>API REST - Gestão Inteligente de Vagas (GIV-Saúde)</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                .header { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 20px; }
                .endpoint { background: #ecf0f1; padding: 15px; margin: 10px 0; border-radius: 5px; }
                .method { background: #3498db; color: white; padding: 5px 10px; border-radius: 3px; font-weight: bold; }
                .method.post { background: #27ae60; }
                .method.get { background: #3498db; }
                a { color: #3498db; text-decoration: none; }
                a:hover { text-decoration: underline; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🏥 API REST - Gestão Inteligente de Vagas (GIV-Saúde)</h1>
                    <p>API completa para gestão de vagas hospitalares com Machine Learning</p>
                </div>
                
                <h2>📚 Documentação</h2>
                <div class="endpoint">
                    <span class="method get">GET</span> 
                    <a href="/docs">/docs</a> - Documentação interativa (Swagger UI)
                </div>
                <div class="endpoint">
                    <span class="method get">GET</span> 
                    <a href="/redoc">/redoc</a> - Documentação alternativa (ReDoc)
                </div>
                
                <h2>🔐 Autenticação</h2>
                <div class="endpoint">
                    <span class="method post">POST</span> 
                    <a href="/auth/login">/auth/login</a> - Login e obtenção de token JWT
                </div>
                
                <h2>📊 Endpoints Principais</h2>
                <div class="endpoint">
                    <span class="method get">GET</span> 
                    <a href="/api/v1/status">/api/v1/status</a> - Status da API
                </div>
                <div class="endpoint">
                    <span class="method get">GET</span> 
                    <a href="/api/v1/dashboard/kpis">/api/v1/dashboard/kpis</a> - KPIs do dashboard
                </div>
                <div class="endpoint">
                    <span class="method get">GET</span> 
                    <a href="/api/v1/dashboard/dados">/api/v1/dashboard/dados</a> - Dados do dashboard
                </div>
                <div class="endpoint">
                    <span class="method get">GET</span> 
                    <a href="/api/v1/analise/predicao">/api/v1/analise/predicao</a> - Análise preditiva com ML
                </div>
                
                <h2>🔍 Consultas e Filtros</h2>
                <div class="endpoint">
                    <span class="method get">GET</span> 
                    <a href="/api/v1/solicitacoes">/api/v1/solicitacoes</a> - Listar solicitações
                </div>
                <div class="endpoint">
                    <span class="method get">GET</span> 
                    <a href="/api/v1/procedimentos">/api/v1/procedimentos</a> - Listar procedimentos
                </div>
                <div class="endpoint">
                    <span class="method get">GET</span> 
                    <a href="/api/v1/relatorios/resumo">/api/v1/relatorios/resumo</a> - Relatório resumido
                </div>
                
                <h2>🤖 Machine Learning</h2>
                <div class="endpoint">
                    <span class="method get">GET</span> 
                    <a href="/api/v1/ml/modelo/info">/api/v1/ml/modelo/info</a> - Informações do modelo ML
                </div>
                <div class="endpoint">
                    <span class="method post">POST</span> 
                    <a href="/api/v1/ml/predicao">/api/v1/ml/predicao</a> - Fazer predições ML
                </div>
                
                <p style="margin-top: 30px; color: #7f8c8d;">
                    <strong>Versão:</strong> 1.0.0 | 
                    <strong>Autor:</strong> Sistema GIV-Saúde | 
                    <strong>Data:</strong> Outubro 2025
                </p>
            </div>
        </body>
    </html>
    """

# ===== AUTENTICAÇÃO =====

@app.post("/auth/login")
async def login(username: str, password: str):
    """Login e obtenção de token JWT"""
    if username in USUARIOS_VALIDOS and USUARIOS_VALIDOS[username] == password:
        token = criar_token_jwt(username)
        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": username
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )

# ===== ENDPOINTS PRINCIPAIS =====

@app.get("/api/v1/status")
async def get_status():
    """Status da API e informações básicas"""
    try:
        df = carregar_dados()
        return {
            "status": "OK",
            "versao": "1.0.0",
            "nome": "API REST - Gestão Inteligente de Vagas (GIV-Saúde)",
            "total_registros": len(df),
            "timestamp": datetime.now().isoformat(),
            "modelo_ml_treinado": modelo_global.treinado,
            "cache_ativado": _dados_cache is not None
        }
    except Exception as e:
        return {
            "status": "ERRO",
            "erro": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/api/v1/dashboard/kpis")
async def get_dashboard_kpis(
    risco: Optional[List[str]] = Query(None),
    especialidade: Optional[List[str]] = Query(None),
    current_user: str = Depends(verificar_token_jwt)
):
    """KPIs do dashboard com filtros"""
    try:
        df_completo = carregar_dados()
        df_filtrado = df_completo
        
        # Aplicar filtros
        if risco:
            df_filtrado = df_filtrado.filter(pl.col("solicitacao_risco").is_in(risco))
        if especialidade:
            df_filtrado = df_filtrado.filter(pl.col("procedimento_especialidade").is_in(especialidade))
        
        # Métricas
        total = len(df_filtrado)
        total_sistema = len(df_completo)
        
        # KPIs
        taxa_conf = 0
        risco_critico = 0
        sem_agendamento = 0
        sem_agendamento_total = 0
        
        if total > 0:
            confirmados = df_filtrado.filter(
                pl.col("solicitacao_status").str.contains("CONFIRMADO")
            ).height
            taxa_conf = confirmados / total * 100
            
            criticos = df_filtrado.filter(
                pl.col("solicitacao_risco").is_in(["VERMELHO", "AMARELO"])
            ).height
            risco_critico = criticos / total * 100
            
            nao_agendados = df_filtrado.filter(
                ~pl.col("solicitacao_status").str.contains("AGENDAMENTO")
            ).height
            sem_agendamento = nao_agendados / total * 100
            sem_agendamento_total = nao_agendados
        
        return {
            "status": "sucesso",
            "filtros_aplicados": {
                "risco": risco,
                "especialidade": especialidade
            },
            "kpis": {
                "total_solicitacoes": total,
                "total_sistema": total_sistema,
                "taxa_confirmacao": round(taxa_conf, 2),
                "risco_critico": round(risco_critico, 2),
                "sem_agendamento": round(sem_agendamento, 2),
                "sem_agendamento_total": sem_agendamento_total
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao calcular KPIs: {str(e)}")

@app.get("/api/v1/dashboard/dados")
async def get_dashboard_dados(
    risco: Optional[List[str]] = Query(None),
    especialidade: Optional[List[str]] = Query(None),
    limit: int = Query(1000, ge=1, le=10000),
    current_user: str = Depends(verificar_token_jwt)
):
    """Dados do dashboard com filtros e paginação"""
    try:
        df_completo = carregar_dados()
        df_filtrado = df_completo
        
        # Aplicar filtros
        if risco:
            df_filtrado = df_filtrado.filter(pl.col("solicitacao_risco").is_in(risco))
        if especialidade:
            df_filtrado = df_filtrado.filter(pl.col("procedimento_especialidade").is_in(especialidade))
        
        # Limitar resultados
        df_limitado = df_filtrado.head(limit)
        
        # Converter para dict
        dados = df_limitado.to_dicts()
        
        return {
            "status": "sucesso",
            "filtros_aplicados": {
                "risco": risco,
                "especialidade": especialidade
            },
            "total_registros": len(df_filtrado),
            "registros_retornados": len(dados),
            "limit": limit,
            "dados": dados,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar dados: {str(e)}")

@app.get("/api/v1/analise/predicao")
async def get_analise_predicao(
    risco: Optional[List[str]] = Query(None),
    especialidade: Optional[List[str]] = Query(None),
    current_user: str = Depends(verificar_token_jwt)
):
    """Análise preditiva com Machine Learning"""
    try:
        df_completo = carregar_dados()
        df_filtrado = df_completo
        
        # Aplicar filtros
        if risco:
            df_filtrado = df_filtrado.filter(pl.col("solicitacao_risco").is_in(risco))
        if especialidade:
            df_filtrado = df_filtrado.filter(pl.col("procedimento_especialidade").is_in(especialidade))
        
        # Pacientes sem agendamento
        df_sem_agend = df_filtrado.filter(
            ~pl.col("solicitacao_status").str.contains("AGENDAMENTO")
        )
        
        if len(df_sem_agend) == 0:
            return {
                "status": "sucesso",
                "mensagem": "Nenhum paciente sem agendamento encontrado",
                "predicao": None,
                "timestamp": datetime.now().isoformat()
            }
        
        # Análise preditiva
        predicao = analisar_predicao_sem_agendamento(df_sem_agend)
        
        return {
            "status": "sucesso",
            "filtros_aplicados": {
                "risco": risco,
                "especialidade": especialidade
            },
            "total_sem_agendamento": len(df_sem_agend),
            "predicao": predicao,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na análise preditiva: {str(e)}")

# ===== ENDPOINTS DE CONSULTA =====

@app.get("/api/v1/solicitacoes")
async def get_solicitacoes(
    risco: Optional[str] = Query(None),
    especialidade: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=5000),
    offset: int = Query(0, ge=0),
    current_user: str = Depends(verificar_token_jwt)
):
    """Listar solicitações com filtros"""
    try:
        df_completo = carregar_dados()
        df_filtrado = df_completo
        
        # Aplicar filtros
        if risco:
            df_filtrado = df_filtrado.filter(pl.col("solicitacao_risco") == risco)
        if especialidade:
            df_filtrado = df_filtrado.filter(pl.col("procedimento_especialidade") == especialidade)
        if status:
            df_filtrado = df_filtrado.filter(pl.col("solicitacao_status").str.contains(status))
        
        # Paginação
        total = len(df_filtrado)
        df_paginado = df_filtrado.slice(offset, limit)
        
        dados = df_paginado.to_dicts()
        
        return {
            "status": "sucesso",
            "filtros_aplicados": {
                "risco": risco,
                "especialidade": especialidade,
                "status": status
            },
            "paginacao": {
                "total": total,
                "limit": limit,
                "offset": offset,
                "retornados": len(dados)
            },
            "dados": dados,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar solicitações: {str(e)}")

@app.get("/api/v1/procedimentos")
async def get_procedimentos(
    especialidade: Optional[str] = Query(None),
    tipo: Optional[str] = Query(None),
    current_user: str = Depends(verificar_token_jwt)
):
    """Listar procedimentos com filtros"""
    try:
        df_completo = carregar_dados()
        
        # Filtrar apenas procedimentos (sem duplicatas)
        df_procedimentos = df_completo.select([
            "procedimento_sisreg_id",
            "procedimento",
            "procedimento_especialidade",
            "procedimento_tipo"
        ]).unique()
        
        # Aplicar filtros
        if especialidade:
            df_procedimentos = df_procedimentos.filter(pl.col("procedimento_especialidade") == especialidade)
        if tipo:
            df_procedimentos = df_procedimentos.filter(pl.col("procedimento_tipo") == tipo)
        
        dados = df_procedimentos.to_dicts()
        
        return {
            "status": "sucesso",
            "filtros_aplicados": {
                "especialidade": especialidade,
                "tipo": tipo
            },
            "total_procedimentos": len(dados),
            "dados": dados,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar procedimentos: {str(e)}")

# ===== ENDPOINTS DE RELATÓRIOS =====

@app.get("/api/v1/relatorios/resumo")
async def get_relatorio_resumo(
    current_user: str = Depends(verificar_token_jwt)
):
    """Relatório resumido do sistema"""
    try:
        df_completo = carregar_dados()
        
        # Estatísticas gerais
        total_solicitacoes = len(df_completo)
        
        # Por risco
        risco_stats = df_completo.group_by("solicitacao_risco").count().to_dicts()
        
        # Por especialidade (top 10)
        especialidade_stats = (
            df_completo.group_by("procedimento_especialidade")
            .count()
            .sort("count", descending=True)
            .head(10)
            .to_dicts()
        )
        
        # Por status (top 10)
        status_stats = (
            df_completo.group_by("solicitacao_status")
            .count()
            .sort("count", descending=True)
            .head(10)
            .to_dicts()
        )
        
        # Confirmados vs Não confirmados
        confirmados = df_completo.filter(
            pl.col("solicitacao_status").str.contains("CONFIRMADO")
        ).height
        
        nao_confirmados = total_solicitacoes - confirmados
        
        return {
            "status": "sucesso",
            "resumo": {
                "total_solicitacoes": total_solicitacoes,
                "confirmados": confirmados,
                "nao_confirmados": nao_confirmados,
                "taxa_confirmacao": round((confirmados / total_solicitacoes * 100), 2) if total_solicitacoes > 0 else 0
            },
            "distribuicao_risco": risco_stats,
            "top_especialidades": especialidade_stats,
            "top_status": status_stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar relatório: {str(e)}")

# ===== ENDPOINTS DE MACHINE LEARNING =====

@app.get("/api/v1/ml/modelo/info")
async def get_modelo_info(current_user: str = Depends(verificar_token_jwt)):
    """Informações sobre o modelo de Machine Learning"""
    try:
        return {
            "status": "sucesso",
            "modelo": {
                "treinado": modelo_global.treinado,
                "algoritmo": "Random Forest Classifier",
                "parametros": {
                    "n_estimators": 100,
                    "max_depth": 10,
                    "min_samples_split": 20,
                    "min_samples_leaf": 10
                },
                "metricas": modelo_global.metricas if modelo_global.treinado else None,
                "feature_importance": modelo_global.feature_importance if modelo_global.treinado else None
            },
            "features": [
                "solicitacao_risco",
                "procedimento_especialidade",
                "paciente_faixa_etaria",
                "tempo_espera_dias",
                "status_critico"
            ],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar informações do modelo: {str(e)}")

@app.post("/api/v1/ml/predicao")
async def fazer_predicao_ml(
    dados: Dict[str, Any],
    current_user: str = Depends(verificar_token_jwt)
):
    """Fazer predição ML personalizada"""
    try:
        # Validar dados de entrada
        campos_obrigatorios = ["risco", "especialidade", "faixa_etaria"]
        for campo in campos_obrigatorios:
            if campo not in dados:
                raise HTTPException(status_code=400, detail=f"Campo obrigatório ausente: {campo}")
        
                # Criar DataFrame temporário para predição
        df_temp = pl.DataFrame([dados])
       
        # Treinar modelo se necessário
        if not modelo_global.treinado:
            df_completo = carregar_dados()
            modelo_global.treinar(df_completo)
        
        # Fazer predição
        df_pred = modelo_global.predizer_agravamentos(df_temp)

        resultado = df_pred.to_dicts()[0]
        
        return {
            "status": "sucesso",
            "entrada": dados,
            "predicao": {
                "probabilidade_agravamento": float(resultado.get("probabilidade_agravamento", 0)),
                "predicao_agravamento": int(resultado.get("predicao_agravamento", 0)),
                "classificacao": "Alto Risco" if resultado.get("probabilidade_agravamento", 0) > 0.7 else 
                               "Médio Risco" if resultado.get("probabilidade_agravamento", 0) > 0.4 else "Baixo Risco"
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na predição ML: {str(e)}")

# ===== ENDPOINTS DE FILTROS E OPÇÕES =====

@app.get("/api/v1/filtros/opcoes")
async def get_filtros_opcoes(current_user: str = Depends(verificar_token_jwt)):
    """Obter opções disponíveis para filtros"""
    try:
        df_completo = carregar_dados()
        
        # Opções de risco
        riscos = df_completo["solicitacao_risco"].unique().drop_nulls().sort().to_list()
        
        # Opções de especialidade
        especialidades = df_completo["procedimento_especialidade"].unique().drop_nulls().sort().to_list()
        
        # Opções de status (top 20)
        status = (
            df_completo.group_by("solicitacao_status")
            .count()
            .sort("count", descending=True)
            .head(20)["solicitacao_status"]
            .to_list()
        )
        
        return {
            "status": "sucesso",
            "filtros": {
                "riscos": riscos,
                "especialidades": especialidades,
                "status": status
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar opções de filtros: {str(e)}")

# ===== ENDPOINT DE SAÚDE =====

@app.get("/health")
async def health_check():
    """Endpoint de saúde da API"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

# ===== INICIALIZAÇÃO =====

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Iniciando API REST - Gestão Inteligente de Vagas (GIV-Saúde)")
    print("📊 Carregando dados...")
    
    try:
        # Carregar dados na inicialização
        carregar_dados()
        print("✅ Dados carregados com sucesso!")
        
        # Iniciar servidor
        uvicorn.run(
            app, 
            host="127.0.0.1", 
            port=8000,
            log_level="info"
        )
    except Exception as e:
        print(f"❌ Erro ao iniciar API: {e}")
        exit(1)
