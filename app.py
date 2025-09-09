from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('API_KEY')

if not API_KEY:
    print("Erro: A chave da API não foi encontrada.")
    print("Por favor, crie um arquivo '.env' e adicione a linha: OPENAI_API_KEY='sua_chave_aqui'")
else:
    try:
        client = OpenAI(api_key=API_KEY)

        try:
            with open('Banco de dados\Instructions.txt', 'r', encoding='utf-8') as file:
                instrucoes = file.read()
        except FileNotFoundError:
            print("Aviso: O arquivo 'instructions.txt' não foi encontrado. Usando instruções padrão.")
            instrucoes = "Você é um assistente de vendas de seguros, especialista em encontrar a melhor apólice para cada cliente. Seja cordial, prestativo e claro em suas explicações."

        print("Iniciando o agente de vendas... Faça sua pergunta.")
        pergunta_do_usuario = input("Você: ")

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": instrucoes
                },
                {
                    "role": "user",
                    "content": pergunta_do_usuario
                }
            ]
        )

        resposta_do_agente = response.choices[0].message.content

        print("\nAgente de Vendas IA:")
        print(resposta_do_agente)

    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")

