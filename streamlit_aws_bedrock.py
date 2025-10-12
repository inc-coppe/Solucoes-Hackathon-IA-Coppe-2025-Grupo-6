import streamlit as st
import boto3
import json

# Configurar cliente Bedrock
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

st.title("Chat com Claude 3.5 Sonnet")

# Input do usuário
prompt = st.text_area("Digite seu prompt:", height=100)

if st.button("Enviar"):
    if prompt:
        try:
            # Preparar payload para Claude 3.5 Sonnet
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1000,
                "messages": [{"role": "user", "content": prompt}]
            })
            
            # Invocar modelo usando inference profile
            response = bedrock.invoke_model(
                modelId="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
                body=body
            )
            
            # Processar resposta
            result = json.loads(response['body'].read())
            answer = result['content'][0]['text']
            
            st.subheader("Resposta:")
            st.write(answer)
            
        except Exception as e:
            st.error(f"Erro: {str(e)}")
    else:
        st.warning("Digite um prompt primeiro.")
