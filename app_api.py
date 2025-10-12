# api_class.py

import jwt
import datetime
from functools import wraps
from flask import Flask, request, jsonify
import polars as pl
from datetime import datetime, timedelta

def token_required(f):
    """
    Decorator para validar o token JWT fornecido no header da requisição.
    """
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
            # ✅ use a mesma SECRET_KEY da app (opcional, mas melhor)
            jwt.decode(token, 'sua-chave-secreta-aqui', algorithms=["HS256"])
            # ou: jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expirado!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token inválido!'}), 401

        return f(*args, **kwargs)

    return decorated

class HackathonAPI:
    """
    Classe que define o artefato da API REST para a Hackathon.
    """
    def __init__(self):
        self.app = Flask(__name__)
        # A chave secreta é usada para codificar e decodificar os tokens JWT
        self.app.config['SECRET_KEY'] = 'sua-chave-secreta-aqui'
        
        # Simulação de um banco de dados de usuários para autenticação
        self.users = {
            "user_hackathon": "senha123"
        }

        self.setup_routes()

    def setup_routes(self):
        """
        Configura as rotas (endpoints) da API.
        """

        @self.app.route('/token', methods=['POST']) # http://127.0.0.1:5000/token
        def get_token():
            """
            Endpoint de Autenticação.
            Recebe 'login' e 'senha' e retorna um token de acesso JWT.
            """
            auth_data = request.get_json()
            if not auth_data or not auth_data.get('login') or not auth_data.get('senha'):
                return jsonify({"message": "Credenciais não fornecidas"}), 401

            login = auth_data.get('login')
            senha = auth_data.get('senha')

            # Valida as credenciais do usuário
            if login in self.users and self.users[login] == senha:
                # Gera o token JWT com tempo de expiração de uma hora
                token = jwt.encode({
                    'user': login,
                    'exp': datetime.utcnow() + timedelta(hours=1)
                }, self.app.config['SECRET_KEY'], algorithm="HS256")
                
                return jsonify({'token': token})

            return jsonify({"message": "Credenciais inválidas"}), 401

        @self.app.route('/task', methods=['POST']) # http://127.0.0.1:5000/task
        @token_required
        def execute_task():
            """
            Endpoint de Execução da tarefa principal da Hackathon.
            """
            # --- Início da lógica de processamento do artefato ---
            try:
                # Carrega os datasets
                df = pl.read_csv('datasets/solicitacao.csv')
                proce = pl.read_csv("datasets/procedimento.csv")

                # Filtra por solicitações pendentes
                df_novo = df.filter(pl.col("solicitacao_status") == "SOLICITAÇÃO / PENDENTE / REGULADOR")

                # Seleciona colunas de procedimento e ajusta tipo de dado para o merge
                proce_sel = proce.select(["procedimento_sisreg_id", "procedimento", "procedimento_especialidade"])
                df_novo = df_novo.with_columns(pl.col("procedimento_sisreg_id").cast(pl.Int64))
                
                # Realiza o merge dos dataframes
                df_merged = df_novo.join(
                    proce_sel,
                    left_on="procedimento_sisreg_id",
                    right_on="procedimento_sisreg_id",
                    how="left"
                )

                # Calcula o tempo teórico máximo de espera em dias com base no risco
                df_merged = df_merged.with_columns(
                    pl.when(pl.col("solicitacao_risco").str.to_lowercase() == "vermelho").then(30)
                      .when(pl.col("solicitacao_risco").str.to_lowercase() == "amarelo").then(90)
                      .when(pl.col("solicitacao_risco").str.to_lowercase() == "verde").then(180)
                      .alias("tempo_teorico_max_espera_dias")
                )

                # Converte a coluna de data da solicitação para o tipo datetime
                df_merged = df_merged.with_columns([
                    pl.col("data_solicitacao")
                    .str.strptime(pl.Datetime, format="%Y-%m-%d %H:%M:%S%.f %Z", strict=False)
                    .alias("solicitacao_dt")
                ])

                # Calcula os dias desde a solicitação até a data atual
                hoje = datetime.now()
                df_merged = df_merged.with_columns([
                    (
                        (pl.lit(hoje).cast(pl.Datetime) - pl.col("solicitacao_dt"))
                        .dt.total_seconds() / 86400
                    ).cast(pl.Int64)
                    .alias("dias_desde_solicitacao")
                ])
                
                # Define as colunas desejadas para o resultado
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

                # Seleciona apenas as colunas desejadas
                df_merged_sub = df_merged.select(colunas_desejadas)
                
                # Converte o dataframe resultante para uma lista de dicionários para ser serializável em JSON
                processed_result = df_merged_sub.to_dicts()

                # A saída da requisição deve seguir o formato especificado para a tarefa
                return jsonify({
                    "status": "sucesso",
                    "dados_processados": processed_result,
                    "mensagem": "Tarefa processada com sucesso."
                }), 200

            except Exception as e:
                # Em caso de erro durante o processamento, retorna uma mensagem de erro
                return jsonify({
                    "status": "erro",
                    "mensagem": f"Ocorreu um erro durante o processamento: {str(e)}"
                }), 500
            # --- Fim da lógica de processamento ---


    def run(self, host='0.0.0.0', port=5000):
        """
        Executa o servidor da aplicação Flask.
        """
        self.app.run(host=host, port=port, debug=True)
        
if __name__ == '__main__':
    # Instancia a classe da API a partir do arquivo api_class.py
    api_instance = HackathonAPI()
    
    # Inicia a execução do servidor da API
    print("Iniciando o servidor da API da Hackathon na porta 5000...")
    api_instance.run()