# api_main.py

from api_class import HackathonAPI

if __name__ == '__main__':
    # Instancia a classe da API a partir do arquivo api_class.py
    api_instance = HackathonAPI()
    
    # Inicia a execução do servidor da API
    print("Iniciando o servidor da API da Hackathon na porta 5000...")
    api_instance.run()