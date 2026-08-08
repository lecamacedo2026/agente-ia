import os
import time
from groq import Groq
import pandas as pd
import streamlit as st

# Inicializa o cliente Groq
client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

st.title("📊 Análise Financeira Pessoal")

# 1. Criação do histórico de transações usando Session State
if "historico_financeiro" not in st.session_state:
    st.session_state.historico_financeiro = []

# Formulário de entrada de dados
valor = st.number_input("Digite o valor (R$): ", min_value=0.0, step=10.0)
tipo_movimentacao = st.radio("Selecione o tipo:", ["Receita", "Despesa"])
descricao = st.text_input(
    "Descrição/Categoria (ex: Salário, Aluguel, Supermercado):"
)

# Botão para adicionar a transação ao histórico e acionar a IA
if st.button("Enviar e Analisar"):
    if valor > 0 and descricao.strip():
        # Adiciona o novo registro à lista do histórico
        st.session_state.historico_financeiro.append(
            {
                "Tipo": tipo_movimentacao,
                "Descrição": descricao,
                "Valor": valor,
            }
        )

        # Transforma o histórico em um texto estruturado para a IA ler
        df_atual = pd.DataFrame(st.session_state.historico_financeiro)

        # Cria a mensagem detalhada combinando o histórico com o comando
        prompt_usuario = f"""
        Aqui está o meu histórico atualizado de movimentações financeiras:
        {df_atual.to_string(index=False)}
        
        Por favor, calcule o meu saldo atual (Receitas menos Despesas) e faça uma análise direta sobre a minha saúde financeira atual.
        """

        # Chamada para a API da Groq
        resposta = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Você é um especialista em análise de gastos"
                        " pessoais. Calcule o saldo líquido atual subtraindo as"
                        " despesas das receitas informadas no histórico. Separe"
                        " e classifique as informações do usuário em categorias"
                        " claras. Siga sempre estas regras: - Responda em"
                        " tópicos quando houver mais de três itens. - Seja"
                        " extremamente direto e evite introduções longas. Fale"
                        " apenas sobre as informações inseridas pelo usuário. -"
                        " Mostre o valor do saldo final claramente no início da"
                        " resposta."
                    ),
                },
                {"role": "user", "content": prompt_usuario},
            ],
        )

        # Exibe a análise da IA na tela
        st.subheader("💡 Análise da IA")
        st.markdown(resposta.choices[0].message.content)

    else:
        st.warning("Por favor, preencha a descrição e insira um valor maior que zero.")

# --- Área Visual do Histórico Cadastrado ---
if st.session_state.historico_financeiro:
    st.divider()
    st.subheader("📋 Movimentações Lançadas")
    df_exibicao = pd.DataFrame(st.session_state.historico_financeiro)
    st.dataframe(df_exibicao, use_container_width=True)

    # Botão para reiniciar o histórico se necessário
    if st.button("Limpar Histórico"):
        st.session_state.historico_financeiro = []
        st.rerun()
