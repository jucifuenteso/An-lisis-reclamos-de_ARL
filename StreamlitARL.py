import pandas as pd
import streamlit as st
import plotly.express as px

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Dashboard Analítico de Quejas",
    page_icon="⚖️",
    layout="wide"
)

# --- CARGA Y PROCESAMIENTO DE DATOS ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("BD_Quejas_clasificadas.csv")
        mapa_meses = {
            1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
            5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
            9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
        }
        df['Mes_Num'] = pd.to_numeric(df['Mes'], errors='coerce')
        df['Mes_Nombre'] = df['Mes_Num'].map(mapa_meses)
        orden_meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
                    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        df['Mes_Nombre'] = pd.Categorical(df['Mes_Nombre'], categories=orden_meses, ordered=True)
        return df
    except Exception as e:
        return pd.DataFrame()

df = load_data()

# --- LÓGICA DE NAVEGACIÓN ---
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = "Start"

def ir_al_dashboard():
    st.session_state.active_tab = "Dashboard"

opciones = ["Start", "Dashboard"]
st.radio("Navegación", options=opciones, key="active_tab", horizontal=True, label_visibility="collapsed")

st.markdown("---")

# --- RENDERIZADO DE CONTENIDO ---

if st.session_state.active_tab == "Start":
    # --- PESTAÑA START (TODO CENTRADO) ---
    st.markdown("""
        <div style="text-align: center; padding: 20px;">
            <h1 style="font-size: 3em;">🚀 Centro de Control de Calidad</h1>
            <p style="font-size: 1.2em; color: #555; max-width: 850px; margin: 0 auto;">
                Este ecosistema de datos ha sido diseñado para transformar los registros de quejas en <b>decisiones estratégicas</b>. 
                Audita la salud de la operación e identifica patrones de insatisfacción en tiempo real.
            </p>
            <div style="display: inline-block; text-align: left; margin-top: 25px;">
                <p>✅ <b>Patrones Temporales:</b> Análisis de volumen mensual.</p>
                <p>✅ <b>Focos de Atención:</b> Categorías con mayor insatisfacción.</p>
                <p>✅ <b>Estrategia de Canales:</b> Participación de medios de contacto.</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Centrado del botón mediante columnas
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1.2, 1, 1.2])
    with c2:
        st.button("📊 ABRIR DASHBOARD COMPLETO", on_click=ir_al_dashboard, type="primary", use_container_width=True)

    if not df.empty:
        st.markdown("<br><hr>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center;'>Resumen Global Rápido</h3>", unsafe_allow_html=True)
        
        # --- CAMBIO AQUÍ: Se agregaron 4 columnas para incluir el tipo de queja ---
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Volumen Histórico", f"{len(df):,}")
        m2.metric("Canal Principal", df['Canal de comunicación'].mode()[0])
        m3.metric("Mes de Mayor Carga", df['Mes_Nombre'].mode()[0])
        # Nueva métrica: Categoría más relevante
        m4.metric("Tipo de Queja Crítico", df['categoria_final'].mode()[0])

else:
    # --- PESTAÑA DASHBOARD (CÓDIGO ORIGINAL RESTAURADO) ---
    if not df.empty:
        # --- LÓGICA DE FILTRADO ---
        st.sidebar.header("⚙️ Panel de Control")
        meses_disponibles = sorted(df['Mes_Nombre'].unique())
        seleccion_meses = st.sidebar.multiselect("Filtrar por Mes:", options=meses_disponibles, default=meses_disponibles)
        
        categorias_disponibles = sorted(df['categoria_final'].unique().tolist())
        seleccion_cats = st.sidebar.multiselect("Filtrar por Categoría:", options=categorias_disponibles, default=categorias_disponibles)
        
        df_filtrado = df[(df['Mes_Nombre'].isin(seleccion_meses)) & (df['categoria_final'].isin(seleccion_cats))]

        st.title("📊 Dashboard de Gestión de Quejas")
        st.markdown("---")

        # --- MÉTRICAS PERSONALIZADAS ---
        col_m1, col_m2 = st.columns(2)
        total_f = len(df_filtrado)

        with col_m1:
            st.markdown(f"""
                <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; border-left: 5px solid #1E3A8A; height: 160px;">
                    <p style="color: #555; margin-bottom: 5px; font-size: 16px; font-weight: bold;">Total Quejas Filtradas</p>
                    <h1 style="margin: 0; color: #1E3A8A; font-size: 45px;">{total_f:,}</h1>
                </div>
            """, unsafe_allow_html=True)

        with col_m2:
            if total_f > 0:
                conteo_cats = df_filtrado['categoria_final'].value_counts()
                cat_top = conteo_cats.idxmax()
                porcentaje_top = (conteo_cats.max() / total_f) * 100
                st.markdown(f"""
                    <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; border-left: 5px solid #3B82F6; height: 160px;">
                        <p style="color: #555; margin-bottom: 2px; font-size: 16px; font-weight: bold;">Categoría más frecuente</p>
                        <p style="margin: 0; color: #1E3A8A; font-size: 18px; line-height: 1.2;">{cat_top}</p>
                        <p style="margin-top: 10px; color: #3B82F6; font-size: 38px; font-weight: 900;">{porcentaje_top:.1f}%</p>
                    </div>
                """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # --- FILA 1: TENDENCIA Y CATEGORÍAS ---
        col_izq, col_der = st.columns(2)
        with col_izq:
            st.subheader("📈 Tendencia Mensual")
            df_mes = df_filtrado.groupby('Mes_Nombre', observed=True).size().reset_index(name='Conteo')
            fig_line = px.line(df_mes, x='Mes_Nombre', y='Conteo', markers=True, text='Conteo', template="plotly_white")
            fig_line.update_traces(line_color='#1E3A8A', textposition="top center")
            fig_line.update_layout(xaxis_title="", yaxis=dict(showticklabels=False, showgrid=False))
            st.plotly_chart(fig_line, use_container_width=True)

        with col_der:
            st.subheader("📊 Volumen por Categoría")
            df_cat = df_filtrado.groupby('categoria_final').size().reset_index(name='Conteo').sort_values('Conteo', ascending=True)
            fig_bar = px.bar(df_cat, y='categoria_final', x='Conteo', orientation='h', text='Conteo', template="plotly_white")
            fig_bar.update_traces(marker_color='#3B82F6', textposition="outside")
            fig_bar.update_layout(xaxis=dict(showticklabels=False, showgrid=False), yaxis_title="", margin=dict(l=150))
            st.plotly_chart(fig_bar, use_container_width=True)

        st.markdown("---")

        # --- FILA 2: PARTICIPACIÓN PORCENTUAL ---
        st.subheader("⚖️ Participación Porcentual de Canales por Mes")
        if not df_filtrado.empty:
            df_part = df_filtrado.groupby(['Mes_Nombre', 'Canal de comunicación'], observed=True).size().reset_index(name='Conteo')
            df_part['Total_Mes'] = df_part.groupby('Mes_Nombre')['Conteo'].transform('sum')
            df_part['Porcentaje'] = (df_part['Conteo'] / df_part['Total_Mes']) * 100
            fig_percent = px.bar(df_part, x='Mes_Nombre', y='Porcentaje', color='Canal de comunicación', text='Porcentaje',
                                template="plotly_white", color_discrete_sequence=px.colors.qualitative.Pastel)
            fig_percent.update_traces(texttemplate='%{text:.1f}%', textposition='inside')
            fig_percent.update_layout(yaxis_title="Participación (%)", xaxis_title="", legend_title="Canal", yaxis=dict(range=[0, 100]))
            st.plotly_chart(fig_percent, use_container_width=True)

        st.markdown("---")

        # --- FILA 3: DONA Y TABLA ---
        col_c1, col_c2 = st.columns([1, 1.5])
        with col_c1:
            st.subheader("📡 Canal de Comunicación (Total)")
            df_canal = df_filtrado.groupby('Canal de comunicación').size().reset_index(name='Conteo')
            fig_donut = px.pie(df_canal, values='Conteo', names='Canal de comunicación', hole=0.5, template="plotly_white")
            fig_donut.update_traces(textinfo='percent+label', showlegend=False)
            st.plotly_chart(fig_donut, use_container_width=True)

        with col_c2:
            st.subheader("📋 Resumen de Registros")
            st.dataframe(df_filtrado[['Mes_Nombre', 'categoria_final', 'Canal de comunicación', 'Nombre del cliente']].head(100), use_container_width=True, height=300)
    else:
        st.warning("No hay datos cargados.")
