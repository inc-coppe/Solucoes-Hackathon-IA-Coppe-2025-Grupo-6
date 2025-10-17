import polars as pl
import plotly.express as px
import plotly.graph_objects as go
from fastapi import FastAPI, Query, Depends, Form, Request, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import List, Optional
import glob
from datetime import datetime, timedelta
from modelo_ml_saude import modelo_global

# Configuração
USUARIOS_VALIDOS = {"admin": "senha123", "tou": "hackathon"}

app = FastAPI(title="Gestão Inteligente de Vagas - GIV", version="2.0.0")

# Cache de dados
_dados_cache = None


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
            df_procedimento = pl.concat(
                [pl.read_parquet(f) for f in procedimento_files]
            )
            print(
                f"OK: {len(procedimento_files)} arquivo(s) de procedimento carregados"
            )

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


def analisar_predicao_sem_agendamento(df_sem_agendamento):
    """
    Análise preditiva do impacto de não agendar pacientes
    AGORA COM MACHINE LEARNING! 🤖

    Utiliza Random Forest Classifier treinado com dados históricos
    para predições mais precisas e personalizadas.
    """
    if df_sem_agendamento.is_empty():
        return None

    print("\n🤖 Executando predição com Machine Learning...")

    # 🔥 MACHINE LEARNING: Treinar modelo e fazer predições
    try:
        # Se o modelo ainda não foi treinado, treina com os dados completos
        if not modelo_global.treinado:
            print("   📚 Treinando modelo pela primeira vez...")
            modelo_global.treinar(df_sem_agendamento)

        # Fazer predições ML
        df_predicoes = modelo_global.predizer_agravamentos(df_sem_agendamento)

        # Calcular métricas baseadas em ML
        metricas_ml = modelo_global.calcular_metricas_predicao(df_predicoes)

        # Adicionar informações do modelo
        metricas_ml["usa_ml"] = True
        metricas_ml["algoritmo"] = "Random Forest Classifier"
        metricas_ml["num_arvores"] = 100

        print("   ✅ Predição ML concluída com sucesso!")

        return metricas_ml

    except Exception as e:
        print(f"   ⚠️ Erro no ML: {e}")
        print("   🔄 Voltando para modelo baseado em regras...")

        # Fallback: modelo baseado em regras (caso ML falhe)
        total_sem_agend = len(df_sem_agendamento)

        riscos_criticos = df_sem_agendamento.filter(
            pl.col("solicitacao_risco").is_in(["VERMELHO", "AMARELO"])
        ).height
        riscos_medios = df_sem_agendamento.filter(
            pl.col("solicitacao_risco") == "VERDE"
        ).height
        riscos_baixos = df_sem_agendamento.filter(
            pl.col("solicitacao_risco") == "AZUL"
        ).height

        df_esp_sem_agend = (
            df_sem_agendamento.group_by("procedimento_especialidade")
            .agg(
                [
                    pl.count().alias("total"),
                    (
                        pl.col("solicitacao_risco").is_in(["VERMELHO", "AMARELO"]).sum()
                    ).alias("criticos"),
                ]
            )
            .sort("criticos", descending=True)
            .head(10)
        )

        especialidades_criticas = (
            df_esp_sem_agend.to_dicts() if len(df_esp_sem_agend) > 0 else []
        )

        agravamento_30_dias = int(riscos_criticos * 0.80 if riscos_criticos > 0 else 0)
        agravamento_60_dias = int(
            riscos_criticos * 0.50 + riscos_medios * 0.20
            if (riscos_criticos + riscos_medios) > 0
            else 0
        )
        agravamento_90_dias = int(riscos_baixos * 0.05 if riscos_baixos > 0 else 0)

        custo_agravamento_unitario = 5000
        custo_estimado_30_dias = agravamento_30_dias * custo_agravamento_unitario
        custo_estimado_total = (
            agravamento_30_dias + agravamento_60_dias + agravamento_90_dias
        ) * custo_agravamento_unitario

        internacoes_projetadas = int(
            (agravamento_30_dias + agravamento_60_dias + agravamento_90_dias) * 0.30
        )

        return {
            "total_sem_agendamento": total_sem_agend,
            "agravamento_30_dias": agravamento_30_dias,
            "agravamento_60_dias": agravamento_60_dias,
            "agravamento_90_dias": agravamento_90_dias,
            "custo_estimado_30_dias": custo_estimado_30_dias,
            "custo_estimado_total": custo_estimado_total,
            "internacoes_projetadas": internacoes_projetadas,
            "especialidades_criticas": especialidades_criticas,
            "usa_ml": False,
            "algoritmo": "Regras Estatísticas (fallback)",
        }


# Autenticação
async def get_current_user(request: Request):
    username = request.cookies.get("session_user")
    if username in USUARIOS_VALIDOS:
        return username
    raise HTTPException(
        status_code=status.HTTP_307_TEMPORARY_REDIRECT,
        detail="Não autenticado",
        headers={"Location": "/login"},
    )


# Rotas
@app.get("/", response_class=HTMLResponse)
async def root():
    return RedirectResponse(url="/login")


