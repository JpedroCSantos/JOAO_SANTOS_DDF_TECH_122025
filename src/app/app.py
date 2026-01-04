import os
import jwt
import time
import pandas as pd
import streamlit as st
import plotly.express as px
import streamlit.components.v1 as components

from pathlib import Path
from openai import OpenAI

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Airbnb Rio - Data App",
    page_icon="🏖️",
    layout="wide"
)

try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except KeyError:
    st.warning("⚠️ Chave da OpenAI não encontrada. O Módulo 2 não funcionará.")
    client = None
    
@st.cache_data
def load_data():
    """Carrega dados dos arquivos CSV locais"""
    
    BASE_DIR = Path(__file__).resolve().parents[2]
    DATA_DIR = BASE_DIR / "data" / "gold"
    path_listings = DATA_DIR / "DIM_LISTINGS.csv"
    path_reviews = DATA_DIR / "FACT_REVIEWS.CSV"

    if not os.path.exists(path_listings) or not os.path.exists(path_reviews):
        return None, None

    df_main = pd.read_csv(path_listings)
    df_rev = pd.read_csv(path_reviews)
    
    return df_main, df_rev

# --- PEGA O URL DO DASHBOARD CRIADO NO METABASE ---
@st.cache_data
def load_metabase_dashboard():
    METABASE_SITE_URL = "http://metabase-treinamentos.dadosfera.ai"
    METABASE_SECRET_KEY = st.secrets["METABASE_SECRET_KEY"]

    payload = {
        "resource": {"dashboard": 233},
        "params": {
            
        },
        "exp": round(time.time()) + (60 * 10) # 10 minute expiration
    }
    token = jwt.encode(payload, METABASE_SECRET_KEY, algorithm="HS256")

    iframeUrl = METABASE_SITE_URL + "/embed/dashboard/" + token + "#bordered=true&titled=true"

    return iframeUrl


df, df_reviews = load_data()
if df is None:
    st.error("❌ Erro: Arquivos de dados não encontrados na pasta 'data/gold'.")
    st.stop()

# --- SIDEBAR DE NAVEGAÇÃO ---
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/6/69/Airbnb_Logo_Bélo.svg", width=150)
st.sidebar.title("Navegação")
page = st.sidebar.radio("Ir para:", ["Dashboard de Mercado", "Gerador de Anúncios", "Smart Investor"])

st.sidebar.markdown("---")
st.sidebar.info("Case Técnico Dadosfera | Deploy Local/File-Based")

