import os
from groq import Groq
import pandas as pd
import streamlit as st


# ============================================================
# INICIALIZAÇÃO DO CLIENTE GROQ
# ============================================================

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)


# ============================================================
# TÍTULO DO APP
# ============================================================

st.title("📊 Análise Financeira Pessoal")


# ============================================================
# HISTÓRICO DE TRANSAÇÕES
# ============================================================

if "historico_financeiro" not in st.session_state:
    st.session_state.historico_financeiro = []


# ============================================================
# FORMULÁRIO DE ENTRADA DE DADOS
# ============================================================

valor = st.number_input(
    "Digite o valor (R$): ",
    min_value=0.0,
    step=0.50,
    format="%.2f"
)

tipo_movimentacao = st.radio(
    "Selecione o tipo:",
    ["Receita", "Despesa"]
)

data = st.date_input(
    "Data do lançamento:"
)

descricao = st.text_input(
    "Descrição/Categoria (ex: Salário, Aluguel, Supermercado):"
)


# ============================================================
# BOTÃO PARA ADICIONAR TRANSAÇÃO E ACIONAR A IA
# ============================================================

if st.button("Enviar e Analisar"):

    if valor > 0 and descricao.strip():

        # Adiciona o novo registro à lista do histórico
        st.session_state.historico_financeiro.append(
            {
                "Tipo": tipo_movimentacao,
                "Descrição": descricao,
                "Valor": valor,
                "Data": data,
            }
        )

        # ====================================================
        # TRANSFORMA O HISTÓRICO EM DATAFRAME
        # ====================================================

        df_atual = pd.DataFrame(
            st.session_state.historico_financeiro
        )

        # ====================================================
        # TRANSFORMA O DATAFRAME EM TEXTO PARA A IA
        # ====================================================

        texto_financeiro = df_atual.to_string(
            index=False
        )

        # ====================================================
        # CRIA O PROMPT PARA A IA
        # ====================================================

        prompt_usuario = f"""
Aqui está o histórico atualizado de movimentações financeiras:

{texto_financeiro}

Calcule o saldo atual e faça uma análise direta sobre a minha saúde financeira atual.
"""

        # ====================================================
        # CHAMADA PARA A API DA GROQ
        # ====================================================

        resposta = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Você é um especialista em análise de gastos "
                        "pessoais. "
                        "Calcule o saldo líquido atual subtraindo as "
                        "despesas das receitas informadas no histórico. "
                        "Separe e classifique as informações do usuário "
                        "em categorias claras. "
                        "Siga sempre estas regras: "
                        "- Responda em tópicos quando houver mais de três itens. "
                        "- Seja extremamente direto e evite introduções longas. "
                        "Fale apenas sobre as informações inseridas pelo usuário. "
                        "- Mostre o valor do saldo final claramente no início "
                        "da resposta."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt_usuario,
                },
            ],
        )

        # ====================================================
        # EXIBE A ANÁLISE DA IA
        # ====================================================

        st.subheader("💡 Análise da IA")

        st.markdown(
            resposta.choices[0].message.content
        )

    else:

        st.warning(
            "Por favor, preencha a descrição e insira um valor maior que zero."
        )


# ============================================================
# ÁREA VISUAL DO HISTÓRICO CADASTRADO
# ============================================================

if st.session_state.historico_financeiro:

    st.divider()

    st.subheader("📋 Movimentações Lançadas")

    df_exibicao = pd.DataFrame(
        st.session_state.historico_financeiro
    )

    st.dataframe(
        df_exibicao,
        use_container_width=True
    )


# ============================================================
# BOTÃO PARA LIMPAR O HISTÓRICO
# ============================================================

if st.button("Limpar Histórico"):

    st.session_state.historico_financeiro = []

    st.rerun()
