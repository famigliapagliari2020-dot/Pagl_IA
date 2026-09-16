import streamlit as st
from huggingface_hub import InferenceClient

st.title("⚡ La Mia IA Privata Ultra-Veloce")
st.caption("Chat protetta connessa alle API serverless ad alta velocità.")

# Puntiamo direttamente al tuo repository GGUF privato
model_id = "Username97482/Pagl_IA_gguf"
model_file = "llama-3-8b.Q4_K_M.gguf"

# Recupera il tuo token Write segreto dai Secrets di Streamlit
hf_token = st.secrets["HF_TOKEN"]

# Configura il client per connettersi in modo sicuro al file privato
client = InferenceClient(token=hf_token)

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Ciao! Ora sono connesso alle API rapide. Fami una domanda e ti risponderò all'istante!"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        try:
            # Chiamata corretta per estrarre le risposte dal GGUF privato senza scaricarlo
            for message in client.chat_completion(
                messages=st.session_state.messages,
                model=model_id,
                max_tokens=256, 
                stream=True,
                extra_body={"model_file": model_file}
            ):
                token = message.choices.delta.content
                if token:
                    full_response += token
                    response_placeholder.markdown(full_response)
        except Exception as e:
            full_response = f"Errore di connessione rapida: {str(e)}"
            response_placeholder.error(full_response)
            
    st.session_state.messages.append({"role": "assistant", "content": full_response})
