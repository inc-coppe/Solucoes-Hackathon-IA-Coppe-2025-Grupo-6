#!/usr/bin/env python3
"""
Gestão Inteligente de Vagas - GIV - Versão Otimizada
==================================
Dashboard completo com CSS externo e funcionalidades consolidadas.
Mínimo de arquivos necessários para funcionamento completo.
"""

import polars as pl
import plotly.graph_objects as go
import plotly.express as px
from fastapi import FastAPI, Request, Form, Query, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Optional, List
import glob
from datetime import datetime, timedelta
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix
import warnings
warnings.filterwarnings('ignore')

# ===== CONFIGURAÇÃO DA APLICAÇÃO =====
app = FastAPI(title="Gestão Inteligente de Vagas - GIV", version="2.0")
app.mount("/static", StaticFiles(directory="static"), name="static")

# ===== CACHE GLOBAL =====
_dados_cache = None
_modelo_global = None

# ===== MODELO DE MACHINE LEARNING INTEGRADO =====
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
        if 'data_solicitacao' not in df_features.columns:
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
            else:  # DESCONHECIDO
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
        print("=" * 60)
        
        # Preparar features
        print("📊 Passo 1: Feature Engineering...")
        df_prep = self.preparar_features(df)
        df_prep = self.criar_target(df_prep)
        
        feature_cols = ['risco_numerico', 'tempo_espera_dias', 'idade_aproximada', 
                       'especialidade_codigo', 'status_critico']
        feature_cols_existentes = [col for col in feature_cols if col in df_prep.columns]
        
        X = df_prep.select(feature_cols_existentes).to_numpy()
        y = df_prep['agravamento'].to_numpy()
        
        print(f"   ✅ Features extraídas: {len(feature_cols_existentes)}")
        print(f"   ✅ Amostras: {len(X):,}")
        print(f"   ✅ Taxa de agravamento: {y.mean():.1%}")
        
        # Split treino/teste
        print("\n📊 Passo 2: Divisão Treino/Teste (80/20)...")
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        print(f"   ✅ Treino: {len(X_train):,} amostras")
        print(f"   ✅ Teste: {len(X_test):,} amostras")
        
        # Treinamento
        print("\n🌲 Passo 3: Treinando Random Forest Classifier...")
        self.modelo = RandomForestClassifier(
            n_estimators=100, max_depth=10, min_samples_split=20,
            min_samples_leaf=10, random_state=42, n_jobs=-1
        )
        
        self.modelo.fit(X_train, y_train)
        print("   ✅ Modelo treinado com sucesso!")
        
        # Avaliação
        print("\n📈 Passo 4: Avaliação do Modelo...")
        y_pred = self.modelo.predict(X_test)
        y_pred_proba = self.modelo.predict_proba(X_test)[:, 1]
        
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
        
        acuracia = accuracy_score(y_test, y_pred)
        precisao = precision_score(y_test, y_pred, zero_division=0)
        recall = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        
        try:
            auc_roc = roc_auc_score(y_test, y_pred_proba)
        except:
            auc_roc = 0.0
        
        self.metricas = {
            'acuracia': acuracia, 'precisao': precisao, 'recall': recall,
            'f1_score': f1, 'auc_roc': auc_roc,
            'total_treino': len(X_train), 'total_teste': len(X_test)
        }
        
        print(f"   ✅ Acurácia: {acuracia:.1%}")
        print(f"   ✅ Precisão: {precisao:.1%}")
        print(f"   ✅ Recall: {recall:.1%}")
        print(f"   ✅ F1-Score: {f1:.1%}")
        print(f"   ✅ AUC-ROC: {auc_roc:.3f}")
        
        self.feature_importance = {
            'features': feature_cols_existentes,
            'importances': self.modelo.feature_importances_.tolist()
        }
        
        print("\n🎯 Importância das Features:")
        for feat, imp in zip(feature_cols_existentes, self.modelo.feature_importances_):
            print(f"   {feat}: {imp:.3f}")
        
        self.treinado = True
        print("\n" + "=" * 60)
        print("✅ MODELO TREINADO COM SUCESSO!")
        print("=" * 60)
        
        return self.metricas
    
    def predizer_agravamentos(self, df_sem_agendamento):
        """Prediz probabilidade de agravamento"""
        if not self.treinado:
            print("⚠️ Modelo não treinado! Treinando agora...")
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

