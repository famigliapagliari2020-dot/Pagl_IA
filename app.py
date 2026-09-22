import streamlit as st
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer
from threading import Thread

st.set_page_config(page_title="IA Privata Locale", page_icon="⚡")
st.title("⚡ La Mia IA Privata in Colab")
st.caption("Chat protetta al 100%, eseguita sulla GPU di Google Colab senza API esterne.")

# 1. Configurazione del modello (Utilizziamo Phi-3 perché è leggero e potente per la GPU di Colab)
MODEL_ID = "Username97482/Pagl_IA_LoRA"

@st.cache_resource
def load_model():
    # Carica il tokenizer e il modello direttamente nella memoria GPU (cuda)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID, 
        torch_dtype=torch.float16, 
        device_map="auto"
    )
    return tokenizer, model

try:
    tokenizer, model = load_model()
except Exception as e:
    st.error(f"Assicurati di aver attivato la GPU T4 su Colab! Errore: {e}")
    st.stop()

# === IL TUO MODELLO PERSONALIZZATO ===
ISTRUZIONI_IL_MIO_MODELLO = """
Tu sei Pagl_IA, l'assistente virtuale privato creato da Username97482. 
Rispondi sempre mantenendo la tua personalità personalizzata, sii utile, 
accurato e segui le linee guida su cui sei stato addestrato.
"""

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Ciao! Ora sono attivo localmente sulla GPU di Colab. Come posso aiutarti oggi?"}
    ]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        # Prepariamo la struttura dei messaggi per il modello
        formatted_messages = [{"role": "system", "content": ISTRUZIONI_IL_MIO_MODELLO}]
        for m in st.session_state.messages:
            formatted_messages.append({"role": m["role"], "content": m["content"]})
            
        # Applichiamo il template di chat del modello
        inputs = tokenizer.apply_chat_template(
            formatted_messages, 
            add_generation_prompt=True, 
            return_tensors="pt"
        ).to("cuda")
        
        # Configuriamo lo streaming del testo in tempo reale su Streamlit
        streamer = TextIteratorStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)
        generation_kwargs = dict(inputs=inputs, streamer=streamer, max_new_tokens=512, temperature=0.7)
        
        # Avviamo la generazione in un thread separato per non bloccare l'interfaccia
        thread = Thread(target=model.generate, kwargs=generation_kwargs)
        thread.start()
        
        for new_text in streamer:
            full_response += new_text
            response_placeholder.markdown(full_response + "▌")
            
        response_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
