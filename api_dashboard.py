import polars as pl
import plotly.express as px
from fastapi import FastAPI, Query, Depends, Form, Request, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import List, Optional

# --- CONFIGURAÇÃO DE SEGURANÇA ---
USUARIOS_VALIDOS = {
    "admin": "senha123",
    "tou": "hackathon"
}

app = FastAPI()

# ==================== INÍCIO DA ALTERAÇÃO 1 ====================
# --- LÓGICA DE DADOS (SEM O BLOCO TRY-EXCEPT) ---
def carregar_e_filtrar_dados(riscos: Optional[List[str]], especialidades: Optional[List[str]]):
    """
    Carrega os dados do CSV e aplica os filtros.
    Se o arquivo não existir, agora a aplicação irá falhar,
    o que é o comportamento esperado.
    """
    # A leitura do CSV agora é a única fonte de dados.
    df_completo = pl.read_csv('/home/tou/Área de trabalho/hackathon/dado_minerado/pessoas_pacientes.csv')

    # O restante da lógica de filtragem permanece o mesmo
    risco_opcoes = df_completo["solicitacao_risco"].unique().drop_nulls().to_list()
    especialidade_opcoes = df_completo["procedimento_especialidade"].unique().drop_nulls().to_list()
    riscos_selecionados = riscos if riscos else risco_opcoes
    especialidades_selecionadas = especialidades if especialidades else especialidade_opcoes
    df_filtrado = df_completo.filter(
        (pl.col("solicitacao_risco").is_in(riscos_selecionados)) &
        (pl.col("procedimento_especialidade").is_in(especialidades_selecionadas))
    )
    return df_filtrado, df_completo
# ===================== FIM DA ALTERAÇÃO 1 ======================

# --- DEPENDÊNCIA DE AUTENTICAÇÃO (Corrigida e Inalterada) ---
async def get_current_user(request: Request):
    username = request.cookies.get("session_user")
    if username in USUARIOS_VALIDOS:
        return username
    raise HTTPException(
        status_code=status.HTTP_307_TEMPORARY_REDIRECT,
        detail="Não autenticado",
        headers={"Location": "/login"},
    )

# --- ROTAS DA API (Inalteradas, exceto o HTML do dashboard) ---
@app.get("/", response_class=HTMLResponse)
async def root(user: str = Depends(get_current_user)):
    return RedirectResponse(url="/dashboard")

