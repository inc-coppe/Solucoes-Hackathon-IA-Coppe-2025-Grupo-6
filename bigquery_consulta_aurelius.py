# Importa as bibliotecas cliente do Google BigQuery e CSV
from google.cloud import bigquery
import csv

# 1. Configure os detalhes do projeto e da query
# O ID do seu projeto no Google Cloud.
project_id = "rj-sms-sandbox"
# A sua query SQL base, sem LIMIT e OFFSET.
base_sql_query = """
    WITH
    -- SLA por risco
    sla_risco AS (
    SELECT * FROM UNNEST([
        STRUCT('VERMELHO' AS risco, 30  AS sla_dias),
        STRUCT('AMARELO'  AS risco, 90  AS sla_dias),
        STRUCT('VERDE'    AS risco, 180 AS sla_dias),
        STRUCT('AZUL'     AS risco, 210 AS sla_dias)
    ])
    ),

    -- Solicitações
    src_s AS (
    SELECT
        solicitacao_id,
        DATE(data_solicitacao) AS data_solicitacao,
        solicitacao_status,
        paciente_id,
        UPPER(solicitacao_risco) AS risco,
        CAST(procedimento_sisreg_id AS STRING) AS procedimento_id
    FROM `rj-sms-sandbox.hackathon_coppe.solicitacao`
    --WHERE data_solicitacao >= '2024-01-01' 
    ),

    -- Marcações (pode haver mais de uma)
    src_m AS (
    SELECT
        solicitacao_id,
        DATE(data_marcacao) AS data_marcacao
    FROM `rj-sms-sandbox.hackathon_coppe.marcacao`
    WHERE TRUE
        AND CAST(marcacao_executada AS INT) = 0
        --AND data_solicitacao >= '2025-01-01'
    ),

    src_procedimento AS (
    SELECT 
        procedimento_sisreg_id, 
        procedimento_tipo, 
        procedimento
    FROM `rj-sms-sandbox.hackathon_coppe.procedimento`

    ),

    -- Join principal: todas as solicitações (LEFT JOIN)
    joined AS (
    SELECT
        s.*,
        m.data_marcacao,
        p.procedimento_tipo,
        p.procedimento
    FROM src_s s
    LEFT JOIN src_m m
        ON s.solicitacao_id = m.solicitacao_id
    JOIN src_procedimento p
        ON s.procedimento_id = p.procedimento_sisreg_id
    ),

    -- Cálculo de prazo de atendimento
    base AS (
    SELECT
        j.*,
    sl.sla_dias,
    DATE_ADD(j.data_solicitacao, INTERVAL sl.sla_dias DAY) AS prazo_atendimento
    FROM joined j
    JOIN sla_risco sl ON j.risco = sl.risco
    ),

    -- Determina se o SLA está vencido
    calc AS (
    SELECT
        *,
        DATE_DIFF(CURRENT_DATE(), prazo_atendimento, DAY) AS dias_de_atraso
    FROM base
    ),

    -- Casos que extrapolaram o SLA e ainda não executaram o procedimento
    sla_vencido_aguardando AS (
    SELECT
        solicitacao_id,
        paciente_id,
        risco,
        data_solicitacao,
        solicitacao_status,
        procedimento_id,
        procedimento_tipo,
        procedimento,
        data_marcacao,
        prazo_atendimento,
        dias_de_atraso
    FROM calc
    )

    -- Resultado final
    SELECT *
    FROM sla_vencido_aguardando
    WHERE TRUE
    --AND CONTAINS_SUBSTR(procedimento, 'RESSONANCIA')
    ORDER BY dias_de_atraso DESC, data_solicitacao ASC
"""

# 2. Crie um cliente BigQuery
try:
    client = bigquery.Client(project=project_id)
    print("Cliente BigQuery criado com sucesso.")

    # 3. Defina os parâmetros de paginação
    offset = 0
    limit = 100000
    lote_numero = 1
    total_registros_gravados = 0

    while True:
        # Adiciona a paginação (LIMIT e OFFSET) à query
        paginated_sql_query = f"{base_sql_query} LIMIT {limit} OFFSET {offset}"
        
        print("-" * 50)
        print(f"Executando a consulta para o lote {lote_numero} (registros a partir de {offset})...")
        
        query_job = client.query(paginated_sql_query)
        results = query_job.result()
        
        # Converte o iterador para uma lista para poder verificar o tamanho
        rows = list(results)
        
        if not rows:
            print("Nenhum registro encontrado neste lote. Finalizando o processo.")
            break

        num_rows_in_batch = len(rows)
        print(f"Recebidos {num_rows_in_batch} registros.")

        # 4. Salve os resultados do lote em um arquivo CSV
        output_filename = f"resultado_bigquery_lote_{lote_numero}.csv"
        print(f"Salvando os resultados no arquivo: {output_filename}")

        with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Escreve o cabeçalho no arquivo
            headers = [field.name for field in results.schema]
            writer.writerow(headers)
            
            # Escreve as linhas do lote atual
            writer.writerows(rows)
        
        total_registros_gravados += num_rows_in_batch
        print(f"Arquivo '{output_filename}' gerado com sucesso.")

        # Se o número de registros retornados for menor que o limite,
        # significa que este é o último lote.
        if num_rows_in_batch < limit:
            print("Este foi o último lote de dados.")
            break
        
        # Prepara para o próximo lote
        offset += limit
        lote_numero += 1

    print("-" * 50)
    print(f"Processo finalizado. Total de {total_registros_gravados} registros gravados em {lote_numero -1} arquivo(s).")


except Exception as e:
    print(f"Ocorreu um erro: {e}")

