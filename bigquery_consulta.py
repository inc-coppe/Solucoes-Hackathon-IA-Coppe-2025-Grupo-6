# Importa a biblioteca cliente do Google BigQuery
from google.cloud import bigquery

# 1. Configure os detalhes do projeto e da query
# O ID do seu projeto no Google Cloud.
project_id = "rj-sms-sandbox"
# A sua query SQL.
sql_query = """
    SELECT *
    FROM `hackathon_coppe.marcacao`
    LIMIT 10
"""

# 2. Crie um cliente BigQuery
# O cliente usará as credenciais configuradas no seu ambiente
# (através do comando 'gcloud auth application-default login').
try:
    client = bigquery.Client(project=project_id)
    print("Cliente BigQuery criado com sucesso.")

    # 3. Execute a query
    print("Executando a query...")
    query_job = client.query(sql_query)  # Faz uma requisição para a API

    print("Query executada. Aguardando resultados...")

    # 4. Imprima os resultados
    print("-" * 30)
    print("Resultados da Query:")
    for row in query_job:
        # 'row' se comporta como uma tupla e também permite acesso por nome de coluna
        print(dict(row))
    print("-" * 30)

except Exception as e:
    print(f"Ocorreu um erro: {e}")