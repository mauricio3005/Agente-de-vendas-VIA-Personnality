import streamlit as st
import requests
import uuid

# --- 1. CONFIGURAÇÃO DA PÁGINA E TÍTULO ---
st.set_page_config(page_title="Demo Agente de Seguros", layout="centered")
st.title("🤖 Agente de Vendas de Seguros")
st.caption("Esta é uma demonstração interativa do bot de seguros. Converse com ele para obter uma cotação.")

# --- 2. URL DA SUA NOVA API (QUE ESTÁ NO RENDER) ---
# MUITO IMPORTANTE: Verifique se esta é a URL correta do seu novo serviço.
URL_DO_BOT_API = "https://agente-de-vendas-via-personnality.onrender.com" 

# --- 3. GERENCIAMENTO DA MEMÓRIA DA CONVERSA NO STREAMLIT ---
# O Streamlit usa um "session_state" para guardar o histórico de cada sessão de chat.

# Inicializa o histórico de mensagens se ele não existir
if "messages" not in st.session_state:
    st.session_state.messages = []

# Gera um ID de usuário único para esta sessão de chat
if "user_id" not in st.session_state:
    st.session_state.user_id = "demo_streamlit_" + str(uuid.uuid4())

# --- 4. FUNÇÃO PARA CHAMAR SUA API NO RENDER ---
def chamar_api_do_bot(id_usuario, mensagem):
    """Envia a mensagem do usuário para a sua API e retorna a resposta."""
    try:
        # Monta o pacote de dados (payload) no formato que sua API espera
        payload = {
            "id_usuario": id_usuario,
            "mensagem": mensagem
        }
        # Faz a chamada POST para a sua API, com um timeout de 60 segundos
        response = requests.post(URL_DO_BOT_API, json=payload, timeout=60)
        
        # Verifica se a chamada foi bem-sucedida
        if response.status_code == 200:
            return response.json()
        else:
            # Retorna uma mensagem de erro se a API falhar
            return {"erro": f"Erro na API: Status {response.status_code}", "resposta_para_usuario": "Desculpe, estou com um problema técnico no momento. Tente novamente mais tarde."}
    
    except requests.exceptions.RequestException as e:
        # Retorna uma mensagem de erro se não conseguir se conectar à API
        return {"erro": f"Erro de conexão: {e}", "resposta_para_usuario": "Não consegui me conectar ao meu cérebro. Verifique a conexão com o servidor."}

# --- 5. LÓGICA DA INTERFACE DE CHAT ---

# Exibe o histórico de mensagens que já aconteceram na tela
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Cria o campo de entrada de texto no final da página
if prompt := st.chat_input("Digite sua solicitação de seguro aqui..."):
    # Adiciona e mostra a mensagem do usuário na tela
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Mostra uma animação de "digitando..." enquanto espera a resposta
    with st.spinner("O agente está analisando seu caso..."):
        # Chama a sua API no Render para obter a resposta inteligente
        resposta_api = chamar_api_do_bot(st.session_state.user_id, prompt)

    # Extrai a resposta da API de forma segura
    resposta_bot = resposta_api.get("resposta_para_usuario", "Não recebi uma resposta válida.")
    
    # Adiciona e mostra a resposta do bot na tela
    st.session_state.messages.append({"role": "assistant", "content": resposta_bot})
    with st.chat_message("assistant"):
        st.markdown(resposta_bot)
        # Se você adicionar gatilhos no futuro, pode exibir avisos aqui.
        # Exemplo:
        # gatilho_cotacao = resposta_api.get("gatilho_cotacao", False)
        # if gatilho_cotacao:
        #     st.info("ℹ️ *Gatilho de Cotação foi detectado!*")
```

---

### **Passo 3: Como Rodar o Chat de Teste**

1.  **Abra o terminal** na pasta do seu projeto (`bot_seguros_api`).
2.  **Instale as bibliotecas** (caso ainda não tenha feito para este projeto):
    ```bash
    pip install streamlit requests
    ```
3.  **Execute o comando:**
    ```bash
    streamlit run chat_teste.py
    
