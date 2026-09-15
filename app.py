import streamlit as st
from huggingface_hub import InferenceClient

# 1. Configurazione Password di sicurezza per te e i tuoi amici
PASSWORD_SEGRETA = "Paglia2012!" # Scegli la password che vuoi

# Controllo della password nell'interfaccia grafica
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.title("🔒 Accesso Riservato")
    user_password = st.text_input("Inserisci la password per usare l'IA:", type="password")
    if st.button("Accedi"):
        if user_password == PASSWORD_SEGRETA:
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("⚠️ Password errata!")
    st.stop()

# 2. Interfaccia della Chat (visibile solo se la password è corretta)
st.title("🤖 La Mia IA Privata")
st.caption("Chat protetta per me e i miei amici.")

# Inserisci il percorso del tuo modello GGUF privato su Hugging Face
model_id = "Username97482/Pagl_IA_gguf"
model_file = "llama-3-8b.Q4_K_M.gguf"

# Recupera in modo sicuro il token che inseriremo nel pannello di Streamlit
hf_token = st.secrets["HF_TOKEN"]
client = InferenceClient(model=f"{model_id}/{model_file}", token=hf_token)

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Ciao! Come posso aiutarti oggi?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    # Richiesta al modello su Hugging Face
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        try:
            for message in client.chat_completion(st.session_state.messages, max_tokens=512, stream=True):
                token = message.choices.delta.content
                if token:
                    full_response += token
                    response_placeholder.markdown(full_response)
        except Exception as e:
            full_response = f"Errore di connessione al modello: {str(e)}"
            response_placeholder.error(full_response)
            
    st.session_state.messages.append({"role": "assistant", "content": full_response})
