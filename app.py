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

# Configurazione titolo dell'applicazione web
st.title("🤖 La Mia IA Privata")
st.caption("Chat protetta e privata collegata al modello GGUF.")

# Percorso esatto del tuo modello privato su Hugging Face
model_id = "Username97482/Pagl_IA_gguf"
model_file = "llama-3-8b-Q4_K_M.gguf"

# RECUPERO DEL TOKEN: Recupera la chiave dai Secrets di Streamlit
hf_token = st.secrets["HF_TOKEN"]

# CONFIGURAZIONE CLIENT CORRETTA:
# Passiamo solo il token. Il modello specifico verrà indicato direttamente nella chiamata.
client = InferenceClient(token=hf_token)

# Gestione della memoria dei messaggi della chat
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Ciao! Ora la connessione è configurata correttamente. Come posso aiutarti oggi?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        try:
            # Invio della richiesta passando il model_id e il file GGUF specifico
            for message in client.chat_completion(
                messages=st.session_state.messages,
                model=model_id,
                max_tokens=512, 
                stream=True,
                extra_body={"model_file": model_file}
            ):
                token = message.choices.delta.content
                if token:
                    full_response += token
                    response_placeholder.markdown(full_response)
        except Exception as e:
            full_response = f"Errore di connessione al modello privato: {str(e)}"
            response_placeholder.error(full_response)
            
    st.session_state.messages.append({"role": "assistant", "content": full_response})
