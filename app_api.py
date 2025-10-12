# api_class.py
import jwt
import datetime
from functools import wraps
from flask import Flask, request, jsonify

# --- dependências de processamento (pacientesE2.py) ---
import os
from datetime import datetime as dt
try:
    import polars as pl
except Exception as e:
    raise RuntimeError(
        "A biblioteca 'polars' é necessária para processar os dados. "
        "Instale com: pip install polars"
    ) from e


def token_required(f):
    """
    Decorator para validar o token JWT fornecido no header da requisição.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # O token deve ser fornecido no header 'Authorization' no formato "Bearer {token}"
        if 'Authorization' in request.headers:
            try:
                token = request.headers['Authorization'].split(" ")[1]
            except IndexError:
                return jsonify({'message': 'Formato do token inválido!'}), 401

        if not token:
            return jsonify({'message': 'Token não encontrado!'}), 401

        try:
            jwt.decode(token, 'sua-chave-secreta-aqui', algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expirado!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token inválido!'}), 401

        return f(*args, **kwargs)
    return decorated


def processar_solicitacoes(status_alvo: str):
    """
    Reproduz a lógica do pacientesE2.py com possibilidade de filtrar o status.
    Retorna um DataFrame Polars com as colunas selecionadas.
    """
    # Caminhos de entrada
    caminho_solic = os.path.join("datasets", "solicitacao.csv")
    caminho_proc = os.path.join("datasets", "procedimento.csv")

    if not os.path.exists(caminho_solic):
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho_solic}")
    if not os.path.exists(caminho_proc):
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho_proc}")

    # Carrega bases
    df = pl.read_csv(caminho_solic)
    proce = pl.read_csv(caminho_proc)

    # Seleção/renomeação conforme o script original
    proce_sel = proce.select(
        ["procedimento_sisreg_id", "procedimento", "procedimento_especialidade"]
    )

    # Filtro pelo status (padrão: "SOLICITAÇÃO / PENDENTE / REGULADOR")
    df_filtrado = df.filter(pl.col("solicitacao_status") == status_alvo)

    # Tipagem e merge
    df_filtrado = df_filtrado.with_columns(
        pl.col("procedimento_sisreg_id").cast(pl.Int64)
    )

    df_merged = df_filtrado.join(
        proce_sel,
        left_on="procedimento_sisreg_id",
        right_on="procedimento_sisreg_id",
        how="left"
    )

    # Mapeia risco -> tempo teórico máximo de espera
    df_merged = df_merged.with_columns(
        pl.when(pl.col("solicitacao_risco").str.to_lowercase() == "vermelho").then(30)
         .when(pl.col("solicitacao_risco").str.to_lowercase() == "amarelo").then(90)
         .when(pl.col("solicitacao_risco").str.to_lowercase() == "verde").then(180)
         # azul não vinha mapeado no script; mantemos sem 'otherwise' como no original
         .alias("tempo_teorico_max_espera_dias")
    )

    # Converte data de solicitação
    df_merged = df_merged.with_columns([
        pl.col("data_solicitacao")
        .str.strptime(pl.Datetime, format="%Y-%m-%d %H:%M:%S%.f %Z", strict=False)
        .alias("solicitacao_dt")
    ])

    # Calcula dias desde a solicitação
    hoje = dt.now()
    df_merged = df_merged.with_columns([
        (
            (pl.lit(hoje).cast(pl.Datetime) - pl.col("solicitacao_dt"))
            .dt.total_seconds() / 86400
        ).cast(pl.Int64).alias("dias_desde_solicitacao")
    ])

    # Subconjunto de colunas (iguais ao script)
    colunas_desejadas = [
        'solicitacao_id',
        'data_solicitacao',
        'solicitacao_status',
        'solicitacao_risco',
        'procedimento_sisreg_id',
        'tempo_teorico_max_espera_dias',
        'dias_desde_solicitacao',
        'procedimento',
        'procedimento_especialidade'
    ]
    df_saida = df_merged.select([c for c in colunas_desejadas if c in df_merged.columns])

    # Mantém a geração do CSV de saída (como no script original)
    os.makedirs(os.path.join("dado_minerado"), exist_ok=True)
    df_saida.write_csv(os.path.join("dado_minerado", "pessoas_pacientes.csv"))

    return df_saida


class HackathonAPI:
    """
    API REST contendo apenas a funcionalidade de processamento de pacientes (pacientesE2.py).
    """
    def __init__(self):
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'sua-chave-secreta-aqui'

        # Simulação de usuários (mantido do original)
        self.users = {"user_hackathon": "senha123"}

        self.setup_routes()

    def setup_routes(self):
        @self.app.route('/token', methods=['POST'])
        def get_token():
            auth_data = request.get_json()
            if not auth_data or not auth_data.get('login') or not auth_data.get('senha'):
                return jsonify({"message": "Credenciais não fornecidas"}), 401

            login = auth_data.get('login')
            senha = auth_data.get('senha')

            if login in self.users and self.users[login] == senha:
                token = jwt.encode({
                    'user': login,
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
                }, self.app.config['SECRET_KEY'], algorithm="HS256")
                return jsonify({'token': token})
            return jsonify({"message": "Credenciais inválidas"}), 401

        @self.app.route('/task', methods=['GET', 'POST'])
        @token_required
        def task():
            """
            Executa o pipeline de pacientes (pacientesE2.py), permitindo informar o status:
              - via query string: /task?status=...
              - via JSON no corpo: {"status": "..."}
            Padrão: "SOLICITAÇÃO / PENDENTE / REGULADOR"
            """
            # 1) lê status da query string
            status_qs = request.args.get("status")

            # 2) lê status do corpo JSON (se houver)
            status_json = None
            if request.is_json:
                body = request.get_json(silent=True) or {}
                status_json = body.get("status")

            # 3) prioridade: query string > JSON > padrão
            status_alvo = status_qs or status_json or "SOLICITAÇÃO / PENDENTE / REGULADOR"

            try:
                df_result = processar_solicitacoes(status_alvo)
            except FileNotFoundError as e:
                return jsonify({
                    "status": "erro",
                    "mensagem": str(e)
                }), 400
            except Exception as e:
                return jsonify({
                    "status": "erro",
                    "mensagem": f"Falha ao processar solicitações: {str(e)}"
                }), 500

            # Converte para JSON (lista de dicts)
            registros = df_result.to_dicts()
            return jsonify({
                "status": "sucesso",
                "filtro_status": status_alvo,
                "quantidade": len(registros),
                "resultado": registros,
                "saida_csv": "dado_minerado/pessoas_pacientes.csv"
            }), 200
            
        @self.app.route("/healthz", methods=['GET'])
        def healthz():
            return jsonify({
                "status": "ok"
            }), 200

    def run(self, host='0.0.0.0', port=5000):
        self.app.run(host=host, port=port, debug=True)


# Mova a instanciação da classe para o escopo global do módulo
api_instance = HackathonAPI()

# Crie uma variável 'app' que aponta diretamente para a aplicação Flask.
# Esta é a convenção que o Gunicorn procura.
app = api_instance.app

# Mantenha apenas a execução do servidor de desenvolvimento dentro do 'if'
if __name__ == '__main__':
    print("Iniciando o servidor de DESENVOLVIMENTO da API na porta 5000...")
    # Note que agora usamos a variável 'app' que já foi criada
    app.run(host='0.0.0.0', port=5000, debug=True)
