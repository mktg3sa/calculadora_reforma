import streamlit as st
import pandas as pd

def parse_brl(valor_str):
    """
    Converte uma string no formato brasileiro (1.234,56) para float.
    Caso o usuário não informe valor, retorna 0.0.
    Se o valor for inválido, exibe mensagem de erro e interrompe a execução.
    """
    if not valor_str:
        return 0.0
    try:
        # Remove os pontos (separador de milhares) e substitui a vírgula pelo ponto (separador decimal)
        return float(valor_str.replace('.', '').replace(',', '.'))
    except ValueError:
        st.error(f"Valor inválido: {valor_str}. Por favor, insira no formato 1.234,56")
        st.stop()

def parse_percentage(valor_str):
    """
    Converte uma string no formato brasileiro para float e garante que o valor esteja entre 0 e 100.
    """
    valor = parse_brl(valor_str)
    if valor < 0 or valor > 100:
        st.error("Por favor, insira um valor entre 0 e 100.")
        st.stop()
    return valor

def format_brl(valor):
    """
    Formata um número float para o padrão brasileiro:
    ponto para milhares e vírgula para decimais.
    """
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def calcular_cenarios(piscofins, iss, receita_anual, receita_zfm_prct,
                      custos_operacao, custos_simples_prct):
    carga_tributaria_atual = piscofins + iss

    aliqs = [0.25, 0.26, 0.27, 0.28]
    dados = []

    for aliq in aliqs:
        debitos = receita_anual * (100 - receita_zfm_prct) / 100 * aliq

        custos_simples = custos_simples_prct / 100 * custos_operacao
        custos_nao_simples = custos_operacao - custos_simples

        creditos = (custos_simples * 0.08) + (custos_nao_simples * aliq)

        carga_estimada = debitos - creditos

        dados.append({
            'Alíquota (%)': aliq * 100,
            'Débitos (R$)': debitos,
            'Créditos (R$)': creditos,
            'Carga Tributária Estimada (R$)': carga_estimada
        })

    df_cenarios = pd.DataFrame(dados)

    max_carga = df_cenarios['Carga Tributária Estimada (R$)'].max()
    min_carga = df_cenarios['Carga Tributária Estimada (R$)'].min()

    dados_resumo = {
        'Cenário': ['Melhor Caso', 'Pior Caso'],
        'Carga Estimada (R$)': [min_carga, max_carga],
        'Carga Atual (R$)': [carga_tributaria_atual, carga_tributaria_atual],
        'Diferença (R$)': [min_carga - carga_tributaria_atual, 
                           max_carga - carga_tributaria_atual]
    }

    df_resumo = pd.DataFrame(dados_resumo)

    return df_cenarios, df_resumo, carga_tributaria_atual

# Configuração da página
st.set_page_config(page_title="Calculadora Tributária", layout="wide")

# Parte 1: Formulário
with st.form(key='main_form'):
    st.header("📋 Insira os dados da sua empresa")

    # Seção 1: Impostos Pagos Atualmente
    with st.container():
        st.subheader("Impostos Pagos Atualmente")
        col1, col2 = st.columns(2)
        with col1:
            piscofins_str = st.text_input("PIS/COFINS anual (R$)", value="0,00")
        with col2:
            iss_str = st.text_input("ISS anual (R$)", value="0,00")

    # Seção 2: Receita Atual
    with st.container():
        st.subheader("Receita Atual")
        col3, col4 = st.columns(2)
        with col3:
            receita_anual_str = st.text_input("Receita anual (R$)", value="0,00")
        with col4:
            # Esse campo agora usará parse_percentage para validar valores entre 0 e 100
            receita_zfm_prct_str = st.text_input("% Receita na Zona Franca de Manaus", value="0,00")

    # Seção 3: Custos da Operação
    with st.container():
        st.subheader("Custos da Operação")
        col5, col6 = st.columns(2)
        with col5:
            custos_operacao_str = st.text_input("Custo operacional anual (R$)", value="0,00")
        with col6:
            # Esse campo agora usará parse_percentage para validar valores entre 0 e 100
            custos_simples_prct_str = st.text_input("% Custos com fornecedores do Simples Nacional", value="0,00")

    # Botão de submissão centralizado
    st.markdown("---")
    submitted = st.form_submit_button("🚀 Calcular Impacto", use_container_width=True)