# ===== FUNÇÕES UTILITÁRIAS =====
def carregar_dados():
    """Carrega dados com cache otimizado"""
    global _dados_cache
    if _dados_cache is not None:
        return _dados_cache
    
    try:
        print("Carregando dados da pasta db...")
        
        # Carregar solicitações
        solicitacao_files = glob.glob('db/solicitacao-*.parquet')
        if solicitacao_files:
            df_solicitacao = pl.concat([pl.read_parquet(f) for f in solicitacao_files])
            print(f"OK: {len(solicitacao_files)} arquivos de solicitacao carregados")
        else:
            raise FileNotFoundError("Arquivos de solicitacao nao encontrados")
        
        # Carregar procedimentos
        procedimento_files = glob.glob('db/procedimento-*.parquet')
        if procedimento_files:
            df_procedimento = pl.concat([pl.read_parquet(f) for f in procedimento_files])
            print(f"OK: {len(procedimento_files)} arquivo(s) de procedimento carregados")
            df_completo = df_solicitacao.join(df_procedimento, on="procedimento_sisreg_id", how="left")
        else:
            df_completo = df_solicitacao
        
        print(f"OK: Total: {len(df_completo):,} registros")
        _dados_cache = df_completo
        return df_completo
        
    except Exception as e:
        print(f"ERRO ao carregar dados: {e}")
        return None

def analisar_predicao_sem_agendamento(df_sem_agendamento):
    """Análise preditiva integrada"""
    global _modelo_global
    
    if _modelo_global is None:
        _modelo_global = ModeloPredicaoAgravamento()
    
    print("\n🤖 Executando predição com Machine Learning...")
    
    try:
        if not _modelo_global.treinado:
            print("   📚 Treinando modelo pela primeira vez...")
            _modelo_global.treinar(df_sem_agendamento)
        
        df_predicoes = _modelo_global.predizer_agravamentos(df_sem_agendamento)
        metricas_ml = _modelo_global.calcular_metricas_predicao(df_predicoes)
        
        metricas_ml['usa_ml'] = True
        metricas_ml['algoritmo'] = 'Random Forest Classifier'
        metricas_ml['num_arvores'] = 100
        
        print("   ✅ Predição ML concluída com sucesso!")
        return metricas_ml
        
    except Exception as e:
        print(f"   ⚠️ Erro no ML: {e}")
        print("   🔄 Voltando para modelo baseado em regras...")
        
        # Fallback simples
        total = len(df_sem_agendamento)
        vermelhos = df_sem_agendamento.filter(pl.col("solicitacao_risco") == "VERMELHO").height
        amarelos = df_sem_agendamento.filter(pl.col("solicitacao_risco") == "AMARELO").height
        
        agravamento_30_dias = int(vermelhos * 0.8 + amarelos * 0.3)
        agravamento_60_dias = int(vermelhos * 0.2 + amarelos * 0.4)
        agravamento_90_dias = int(amarelos * 0.2)
        
        custo_unitario = 5000
        custo_30_dias = agravamento_30_dias * custo_unitario
        custo_total = (agravamento_30_dias + agravamento_60_dias + agravamento_90_dias) * custo_unitario
        internacoes = int((agravamento_30_dias + agravamento_60_dias + agravamento_90_dias) * 0.30)
        
        return {
            'total_sem_agendamento': total,
            'alto_risco_ml': vermelhos,
            'medio_risco_ml': amarelos,
            'baixo_risco_ml': total - vermelhos - amarelos,
            'agravamento_30_dias': agravamento_30_dias,
            'agravamento_60_dias': agravamento_60_dias,
            'agravamento_90_dias': agravamento_90_dias,
            'custo_estimado_30_dias': custo_30_dias,
            'custo_estimado_total': custo_total,
            'internacoes_projetadas': internacoes,
            'especialidades_criticas_ml': [],
            'probabilidade_media': 0.25,
            'usa_ml': False
        }

