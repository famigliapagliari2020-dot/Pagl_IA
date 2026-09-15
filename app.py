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

# 1. CARICAMENTO DEL MODELLO (Eseguito solo al primo avvio)
@st.cache_resource
def load_private_model():
    try:
        hf_token = st.secrets["HF_TOKEN"]
        
        with st.spinner("Scarimento del file GGUF da Hugging Face... Attendere prego."):
            model_path = hf_hub_download(
                repo_id=model_id,
                filename=model_file,
                token=hf_token
            )
        
        # Importiamo il motore aggiornato Llama-cpp
        from llama_cpp import Llama
        
        with st.spinner("Inizializzazione del modello in memoria..."):
            llm = Llama(
                model_path=model_path,
                n_ctx=2048, # Lunghezza massima del contesto
                n_threads=2 # Ottimizzato per la CPU gratuita di Streamlit
            )
        return llm
    except Exception as e:
        st.error(f"Errore critico durante il caricamento del file privato: {str(e)}")
        return None

# Avvia l'inizializzazione del modello
llm = load_private_model()

# 2. GESTIONE DELLA CHAT GRAFICA
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Ciao! Il motore Llama-CPP è pronto. Come posso aiutarti oggi?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    if llm is None:
        st.error("Impossibile rispondere: il modello non è stato caricato correttamente.")
        st.stop()
        
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        try:
            # Prepariamo il prompt convertendo la cronologia in formato testo semplice
            prompt_text = ""
            for m in st.session_state.messages:
                prompt_text += f"<|im_start|>{m['role']}\n{m['content']}<|im_end|>\n"
            prompt_text += "<|im_start|>assistant\n"
            
            # Generazione in streaming parola per parola
            response_stream = llm(
                prompt_text,
                max_tokens=256,
                stream=True,
                stop=["<|im_end|>", "user:", "assistant:"]
            )
            
            for chunk in response_stream:
                token = chunk["choices"][0]["text"]
                if token:
                    full_response += token
                    response_placeholder.markdown(full_response + "▌")
                    
            response_placeholder.markdown(full_response)
        except Exception as e:
            full_response = f"Errore di elaborazione interna: {str(e)}"
            response_placeholder.error(full_response)
            
    st.session_state.messages.append({"role": "assistant", "content": full_response})
