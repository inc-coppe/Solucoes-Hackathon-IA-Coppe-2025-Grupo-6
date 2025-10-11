# api_class.py

import jwt
import datetime
from functools import wraps
from flask import Flask, request, jsonify

def token_required(f):
    """
    Decorator para validar o token JWT fornecido no header da requisição.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # O token deve ser fornecido no header 'Authorization' no formato "Bearer {token}" [cite: 15]
        if 'Authorization' in request.headers:
            try:
                token = request.headers['Authorization'].split(" ")[1]
            except IndexError:
                return jsonify({'message': 'Formato do token inválido!'}), 401

        if not token:
            return jsonify({'message': 'Token não encontrado!'}), 401

        try:
            # A chave secreta deve ser mantida em segurança em uma aplicação real
            # Este endpoint só executa com um token válido [cite: 14]
            jwt.decode(token, 'sua-chave-secreta-aqui', algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expirado!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token inválido!'}), 401

        return f(*args, **kwargs)
    return decorated

class HackathonAPI:
    """
    Classe que define o artefato da API REST para a Hackathon[cite: 2, 4].
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
            Endpoint de Autenticação[cite: 9].
            Recebe 'login' e 'senha' e retorna um token de acesso JWT[cite: 11].
            """
            auth_data = request.get_json()
            if not auth_data or not auth_data.get('login') or not auth_data.get('senha'):
                return jsonify({"message": "Credenciais não fornecidas"}), 401

            login = auth_data.get('login')
            senha = auth_data.get('senha')

            # Valida as credenciais do usuário
            if login in self.users and self.users[login] == senha:
                # Gera o token JWT com tempo de expiração de uma hora [cite: 10]
                token = jwt.encode({
                    'user': login,
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
                }, self.app.config['SECRET_KEY'], algorithm="HS256")
                
                return jsonify({'token': token})

            return jsonify({"message": "Credenciais inválidas"}), 401

        @self.app.route('/task', methods=['POST']) # http://127.0.0.1:5000/task
        @token_required
        def execute_task():
            """
            Endpoint de Execução da tarefa principal da Hackathon[cite: 12, 13].
            """
            # O corpo da requisição pode receber dados em qualquer formato aplicável [cite: 16]
            input_data = request.get_json()
            
            # --- Início da lógica de processamento do artefato ---
            # A lógica específica da sua tarefa deve ser implementada aqui.
            # Como exemplo, a API simplesmente retornará os dados recebidos.
            processed_result = {
                "status": "sucesso",
                "dados_recebidos": input_data,
                "mensagem": "Tarefa processada com sucesso."
            }
            # --- Fim da lógica de processamento ---

            # A saída da requisição deve seguir o formato especificado para a tarefa [cite: 17]
            return jsonify(processed_result), 200

    def run(self, host='0.0.0.0', port=5000):
        """
        Executa o servidor da aplicação Flask.
        """
        self.app.run(host=host, port=port, debug=True)