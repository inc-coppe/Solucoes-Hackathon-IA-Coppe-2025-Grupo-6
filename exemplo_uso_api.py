#!/usr/bin/env python3
"""
Exemplo de Uso da API REST - Gestão Inteligente de Vagas (GIV)
==============================================================

Este script demonstra como usar a API REST GIV para:
- Autenticação
- Consultas de dados
- Análises preditivas
- Relatórios

Autor: Sistema GIV
Versão: 1.0
Data: Janeiro 2025
"""

import requests
import json
from datetime import datetime
import time

# ===== CONFIGURAÇÃO =====
API_BASE_URL = "http://127.0.0.1:8000"
USERNAME = "admin"
PASSWORD = "admin123"

class APIGIVClient:
    """Cliente para a API REST GIV"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.token = None
        self.headers = {"Content-Type": "application/json"}
    
    def login(self, username: str, password: str) -> bool:
        """Fazer login e obter token JWT"""
        try:
            url = f"{self.base_url}/auth/login"
            data = {
                "username": username,
                "password": password
            }
            
            response = requests.post(url, data=data)
            
            if response.status_code == 200:
                result = response.json()
                self.token = result["access_token"]
                self.headers["Authorization"] = f"Bearer {self.token}"
                print(f"✅ Login realizado com sucesso para usuário: {username}")
                return True
            else:
                print(f"❌ Erro no login: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Erro na requisição de login: {e}")
            return False
    
    def get_status(self) -> dict:
        """Obter status da API"""
        try:
            url = f"{self.base_url}/api/v1/status"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Erro ao obter status: {response.status_code}")
                return {}
                
        except Exception as e:
            print(f"❌ Erro na requisição de status: {e}")
            return {}
    
    def get_kpis(self, risco: list = None, especialidade: list = None) -> dict:
        """Obter KPIs do dashboard"""
        try:
            url = f"{self.base_url}/api/v1/dashboard/kpis"
            params = {}
            
            if risco:
                params["risco"] = risco
            if especialidade:
                params["especialidade"] = especialidade
            
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Erro ao obter KPIs: {response.status_code}")
                return {}
                
        except Exception as e:
            print(f"❌ Erro na requisição de KPIs: {e}")
            return {}
    
    def get_dados_dashboard(self, limit: int = 100, risco: list = None) -> dict:
        """Obter dados do dashboard"""
        try:
            url = f"{self.base_url}/api/v1/dashboard/dados"
            params = {"limit": limit}
            
            if risco:
                params["risco"] = risco
            
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Erro ao obter dados: {response.status_code}")
                return {}
                
        except Exception as e:
            print(f"❌ Erro na requisição de dados: {e}")
            return {}
    
    def get_analise_predicao(self, risco: list = None, especialidade: list = None) -> dict:
        """Obter análise preditiva"""
        try:
            url = f"{self.base_url}/api/v1/analise/predicao"
            params = {}
            
            if risco:
                params["risco"] = risco
            if especialidade:
                params["especialidade"] = especialidade
            
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Erro ao obter análise preditiva: {response.status_code}")
                return {}
                
        except Exception as e:
            print(f"❌ Erro na requisição de análise preditiva: {e}")
            return {}
    
    def get_solicitacoes(self, risco: str = None, limit: int = 10, offset: int = 0) -> dict:
        """Obter solicitações"""
        try:
            url = f"{self.base_url}/api/v1/solicitacoes"
            params = {"limit": limit, "offset": offset}
            
            if risco:
                params["risco"] = risco
            
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Erro ao obter solicitações: {response.status_code}")
                return {}
                
        except Exception as e:
            print(f"❌ Erro na requisição de solicitações: {e}")
            return {}
    
    def get_relatorio_resumo(self) -> dict:
        """Obter relatório resumido"""
        try:
            url = f"{self.base_url}/api/v1/relatorios/resumo"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Erro ao obter relatório: {response.status_code}")
                return {}
                
        except Exception as e:
            print(f"❌ Erro na requisição de relatório: {e}")
            return {}
    
    def get_modelo_info(self) -> dict:
        """Obter informações do modelo ML"""
        try:
            url = f"{self.base_url}/api/v1/ml/modelo/info"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Erro ao obter info do modelo: {response.status_code}")
                return {}
                
        except Exception as e:
            print(f"❌ Erro na requisição de info do modelo: {e}")
            return {}
    
    def fazer_predicao_ml(self, dados: dict) -> dict:
        """Fazer predição ML personalizada"""
        try:
            url = f"{self.base_url}/api/v1/ml/predicao"
            response = requests.post(url, headers=self.headers, json=dados)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Erro na predição ML: {response.status_code}")
                return {}
                
        except Exception as e:
            print(f"❌ Erro na requisição de predição ML: {e}")
            return {}
    
    def get_filtros_opcoes(self) -> dict:
        """Obter opções de filtros"""
        try:
            url = f"{self.base_url}/api/v1/filtros/opcoes"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Erro ao obter opções de filtros: {response.status_code}")
                return {}
                
        except Exception as e:
            print(f"❌ Erro na requisição de opções de filtros: {e}")
            return {}

def main():
    """Função principal de exemplo"""
    print("🏥 EXEMPLO DE USO DA API REST - GESTÃO INTELIGENTE DE VAGAS (GIV)")
    print("=" * 70)
    
    # Criar cliente
    client = APIGIVClient(API_BASE_URL)
    
    # 1. Login
    print("\n1️⃣ FAZENDO LOGIN...")
    if not client.login(USERNAME, PASSWORD):
        print("❌ Falha no login. Verifique se a API está rodando.")
        return
    
    # 2. Status da API
    print("\n2️⃣ VERIFICANDO STATUS DA API...")
    status = client.get_status()
    if status:
        print(f"✅ Status: {status.get('status', 'N/A')}")
        print(f"✅ Versão: {status.get('versao', 'N/A')}")
        print(f"✅ Total de registros: {status.get('total_registros', 'N/A'):,}")
        print(f"✅ Modelo ML treinado: {status.get('modelo_ml_treinado', 'N/A')}")
    
    # 3. KPIs Gerais
    print("\n3️⃣ OBTENDO KPIS GERAIS...")
    kpis = client.get_kpis()
    if kpis and kpis.get('status') == 'sucesso':
        kpi_data = kpis['kpis']
        print(f"✅ Total de solicitações: {kpi_data.get('total_solicitacoes', 'N/A'):,}")
        print(f"✅ Taxa de confirmação: {kpi_data.get('taxa_confirmacao', 'N/A')}%")
        print(f"✅ Risco crítico: {kpi_data.get('risco_critico', 'N/A')}%")
        print(f"✅ Sem agendamento: {kpi_data.get('sem_agendamento', 'N/A')}%")
    
    # 4. KPIs por Risco Vermelho
    print("\n4️⃣ OBTENDO KPIS PARA RISCO VERMELHO...")
    kpis_vermelho = client.get_kpis(risco=["VERMELHO"])
    if kpis_vermelho and kpis_vermelho.get('status') == 'sucesso':
        kpi_data = kpis_vermelho['kpis']
        print(f"✅ Solicitações vermelhas: {kpi_data.get('total_solicitacoes', 'N/A'):,}")
        print(f"✅ Taxa de confirmação: {kpi_data.get('taxa_confirmacao', 'N/A')}%")
        print(f"✅ Sem agendamento: {kpi_data.get('sem_agendamento_total', 'N/A'):,}")
    
    # 5. Análise Preditiva
    print("\n5️⃣ ANÁLISE PREDITIVA COM MACHINE LEARNING...")
    predicao = client.get_analise_predicao()
    if predicao and predicao.get('status') == 'sucesso':
        pred_data = predicao['predicao']
        if pred_data:
            print(f"✅ Total sem agendamento: {pred_data.get('total_sem_agendamento', 'N/A'):,}")
            print(f"✅ Agravamentos em 30 dias: {pred_data.get('agravamento_30_dias', 'N/A'):,}")
            print(f"✅ Custo estimado (30 dias): R$ {pred_data.get('custo_estimado_30_dias', 'N/A'):,}")
            print(f"✅ Internações projetadas: {pred_data.get('internacoes_projetadas', 'N/A'):,}")
            print(f"✅ Algoritmo usado: {pred_data.get('algoritmo', 'N/A')}")
        else:
            print("ℹ️ Nenhum paciente sem agendamento encontrado")
    
    # 6. Solicitações de Risco Alto
    print("\n6️⃣ SOLICITAÇÕES DE RISCO ALTO...")
    solicitacoes = client.get_solicitacoes(risco="VERMELHO", limit=5)
    if solicitacoes and solicitacoes.get('status') == 'sucesso':
        dados = solicitacoes['dados']
        print(f"✅ Encontradas {len(dados)} solicitações de risco vermelho:")
        for i, sol in enumerate(dados[:3], 1):
            print(f"   {i}. ID: {sol.get('solicitacao_id', 'N/A')}")
            print(f"      Especialidade: {sol.get('procedimento_especialidade', 'N/A')}")
            print(f"      Status: {sol.get('solicitacao_status', 'N/A')}")
    
    # 7. Relatório Resumido
    print("\n7️⃣ RELATÓRIO RESUMIDO...")
    relatorio = client.get_relatorio_resumo()
    if relatorio and relatorio.get('status') == 'sucesso':
        resumo = relatorio['resumo']
        print(f"✅ Total de solicitações: {resumo.get('total_solicitacoes', 'N/A'):,}")
        print(f"✅ Confirmados: {resumo.get('confirmados', 'N/A'):,}")
        print(f"✅ Taxa de confirmação: {resumo.get('taxa_confirmacao', 'N/A')}%")
        
        # Top especialidades
        top_esp = relatorio.get('top_especialidades', [])
        if top_esp:
            print("✅ Top 3 especialidades:")
            for i, esp in enumerate(top_esp[:3], 1):
                print(f"   {i}. {esp.get('procedimento_especialidade', 'N/A')}: {esp.get('count', 'N/A'):,} solicitações")
    
    # 8. Informações do Modelo ML
    print("\n8️⃣ INFORMAÇÕES DO MODELO ML...")
    modelo_info = client.get_modelo_info()
    if modelo_info and modelo_info.get('status') == 'sucesso':
        modelo = modelo_info['modelo']
        print(f"✅ Modelo treinado: {modelo.get('treinado', 'N/A')}")
        print(f"✅ Algoritmo: {modelo.get('algoritmo', 'N/A')}")
        
        metricas = modelo.get('metricas', {})
        if metricas:
            print(f"✅ Acurácia: {metricas.get('acuracia', 'N/A'):.1%}")
            print(f"✅ Precisão: {metricas.get('precisao', 'N/A'):.1%}")
            print(f"✅ Recall: {metricas.get('recall', 'N/A'):.1%}")
            print(f"✅ F1-Score: {metricas.get('f1_score', 'N/A'):.1%}")
    
    # 9. Predição ML Personalizada
    print("\n9️⃣ PREDIÇÃO ML PERSONALIZADA...")
    dados_predicao = {
        "solicitacao_risco": "VERMELHO",
        "procedimento_especialidade": "Cardiologia",
        "paciente_faixa_etaria": "60-74"
    }
    
    predicao_ml = client.fazer_predicao_ml(dados_predicao)
    if predicao_ml and predicao_ml.get('status') == 'sucesso':
        pred = predicao_ml['predicao']
        print(f"✅ Probabilidade de agravamento: {pred.get('probabilidade_agravamento', 'N/A'):.1%}")
        print(f"✅ Classificação: {pred.get('classificacao', 'N/A')}")
        print(f"✅ Predição: {pred.get('predicao_agravamento', 'N/A')}")
    
    # 10. Opções de Filtros
    print("\n🔟 OPÇÕES DE FILTROS DISPONÍVEIS...")
    filtros = client.get_filtros_opcoes()
    if filtros and filtros.get('status') == 'sucesso':
        filtros_data = filtros['filtros']
        riscos = filtros_data.get('riscos', [])
        especialidades = filtros_data.get('especialidades', [])
        
        print(f"✅ Riscos disponíveis: {', '.join(riscos)}")
        print(f"✅ Total de especialidades: {len(especialidades)}")
        if especialidades:
            print(f"✅ Primeiras 5 especialidades: {', '.join(especialidades[:5])}")
    
    print("\n" + "=" * 70)
    print("✅ EXEMPLO CONCLUÍDO COM SUCESSO!")
    print("📚 Para mais informações, consulte a documentação completa.")
    print("🌐 Acesse: http://127.0.0.1:8000/docs para interface interativa")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Exemplo interrompido pelo usuário.")
    except Exception as e:
        print(f"\n\n❌ Erro durante execução: {e}")
        print("💡 Verifique se a API está rodando em http://127.0.0.1:8000")

