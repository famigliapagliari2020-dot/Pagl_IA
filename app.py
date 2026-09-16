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

st.title("⚡ La Mia IA Privata Ultra-Veloce")
st.caption("Chat istantanea collegata alle API di Hugging Face.")

# Puntiamo al nuovo modello con i pesi già uniti
model_id = "Username97482/Pagl_IA_Veloce"

# Recupera il token inserito nei Secrets di Streamlit
hf_token = st.secrets["HF_TOKEN"]

# Inizializza il client API ultra-veloce
client = InferenceClient(token=hf_token)

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Ciao! Ora sono attivo sui server ultra-rapidi. Come posso aiutarti?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        try:
            # Chiamata diretta nativa per i modelli di chat (ora funzionerà perché non è un GGUF isolato!)
            for message in client.chat_completion(
                messages=st.session_state.messages,
                model=model_id,
                max_tokens=512, 
                stream=True
            ):
                token = message.choices.delta.content
                if token:
                    full_response += token
                    response_placeholder.markdown(full_response)
        except Exception as e:
            full_response = f"Errore di connessione rapida: {str(e)}"
            response_placeholder.error(full_response)
            
    st.session_state.messages.append({"role": "assistant", "content": full_response})

            full_response = f"Errore di elaborazione interna: {str(e)}"
            response_placeholder.error(full_response)
            
    st.session_state.messages.append({"role": "assistant", "content": full_response})
