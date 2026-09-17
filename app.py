import streamlit as st
from groq import Groq

st.set_page_config(page_title="IA Privata", page_icon="⚡")
st.title("⚡ La Mia IA Privata Ultra-Veloce")
st.caption("Chat protetta e istantanea alimentata dai server ad alta velocità di Groq.")

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# === IL TUO MODELLO PERSONALIZZATO (Sotto forma di System Prompt) ===
# Descrivi qui dentro esattamente come si deve comportare la tua IA,
# cosa sa fare, qual è il suo scopo o quali dati specifici deve ricordare.
ISTRUZIONI_IL_MIO_MODELLO = """
Tu sei Pagl_IA, l'assistente virtuale privato creato da Username97482. 
Rispondi sempre mantenendo la tua personalità personalizzata, sii utile, 
accurato e segui le linee guida su cui sei stato addestrato.
"""
# ===================================================================

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Ciao! Ora sono attivo sui server di Groq con le personalizzazioni del tuo modello. Come posso aiutarti oggi?"}
    ]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        try:
            # Prepariamo la lista dei messaggi includendo le istruzioni del tuo modello all'inizio
            messages_with_system = [
                {"role": "system", "content": ISTRUZIONI_IL_MIO_MODELLO}
            ] + st.session_state.messages

            completion = client.chat.completions.create(
                model="llama3-8b-8192", # Sfrutta l'hardware atomico di Groq
                messages=messages_with_system, # Passa la memoria + la tua personalizzazione
                temperature=0.7,
                stream=True
            )
            for chunk in completion:
                delta = chunk.choices[0].delta.content
                if delta:
                    full_response += delta
                    response_placeholder.markdown(full_response + "▌")
            response_placeholder.markdown(full_response)
        except Exception as e:
            full_response = f"Errore nell'SDK di Groq: {str(e)}"
            response_placeholder.error(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