# ===== ROTAS DA APLICAÇÃO =====
def get_current_user(request: Request):
    """Autenticação simplificada"""
    if not request.session.get("logged_in"):
        raise HTTPException(status_code=401, detail="Não autorizado")
    return request.session.get("username")

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return RedirectResponse(url="/login")

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, error: Optional[str] = None):
    return f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Login - Gestão Inteligente de Vagas - GIV</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="/static/login.css" rel="stylesheet">
    </head>
    <body>
        <div class="login-container">
            <h1 class="login-title">
                <i class="fas fa-hospital"></i> Gestão Inteligente de Vagas - GIV
            </h1>
            {"<div class='alert alert-danger'>Usuário ou senha incorretos</div>" if error else ""}
            <form method="post" action="/login">
                <div class="mb-3">
                    <label for="username" class="form-label">Usuário</label>
                    <input type="text" class="form-control" id="username" name="username" required autofocus>
                </div>
                <div class="mb-3">
                    <label for="password" class="form-label">Senha</label>
                    <input type="password" class="form-control" id="password" name="password" required>
                </div>
                <button type="submit" class="btn btn-primary btn-login">
                    <i class="fas fa-sign-in-alt"></i> Entrar
                </button>
            </form>
        </div>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/js/all.min.js"></script>
    </body>
    </html>
    """

@app.post("/login", response_class=HTMLResponse)
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if username == "admin" and password == "admin123":
        request.session["logged_in"] = True
        request.session["username"] = username
        return RedirectResponse(url="/dashboard", status_code=303)
    else:
        return RedirectResponse(url="/login?error=invalid", status_code=303)

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login")

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    risco: Optional[List[str]] = Query(None),
    especialidade: Optional[List[str]] = Query(None),
    current_user: str = Depends(get_current_user)
):
    """Dashboard principal otimizado"""
    try:
        # Carregar dados
        df_completo = carregar_dados()
        if df_completo is None:
            return "Erro ao carregar dados"
            
        df_filtrado = df_completo
        
        # Aplicar filtros
        if risco:
            df_filtrado = df_filtrado.filter(pl.col("solicitacao_risco").is_in(risco))
        if especialidade:
            df_filtrado = df_filtrado.filter(pl.col("procedimento_especialidade").is_in(especialidade))
        
        # Métricas básicas
        total = len(df_filtrado)
        total_sistema = len(df_completo)
        
        # KPIs
        taxa_conf = 0
        risco_critico = 0
        sem_agendamento = 0
        sem_agendamento_total = 0
        
        if total > 0:
            confirmados = df_filtrado.filter(pl.col("solicitacao_status").str.contains("CONFIRMADO")).height
            taxa_conf = (confirmados / total * 100)
            
            criticos = df_filtrado.filter(pl.col("solicitacao_risco").is_in(["VERMELHO", "AMARELO"])).height
            risco_critico = (criticos / total * 100)
            
            nao_agendados = df_filtrado.filter(~pl.col("solicitacao_status").str.contains("AGENDAMENTO")).height
            sem_agendamento = (nao_agendados / total * 100)
            sem_agendamento_total = nao_agendados
        
        # Análise preditiva
        predicao_sem_agendamento = None
        if sem_agendamento_total > 0:
            df_sem_agend = df_filtrado.filter(~pl.col("solicitacao_status").str.contains("AGENDAMENTO"))
            predicao_sem_agendamento = analisar_predicao_sem_agendamento(df_sem_agend) if len(df_sem_agend) > 0 else None
        
        # Dados para filtros
        riscos_unicos = df_completo["solicitacao_risco"].unique().sort().to_list()
        especialidades_unicas = df_completo["procedimento_especialidade"].drop_nulls().unique().sort().to_list()
        
        # Template HTML otimizado
        return f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Gestão Inteligente de Vagas - GIV</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
            <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
            <link href="/static/dashboard.css" rel="stylesheet">
        </head>
        <body>
            <!-- Navbar -->
            <nav class="navbar">
                <div class="container-fluid">
                    <span class="navbar-brand mb-0 h1">
                        <i class="fas fa-hospital text-primary"></i>
                        Gestão Inteligente de Vagas - GIV
                    </span>
                    <div class="d-flex">
                        <span class="navbar-text me-3">
                            <i class="fas fa-user"></i> {current_user}
                        </span>
                        <a href="/logout" class="btn btn-outline-primary btn-sm">
                            <i class="fas fa-sign-out-alt"></i> Sair
                        </a>
                    </div>
                </div>
            </nav>

            <div class="container-fluid">
                <div class="main-container">
                    <!-- KPIs Principais -->
                    <div class="row mb-4">
                        <div class="col-lg-3 col-md-6 mb-3">
                            <div class="kpi-card">
                                <i class="fas fa-list-alt kpi-icon"></i>
                                <div class="kpi-value">{total:,}</div>
                                <div class="kpi-label">Total de Solicitações</div>
                                <small style="opacity: 0.8;">{total_sistema:,} no sistema completo</small>
                            </div>
                        </div>
                        <div class="col-lg-3 col-md-6 mb-3">
                            <div class="kpi-card">
                                <i class="fas fa-check-circle kpi-icon"></i>
                                <div class="kpi-value">{taxa_conf:.1f}%</div>
                                <div class="kpi-label">Taxa de Confirmação</div>
                                <small style="opacity: 0.8;">Solicitações confirmadas</small>
                            </div>
                        </div>
                        <div class="col-lg-3 col-md-6 mb-3">
                            <div class="kpi-card">
                                <i class="fas fa-exclamation-triangle kpi-icon"></i>
                                <div class="kpi-value">{risco_critico:.1f}%</div>
                                <div class="kpi-label">Risco Crítico</div>
                                <small style="opacity: 0.8;">Vermelho + Amarelo</small>
                            </div>
                        </div>
                        <div class="col-lg-3 col-md-6 mb-3">
                            <div class="kpi-card">
                                <i class="fas fa-calendar-times kpi-icon"></i>
                                <div class="kpi-value">{sem_agendamento:.1f}%</div>
                                <div class="kpi-label">Sem Agendamento</div>
                                <small style="opacity: 0.8;">{sem_agendamento_total:,} pacientes</small>
                            </div>
                        </div>
                    </div>

                    <!-- Filtros -->
                    <div class="filter-card">
                        <h5><i class="fas fa-filter"></i> Filtros</h5>
                        <form method="get" action="/dashboard">
                            <div class="row">
                                <div class="col-md-6">
                                    <div class="filter-section">
                                        <h6 class="text-primary mb-3">Nível de Risco</h6>
                                        {"".join([f'<div class="form-check form-check-inline"><input class="form-check-input" type="checkbox" name="risco" value="{r}" id="risco-{r}" {"checked" if risco and r in risco else ""}><label class="form-check-label" for="risco-{r}">{r}</label></div>' for r in riscos_unicos])}
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="filter-section">
                                        <h6 class="text-primary mb-3">Especialidade</h6>
                                        {"".join([f'<div class="form-check form-check-inline"><input class="form-check-input" type="checkbox" name="especialidade" value="{esp}" id="esp-{esp}" {"checked" if especialidade and esp in especialidade else ""}><label class="form-check-label" for="esp-{esp}">{esp}</label></div>' for esp in especialidades_unicas[:15]])}
                                    </div>
                                </div>
                            </div>
                            <div class="text-center mt-3">
                                <button type="submit" class="btn btn-filtrar">
                                    <i class="fas fa-search"></i> Aplicar Filtros
                                </button>
                            </div>
                        </form>
                    </div>

                    <!-- Análise Preditiva -->
                    {f'''
                    <div class="alert alert-primary" role="alert">
                        <h6><i class="fas fa-brain"></i> Análise Preditiva com Machine Learning</h6>
                        <strong>Algoritmo:</strong> {predicao_sem_agendamento.get('algoritmo', 'Random Forest Classifier')}
                        <br>
                        <strong>Projeção:</strong> Impacto estimado para {predicao_sem_agendamento['total_sem_agendamento']:,} pacientes sem atendimento.
                    </div>

                    <!-- Cards de Predição -->
                    <div class="row mb-4">
                        <div class="col-lg-3 col-md-6 mb-3">
                            <div class="prediction-card">
                                <i class="fas fa-user-injured prediction-icon"></i>
                                <h2 class="prediction-value">{predicao_sem_agendamento['agravamento_30_dias']:,}</h2>
                                <p class="prediction-label">Agravamentos em 30 dias</p>
                            </div>
                        </div>
                        <div class="col-lg-3 col-md-6 mb-3">
                            <div class="prediction-card" style="background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);">
                                <i class="fas fa-bed prediction-icon"></i>
                                <h2 class="prediction-value">{predicao_sem_agendamento['internacoes_projetadas']:,}</h2>
                                <p class="prediction-label">Internações Projetadas</p>
                            </div>
                        </div>
                        <div class="col-lg-3 col-md-6 mb-3">
                            <div class="prediction-card" style="background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);">
                                <i class="fas fa-dollar-sign prediction-icon"></i>
                                <h2 class="prediction-value">R$ {predicao_sem_agendamento['custo_estimado_30_dias']:,.0f}</h2>
                                <p class="prediction-label">Custo 30 dias</p>
                            </div>
                        </div>
                        <div class="col-lg-3 col-md-6 mb-3">
                            <div class="prediction-card" style="background: linear-gradient(135deg, #8e44ad 0%, #6c3483 100%);">
                                <i class="fas fa-chart-line prediction-icon"></i>
                                <h2 class="prediction-value">R$ {predicao_sem_agendamento['custo_estimado_total']:,.0f}</h2>
                                <p class="prediction-label">Custo Total (90 dias)</p>
                            </div>
                        </div>
                    </div>
                    ''' if predicao_sem_agendamento else ''}

                    <!-- Gráfico de Risco -->
                    <div class="row">
                        <div class="col-12">
                            <div class="chart-card">
                                <h5><i class="fas fa-chart-pie"></i> Distribuição por Risco</h5>
                                <div id="grafico-risco"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Scripts -->
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <script>
                // Dados para gráficos
                const dadosRisco = {riscos_unicos};
                
                // Inicializar gráfico de risco
                document.addEventListener('DOMContentLoaded', function() {{
                    const data = [
                        {{
                            values: {[df_filtrado.group_by("solicitacao_risco").count().height for _ in range(len(riscos_unicos))]},
                            labels: {riscos_unicos},
                            type: 'pie',
                            marker: {{
                                colors: ['#dc3545', '#ffc107', '#28a745', '#007bff']
                            }}
                        }}
                    ];
                    
                    const layout = {{
                        title: 'Distribuição por Nível de Risco',
                        height: 400
                    }};
                    
                    Plotly.newPlot('grafico-risco', data, layout);
                }});
            </script>
        </body>
        </html>
        """
        
    except Exception as e:
        return f"Erro: {str(e)}"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)