# ==============================================================================
# MÓDULO 1: DASHBOARD
# ==============================================================================
if page == "Dashboard de Mercado":
    st.title("Market Intelligence: Rio de Janeiro")
    st.markdown("Visão analítica sobre precificação, oferta e satisfação dos hóspedes.")

    # Filtros
    col_f1, col_f2 = st.columns(2)
    bairro_filter = col_f1.multiselect("Filtrar Bairro", options=sorted(df['NM_BAIRRO'].unique()))
    vibe_filter = col_f2.multiselect("Filtrar Vibe (IA)", options=sorted(df['CAT_VIBE_IA'].unique()))

    df_filtered = df.copy()
    if bairro_filter:
        df_filtered = df_filtered[df_filtered['NM_BAIRRO'].isin(bairro_filter)]
    if vibe_filter:
        df_filtered = df_filtered[df_filtered['CAT_VIBE_IA'].isin(vibe_filter)]

    # KPIs
    st.markdown("### Indicadores Chave")
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Ticket Médio (Diária)", f"R$ {df_filtered['VLR_DIARIA_BRL'].mean():.2f}")
    kpi2.metric("Total de Imóveis", f"{len(df_filtered)}")
    kpi3.metric("Imóvel Mais Caro", f"R$ {df_filtered['VLR_DIARIA_BRL'].max():.2f}")

    kpi4, kpi5, kpi6 = st.columns(3)

    pct_negativos = (
        df_reviews[df_reviews["CAT_SENTIMENTO"] == "Negativo"].shape[0]
        / len(df_reviews)
    ) * 100
    kpi4.metric("Reviews Negativos (%)", f"{pct_negativos:.1f}%")
    pct_urgencia = (
        df_reviews[df_reviews["FLG_URGENCIA"] == True].shape[0]
        / len(df_reviews)
    ) * 100
    kpi5.metric("Reviews com Urgência (%)", f"{pct_urgencia:.1f}%")
    bairro_top = (
        df_reviews[df_reviews["CAT_SENTIMENTO"] == "Positivo"]
            .merge(df, on="SK_LISTING", how="left")
            .groupby("NM_BAIRRO")
            .size()
            .sort_values(ascending=False)
            .index[0]
    )
    kpi6.metric("Bairro com Mais Reviews Positivos", bairro_top)
    st.markdown("---")
    c1, c2 = st.columns([2, 1])
    
    with c1:
        st.subheader("Distribuição Geográfica")
        fig_map = px.scatter_mapbox(
            df_filtered, 
            lat="NR_LATITUDE", lon="NR_LONGITUDE",
            color="CAT_VIBE_IA", size="VLR_DIARIA_BRL",
            hover_name="NM_BAIRRO",
            zoom=10, height=500,
            mapbox_style="carto-positron"
        )
        st.plotly_chart(fig_map, use_container_width=True)

    with c2:
        df_sent_summary = (
            df_reviews
                .groupby(["CAT_TOPICO", "CAT_SENTIMENTO"])
                .size()
                .reset_index(name="TOTAL")
        )
        st.subheader("Sentimento dos Reviews")
        fig_sent = px.bar(
            df_sent_summary,
            x="TOTAL",
            y="CAT_TOPICO",
            color="CAT_SENTIMENTO",
            orientation="h",
            title="Volume de Menções por Tópico",
            color_discrete_map={
                "Positivo": "#00CC96",
                "Negativo": "#EF553B",
                "Neutro": "#AB63FA"
            }
        )

        st.plotly_chart(fig_sent, use_container_width=True)

# ==============================================================================
# MÓDULO 2: GERADOR DE ANÚNCIOS (GEN AI)
# ==============================================================================
elif page == "Gerador de Anúncios":
    st.title("O Gerador de Anúncios Perfeitos")
    st.markdown("Utilize Inteligência Artificial para criar descrições persuasivas.")

    col_input, col_result = st.columns(2)

    with col_input:
        st.subheader("📝 Detalhes do Imóvel")
        input_bairro = st.selectbox("Onde fica o imóvel?", options=sorted(df['NM_BAIRRO'].unique()))
        input_tipo = st.selectbox("Tipo de Acomodação", options=["Casa Inteira", "Quarto Privativo", "Cobertura"])
        
        st.markdown("**Selecione os diferenciais:**")
        feat_wifi = st.checkbox("Wi-Fi Alta Velocidade")
        feat_view = st.checkbox("Vista para o Mar")
        feat_metro = st.checkbox("Próximo ao Metrô")
        feat_ar_cond = st.checkbox("Ar-condicionado")
        feat_silencio = st.checkbox("Ambiente Silencioso")
        feat_checkin = st.checkbox("Check-in Fácil")
        feat_host = st.checkbox("Host Responsivo")
        feat_seguranca = st.checkbox("Região Segura")
        feat_trabalho = st.checkbox("Ideal para Trabalho Remoto")
        feat_praia = st.checkbox("Próximo à Praia")

        features_list = []
        # Conforto
        if feat_wifi: features_list.append("Wi-Fi rápido")
        if feat_ar_cond: features_list.append("Ar-condicionado")
        if feat_silencio: features_list.append("Ambiente silencioso")
        # Localização
        if feat_view: features_list.append("Vista para o mar")
        if feat_metro: features_list.append("Próximo ao metrô")
        if feat_praia: features_list.append("Próximo à praia")
        # Experiência
        if feat_checkin: features_list.append("Check-in fácil")
        if feat_host: features_list.append("Host responsivo")
        if feat_seguranca: features_list.append("Região segura")
        # Público
        if feat_trabalho: features_list.append("Ideal para trabalho remoto")
        
        generate_btn = st.button("✨ Gerar Anúncio com IA")

    with col_result:
        if generate_btn:
            mask = (df['NM_BAIRRO'] == input_bairro)
            if len(df[mask]) > 0:
                stats = df[mask]['VLR_DIARIA_BRL'].describe()
                preco_sugerido = stats['50%'] 
                st.success(f"💰 **Preço Sugerido:** R$ {preco_sugerido:.2f} / noite")
                st.caption(f"Baseado em {stats['count']:.0f} imóveis similares.")
            else:
                st.warning("Dados insuficientes para precificação neste bairro.")

            # Chamada à OpenAI
            prompt = f"""
            Crie um título e uma descrição para um anúncio de Airbnb.

            Bairro: {input_bairro}
            Tipo de imóvel: {input_tipo}
            Destaques do imóvel: {', '.join(features_list)}

            Use emojis, tom convidativo e foco em conversão.
            """

            with st.spinner("A IA está criando..."):
                if client is None:
                    st.error("API da OpenAI não configurada.")
                else:
                    try:
                        response = client.responses.create(
                            model="gpt-4.1-mini",
                            input=prompt,
                            temperature=0.7
                        )
                        st.text_area(
                            "📢 Resultado:",
                            value=response.output_text,
                            height=300
                        )
                    except Exception as e:
                        st.error(f"Erro na API OpenAI: {e}")

