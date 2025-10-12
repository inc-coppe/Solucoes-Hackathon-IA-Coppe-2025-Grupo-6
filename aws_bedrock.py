import boto3
import json

# 1. Crie um cliente para o Amazon Bedrock Runtime
# Certifique-se de que sua região está correta
bedrock_runtime = boto3.client(
    service_name='bedrock-runtime', 
    region_name='us-east-1'
)

# 2. Defina o prompt e o ID do modelo
prompt = "Olá! Por favor, escreva um poema curto sobre a beleza da Amazônia."
model_id = 'anthropic.claude-3-sonnet-20240229-v1:0'

# 3. Estruture o corpo da requisição (payload)
# A estrutura do corpo da requisição varia para cada modelo.
# Este é o formato para o Claude 3 Sonnet.
body = json.dumps({
    "anthropic_version": "bedrock-2023-05-31",
    "max_tokens": 1024,
    "messages": [
        {
            "role": "user",
            "content": [{"type": "text", "text": prompt}]
        }
    ]
})

try:
    # 4. Invoque o modelo
    response = bedrock_runtime.invoke_model(
        body=body,
        modelId=model_id,
        accept='application/json',
        contentType='application/json'
    )

    # 5. Processe a resposta
    response_body = json.loads(response.get('body').read())
    
    # Extrai o texto gerado da resposta
    generated_text = response_body.get('content')[0].get('text')

    print("Prompt Original:")
    print(prompt)
    print("\nResposta do Modelo:")
    print(generated_text)

except Exception as e:
    print(f"Ocorreu um erro ao invocar o modelo: {e}")