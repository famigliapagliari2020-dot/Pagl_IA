import streamlit as st
from google.protobuf import sys

# Proviamo a importare groq, altrimenti usiamo una richiesta HTTP pulita
import requests

st.title("⚡ La Mia IA Privata Ultra-Veloce")
st.caption("Chat protetta e istantanea alimentata dai server ad alta velocità di Groq.")

# Recupera la chiave dai Secrets di Streamlit
groq_api_key = st.secrets["GROQ_API_KEY"]

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Ciao! Ora sono attivo sui server di Groq a super velocità. Come posso aiutarti oggi?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        try:
            # Effettuiamo la chiamata diretta alle API di Groq per usare Llama 3 in modo istantaneo
            headers = {
                "Authorization": f"Bearer {groq_api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "llama3-8b-8192", # Usa Llama 3 8B ufficiale alla massima velocità
                "messages": st.session_state.messages,
                "temperature": 0.7
            }
            
            response = requests.post("https://groq.com", headers=headers, json=data)
            result = response.json()
            
            if "choices" in result:
                full_response = result["choices"][0]["message"]["content"]
                response_placeholder.markdown(full_response)
            else:
                full_response = f"Errore API: {result.get('error', {}).get('message', 'Errore sconosciuto')}"
                response_placeholder.error(full_response)
                
        except Exception as e:
            full_response = f"Errore di connessione rapida: {str(e)}"
            response_placeholder.error(full_response)
            
    st.session_state.messages.append({"role": "assistant", "content": full_response})
