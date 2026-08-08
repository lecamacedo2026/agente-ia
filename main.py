from groq import Groq
import streamlit as st 



# pip install groq 

client = Groq (
api_key = "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"
)

st.title("Conversa com o Piloto") 
pergunta  = st.text_input('pergunta:')
if st.button('enviar'):
    # if pergunta.strip():
        reposta =  client.chat.completions.create(
        model = "llama-3.3-70b-versatile",
        # temperature=0.7,

        messages=[
        {
        'role':'system',
        'content':"Você é um piloto de avião."
        },
        {
            'role':'user',
            'content': pergunta
            
        }
        ]
        )

        st.text(reposta.choices[0].message.content)