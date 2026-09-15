import streamlit as st
from huggingface_hub import hf_hub_download
import os

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
st.caption("Chat protetta caricata localmente in cloud dal tuo modello GGUF.")

# Identificativi del modello privato su Hugging Face
model_id = "Username97482/Pagl_IA_gguf"
model_file = "llama-3-8b.Q4_K_M.gguf"

# 1. SCARICAMENTO E CARICAMENTO DEL MODELLO (Eseguito solo la prima volta)
@st.cache_resource
def load_private_model():
    try:
        # Recupera il token segreto per superare il blocco del repo privato
        hf_token = st.secrets["HF_TOKEN"]
        
        # Scarica il file GGUF nella memoria temporanea del server di Streamlit
        with st.spinner("Caricamento del modello privato in corso... Attendere circa 1-2 minuti."):
            model_path = hf_hub_download(
                repo_id=model_id,
                filename=model_file,
                token=hf_token
            )
        
        # Usiamo ctransformers (incluso nelle dipendenze) per far girare il file .gguf
        from ctransformers import AutoModelForCausalLM
        llm = AutoModelForCausalLM.from_pretrained(
            model_path,
            model_type="llama",
            gpu_layers=0 # Gira interamente su CPU gratuita di Streamlit
        )
        return llm
    except Exception as e:
        st.error(f"Errore critico durante il caricamento del file privato: {str(e)}")
        return None

# Avvia l'inizializzazione del modello
llm = load_private_model()

# 2. GESTIONE DELLA CHAT GRAFICA
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Ciao! Il modello è stato caricato correttamente nel server Streamlit. Come posso aiutarti oggi?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    if llm is None:
        st.error("Impossibile rispondere: il modello non è stato caricato.")
        st.stop()
        
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        
        # Generazione della risposta locale
        try:
            full_response = ""
            # Converte la cronologia dei messaggi in testo semplice per il modello
            context = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages]) + "\nassistant: "
            
            # Genera i token in modalità streaming (parola per parola)
            for token in llm(context, stream=True, max_new_tokens=256):
                full_response += token
                response_placeholder.markdown(full_response + "▌")
                
            response_placeholder.markdown(full_response)
        except Exception as e:
            full_response = f"Errore di elaborazione interna: {str(e)}"
            response_placeholder.error(full_response)
            
    st.session_state.messages.append({"role": "assistant", "content": full_response})
