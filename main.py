from groq import Groq
import streamlit as st 
import time
import os

# pip install groq 

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

st.title("Converse com um piloto e avião") 
pergunta  = st.text_input('Pergunta: ')

if st.button('enviar'):
    # if pergunta.strip():
        reposta =  client.chat.completions.create(
        model = "llama-3.3-70b-versatile",
        # temperature=0.7,

        messages=[
        {
        'role':'system',
        'content':"Você é piloto internecional e especialista em motores de avião"
        },
        {
            'role':'user',
            'content': pergunta
            
        }
        ]
        )

        st.text(reposta.choices[0].message.content)
        time.sleep(0)
   