@app.get("/login", response_class=HTMLResponse)
async def login_form(error: Optional[str] = None):
    error_html = f'<div class="alert alert-danger">{error}</div>' if error else ""

    return HTMLResponse(
        f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Login - Gestão Inteligente de Vagas - GIV</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {{
                background: linear-gradient(135deg, #003087 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }}
            .login-container {{
                background: white;
                border-radius: 20px;
                padding: 50px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                max-width: 450px;
                width: 100%;
            }}
            .login-title {{
                color: #003087;
                font-weight: bold;
                margin-bottom: 30px;
            }}
            .btn-login {{
                background: linear-gradient(135deg, #003087 0%, #764ba2 100%);
                border: none;
                padding: 12px;
                font-weight: 600;
            }}
        </style>
    </head>
    <body>
        <div class="login-container">
            <h2 class="login-title text-center">Gestão Inteligente de Vagas - GIV</h2>
            {error_html}
            <form method="post" action="/login">
                <div class="mb-3">
                    <label class="form-label">Usuário</label>
                    <input type="text" name="username" class="form-control" required autofocus>
                </div>
                <div class="mb-3">
                    <label class="form-label">Senha</label>
                    <input type="password" name="password" class="form-control" required>
                </div>
                <button type="submit" class="btn btn-primary btn-login w-100">Entrar</button>
                <div class="mt-3 text-muted text-center small">
                    <p>Usuários: admin/senha123 ou tou/hackathon</p>
                </div>
            </form>
        </div>
    </body>
    </html>
    """
    )


@app.post("/login")
async def handle_login(username: str = Form(), password: str = Form()):
    if USUARIOS_VALIDOS.get(username) == password:
        response = RedirectResponse(url="/dashboard", status_code=303)
        response.set_cookie(
            key="session_user", value=username, httponly=True, max_age=3600
        )
        return response
    return RedirectResponse(
        url="/login?error=Usuário ou senha incorretos", status_code=303
    )


@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/login")
    response.delete_cookie(key="session_user")
    return response


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    risco: Optional[List[str]] = Query(None),
    especialidade: Optional[List[str]] = Query(None),
    current_user: str = Depends(get_current_user),
):
    try:
        # Carregar dados
        df_completo = carregar_dados()
        df_filtrado = df_completo

        # Aplicar filtros
        if risco:
            df_filtrado = df_filtrado.filter(pl.col("solicitacao_risco").is_in(risco))
        if especialidade:
            df_filtrado = df_filtrado.filter(
                pl.col("procedimento_especialidade").is_in(especialidade)
            )

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

            # Pacientes sem agendamento (status que não contém "AGENDAMENTO")
            nao_agendados = df_filtrado.filter(
                ~pl.col("solicitacao_status").str.contains("AGENDAMENTO")
            ).height
            sem_agendamento = nao_agendados / total * 100
            sem_agendamento_total = nao_agendados

        # Gráficos
        grafico_risco_html = ""
        grafico_especialidade_html = ""
        grafico_sem_agendamento_html = ""
        grafico_status_sem_agendamento_html = ""

        # Área de detalhamento de especialidade única
        especialidade_unica = None
        grafico_esp_risco_html = ""
        grafico_esp_status_html = ""
        grafico_esp_faixa_etaria_html = ""
        estatisticas_especialidade = None

        # Detectar se apenas 1 especialidade está selecionada
        if especialidade and len(especialidade) == 1:
            especialidade_unica = especialidade[0]

        if total > 0:
            # Gráfico 1: Distribuição por Risco (PIZZA)
            # Mapeamento correto de cores por risco
            color_map = {
                "AZUL": "#007bff",  # Azul
                "VERDE": "#28a745",  # Verde
                "AMARELO": "#ffc107",  # Amarelo
                "VERMELHO": "#dc3545",  # Vermelho
            }

            # Ordem FIXA de criticidade: Vermelho > Amarelo > Verde > Azul
            riscos_ordem_fixa = ["VERMELHO", "AMARELO", "VERDE", "AZUL"]
            ordem_map = {risco: idx for idx, risco in enumerate(riscos_ordem_fixa)}

            df_risco = df_filtrado.group_by("solicitacao_risco").count()
            if len(df_risco) > 0:
                # Adicionar coluna de ordem para manter a sequência de criticidade
                df_risco_ordenado = df_risco.with_columns(
                    [pl.col("solicitacao_risco").replace(ordem_map).alias("ordem")]
                ).sort("ordem")

                # Pegar apenas os riscos que EXISTEM nos dados (count > 0)
                riscos = df_risco_ordenado["solicitacao_risco"].to_list()
                valores = df_risco_ordenado["count"].to_list()
                cores = [color_map[r] for r in riscos]

                # Gráfico de Pizza (apenas com riscos que têm dados)
                fig1 = go.Figure(
                    data=[
                        go.Pie(
                            labels=riscos,
                            values=valores,
                            marker=dict(colors=cores),
                            textinfo="value+percent",
                            texttemplate="%{value:,}<br>(%{percent})",
                            hole=0.3,  # Donut chart
                            sort=False,  # Não ordenar automaticamente, manter ordem dos dados
                        )
                    ]
                )
                fig1.update_layout(
                    title="Distribuição por Nível de Risco",
                    height=400,
                    showlegend=True,
                    legend=dict(
                        orientation="v",
                        yanchor="middle",
                        y=0.5,
                        xanchor="right",
                        x=-0.05,  # Posicionar à esquerda
                        traceorder="normal",  # Manter ordem da série de dados
                    ),
                    margin=dict(l=150),  # Margem esquerda para acomodar a legenda
                )
                grafico_risco_html = fig1.to_html(
                    full_html=False, include_plotlyjs="cdn"
                )

            # Gráfico 2: Especialidades (limite de 10 principais)
            df_esp = (
                df_filtrado.group_by("procedimento_especialidade")
                .count()
                .sort("count", descending=True)
                .head(10)
            )
            if len(df_esp) > 0:
                num_esp = len(df_esp)
                # Título dinâmico que mostra a quantidade real de especialidades no gráfico
                if num_esp == 1:
                    titulo_esp = "Especialidades (1 especialidade)"
                else:
                    titulo_esp = f"Especialidades ({num_esp} especialidades)"

                fig2 = go.Figure(
                    data=[
                        go.Bar(
                            y=df_esp["procedimento_especialidade"].to_list(),
                            x=df_esp["count"].to_list(),
                            orientation="h",
                            marker=dict(color="#003087"),
                        )
                    ]
                )
                fig2.update_layout(
                    title=titulo_esp,
                    height=450,
                    xaxis_title="Número de Solicitações",
                    yaxis_title="Especialidade",
                )
                grafico_especialidade_html = fig2.to_html(
                    full_html=False, include_plotlyjs="cdn"
                )

            # Gráfico 3: Pacientes SEM Agendamento - Distribuição por Risco
            df_sem_agend = df_filtrado.filter(
                ~pl.col("solicitacao_status").str.contains("AGENDAMENTO")
            )

            # Análise Preditiva
            predicao_sem_agendamento = (
                analisar_predicao_sem_agendamento(df_sem_agend)
                if len(df_sem_agend) > 0
                else None
            )

            if len(df_sem_agend) > 0:
                df_sem_agend_risco = df_sem_agend.group_by("solicitacao_risco").count()

                # Adicionar coluna de ordem para manter a sequência de criticidade
                df_sem_agend_ordenado = df_sem_agend_risco.with_columns(
                    [pl.col("solicitacao_risco").replace(ordem_map).alias("ordem")]
                ).sort("ordem")

                # Pegar apenas os riscos que EXISTEM nos dados (count > 0)
                riscos_sem = df_sem_agend_ordenado["solicitacao_risco"].to_list()
                valores_sem = df_sem_agend_ordenado["count"].to_list()
                cores_sem = [color_map[r] for r in riscos_sem]

                fig3 = go.Figure(
                    data=[
                        go.Bar(
                            x=riscos_sem,
                            y=valores_sem,
                            marker=dict(color=cores_sem),
                            text=valores_sem,
                            textposition="auto",
                            texttemplate="%{text:,}",
                        )
                    ]
                )
                fig3.update_layout(
                    title=f"Sem Agendamento por Risco ({len(df_sem_agend):,} pacientes)",
                    height=400,
                    xaxis_title="Nível de Risco",
                    yaxis_title="Quantidade de Pacientes",
                    showlegend=False,
                )
                grafico_sem_agendamento_html = fig3.to_html(
                    full_html=False, include_plotlyjs="cdn"
                )

            # Gráfico 4: Status de Pacientes SEM Agendamento
            if len(df_sem_agend) > 0:
                df_status_sem = (
                    df_sem_agend.group_by("solicitacao_status")
                    .count()
                    .sort("count", descending=True)
                    .head(8)
                )

                fig4 = go.Figure(
                    data=[
                        go.Bar(
                            x=df_status_sem["solicitacao_status"].to_list(),
                            y=df_status_sem["count"].to_list(),
                            marker=dict(
                                color=df_status_sem["count"].to_list(),
                                colorscale="Reds",
                                showscale=False,
                            ),
                            text=df_status_sem["count"].to_list(),
                            textposition="auto",
                            texttemplate="%{text:,}",
                        )
                    ]
                )
                fig4.update_layout(
                    title="Top 8 Status - Pacientes SEM Agendamento",
                    height=450,
                    xaxis_title="Status",
                    yaxis_title="Número de Pacientes",
                    xaxis={"tickangle": -45},
                )
                grafico_status_sem_agendamento_html = fig4.to_html(
                    full_html=False, include_plotlyjs="cdn"
                )

            # Gráficos detalhados para ESPECIALIDADE ÚNICA
            if especialidade_unica and total > 0:
                # Estatísticas da especialidade
                df_esp_unica = df_filtrado.filter(
                    pl.col("procedimento_especialidade") == especialidade_unica
                )
                total_esp = len(df_esp_unica)

                if total_esp > 0:
                    # Estatísticas
                    confirmados_esp = df_esp_unica.filter(
                        pl.col("solicitacao_status").str.contains("CONFIRMADO")
                    ).height
                    taxa_conf_esp = (
                        (confirmados_esp / total_esp * 100) if total_esp > 0 else 0
                    )

                    criticos_esp = df_esp_unica.filter(
                        pl.col("solicitacao_risco").is_in(["VERMELHO", "AMARELO"])
                    ).height
                    taxa_critico_esp = (
                        (criticos_esp / total_esp * 100) if total_esp > 0 else 0
                    )

                    sem_agend_esp = df_esp_unica.filter(
                        ~pl.col("solicitacao_status").str.contains("AGENDAMENTO")
                    ).height
                    taxa_sem_agend_esp = (
                        (sem_agend_esp / total_esp * 100) if total_esp > 0 else 0
                    )

                    estatisticas_especialidade = {
                        "total": total_esp,
                        "confirmados": confirmados_esp,
                        "taxa_confirmacao": taxa_conf_esp,
                        "criticos": criticos_esp,
                        "taxa_critico": taxa_critico_esp,
                        "sem_agendamento": sem_agend_esp,
                        "taxa_sem_agendamento": taxa_sem_agend_esp,
                    }

                    # Gráfico 1: Distribuição por Risco (especialidade única) - PIZZA
                    df_esp_risco = df_esp_unica.group_by("solicitacao_risco").count()

                    # Adicionar coluna de ordem para manter a sequência de criticidade
                    df_esp_risco_ordenado = df_esp_risco.with_columns(
                        [pl.col("solicitacao_risco").replace(ordem_map).alias("ordem")]
                    ).sort("ordem")

                    # Pegar apenas os riscos que EXISTEM nos dados (count > 0)
                    riscos_esp = df_esp_risco_ordenado["solicitacao_risco"].to_list()
                    valores_esp = df_esp_risco_ordenado["count"].to_list()
                    cores_esp = [color_map[r] for r in riscos_esp]

                    # Gráfico de Pizza (apenas com riscos que têm dados)
                    fig_esp1 = go.Figure(
                        data=[
                            go.Pie(
                                labels=riscos_esp,
                                values=valores_esp,
                                marker=dict(colors=cores_esp),
                                textinfo="value+percent",
                                texttemplate="%{value:,}<br>(%{percent})",
                                hole=0.3,  # Donut chart
                                sort=False,  # Não ordenar automaticamente, manter ordem dos dados
                            )
                        ]
                    )
                    fig_esp1.update_layout(
                        title=f"Distribuição por Risco - {especialidade_unica}",
                        height=350,
                        showlegend=True,
                        legend=dict(
                            orientation="v",
                            yanchor="middle",
                            y=0.5,
                            xanchor="right",
                            x=-0.05,  # Posicionar à esquerda
                            traceorder="normal",  # Manter ordem da série de dados
                        ),
                        margin=dict(l=150),  # Margem esquerda para acomodar a legenda
                    )
                    grafico_esp_risco_html = fig_esp1.to_html(
                        full_html=False, include_plotlyjs="cdn"
                    )

                    # Gráfico 2: Top 10 Status (especialidade única)
                    df_esp_status = (
                        df_esp_unica.group_by("solicitacao_status")
                        .count()
                        .sort("count", descending=True)
                        .head(10)
                    )

                    if len(df_esp_status) > 0:
                        fig_esp2 = go.Figure(
                            data=[
                                go.Bar(
                                    x=df_esp_status["solicitacao_status"].to_list(),
                                    y=df_esp_status["count"].to_list(),
                                    marker=dict(
                                        color=df_esp_status["count"].to_list(),
                                        colorscale="Viridis",
                                        showscale=False,
                                    ),
                                    text=df_esp_status["count"].to_list(),
                                    textposition="auto",
                                    texttemplate="%{text:,}",
                                )
                            ]
                        )
                        fig_esp2.update_layout(
                            title=f"Top 10 Status - {especialidade_unica}",
                            height=450,
                            xaxis_title="Status",
                            yaxis_title="Quantidade de Pacientes",
                            xaxis={"tickangle": -45},
                            margin=dict(
                                b=120
                            ),  # Margem inferior para labels rotacionados
                        )
                        grafico_esp_status_html = fig_esp2.to_html(
                            full_html=False, include_plotlyjs="cdn"
                        )

                    # Gráfico 3: Distribuição por Faixa Etária (especialidade única)
                    if "paciente_faixa_etaria" in df_esp_unica.columns:
                        df_esp_idade = (
                            df_esp_unica.group_by("paciente_faixa_etaria")
                            .count()
                            .sort("count", descending=True)
                            .head(10)
                        )

                        if len(df_esp_idade) > 0:
                            fig_esp3 = go.Figure(
                                data=[
                                    go.Bar(
                                        x=df_esp_idade[
                                            "paciente_faixa_etaria"
                                        ].to_list(),
                                        y=df_esp_idade["count"].to_list(),
                                        marker=dict(color="#17a2b8"),
                                        text=df_esp_idade["count"].to_list(),
                                        textposition="auto",
                                    )
                                ]
                            )
                            fig_esp3.update_layout(
                                title=f"Distribuição por Faixa Etária - {especialidade_unica}",
                                height=350,
                                xaxis_title="Faixa Etária",
                                yaxis_title="Quantidade de Pacientes",
                            )
                            grafico_esp_faixa_etaria_html = fig_esp3.to_html(
                                full_html=False, include_plotlyjs="cdn"
                            )

        # Opções de filtro
        # Ordem FIXA dos riscos (sempre a mesma ordem)
        riscos_disponiveis = ["VERMELHO", "AMARELO", "VERDE", "AZUL"]
        especialidades_disponiveis = sorted(
            df_completo["procedimento_especialidade"].unique().drop_nulls().to_list()
        )

        # Checkboxes com ordem fixa de risco e indicadores de cor
        cores_risco_badge = {
            "VERMELHO": "background-color: #dc3545; color: white;",
            "AMARELO": "background-color: #ffc107; color: black;",
            "VERDE": "background-color: #28a745; color: white;",
            "AZUL": "background-color: #007bff; color: white;",
        }

        riscos_html = "".join(
            [
                f'<div class="form-check form-check-inline">'
                f'<input class="form-check-input" type="checkbox" name="risco" value="{r}" id="r_{r}" {"checked" if not risco or r in risco else ""}>'
                f'<label class="form-check-label" for="r_{r}">'
                f'<span style="{cores_risco_badge[r]} padding: 2px 8px; border-radius: 4px; font-weight: 600; font-size: 0.85rem;">{r}</span>'
                f"</label></div>"
                for r in riscos_disponiveis
            ]
        )

        # Todas as especialidades em ordem alfabética
        especialidades_html = "".join(
            [
                f'<div class="form-check">'
                f'<input class="form-check-input" type="checkbox" name="especialidade" value="{e}" id="e_{i}" {"checked" if not especialidade or e in especialidade else ""}>'
                f'<label class="form-check-label" for="e_{i}">{e}</label></div>'
                for i, e in enumerate(especialidades_disponiveis)
            ]
        )

        # Preparar dados para tabelas (TODOS os registros em JSON para paginação)
        import json

        dados_geral = []
        dados_confirmados = []
        dados_criticos = []
        dados_sem_agendamento = []

        total_geral = 0
        total_confirmados = 0
        total_criticos = 0
        total_sem_agendamento = 0

        if not df_filtrado.is_empty():
            colunas_exibir = [
                "solicitacao_id",
                "paciente_faixa_etaria",
                "solicitacao_risco",
                "solicitacao_status",
                "procedimento_especialidade",
                "data_solicitacao",
            ]
            colunas_disponiveis = [
                c for c in colunas_exibir if c in df_filtrado.columns
            ]

            # Função para converter datas para string - solução robusta
            def preparar_dados_json(df):
                import datetime

                # Converter TODAS as colunas de data/datetime para string no Polars
                for col in df.columns:
                    dtype = df[col].dtype
                    if dtype in [pl.Date, pl.Datetime, pl.Time]:
                        df = df.with_columns(pl.col(col).cast(pl.Utf8).alias(col))

                # Converter para pandas (lida melhor com tipos) e depois para dict
                df_pandas = df.to_pandas()

                # Converter colunas datetime do pandas para string
                for col in df_pandas.columns:
                    if df_pandas[col].dtype == "object":
                        df_pandas[col] = df_pandas[col].apply(
                            lambda x: (
                                str(x)
                                if isinstance(
                                    x, (datetime.datetime, datetime.date, datetime.time)
                                )
                                else x
                            )
                        )

                # Converter para lista de dicionários
                dados = df_pandas.to_dict("records")

                # Última verificação: garantir que TODOS os valores são serializáveis
                for row in dados:
                    for key, value in list(row.items()):
                        if isinstance(
                            value, (datetime.datetime, datetime.date, datetime.time)
                        ):
                            row[key] = str(value)
                        elif hasattr(value, "__dict__") and not isinstance(
                            value, (str, int, float, bool, type(None))
                        ):
                            row[key] = str(value)

                return dados

            # Limitar dados para performance (máximo 5000 registros por tabela)
            LIMITE_REGISTROS = 5000

            # Dados gerais - Limitados para performance
            df_temp = df_filtrado.select(colunas_disponiveis)
            total_geral = len(df_temp)
            dados_geral = preparar_dados_json(df_temp.head(LIMITE_REGISTROS))

            # Confirmados - Limitados para performance
            if confirmados > 0:
                df_confirmados_temp = df_filtrado.filter(
                    pl.col("solicitacao_status").str.contains("CONFIRMADO")
                ).select(colunas_disponiveis)
                total_confirmados = len(df_confirmados_temp)
                dados_confirmados = preparar_dados_json(
                    df_confirmados_temp.head(LIMITE_REGISTROS)
                )

            # Risco Crítico - Limitados para performance
            if criticos > 0:
                df_criticos_temp = df_filtrado.filter(
                    pl.col("solicitacao_risco").is_in(["VERMELHO", "AMARELO"])
                ).select(colunas_disponiveis)
                total_criticos = len(df_criticos_temp)
                dados_criticos = preparar_dados_json(
                    df_criticos_temp.head(LIMITE_REGISTROS)
                )

            # Sem Agendamento - Limitados para performance
            if nao_agendados > 0:
                df_sem_agend_temp = df_filtrado.filter(
                    ~pl.col("solicitacao_status").str.contains("AGENDAMENTO")
                ).select(colunas_disponiveis)
                total_sem_agendamento = len(df_sem_agend_temp)
                dados_sem_agendamento = preparar_dados_json(
                    df_sem_agend_temp.head(LIMITE_REGISTROS)
                )

        # Converter para JSON (escape para JavaScript) com tratamento de erro
        try:
            dados_geral_json = json.dumps(dados_geral, default=str)
            dados_confirmados_json = json.dumps(dados_confirmados, default=str)
            dados_criticos_json = json.dumps(dados_criticos, default=str)
            dados_sem_agendamento_json = json.dumps(dados_sem_agendamento, default=str)
        except Exception as e:
            print(f"ERRO ao serializar JSON: {e}")
            # Fallback: usar default=str para converter qualquer objeto não serializável
            dados_geral_json = json.dumps(dados_geral, default=str)
            dados_confirmados_json = json.dumps(dados_confirmados, default=str)
            dados_criticos_json = json.dumps(dados_criticos, default=str)
            dados_sem_agendamento_json = json.dumps(dados_sem_agendamento, default=str)

        # Nomes das colunas para o cabeçalho
        colunas_nomes = {
            "solicitacao_id": "ID Solicitação",
            "paciente_faixa_etaria": "Faixa Etária",
            "solicitacao_risco": "Risco",
            "solicitacao_status": "Status",
            "procedimento_especialidade": "Especialidade",
            "data_solicitacao": "Data Solicitação",
        }

        if not df_filtrado.is_empty():
            colunas_disponiveis_nomes = [
                colunas_nomes.get(c, c) for c in colunas_disponiveis
            ]
        else:
            colunas_disponiveis = []
            colunas_disponiveis_nomes = []

        # HTML
        return HTMLResponse(
            f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gestão Inteligente de Vagas - GIV</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>

        body {{
            background: linear-gradient(135deg, #003087 0%, #764ba2 100%);
            min-height: 100vh;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            padding: 20px;
        }}
        .navbar {{
            background: rgba(255,255,255,0.95);
            border-radius: 15px;
            padding: 15px 30px;
            margin-bottom: 20px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        }}
        .main-container {{
            background: rgba(255,255,255,0.95);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }}
            .kpi-card {{
                background: linear-gradient(135deg, #003087 0%, #764ba2 100%);
                color: white;
                border-radius: 15px;
                padding: 30px;
                margin-bottom: 20px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                text-align: center;
                transition: all 0.3s;
                cursor: pointer;
            }}
            .kpi-card:hover {{
                transform: translateY(-5px);
                box-shadow: 0 15px 40px rgba(0,0,0,0.2);
            }}
            .kpi-card:active {{
                transform: translateY(-2px);
            }}
            .kpi-card.active {{
                box-shadow: 0 0 20px rgba(102, 126, 234, 0.6);
                border: 2px solid white;
            }}
        .kpi-icon {{
            font-size: 2.5rem;
            margin-bottom: 10px;
            opacity: 0.9;
        }}
        .kpi-value {{
            font-size: 2.5rem;
            font-weight: bold;
            margin: 10px 0;
        }}
        .kpi-label {{
            font-size: 1rem;
            opacity: 0.9;
        }}
        .chart-card {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.05);
        }}
        .filter-card {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.05);
        }}
        .filter-section {{
            background: #f8f9fa;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 15px;
            max-height: 250px;
            overflow-y: auto;
        }}
        .form-check-inline {{
            margin-right: 15px;
            margin-bottom: 10px;
        }}
        .form-check-inline .form-check-label {{
            cursor: pointer;
        }}
            .btn-filtrar {{
                background: linear-gradient(135deg, #003087 0%, #764ba2 100%);
                border: none;
                padding: 12px 40px;
                font-weight: 600;
                border-radius: 25px;
            }}
            
            .data-section {{
                display: none;
                margin-top: 30px;
                animation: fadeIn 0.5s;
            }}
            
            .data-section.show {{
                display: block;
            }}
            
            .table-responsive {{
                max-height: 500px;
                overflow-y: auto;
                border-radius: 10px;
            }}
            
            .pagination-controls {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-top: 15px;
                padding: 15px;
                background: #f8f9fa;
                border-radius: 10px;
            }}
            
            .pagination-buttons {{
                display: flex;
                gap: 10px;
            }}
            
            .pagination-buttons button {{
                padding: 8px 16px;
                border: 1px solid #dee2e6;
                background: white;
                border-radius: 5px;
                cursor: pointer;
                transition: all 0.3s;
            }}
            
            .pagination-buttons button:hover:not(:disabled) {{
                background: #003087;
                color: white;
                border-color: #003087;
            }}
            
            .pagination-buttons button:disabled {{
                opacity: 0.5;
                cursor: not-allowed;
            }}
            
            .pagination-info {{
                font-weight: 600;
                color: #495057;
            }}
            
            .page-size-select {{
                padding: 5px 10px;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                margin-left: 10px;
            }}
            
            .sortable-header {{
                cursor: pointer;
                user-select: none;
                position: relative;
                padding-right: 20px;
                transition: all 0.2s ease;
            }}
            
            .sortable-header:hover {{
                background-color: #e9ecef;
                transform: translateY(-2px);
            }}
            
            .sortable-header:active {{
                transform: translateY(0);
            }}
            
            .sort-indicator {{
                position: absolute;
                right: 5px;
                font-size: 0.8rem;
                color: #003087;
                font-weight: bold;
                animation: fadeIn 0.3s ease;
            }}
            
            @keyframes fadeIn {{
                from {{
                    opacity: 0;
                    transform: scale(0.5);
                }}
                to {{
                    opacity: 1;
                    transform: scale(1);
                }}
            }}
            
            @keyframes slideDown {{
                from {{
                    opacity: 0;
                    transform: translateY(-20px);
                }}
                to {{
                    opacity: 1;
                    transform: translateY(0);
                }}
            }}
            
            .especialidade-detalhada {{
                animation: slideDown 0.6s ease;
                border-left: 5px solid #003087;
                margin-bottom: 30px;
            }}
            
            .table thead th {{
                background-color: #f8f9fa;
                font-weight: 600;
                border-bottom: 2px solid #dee2e6;
                padding: 12px 8px;
                vertical-align: middle;
            }}
            
            .table tbody td {{
                vertical-align: middle;
            }}
        </style>
</head>
<body>
    <!-- Navbar -->
    <nav class="navbar">
        <div class="container-fluid">
            <span class="navbar-brand mb-0 h1">
                <i class="fas fa-hospital text-primary"></i>
                Gestão Inteligente de Vagas - GIV
            </span>
            <div>
                <span class="me-3">
                    <i class="fas fa-user"></i> {current_user}
                </span>
                <a href="/logout" class="btn btn-sm btn-outline-danger">
                    <i class="fas fa-sign-out-alt"></i> Sair
                </a>
            </div>
        </div>
    </nav>

    <div class="main-container">
        <!-- KPIs Clicáveis -->
        <div class="row mb-4">
            <div class="col-lg-3 col-md-6 mb-3">
                <div class="kpi-card" onclick="toggleDataSection('geral')" data-table="geral">
                    <i class="fas fa-file-medical kpi-icon"></i>
                    <div class="kpi-value">{total:,}</div>
                    <div class="kpi-label">Solicitações Filtradas</div>
                    <small class="text-white-50 mt-2 d-block">Clique para ver dados</small>
                </div>
            </div>
            <div class="col-lg-3 col-md-6 mb-3">
                <div class="kpi-card" onclick="toggleDataSection('confirmados')" data-table="confirmados">
                    <i class="fas fa-check-circle kpi-icon"></i>
                    <div class="kpi-value">{taxa_conf:.1f}%</div>
                    <div class="kpi-label">Taxa Confirmação</div>
                    <small class="text-white-50 mt-2 d-block">Clique para ver dados</small>
                </div>
            </div>
            <div class="col-lg-3 col-md-6 mb-3">
                <div class="kpi-card" onclick="toggleDataSection('criticos')" data-table="criticos">
                    <i class="fas fa-exclamation-triangle kpi-icon"></i>
                    <div class="kpi-value">{risco_critico:.1f}%</div>
                    <div class="kpi-label">Risco Crítico</div>
                    <small class="text-white-50 mt-2 d-block">Clique para ver dados</small>
                </div>
            </div>
            <div class="col-lg-3 col-md-6 mb-3">
                <div class="kpi-card" style="background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);" onclick="toggleDataSection('sem-agendamento')" data-table="sem-agendamento">
                    <i class="fas fa-calendar-times kpi-icon"></i>
                    <div class="kpi-value">{sem_agendamento_total:,}</div>
                    <div class="kpi-label">Sem Agendamento ({sem_agendamento:.1f}%)</div>
                    <small class="text-white-50 mt-2 d-block">Clique para ver dados</small>
                </div>
            </div>
        </div>

        <!-- Filtros -->
        <div class="filter-card">
            <h5><i class="fas fa-filter"></i> Filtros</h5>
            <div class="alert alert-info" style="padding: 10px; font-size: 0.9rem; margin-bottom: 15px;">
                <i class="fas fa-lightbulb me-2"></i>
                <strong>Dica:</strong> Selecione apenas <strong>1 especialidade</strong> para ver uma análise detalhada completa com gráficos e estatísticas específicas!
            </div>
            <form method="get" action="/dashboard">
                <div class="row">
                    <div class="col-md-6">
                        <label class="form-label fw-bold">Nível de Risco:</label>
                        <div class="filter-section">
                            <div class="form-check mb-2" style="background: #e3f2fd; padding: 8px; border-radius: 5px; border-left: 3px solid #2196f3;">
                                <input class="form-check-input" type="checkbox" id="selecionar-todos-riscos" onchange="toggleTodosRiscos(this)" checked>
                                <label class="form-check-label fw-bold" for="selecionar-todos-riscos" style="color: #1976d2;">
                                    <i class="fas fa-check-double"></i> Selecionar Todos
                                </label>
                            </div>
                            {riscos_html}
                        </div>
                    </div>
                    <div class="col-md-6">
                        <label class="form-label fw-bold">Especialidade:</label>
                        <div class="filter-section">
                            <div class="form-check mb-2" style="background: #e8f5e9; padding: 8px; border-radius: 5px; border-left: 3px solid #4caf50;">
                                <input class="form-check-input" type="checkbox" id="selecionar-todas-especialidades" onchange="toggleTodasEspecialidades(this)" checked>
                                <label class="form-check-label fw-bold" for="selecionar-todas-especialidades" style="color: #2e7d32;">
                                    <i class="fas fa-check-double"></i> Selecionar Todas
                                </label>
                            </div>
                            {especialidades_html}
                        </div>
                    </div>
                </div>
                <div class="text-center mt-3">
                    <button type="submit" class="btn btn-primary btn-filtrar text-white">
                        <i class="fas fa-search"></i> Aplicar Filtros
                    </button>
                </div>
            </form>
        </div>

        <!-- Gráficos Principais -->
        <h5 class="mb-3"><i class="fas fa-chart-column me-2"></i>Visão Geral</h5>
        <div class="row mb-4">
            <div class="col-lg-6 mb-3">
                <div class="chart-card">
                    <h6 class="mb-3">Distribuição por Risco</h6>
                    {grafico_risco_html if grafico_risco_html else '<div class="text-center text-muted p-5"><i class="fas fa-chart-column fa-3x mb-3"></i><p>Nenhum dado disponível</p></div>'}
                </div>
            </div>
            <div class="col-lg-6 mb-3">
                <div class="chart-card">
                    <h6 class="mb-3">Especialidades</h6>
                    {grafico_especialidade_html if grafico_especialidade_html else '<div class="text-center text-muted p-5"><i class="fas fa-chart-bar fa-3x mb-3"></i><p>Nenhum dado disponível</p></div>'}
                </div>
            </div>
        </div>

        <!-- Seção de Detalhamento de Especialidade Única -->
        {f'''
        <div class="especialidade-detalhada">
            <div class="alert alert-primary" role="alert" style="background: linear-gradient(135deg, #003087 0%, #764ba2 100%); border: none; color: white;">
                <h5 class="alert-heading"><i class="fas fa-microscope me-2"></i>Análise Detalhada: {especialidade_unica}</h5>
                <p class="mb-0">Detalhamento completo dos dados da especialidade selecionada.</p>
            </div>
        
        <!-- KPIs da Especialidade -->
        <div class="row mb-4">
            <div class="col-lg-3 col-md-6 mb-3">
                <div class="chart-card text-center" style="background: linear-gradient(135deg, #003087 0%, #764ba2 100%); color: white;">
                    <i class="fas fa-list-alt" style="font-size: 2rem; margin-bottom: 10px;"></i>
                    <h3 class="mb-2">{estatisticas_especialidade['total']:,}</h3>
                    <p class="mb-0">Total de Solicitações</p>
                </div>
            </div>
            <div class="col-lg-3 col-md-6 mb-3">
                <div class="chart-card text-center" style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%); color: white;">
                    <i class="fas fa-check-circle" style="font-size: 2rem; margin-bottom: 10px;"></i>
                    <h3 class="mb-2">{estatisticas_especialidade['taxa_confirmacao']:.1f}%</h3>
                    <p class="mb-0">Taxa de Confirmação</p>
                    <small>({estatisticas_especialidade['confirmados']:,} confirmados)</small>
                </div>
            </div>
            <div class="col-lg-3 col-md-6 mb-3">
                <div class="chart-card text-center" style="background: linear-gradient(135deg, #ffc107 0%, #ff9800 100%); color: white;">
                    <i class="fas fa-exclamation-triangle" style="font-size: 2rem; margin-bottom: 10px;"></i>
                    <h3 class="mb-2">{estatisticas_especialidade['taxa_critico']:.1f}%</h3>
                    <p class="mb-0">Risco Crítico</p>
                    <small>({estatisticas_especialidade['criticos']:,} pacientes)</small>
                </div>
            </div>
            <div class="col-lg-3 col-md-6 mb-3">
                <div class="chart-card text-center" style="background: linear-gradient(135deg, #dc3545 0%, #c82333 100%); color: white;">
                    <i class="fas fa-calendar-times" style="font-size: 2rem; margin-bottom: 10px;"></i>
                    <h3 class="mb-2">{estatisticas_especialidade['sem_agendamento']:,}</h3>
                    <p class="mb-0">Sem Agendamento</p>
                    <small>({estatisticas_especialidade['taxa_sem_agendamento']:.1f}%)</small>
                </div>
            </div>
        </div>
        
        <!-- Gráficos Detalhados da Especialidade -->
        <!-- Linha 1: Risco e Faixa Etária -->
        <div class="row mb-4">
            <div class="col-lg-6 mb-3">
                <div class="chart-card">
                    <h6 class="mb-3">Distribuição por Risco</h6>
                    {grafico_esp_risco_html if grafico_esp_risco_html else '<div class="text-center text-muted p-5"><p>Nenhum dado disponível</p></div>'}
                </div>
            </div>
            <div class="col-lg-6 mb-3">
                <div class="chart-card">
                    <h6 class="mb-3">Faixa Etária</h6>
                    {grafico_esp_faixa_etaria_html if grafico_esp_faixa_etaria_html else '<div class="text-center text-muted p-5"><p>Nenhum dado disponível</p></div>'}
                </div>
            </div>
        </div>
        
        <!-- Linha 2: Status dos Pacientes (linha exclusiva) -->
        <div class="row mb-4">
            <div class="col-12">
                <div class="chart-card">
                    <h6 class="mb-3">Status dos Pacientes</h6>
                    {grafico_esp_status_html if grafico_esp_status_html else '<div class="text-center text-muted p-5"><p>Nenhum dado disponível</p></div>'}
                </div>
            </div>
        </div>
        </div>
        ''' if especialidade_unica and estatisticas_especialidade else ''}

        <!-- Seção de Pacientes SEM Agendamento -->
        {f'''
        <div class="alert alert-danger" role="alert">
            <h5 class="alert-heading"><i class="fas fa-calendar-times me-2"></i>Pacientes SEM Agendamento</h5>
            <p class="mb-0">Atenção: <strong>{sem_agendamento_total:,} pacientes ({sem_agendamento:.1f}%)</strong> não tiveram agendamento marcado.</p>
        </div>
        
        <!-- Análise Preditiva: O que acontece se nada for feito? -->
        {f"""
        <div class="alert alert-warning" role="alert" style="background: linear-gradient(135deg, #003087 0%, #764ba2 100%); border: none; color: white; margin-bottom: 30px;">
            <h5 class="alert-heading">
                <i class="fas fa-brain me-2"></i>🤖 Análise Preditiva com Machine Learning
            </h5>
            <p class="mb-2">
                <strong>Algoritmo:</strong> {predicao_sem_agendamento.get('algoritmo', 'Random Forest Classifier')} 
                {f"({predicao_sem_agendamento.get('num_arvores', 100)} árvores de decisão)" if predicao_sem_agendamento.get('usa_ml') else ''}
            </p>
            <p class="mb-0">
                <strong>Projeção:</strong> Impacto estimado se nenhum agendamento for realizado para os {predicao_sem_agendamento['total_sem_agendamento']:,} pacientes sem atendimento.
            </p>
        </div>
        
        <!-- Métricas do Modelo ML -->
        {f'''
        <div class="row mb-4">
            <div class="col-12">
                <div class="alert alert-info" role="alert">
                    <h6><i class="fas fa-chart-line me-2"></i>Performance do Modelo de Machine Learning</h6>
                    <div class="row">
                        <div class="col-md-3">
                            <strong>Acurácia:</strong> {predicao_sem_agendamento.get('modelo_metricas', {}).get('acuracia', 0):.1%}
                        </div>
                        <div class="col-md-3">
                            <strong>Precisão:</strong> {predicao_sem_agendamento.get('modelo_metricas', {}).get('precisao', 0):.1%}
                        </div>
                        <div class="col-md-3">
                            <strong>Recall:</strong> {predicao_sem_agendamento.get('modelo_metricas', {}).get('recall', 0):.1%}
                        </div>
                        <div class="col-md-3">
                            <strong>F1-Score:</strong> {predicao_sem_agendamento.get('modelo_metricas', {}).get('f1_score', 0):.1%}
                        </div>
                    </div>
                    <small class="text-muted mt-2 d-block">
                        <i class="fas fa-info-circle me-1"></i>
                        Modelo treinado com {predicao_sem_agendamento.get('modelo_metricas', {}).get('total_treino', 0):,} amostras | 
                        Testado com {predicao_sem_agendamento.get('modelo_metricas', {}).get('total_teste', 0):,} amostras
                    </small>
                </div>
            </div>
        </div>
        ''' if predicao_sem_agendamento.get('usa_ml') and 'modelo_metricas' in predicao_sem_agendamento else ''}
        
        
        <!-- KPIs de Predição -->
        <div class="row mb-4">
            <div class="col-lg-3 col-md-6 mb-3">
                <div class="chart-card text-center" style="background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%); color: white; border-left: 5px solid #c0392b;">
                    <i class="fas fa-user-injured" style="font-size: 2.5rem; margin-bottom: 10px; opacity: 0.9;"></i>
                    <h2 class="mb-2">{predicao_sem_agendamento['agravamento_30_dias']:,}</h2>
                    <p class="mb-1"><strong>Agravamentos em 30 dias</strong></p>
                    <small style="opacity: 0.8;">Baseado em {predicao_sem_agendamento.get('alto_risco_ml', 0):,} pacientes de alto risco (ML)</small>
                </div>
            </div>
            <div class="col-lg-3 col-md-6 mb-3">
                <div class="chart-card text-center" style="background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%); color: white; border-left: 5px solid #d35400;">
                    <i class="fas fa-bed" style="font-size: 2.5rem; margin-bottom: 10px; opacity: 0.9;"></i>
                    <h2 class="mb-2">{predicao_sem_agendamento['internacoes_projetadas']:,}</h2>
                    <p class="mb-1"><strong>Internações Projetadas</strong></p>
                    <small style="opacity: 0.8;">30% dos agravamentos resultam em internação hospitalar</small>
                </div>
            </div>
            <div class="col-lg-3 col-md-6 mb-3">
                <div class="chart-card text-center" style="background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%); color: white; border-left: 5px solid #a93226;">
                    <i class="fas fa-dollar-sign" style="font-size: 2.5rem; margin-bottom: 10px; opacity: 0.9;"></i>
                    <h2 class="mb-2">R$ {predicao_sem_agendamento['custo_estimado_30_dias']:,.0f}</h2>
                    <p class="mb-1"><strong>Custo Estimado (30 dias)</strong></p>
                    <small style="opacity: 0.8;">R$ 5.000/agravamento em média</small>
                </div>
            </div>
            <div class="col-lg-3 col-md-6 mb-3">
                <div class="chart-card text-center" style="background: linear-gradient(135deg, #8e44ad 0%, #6c3483 100%); color: white; border-left: 5px solid #5b2c6f;">
                    <i class="fas fa-chart-line" style="font-size: 2.5rem; margin-bottom: 10px; opacity: 0.9;"></i>
                    <h2 class="mb-2">R$ {predicao_sem_agendamento['custo_estimado_total']:,.0f}</h2>
                    <p class="mb-1"><strong>Custo Total Projetado</strong></p>
                    <small style="opacity: 0.8;">Impacto financeiro total estimado em 90 dias</small>
                </div>
            </div>
        </div>
        
        <!-- Timeline de Agravamento -->
        <div class="chart-card mb-4">
            <h5 class="mb-3"><i class="fas fa-clock me-2"></i>Linha do Tempo de Agravamentos Projetados</h5>
            <div class="row">
                <div class="col-md-4">
                    <div class="alert alert-danger">
                        <h6><i class="fas fa-calendar-day me-2"></i>30 Dias</h6>
                        <h3>{predicao_sem_agendamento['agravamento_30_dias']:,} pacientes</h3>
                        <p class="mb-0 small">Principalmente riscos <strong>VERMELHO</strong> (80% de chance)</p>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="alert alert-warning">
                        <h6><i class="fas fa-calendar-week me-2"></i>60 Dias</h6>
                        <h3>{predicao_sem_agendamento['agravamento_60_dias']:,} pacientes</h3>
                        <p class="mb-0 small">Riscos <strong>AMARELO</strong> e <strong>VERDE</strong> (20-50% de chance)</p>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="alert alert-info">
                        <h6><i class="fas fa-calendar-alt me-2"></i>90 Dias</h6>
                        <h3>{predicao_sem_agendamento['agravamento_90_dias']:,} pacientes</h3>
                        <p class="mb-0 small">Riscos <strong>AZUL</strong> (5% de chance)</p>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Top 10 Especialidades Mais Críticas sem Agendamento -->
        {f'''
        <div class="chart-card mb-4">
            <h5 class="mb-3">
                <i class="fas fa-list-ol me-2"></i>Top 10 Especialidades Mais Críticas sem Agendamento
                {' <span class="badge bg-primary">🤖 ML</span>' if predicao_sem_agendamento.get('usa_ml') else ''}
            </h5>
            <div class="table-responsive">
                <table class="table table-hover">
                    <thead class="table-danger">
                        <tr>
                            <th>#</th>
                            <th>Especialidade</th>
                            <th>Total sem Agendamento</th>
                            {f'<th>Prob. Média Agravamento (ML)</th>' if predicao_sem_agendamento.get('usa_ml') else '<th>Pacientes Críticos</th>'}
                            <th>Alto Risco ML</th>
                            <th>Classificação</th>
                        </tr>
                    </thead>
                    <tbody>
                        {"".join([
                            f'''<tr class="{'table-danger' if esp.get('prob_media', esp.get('criticos', 0) / esp['total']) > 0.6 else 'table-warning' if esp.get('prob_media', esp.get('criticos', 0) / esp['total']) > 0.4 else ''}">
                                <td><strong>{idx + 1}</strong></td>
                                <td><strong>{esp['procedimento_especialidade']}</strong></td>
                                <td>{esp['total']:,}</td>
                                <td>
                                    {f"{esp.get('prob_media', 0):.1%}" if predicao_sem_agendamento.get('usa_ml') else f"{esp.get('criticos', 0):,}"}
                                </td>
                                <td>{esp.get('alto_risco_count', esp.get('criticos', 0)):,}</td>
                                <td>
                                    {('<span class="badge bg-danger">🔴 CRÍTICO</span>' if esp.get('prob_media', esp.get('criticos', 0) / esp['total']) > 0.6 else 
                                     '<span class="badge bg-warning text-dark">🟡 ALTO</span>' if esp.get('prob_media', esp.get('criticos', 0) / esp['total']) > 0.4 else 
                                     '<span class="badge bg-info">🟢 MÉDIO</span>')}
                                </td>
                            </tr>'''
                            for idx, esp in enumerate(predicao_sem_agendamento.get('especialidades_criticas_ml', predicao_sem_agendamento.get('especialidades_criticas', [])))
                        ])}
                    </tbody>
                </table>
            </div>
            {f'''<small class="text-muted">
                <i class="fas fa-lightbulb me-1"></i>
                <strong>ML:</strong> Probabilidades calculadas pelo modelo Random Forest considerando múltiplas variáveis (risco, tempo espera, idade, especialidade).
            </small>''' if predicao_sem_agendamento.get('usa_ml') else ''}
        </div>
        ''' if len(predicao_sem_agendamento.get('especialidades_criticas_ml', predicao_sem_agendamento.get('especialidades_criticas', []))) > 0 else ''}
        
        <!-- Informações sobre o Modelo -->
        <div class="alert alert-light border" role="alert">
            {f'''
            <h6><i class="fas fa-brain me-2"></i>Como Funciona o Machine Learning</h6>
            <div class="row">
                <div class="col-md-6">
                    <h6 class="text-primary mt-2">🎯 Algoritmo</h6>
                    <ul class="small mb-3">
                        <li><strong>Random Forest Classifier</strong> com 100 árvores de decisão</li>
                        <li>Treinado com {predicao_sem_agendamento['modelo_metricas']['total_treino']:,} amostras</li>
                        <li>Validado com {predicao_sem_agendamento['modelo_metricas']['total_teste']:,} amostras</li>
                        <li>Acurácia: {predicao_sem_agendamento['modelo_metricas']['acuracia']:.1%}</li>
                    </ul>
                    
                    <h6 class="text-primary">🔍 Features Utilizadas</h6>
                    <ul class="small mb-0">
                        <li><strong>Risco do Paciente:</strong> Vermelho, Amarelo, Verde, Azul</li>
                        <li><strong>Tempo de Espera:</strong> Dias aguardando atendimento</li>
                        <li><strong>Idade:</strong> Faixa etária do paciente</li>
                        <li><strong>Especialidade:</strong> Tipo de procedimento solicitado</li>
                        <li><strong>Status Crítico:</strong> Indicadores de urgência</li>
                    </ul>
                </div>
                <div class="col-md-6">
                    <h6 class="text-success mt-2">✅ Vantagens do ML</h6>
                    <ul class="small mb-3">
                        <li>Aprende padrões complexos dos dados históricos</li>
                        <li>Predições personalizadas para cada paciente</li>
                        <li>Considera múltiplas variáveis simultaneamente</li>
                        <li>Se adapta automaticamente a novos dados</li>
                    </ul>
                    
                    <h6 class="text-info">💰 Premissas Financeiras</h6>
                    <ul class="small mb-0">
                        <li><strong>Custo por Agravamento:</strong> R$ 5.000,00 (média hospitalar)</li>
                        <li><strong>Taxa de Internação:</strong> 30% dos casos graves</li>
                        <li><strong>Classificação de Risco:</strong>
                            <ul>
                                <li>Alto: Probabilidade > 70%</li>
                                <li>Médio: Probabilidade 40-70%</li>
                                <li>Baixo: Probabilidade < 40%</li>
                            </ul>
                        </li>
                    </ul>
                </div>
            </div>
            ''' if predicao_sem_agendamento.get('usa_ml') else '''
            <h6><i class="fas fa-info-circle me-2"></i>Premissas do Modelo Baseado em Regras</h6>
            <ul class="mb-0 small">
                <li><strong>Risco VERMELHO:</strong> 80% de chance de agravamento em 30 dias</li>
                <li><strong>Risco AMARELO:</strong> 50% de chance de agravamento em 60 dias</li>
                <li><strong>Risco VERDE:</strong> 20% de chance de agravamento em 90 dias</li>
                <li><strong>Risco AZUL:</strong> 5% de chance de agravamento em 120 dias</li>
                <li><strong>Taxa de Internação:</strong> 30% dos agravamentos resultam em internação hospitalar</li>
                <li><strong>Custo Médio:</strong> R$ 5.000,00 por agravamento (baseado em custos médios hospitalares)</li>
            </ul>
            '''}
        </div>
        """ if predicao_sem_agendamento else ''}
        
        <div class="row mb-4">
            <div class="col-lg-6 mb-3">
                <div class="chart-card">
                    <h6 class="mb-3">Sem Agendamento - Distribuição por Risco</h6>
                    {grafico_sem_agendamento_html if grafico_sem_agendamento_html else '<div class="text-center text-muted p-5"><i class="fas fa-chart-column fa-3x mb-3"></i><p>Nenhum paciente sem agendamento</p></div>'}
                </div>
            </div>
            <div class="col-lg-6 mb-3">
                <div class="chart-card">
                    <h6 class="mb-3">Sem Agendamento - Status</h6>
                    {grafico_status_sem_agendamento_html if grafico_status_sem_agendamento_html else '<div class="text-center text-muted p-5"><i class="fas fa-chart-bar fa-3x mb-3"></i><p>Nenhum paciente sem agendamento</p></div>'}
                </div>
            </div>
        </div>
        ''' if sem_agendamento_total > 0 else ''}

        <!-- Seção de Dados Detalhados -->
        <div id="data-section-container">
            <!-- Tabela 1: Dados Gerais -->
            <div id="data-geral" class="data-section">
                <div class="chart-card">
                    <h5 class="mb-3">
                        <i class="fas fa-table me-2"></i>
                        Dados Gerais (Exibindo até 5.000 de {total_geral:,} registros)
                    </h5>
                    <div class="alert alert-info alert-dismissible fade show" role="alert" style="padding: 8px 15px; font-size: 0.9rem;">
                        <i class="fas fa-info-circle me-2"></i>
                        <strong>Dica:</strong> Clique nos cabeçalhos das colunas para ordenar os dados. Clique novamente para inverter a ordem.
                        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close" style="padding: 8px; font-size: 0.7rem;"></button>
                    </div>
                    <div class="table-responsive">
                        <table class="table table-striped table-hover table-sm" id="table-geral">
                            <thead><tr id="thead-geral"></tr></thead>
                            <tbody id="tbody-geral"></tbody>
                        </table>
                    </div>
                    <div class="pagination-controls">
                        <div class="pagination-info">
                            <span id="info-geral">Mostrando 0 de 0 registros</span>
                            <select class="page-size-select" id="pagesize-geral" onchange="changePageSize('geral')">
                                <option value="25">25 por página</option>
                                <option value="50" selected>50 por página</option>
                                <option value="100">100 por página</option>
                                <option value="500">500 por página</option>
                            </select>
                        </div>
                        <div class="pagination-buttons">
                            <button onclick="changePage('geral', 'first')">Primeira</button>
                            <button onclick="changePage('geral', 'prev')">Anterior</button>
                            <span class="pagination-info" id="page-geral">Página 1 de 1</span>
                            <button onclick="changePage('geral', 'next')">Próxima</button>
                            <button onclick="changePage('geral', 'last')">Última</button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Tabela 2: Confirmados -->
            <div id="data-confirmados" class="data-section">
                <div class="chart-card">
                    <h5 class="mb-3">
                        <i class="fas fa-check-circle me-2"></i>
                        Pacientes Confirmados (Exibindo até 5.000 de {total_confirmados:,} registros)
                    </h5>
                    <div class="alert alert-info alert-dismissible fade show" role="alert" style="padding: 8px 15px; font-size: 0.9rem;">
                        <i class="fas fa-info-circle me-2"></i>
                        <strong>Dica:</strong> Clique nos cabeçalhos das colunas para ordenar os dados. Clique novamente para inverter a ordem.
                        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close" style="padding: 8px; font-size: 0.7rem;"></button>
                    </div>
                    <div class="table-responsive">
                        <table class="table table-striped table-hover table-sm" id="table-confirmados">
                            <thead><tr id="thead-confirmados"></tr></thead>
                            <tbody id="tbody-confirmados"></tbody>
                        </table>
                    </div>
                    <div class="pagination-controls">
                        <div class="pagination-info">
                            <span id="info-confirmados">Mostrando 0 de 0 registros</span>
                            <select class="page-size-select" id="pagesize-confirmados" onchange="changePageSize('confirmados')">
                                <option value="25">25 por página</option>
                                <option value="50" selected>50 por página</option>
                                <option value="100">100 por página</option>
                                <option value="500">500 por página</option>
                            </select>
                        </div>
                        <div class="pagination-buttons">
                            <button onclick="changePage('confirmados', 'first')">Primeira</button>
                            <button onclick="changePage('confirmados', 'prev')">Anterior</button>
                            <span class="pagination-info" id="page-confirmados">Página 1 de 1</span>
                            <button onclick="changePage('confirmados', 'next')">Próxima</button>
                            <button onclick="changePage('confirmados', 'last')">Última</button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Tabela 3: Risco Crítico -->
            <div id="data-criticos" class="data-section">
                <div class="chart-card">
                    <h5 class="mb-3">
                        <i class="fas fa-exclamation-triangle me-2"></i>
                        Pacientes com Risco Crítico (Exibindo até 5.000 de {total_criticos:,} registros)
                    </h5>
                    <div class="alert alert-info alert-dismissible fade show" role="alert" style="padding: 8px 15px; font-size: 0.9rem;">
                        <i class="fas fa-info-circle me-2"></i>
                        <strong>Dica:</strong> Clique nos cabeçalhos das colunas para ordenar os dados. Clique novamente para inverter a ordem.
                        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close" style="padding: 8px; font-size: 0.7rem;"></button>
                    </div>
                    <div class="table-responsive">
                        <table class="table table-striped table-hover table-sm" id="table-criticos">
                            <thead><tr id="thead-criticos"></tr></thead>
                            <tbody id="tbody-criticos"></tbody>
                        </table>
                    </div>
                    <div class="pagination-controls">
                        <div class="pagination-info">
                            <span id="info-criticos">Mostrando 0 de 0 registros</span>
                            <select class="page-size-select" id="pagesize-criticos" onchange="changePageSize('criticos')">
                                <option value="25">25 por página</option>
                                <option value="50" selected>50 por página</option>
                                <option value="100">100 por página</option>
                                <option value="500">500 por página</option>
                            </select>
                        </div>
                        <div class="pagination-buttons">
                            <button onclick="changePage('criticos', 'first')">Primeira</button>
                            <button onclick="changePage('criticos', 'prev')">Anterior</button>
                            <span class="pagination-info" id="page-criticos">Página 1 de 1</span>
                            <button onclick="changePage('criticos', 'next')">Próxima</button>
                            <button onclick="changePage('criticos', 'last')">Última</button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Tabela 4: Sem Agendamento -->
            <div id="data-sem-agendamento" class="data-section">
                <div class="chart-card">
                    <h5 class="mb-3">
                        <i class="fas fa-calendar-times me-2"></i>
                        Pacientes SEM Agendamento (Exibindo até 5.000 de {total_sem_agendamento:,} registros)
                    </h5>
                    <div class="alert alert-info alert-dismissible fade show" role="alert" style="padding: 8px 15px; font-size: 0.9rem;">
                        <i class="fas fa-info-circle me-2"></i>
                        <strong>Dica:</strong> Clique nos cabeçalhos das colunas para ordenar os dados. Clique novamente para inverter a ordem.
                        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close" style="padding: 8px; font-size: 0.7rem;"></button>
                    </div>
                    <div class="table-responsive">
                        <table class="table table-striped table-hover table-sm" id="table-sem-agendamento">
                            <thead><tr id="thead-sem-agendamento"></tr></thead>
                            <tbody id="tbody-sem-agendamento"></tbody>
                        </table>
                    </div>
                    <div class="pagination-controls">
                        <div class="pagination-info">
                            <span id="info-sem-agendamento">Mostrando 0 de 0 registros</span>
                            <select class="page-size-select" id="pagesize-sem-agendamento" onchange="changePageSize('sem-agendamento')">
                                <option value="25">25 por página</option>
                                <option value="50" selected>50 por página</option>
                                <option value="100">100 por página</option>
                                <option value="500">500 por página</option>
                            </select>
                        </div>
                        <div class="pagination-buttons">
                            <button onclick="changePage('sem-agendamento', 'first')">Primeira</button>
                            <button onclick="changePage('sem-agendamento', 'prev')">Anterior</button>
                            <span class="pagination-info" id="page-sem-agendamento">Página 1 de 1</span>
                            <button onclick="changePage('sem-agendamento', 'next')">Próxima</button>
                            <button onclick="changePage('sem-agendamento', 'last')">Última</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Dados carregados do servidor
        const tableData = {{
            'geral': {dados_geral_json},
            'confirmados': {dados_confirmados_json},
            'criticos': {dados_criticos_json},
            'sem-agendamento': {dados_sem_agendamento_json}
        }};
        
        const columnNames = {json.dumps(colunas_disponiveis_nomes)};
        const columnKeys = {json.dumps(colunas_disponiveis)};
        
        // Estado da paginação para cada tabela
        const paginationState = {{
            'geral': {{ currentPage: 1, pageSize: 50 }},
            'confirmados': {{ currentPage: 1, pageSize: 50 }},
            'criticos': {{ currentPage: 1, pageSize: 50 }},
            'sem-agendamento': {{ currentPage: 1, pageSize: 50 }}
        }};
        
        // Estado da ordenação para cada tabela
        const sortState = {{
            'geral': {{ column: null, direction: 'asc' }},
            'confirmados': {{ column: null, direction: 'asc' }},
            'criticos': {{ column: null, direction: 'asc' }},
            'sem-agendamento': {{ column: null, direction: 'asc' }}
        }};
        
        let currentDataSection = null;
        
        // Função para ordenar dados
        function sortData(tableId, columnIndex) {{
            const data = tableData[tableId];
            const sort = sortState[tableId];
            const columnKey = columnKeys[columnIndex];
            
            // Se clicar na mesma coluna, alterna a direção
            if (sort.column === columnIndex) {{
                if (sort.direction === 'asc') {{
                    sort.direction = 'desc';
                }} else if (sort.direction === 'desc') {{
                    sort.column = null;
                    sort.direction = 'asc';
                    // Resetar para ordem original
                    paginationState[tableId].currentPage = 1;
                    renderTable(tableId);
                    return;
                }}
            }} else {{
                sort.column = columnIndex;
                sort.direction = 'asc';
            }}
            
            // Ordenar os dados
            data.sort((a, b) => {{
                let valA = a[columnKey];
                let valB = b[columnKey];
                
                // Tratar valores nulos
                if (valA === null || valA === undefined || valA === 'N/A') valA = '';
                if (valB === null || valB === undefined || valB === 'N/A') valB = '';
                
                // Converter para string para comparação
                valA = String(valA).toLowerCase();
                valB = String(valB).toLowerCase();
                
                // Tentar converter para número se possível
                const numA = parseFloat(valA);
                const numB = parseFloat(valB);
                
                if (!isNaN(numA) && !isNaN(numB)) {{
                    return sort.direction === 'asc' ? numA - numB : numB - numA;
                }}
                
                // Comparação de strings
                if (valA < valB) return sort.direction === 'asc' ? -1 : 1;
                if (valA > valB) return sort.direction === 'asc' ? 1 : -1;
                return 0;
            }});
            
            // Resetar para primeira página
            paginationState[tableId].currentPage = 1;
            renderTable(tableId);
        }}
        
        function renderTable(tableId) {{
            const data = tableData[tableId];
            const state = paginationState[tableId];
            const sort = sortState[tableId];
            
            if (!data || data.length === 0) {{
                document.getElementById('info-' + tableId).textContent = 'Nenhum dado disponível';
                return;
            }}
            
            // Calcular paginação
            const totalRecords = data.length;
            const totalPages = Math.ceil(totalRecords / state.pageSize);
            const startIdx = (state.currentPage - 1) * state.pageSize;
            const endIdx = Math.min(startIdx + state.pageSize, totalRecords);
            const pageData = data.slice(startIdx, endIdx);
            
            // Renderizar cabeçalho com coluna de número e ordenação
            const thead = document.getElementById('thead-' + tableId);
            thead.innerHTML = '<th style="width: 60px; text-align: center;">#</th>' + 
                columnNames.map((name, idx) => {{
                    const sortIndicator = sort.column === idx 
                        ? `<span class="sort-indicator">${{sort.direction === 'asc' ? '↑' : '↓'}}</span>` 
                        : `<span class="sort-indicator" style="opacity: 0.3;">⇅</span>`;
                    return `<th class="sortable-header" onclick="sortData('${{tableId}}', ${{idx}})" title="Clique para ordenar">${{name}}${{sortIndicator}}</th>`;
                }}).join('');
            
            // Renderizar corpo com numeração
            const tbody = document.getElementById('tbody-' + tableId);
            tbody.innerHTML = pageData.map((row, idx) => {{
                const rowNumber = startIdx + idx + 1;
                const cells = columnKeys.map(key => {{
                    const value = row[key] ?? 'N/A';
                    return `<td>${{value}}</td>`;
                }}).join('');
                return `<tr><td style="text-align: center; font-weight: bold; color: #003087;">${{rowNumber}}</td>${{cells}}</tr>`;
            }}).join('');
            
            // Atualizar informações de paginação
            document.getElementById('info-' + tableId).textContent = 
                `Mostrando ${{startIdx + 1}} a ${{endIdx}} de ${{totalRecords.toLocaleString('pt-BR')}} registros`;
            
            document.getElementById('page-' + tableId).textContent = 
                `Página ${{state.currentPage}} de ${{totalPages}}`;
            
            // Atualizar botões
            const buttons = document.querySelectorAll(`#data-${{tableId}} .pagination-buttons button`);
            buttons[0].disabled = state.currentPage === 1; // First
            buttons[1].disabled = state.currentPage === 1; // Prev
            buttons[3].disabled = state.currentPage === totalPages; // Next
            buttons[4].disabled = state.currentPage === totalPages; // Last
        }}
        
        function changePage(tableId, action) {{
            const state = paginationState[tableId];
            const data = tableData[tableId];
            const totalPages = Math.ceil(data.length / state.pageSize);
            
            switch(action) {{
                case 'first':
                    state.currentPage = 1;
                    break;
                case 'prev':
                    if (state.currentPage > 1) state.currentPage--;
                    break;
                case 'next':
                    if (state.currentPage < totalPages) state.currentPage++;
                    break;
                case 'last':
                    state.currentPage = totalPages;
                    break;
            }}
            
            renderTable(tableId);
        }}
        
        function changePageSize(tableId) {{
            const select = document.getElementById('pagesize-' + tableId);
            paginationState[tableId].pageSize = parseInt(select.value);
            paginationState[tableId].currentPage = 1; // Reset to first page
            renderTable(tableId);
        }}

        function toggleDataSection(sectionId) {{
            const section = document.getElementById('data-' + sectionId);
            const allCards = document.querySelectorAll('.kpi-card');
            const clickedCard = document.querySelector(`[data-table="${{sectionId}}"]`);
            
            // Se clicar na mesma seção, esconde
            if (currentDataSection === sectionId) {{
                section.classList.remove('show');
                clickedCard.classList.remove('active');
                currentDataSection = null;
                return;
            }}
            
            // Esconde todas as seções
            document.querySelectorAll('.data-section').forEach(s => s.classList.remove('show'));
            
            // Remove active de todos os cards
            allCards.forEach(card => card.classList.remove('active'));
            
            // Mostra a seção clicada
            section.classList.add('show');
            clickedCard.classList.add('active');
            currentDataSection = sectionId;
            
            // Renderizar a tabela quando mostrar a seção
            renderTable(sectionId);
            
            // Scroll suave até a tabela
            setTimeout(() => {{
                section.scrollIntoView({{ behavior: 'smooth', block: 'nearest' }});
            }}, 100);
        }}
        
        // Função para toggle de todos os riscos
        function toggleTodosRiscos(checkbox) {{
            const checkboxes = document.querySelectorAll('input[name="risco"]');
            checkboxes.forEach(cb => {{
                cb.checked = checkbox.checked;
            }});
        }}
        
        // Função para toggle de todas as especialidades
        function toggleTodasEspecialidades(checkbox) {{
            const checkboxes = document.querySelectorAll('input[name="especialidade"]');
            checkboxes.forEach(cb => {{
                cb.checked = checkbox.checked;
            }});
        }}
        
        // Atualizar o estado do checkbox "Selecionar Todos" quando itens individuais mudam
        document.addEventListener('DOMContentLoaded', function() {{
            // Monitorar mudanças nos checkboxes de risco
            const riscosCheckboxes = document.querySelectorAll('input[name="risco"]');
            riscosCheckboxes.forEach(cb => {{
                cb.addEventListener('change', function() {{
                    const selecionarTodosRiscos = document.getElementById('selecionar-todos-riscos');
                    const todosMarcados = Array.from(riscosCheckboxes).every(checkbox => checkbox.checked);
                    const nenhumMarcado = Array.from(riscosCheckboxes).every(checkbox => !checkbox.checked);
                    
                    if (todosMarcados) {{
                        selecionarTodosRiscos.checked = true;
                        selecionarTodosRiscos.indeterminate = false;
                    }} else if (nenhumMarcado) {{
                        selecionarTodosRiscos.checked = false;
                        selecionarTodosRiscos.indeterminate = false;
                    }} else {{
                        selecionarTodosRiscos.indeterminate = true;
                    }}
                }});
            }});
            
            // Monitorar mudanças nos checkboxes de especialidade
            const especialidadesCheckboxes = document.querySelectorAll('input[name="especialidade"]');
            especialidadesCheckboxes.forEach(cb => {{
                cb.addEventListener('change', function() {{
                    const selecionarTodasEsp = document.getElementById('selecionar-todas-especialidades');
                    const todosMarcados = Array.from(especialidadesCheckboxes).every(checkbox => checkbox.checked);
                    const nenhumMarcado = Array.from(especialidadesCheckboxes).every(checkbox => !checkbox.checked);
                    
                    if (todosMarcados) {{
                        selecionarTodasEsp.checked = true;
                        selecionarTodasEsp.indeterminate = false;
                    }} else if (nenhumMarcado) {{
                        selecionarTodasEsp.checked = false;
                        selecionarTodasEsp.indeterminate = false;
                    }} else {{
                        selecionarTodasEsp.indeterminate = true;
                    }}
                }});
            }});
        }});
    </script>
</body>
</html>
        """
        )

    except Exception as e:
        return HTMLResponse(
            f"""
        <html>
        <head><title>Erro</title></head>
        <body>
        <h1>Erro ao carregar dashboard</h1>
        <p>Detalhes: {str(e)}</p>
        <a href="/logout">Voltar ao login</a>
        </body>
        </html>
        """,
            status_code=500,
        )


@app.get("/status")
async def get_status():
    try:
        df = carregar_dados()
        return {
            "status": "OK",
            "total_registros": len(df),
            "versao": "2.0.0",
            "mensagem": "Dashboard funcionando!",
        }
    except Exception as e:
        return {"status": "ERRO", "erro": str(e)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8001)