# Parte 2: Processamento e Resultados
if submitted:
    # Converte as entradas no formato brasileiro para float
    piscofins = parse_brl(piscofins_str)
    iss = parse_brl(iss_str)
    receita_anual = parse_brl(receita_anual_str)
    receita_zfm_prct = parse_percentage(receita_zfm_prct_str)
    custos_operacao = parse_brl(custos_operacao_str)
    custos_simples_prct = parse_percentage(custos_simples_prct_str)

    df_cenarios, df_resumo, carga_atual = calcular_cenarios(
        piscofins, iss, receita_anual, receita_zfm_prct,
        custos_operacao, custos_simples_prct
    )

    max_diferenca = df_resumo['Diferença (R$)'].max()
    carga_estimada_max = max(df_resumo['Carga Estimada (R$)'])

    if max_diferenca > 0 and carga_atual > 0:
        percentual_aumento = (max_diferenca / carga_atual) * 100
        st.error(f"""
        ⚠️ **Atenção:** Sua carga tributária pode aumentar em até **{percentual_aumento:.1f}%** após a Reforma Tributária!
        """)
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="Carga Tributária Atual (R$)", value=format_brl(carga_atual))
        with col2:
            st.metric(label="Carga Tributária Estimada Máxima (R$)", value=format_brl(carga_estimada_max))
        st.subheader("📊 Comparativo de Carga Tributária")
        dados_grafico = pd.DataFrame({
            'Cenário': ['Atual', 'Melhor Cenário', 'Pior Cenário'],
            'Valor (R$)': [carga_atual, min(df_resumo['Carga Estimada (R$)']), carga_estimada_max]
        })
        st.bar_chart(
            dados_grafico.set_index('Cenário'),
            color="#FF4B4B",
            use_container_width=True,
            height=400
        )
    else:
        st.success("""
        🎉 **Atenção:** Pode ser que a Reforma Tributária traga impactos positivos para a sua operação! Acesse a análise 
                   completa e saiba como aproveitar essa oportunidade!
        """)
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="Carga Tributária Atual (R$)", value=format_brl(carga_atual))
        with col2:
            st.metric(label="Carga Tributária Estimada Máxima (R$)", value=format_brl(carga_estimada_max))
        st.subheader("📊 Comparativo de Carga Tributária")
        dados_grafico = pd.DataFrame({
            'Cenário': ['Atual', 'Estimado'],
            'Valor (R$)': [carga_atual, df_resumo['Carga Estimada (R$)'].mean()]
        })
        st.bar_chart(
            dados_grafico.set_index('Cenário'),
            color="#00C0F2",
            use_container_width=True,
            height=400
        )

    st.subheader("Detalhamento dos Cenários")
    df_detalhado = df_cenarios.copy()
    df_detalhado["Alíquota Estimada (%)"] = df_detalhado["Alíquota (%)"].apply(lambda x: f"{x:.2f}%".replace('.', ','))
    df_detalhado["Débitos (R$)"] = df_detalhado["Débitos (R$)"].apply(format_brl)
    df_detalhado["Créditos (R$)"] = df_detalhado["Créditos (R$)"].apply(format_brl)
    df_detalhado["Carga estimada (R$)"] = df_detalhado["Carga Tributária Estimada (R$)"].apply(format_brl)
    df_detalhado = df_detalhado.reset_index(drop=True)
    df_detalhado.insert(0, "Cenários", [f"Cenário {i+1}" for i in range(len(df_detalhado))])
    table_html = df_detalhado.to_html(index=False, escape=False)
    st.markdown(table_html, unsafe_allow_html=True)
    
    st.caption("🔍 Valores estimados considerando diferentes alíquotas da reforma tributária")
    
    with st.expander("📩 **QUERO MINHA ANÁLISE COMPLETA!**", expanded=False):
        st.markdown("""
        🚨 **Não perca tempo!** Nossos especialistas prepararam um relatório personalizado com:
        - Detalhamento de débitos e créditos
        - Comparativos entre cenários de tributação
        - Análise de riscos e oportunidades
        """)
        with st.form(key='cta_form'):
            col_a, col_b = st.columns(2)
            with col_a:
                empresa = st.text_input("🏢 Nome da empresa")
                cnpj = st.text_input("📋 CNPJ")
                regime = st.selectbox("📈 Regime Tributário", ["Lucro Presumido", "Lucro Real"])
            with col_b:
                nome = st.text_input("👤 Nome completo")
                telefone = st.text_input("📱 Telefone para contato")
                email = st.text_input("📧 E-mail para envio do relatório")
            if st.form_submit_button("👉 ENVIAR RELATÓRIO AGORA"):
                st.success("""
                ✅ Relatório enviado com sucesso! Verifique sua caixa de entrada nos próximos minutos.
                🔔 Fique atento à nossa equipe entrará em contato para oferecer suporte personalizado!
                """)
    
    st.markdown("---")