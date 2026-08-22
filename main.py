import os
import pandas as pd
import streamlit as st
from groq import Groq

# Configuração da página Streamlit
st.set_page_config(page_title="Análise Financeira Pessoal", page_icon="📊")

# ============================================================
# INICIALIZAÇÃO DO CLIENTE GROQ
# ============================================================
# O SDK da Groq busca automaticamente a variável GROQ_API_KEY no ambiente
api_key = os.environ.get("GROQ_API_KEY")

if not api_key:
    st.error("⚠️ A variável de ambiente GROQ_API_KEY não foi configurada no Render!")
    st.stop()

client = Groq(api_key=api_key)

# ============================================================
# TÍTULO DO APP
# ============================================================
st.title("📊 Análise Financeira Pessoal")

# ============================================================
# INICIALIZAÇÃO DO SESSION STATE
# ============================================================
if "historico_financeiro" not in st.session_state:
    st.session_state.historico_financeiro = []

if "ultima_analise" not in st.session_state:
    st.session_state.ultima_analise = None

# ============================================================
# FORMULÁRIO DE ENTRADA DE DADOS
# ============================================================
with st.form(key="form_transacao"):
    valor = st.number_input(
        "Digite o valor (R$):",
        min_value=0.0,
        step=0.50,
        format="%.2f"
    )
    
    tipo_movimentacao = st.radio(
        "Selecione o tipo:",
        ["Receita", "Despesa"],
        horizontal=True
    )
    
    data = st.date_input("Data do lançamento:")
    
    descricao = st.text_input(
        "Descrição/Categoria (ex: Salário, Aluguel, Supermercado):"
    )
    
    submit_button = st.form_submit_button("Enviar e Analisar")

# ============================================================
# PROCESSAMENTO DO FORMULÁRIO E CHAMADA DA IA
# ============================================================
if submit_button:
    if valor > 0 and descricao.strip():
        # Adiciona o novo registro
        st.session_state.historico_financeiro.append(
            {
                "Tipo": tipo_movimentacao,
                "Descrição": descricao.strip(),
                "Valor": valor,
                "Data": data.strftime("%d/%m/%Y"),
            }
        )

        df_atual = pd.DataFrame(st.session_state.historico_financeiro)
        texto_financeiro = df_atual.to_string(index=False)

        prompt_usuario = f"""
Aqui está o histórico atualizado de movimentações financeiras:

{texto_financeiro}

Calcule o saldo atual e faça uma análise direta sobre a minha saúde financeira atual.
"""

        with st.spinner("Analisando seus dados financeiros com IA..."):
            try:
                resposta = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "Você é um especialista em análise de gastos pessoais. "
                                "Calcule o saldo líquido atual subtraindo as despesas das receitas. "
                                "Separe e classifique as informações do usuário em categorias claras. "
                                "Siga sempre estas regras: "
                                "- Responda em tópicos quando houver mais de três itens. "
                                "- Seja extremamente direto e evite introduções longas. "
                                "- Fale apenas sobre as informações inseridas pelo usuário. "
                                "- Mostre o valor do saldo final claramente no início da resposta."
                            ),
                        },
                        {
                            "role": "user",
                            "content": prompt_usuario,
                        },
                    ],
                )
                # Salva no estado para a resposta não sumir nas interações
                st.session_state.ultima_analise = resposta.choices[0].message.content
            except Exception as e:
                st.error(f"Erro ao conectar com a API da Groq: {e}")
    else:
        st.warning("Por favor, preencha a descrição e insira um valor maior que zero.")

# ============================================================
# EXIBE A ANÁLISE DA IA (SE EXISTIR)
# ============================================================
if st.session_state.ultima_analise:
    st.subheader("💡 Análise da IA")
    st.markdown(st.session_state.ultima_analise)

# ============================================================
# ÁREA VISUAL DO HISTÓRICO CADASTRADO E BOTÃO LIMPAR
# ============================================================
if st.session_state.historico_financeiro:
    st.divider()
    st.subheader("📋 Movimentações Lançadas")

    df_exibicao = pd.DataFrame(st.session_state.historico_financeiro)
    st.dataframe(df_exibicao, use_container_width=True)

    if st.button("Limpar Histórico"):
        st.session_state.historico_financeiro = []
        st.session_state.ultima_analise = None
        st.rerun()
