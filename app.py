import jwt
import datetime
from functools import wraps
from flask import Flask, request, jsonify
import os
from datetime import datetime as dt
try:
    import polars as pl
except Exception as e:
    raise RuntimeError(
        "A biblioteca 'polars' é necessária para processar os dados. "
        "Instale com: pip install polars"
    ) from e


# ------------------------------------------------------------
# Autenticação via token JWT
# ------------------------------------------------------------
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            try:
                token = request.headers['Authorization'].split(" ")[1]
            except IndexError:
                return jsonify({'message': 'Formato do token inválido!'}), 401

        if not token:
            return jsonify({'message': 'Token não encontrado!'}), 401

        try:
            import os
            secret_key = os.getenv("APP_SECRET_KEY", "chave-fixa-temporaria")
            jwt.decode(token, secret_key, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expirado!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token inválido!'}), 401

        return f(*args, **kwargs)
    return decorated


# ------------------------------------------------------------
# Função de processamento de solicitações
# ------------------------------------------------------------
def processar_solicitacoes(status_alvo: str):
    caminho_solic = os.path.join("datasets", "solicitacao.csv")
    caminho_proc = os.path.join("datasets", "procedimento.csv")

    if not os.path.exists(caminho_solic):
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho_solic}")
    if not os.path.exists(caminho_proc):
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho_proc}")

    df = pl.read_csv(caminho_solic)
    proce = pl.read_csv(caminho_proc)

    proce_sel = proce.select(
        ["procedimento_sisreg_id", "procedimento", "procedimento_especialidade"]
    )

    df_filtrado = df.filter(pl.col("solicitacao_status") == status_alvo)

    df_filtrado = df_filtrado.with_columns(
        pl.col("procedimento_sisreg_id").cast(pl.Int64)
    )

    df_merged = df_filtrado.join(
        proce_sel,
        left_on="procedimento_sisreg_id",
        right_on="procedimento_sisreg_id",
        how="left"
    )

    df_merged = df_merged.with_columns(
        pl.when(pl.col("solicitacao_risco").str.to_lowercase() == "vermelho").then(30)
         .when(pl.col("solicitacao_risco").str.to_lowercase() == "amarelo").then(90)
         .when(pl.col("solicitacao_risco").str.to_lowercase() == "verde").then(180)
         .alias("tempo_teorico_max_espera_dias")
    )

    df_merged = df_merged.with_columns([
        pl.col("data_solicitacao")
        .str.strptime(pl.Datetime, format="%Y-%m-%d %H:%M:%S%.f %Z", strict=False)
        .alias("solicitacao_dt")
    ])

    hoje = dt.now()
    df_merged = df_merged.with_columns([
        (
            (pl.lit(hoje).cast(pl.Datetime) - pl.col("solicitacao_dt"))
            .dt.total_seconds() / 86400
        ).cast(pl.Int64).alias("dias_desde_solicitacao")
    ])

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

    os.makedirs(os.path.join("dado_minerado"), exist_ok=True)
    df_saida.write_csv(os.path.join("dado_minerado", "pessoas_pacientes.csv"))

    return df_saida


# ------------------------------------------------------------
# Configuração do Flask (sem classe e sem SECRET_KEY)
# ------------------------------------------------------------
app = Flask(__name__)

# Usuários fixos para autenticação
USERS = {"user_hackathon": "senha123"}


@app.route('/token', methods=['POST'])
def get_token():
    auth_data = request.get_json()
    if not auth_data or not auth_data.get('login') or not auth_data.get('senha'):
        return jsonify({"message": "Credenciais não fornecidas"}), 401

    login = auth_data.get('login')
    senha = auth_data.get('senha')

    if login in USERS and USERS[login] == senha:
        import os
        secret_key = os.getenv("APP_SECRET_KEY", "chave-fixa-temporaria")
        token = jwt.encode({
            'user': login,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }, secret_key, algorithm="HS256")
        return jsonify({'token': token})

    return jsonify({"message": "Credenciais inválidas"}), 401


@app.route('/task', methods=['GET', 'POST'])
@token_required
def task():
    status_qs = request.args.get("status")
    status_json = None
    if request.is_json:
        body = request.get_json(silent=True) or {}
        status_json = body.get("status")

    status_alvo = status_qs or status_json or "SOLICITAÇÃO / PENDENTE / REGULADOR"

    try:
        df_result = processar_solicitacoes(status_alvo)
    except FileNotFoundError as e:
        return jsonify({"status": "erro", "mensagem": str(e)}), 400
    except Exception as e:
        return jsonify({
            "status": "erro",
            "mensagem": f"Falha ao processar solicitações: {str(e)}"
        }), 500

    registros = df_result.to_dicts()
    return jsonify({
        "status": "sucesso",
        "filtro_status": status_alvo,
        "quantidade": len(registros),
        "resultado": registros,
        "saida_csv": "dado_minerado/pessoas_pacientes.csv"
    }), 200


@app.route("/healthz", methods=['GET'])
def healthz():
    return jsonify({"status": "ok"}), 200


# ------------------------------------------------------------
# Execução do servidor (sem debug=True)
# ------------------------------------------------------------
if __name__ == '__main__':
    print("Iniciando o servidor Flask na porta 5000...")
    app.run(host='0.0.0.0', port=5000)
