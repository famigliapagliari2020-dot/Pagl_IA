import streamlit as st
from huggingface_hub import hf_hub_download
import os

st.title("🤖 La Mia IA Privata")
st.caption("Chat protetta caricata in locale dal tuo modello GGUF.")

# Il tuo modello GGUF originale salvato con successo all'inizio
model_id = "Username97482/Pagl_IA_gguf"
model_file = "llama-3-8b-Q4_K_M.gguf"

# 1. CARICAMENTO DEL MODELLO (Eseguito solo al primo avvio della pagina)
@st.cache_resource
def load_private_model():
    try:
        hf_token = st.secrets["HF_TOKEN"]
        
        with st.spinner("Scaricamento del file GGUF da Hugging Face... Attendere prego (circa 1-2 minuti)."):
            model_path = hf_hub_download(
                repo_id=model_id,
                filename=model_file,
                token=hf_token
            )
        
        from llama_cpp import Llama
        
        with st.spinner("Inizializzazione del modello nella memoria di Streamlit..."):
            llm = Llama(
                model_path=model_path,
                n_ctx=1024, # Finestra di contesto ottimizzata per la CPU gratuita
                n_threads=2 # Sfrutta al meglio i core gratuiti del server
            )
        return llm
    except Exception as e:
        st.error(f"Errore durante il caricamento del file privato: {str(e)}")
        return None

llm = load_private_model()

# 2. INTERFACCIA DELLA CHAT
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Ciao! Il motore GGUF locale è pronto. Come posso aiutarti oggi?"}]

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
        full_response = ""
        
        try:
            # Formattiamo la cronologia dei messaggi in un formato testo semplice standard
            prompt_text = ""
            for m in st.session_state.messages:
                prompt_text += f"{m['role']}: {m['content']}\n"
            prompt_text += "assistant: "
            
            # Generazione in streaming parola per parola
            response_stream = llm(
                prompt_text,
                max_tokens=256,
                stream=True,
                stop=["user:", "assistant:", "\n"]
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
