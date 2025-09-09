import json
import os
import redis
from openai import OpenAI
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# --- 1. INITIALIZATION AND CONFIGURATION ---
load_dotenv()
app = Flask(__name__)
client = OpenAI() # The API key will be read automatically from environment variables

# --- 2. CONNECT TO REDIS DATABASE ---
# Gets the Redis URL from the environment variables you'll set up on Render
redis_url = os.environ.get("REDIS_URL")
if not redis_url:
    raise Exception("The REDIS_URL environment variable has not been set.")
# Connects to Redis. 'decode_responses=True' makes it easier to work with strings.
redis_client = redis.from_url(redis_url, decode_responses=True)

# --- 3. LOAD THE KNOWLEDGE BASE (DONE ONCE AT STARTUP) ---
try:
    # Note the path correction to use os.path.join for compatibility
    instructions_path = os.path.join("Banco de dados", "Instructions.txt")
    with open(instructions_path, "r", encoding="utf-8") as f:
        instrucao_sistema = f.read()
except FileNotFoundError:
    print("Warning: 'Instructions.txt' file not found. Using default instructions.")
    instrucao_sistema = "You are an insurance sales assistant, an expert in finding the best policy for each client. Be cordial, helpful, and clear in your explanations."

# --- 4. THE API ROUTE (THE WEBHOOK THAT RECEIVES MESSAGES) ---
@app.route('/webhook', methods=['POST'])
def webhook():
    dados_recebidos = request.get_json()

    if not dados_recebidos or 'id_usuario' not in dados_recebidos or 'mensagem' not in dados_recebidos:
        return jsonify({"erro": "Invalid data. 'id_usuario' and 'mensagem' are required."}), 400

    id_usuario = dados_recebidos['id_usuario']
    mensagem_usuario = dados_recebidos['mensagem']
    
    # Fetch the user's data (conversation history) from Redis
    historico_json = redis_client.get(id_usuario)
    historico_conversa = json.loads(historico_json) if historico_json else None
    
    # If it's a new user, create a new history for them
    if not historico_conversa:
        historico_conversa = [
            {"role": "system", "content": instrucao_sistema}
        ]
        print(f"New user detected: {id_usuario}")

    # Add the new user message to their personal history
    historico_conversa.append({"role": "user", "content": mensagem_usuario})

    try:
        # Call the OpenAI API with the user's specific history
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=historico_conversa
        )
        resposta_assistente = response.choices[0].message.content

        # Add the AI's response to the user's history
        historico_conversa.append({"role": "assistant", "content": resposta_assistente})

        # Save the updated conversation history back to Redis
        redis_client.set(id_usuario, json.dumps(historico_conversa))
        # Optional: Set an expiration time for the conversation (e.g., 24 hours)
        redis_client.expire(id_usuario, 86400)
        
        # Return a simple JSON response to n8n or any other service
        return jsonify({
            "resposta_para_usuario": resposta_assistente
        })

    except Exception as e:
        print(f"Error processing message for {id_usuario}: {e}")
        return jsonify({"erro": "An internal server error occurred."}), 500

# --- 5. COMMAND TO START THE SERVER ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