@app.get("/login", response_class=HTMLResponse)
async def login_form(error: Optional[str] = None):
    error_message = f"<div class='alert alert-danger'>{error}</div>" if error else ""
    html_content = f"""
    <!DOCTYPE html>
    <html lang="pt-BR" data-bs-theme="dark">
    <head>
        <meta charset="UTF-8"><title>Login</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
        <style> body {{ display: flex; align-items: center; justify-content: center; height: 100vh; }} .login-card {{ max-width: 400px; width: 100%; }} </style>
    </head>
    <body>
        <div class="card login-card">
            <div class="card-body">
                <h2 class="card-title text-center">Login</h2> {error_message}
                <form action="/login" method="post">
                    <div class="mb-3">
                        <label for="username" class="form-label">Usuário</label>
                        <input type="text" id="username" name="username" class="form-control" required>
                    </div>
                    <div class="mb-3">
                        <label for="password" class="form-label">Senha</label>
                        <input type="password" id="password" name="password" class="form-control" required>
                    </div>
                    <button type="submit" class="btn btn-primary w-100">Entrar</button>
                </form>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/login")
async def handle_login(username: str = Form(), password: str = Form()):
    if USUARIOS_VALIDOS.get(username) == password:
        response = RedirectResponse(url="/dashboard", status_code=303)
        response.set_cookie(key="session_user", value=username, httponly=True)
        return response
    return RedirectResponse(url="/login?error=Credenciais inválidas", status_code=303)

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/login")
    response.delete_cookie(key="session_user")
    return response

@app.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard(
    risco: Optional[List[str]] = Query(None),
    especialidade: Optional[List[str]] = Query(None),
    current_user: str = Depends(get_current_user)
):
    df_filtrado, df_completo = carregar_e_filtrar_dados(risco, especialidade)
    tabela_html = df_filtrado.to_pandas().to_html(classes='table table-striped table-dark', index=False, justify='center') if not df_filtrado.is_empty() else "<p class='text-warning'>Nenhum dado disponível.</p>"
    grafico_html = ""
    if not df_filtrado.is_empty():
        df_contagem = df_filtrado.group_by(["procedimento", "solicitacao_risco"]).count()
        mapa_de_cores = {'AZUL': 'blue', 'VERMELHO': 'red', 'AMARELO': 'yellow', 'VERDE': 'green'}
        fig = px.bar(df_contagem.to_pandas(), x="procedimento", y="count", color="solicitacao_risco", title="Contagem de Indivíduos por Procedimento e Risco", labels={"count": "Número de Indivíduos", "procedimento": "Procedimento"}, color_discrete_map=mapa_de_cores, template="plotly_dark")
        grafico_html = fig.to_html(full_html=False, include_plotlyjs='cdn')

    risco_opcoes = df_completo["solicitacao_risco"].unique().drop_nulls().to_list()
    especialidade_opcoes = df_completo["procedimento_especialidade"].unique().drop_nulls().to_list()
    risco_checkboxes = "".join([f'<label class="form-check-label me-3"><input type="checkbox" class="form-check-input" name="risco" value="{opt}" {"checked" if not risco or opt in risco else ""}> {opt}</label>' for opt in risco_opcoes])

    # Adicionando um ID de container para os checkboxes de especialidade
    especialidade_checkboxes = "".join([f'<label class="form-check-label me-3"><input type="checkbox" class="form-check-input" name="especialidade" value="{opt}" {"checked" if not especialidade or opt in especialidade else ""}> {opt}</label>' for opt in especialidade_opcoes])

# ==================== INÍCIO DA ALTERAÇÃO 2 ====================
    html_content = f"""
    <!DOCTYPE html>
    <html lang="pt-BR" data-bs-theme="dark">
    <head>
        <meta charset="UTF-8">
        <title>Dashboard Solicitações</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {{ padding: 20px; }} .container {{ max-width: 1200px; margin: auto; }}
            .table-container {{ max-height: 450px; overflow-y: auto; border: 1px solid #444; border-radius: 5px; }}
            .user-info {{ position: absolute; top: 10px; right: 20px; }}
            .btn-group-sm .btn {{ margin-left: 10px; }}
        </style>
    </head>
    <body>
        <div class="user-info">
            Logado como: <strong>{current_user}</strong> | <a href="/logout">Sair</a>
        </div>
        <div class="container">
            <h1 class="mb-4">Dashboard de Solicitações</h1>
            <div class="card mb-4">
                <div class="card-header"><h2>Filtros</h2></div>
                <div class="card-body">
                    <form action="/dashboard" method="get">
                        <div class="mb-3">
                            <strong>Risco:</strong><br>{risco_checkboxes}
                        </div>
                        <div class="mb-3">
                            <div class="d-flex align-items-center mb-1">
                                <strong>Especialidade:</strong>
                                <div class="btn-group btn-group-sm">
                                    <button type="button" class="btn btn-outline-secondary" onclick="toggleEspecialidades(true)">Marcar Todos</button>
                                    <button type="button" class="btn btn-outline-secondary" onclick="toggleEspecialidades(false)">Desmarcar Todos</button>
                                </div>
                            </div>
                            <div id="especialidades-container">
                                {especialidade_checkboxes}
                            </div>
                        </div>
                        <button type="submit" class="btn btn-primary">Aplicar Filtros</button>
                    </form>
                </div>
            </div>
            <h2>Tabela de Solicitações</h2>
            <div class="table-container">{tabela_html}</div>
            <h2 class="mt-4">Número de Indivíduos por Procedimento</h2>
            {grafico_html}
        </div>

        <script>
            function toggleEspecialidades(checked) {{
                const container = document.getElementById('especialidades-container');
                const checkboxes = container.querySelectorAll('input[type="checkbox"]');
                checkboxes.forEach(cb => {{
                    cb.checked = checked;
                }});
            }}
        </script>
    </body>
    </html>
    """
# ===================== FIM DA ALTERAÇÃO 2 ======================
    return HTMLResponse(content=html_content)