# ==============================================================================
# MÓDULO 3: SMART INVESTOR
# ==============================================================================
elif page == "Smart Investor":
    st.title("Smart Investor")
    st.markdown("Simule oportunidades de investimento com base em liquidez e lacunas de mercado.")

    parcela_alvo = st.number_input(
        "Quanto você deseja pagar por mês na parcela?",
        min_value=1000,
        value=3000,
        step=500
    )
    df_reviews = df_reviews.merge(df[['SK_LISTING', 'NM_BAIRRO', 'CAT_VIBE_IA']],on='SK_LISTING',how='left')
    oferta = (df.groupby(['NM_BAIRRO', 'CAT_VIBE_IA']).size().reset_index(name='QTD_OFERTA'))
    demanda = (df.groupby(['NM_BAIRRO', 'CAT_VIBE_IA'])['QTD_TOTAL_AVALIACOES'].sum().reset_index(name='QTD_DEMANDA'))
    market = oferta.merge(demanda, on=['NM_BAIRRO', 'CAT_VIBE_IA'], how='left').fillna(0)

    market['GAP_DEMANDA'] = market['QTD_DEMANDA'] / market['QTD_OFERTA']
    market['OCUPACAO_ESTIMADA'] = (market['QTD_DEMANDA'] / market.groupby('NM_BAIRRO')['QTD_DEMANDA'].transform('max'))

    precos = (df.groupby(['NM_BAIRRO', 'CAT_VIBE_IA'])['VLR_DIARIA_BRL'].median().reset_index())
    market = market.merge(precos, on=['NM_BAIRRO', 'CAT_VIBE_IA'], how='left')

    market['RECEITA_MENSAL_EST'] = (market['VLR_DIARIA_BRL'] * 30 * market['OCUPACAO_ESTIMADA'])
    oportunidades = market[
        (market['RECEITA_MENSAL_EST'] >= parcela_alvo) &
        (market['QTD_OFERTA'] > 0)
    ].sort_values(
        by=['GAP_DEMANDA', 'RECEITA_MENSAL_EST'],
        ascending=False
    )

    if oportunidades.empty:
        st.warning("Nenhuma oportunidade clara encontrada para esse orçamento.")
    else:
        top = oportunidades.iloc[0]
        top2 = oportunidades.iloc[1]

        st.success(
            f"""
            💡 **Recomendação Inteligente**

            Com uma parcela de **R$ {parcela_alvo:,.0f}**, sugerimos investir no bairro  
            **{top['NM_BAIRRO']}**, focando no perfil **{top['CAT_VIBE_IA']}** ou 
            **{top2['NM_BAIRRO']}**, focando no perfil **{top2['CAT_VIBE_IA']}**.

            📈 **Alta pressão de demanda** e **baixa oferta relativa** indicam oportunidade.
            💰 Receita mensal estimada: **R$ {top['RECEITA_MENSAL_EST']:,.0f}**
            """
        )