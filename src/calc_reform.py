import streamlit as st
import pandas as pd

def calcular_cenarios(piscofins, iss, receita_anual, receita_zfm_prct,
                     custos_operacao, custos_simples_prct):
    carga_tributaria_atual = piscofins + iss
    
    aliqs = [0.25, 0.26, 0.27, 0.28]
    dados = []
    
    for aliq in aliqs:
        debitos = receita_anual * (100 - receita_zfm_prct)/100 * aliq
        
        custos_simples = custos_simples_prct/100 * custos_operacao
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
            piscofins = st.number_input("PIS/COFINS anual (R$)", min_value=0.0, format='%.2f')
        with col2:
            iss = st.number_input("ISS anual (R$)", min_value=0.0, format='%.2f')
    
    # Seção 2: Receita Atual
    with st.container():
        st.subheader("Receita Atual")
        col3, col4 = st.columns(2)
        with col3:
            receita_anual = st.number_input("Receita anual (R$)", min_value=0.0, format='%.2f')
        with col4:
            receita_zfm_prct = st.number_input("% Receita na Zona Franca de Manaus", 
                                             min_value=0.0, max_value=100.0, format='%.2f')
    
    # Seção 3: Custos da Operação
    with st.container():
        st.subheader("Custos da Operação")
        col5, col6 = st.columns(2)
        with col5:
            custos_operacao = st.number_input("Custo operacional anual (R$)", 
                                            min_value=0.0, format='%.2f')
        with col6:
            custos_simples_prct = st.number_input("% Custos com fornecedores do Simples Nacional", 
                                                min_value=0.0, max_value=100.0, format='%.2f')
    
    # Botão de submissão centralizado
    st.markdown("---")
    submitted = st.form_submit_button("🚀 Calcular Impacto", use_container_width=True)

# Parte 2: Resultados e CTA
if submitted:
    df_cenarios, df_resumo, carga_atual = calcular_cenarios(
        piscofins, iss, receita_anual, receita_zfm_prct,
        custos_operacao, custos_simples_prct
    )
    
    max_diferenca = df_resumo['Diferença (R$)'].max()
    
    if max_diferenca > 0 and carga_atual > 0:
        percentual_aumento = (max_diferenca / carga_atual) * 100
        
        # Mensagem de alerta
        st.error(f"""
        ⚠️ **Atenção:** Sua carga tributária pode aumentar em até **{percentual_aumento:.1f}%** após a Reforma Tributária!
        """)
        
        # Gráfico comparativo
        st.subheader("📊 Comparativo de Carga Tributária")
        
        # Preparar dados para o gráfico
        dados_grafico = pd.DataFrame({
            'Cenário': ['Atual', 'Melhor Cenário', 'Pior Cenário'],
            'Valor (R$)': [
                carga_atual,
                df_resumo['Carga Estimada (R$)'].iloc[0],
                df_resumo['Carga Estimada (R$)'].iloc[1]
            ]
        })
        
        # Configurar o gráfico
        st.bar_chart(
            dados_grafico.set_index('Cenário'),
            color="#C7C7C6",
            use_container_width=True,
            height=400
        )       
        
        st.caption("🔍 Valores estimados considerando diferentes alíquotas da reforma tributária")
        
        # Call to Action
        with st.expander("📩 **QUERO MINHA ANÁLISE COMPLETA!**", expanded=True):
            st.markdown("""
            🚨 **Não perca tempo!** Nossos especialistas prepararam um relatório personalizado com:
            - Detalhamento de débitos e créditos
            - Comparativos entre cenários de tributação
            - Análise de riscos e oportunidades
            """)
            
            with st.form(key='cta_form'):
                empresa = st.text_input("🏢 Nome da empresa")
                cnpj = st.text_input("📋 CNPJ")
                nome = st.text_input("👤 Nome completo")
                telefone = st.text_input("📱 Telefone para contato")
                email = st.text_input("📧 E-mail para envio do relatório")
                
                if st.form_submit_button("👉 ENVIAR RELATÓRIO AGORA"):
                    st.success("""
                    ✅ Relatório enviado com sucesso! Verifique sua caixa de entrada nos próximos minutos.
                    🔔 Fique atento à nossa equipe entrará em contato para oferecer suporte personalizado!
                    """)
        
        st.markdown("---")