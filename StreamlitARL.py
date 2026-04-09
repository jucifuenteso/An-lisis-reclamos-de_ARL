import pandas as pd
import streamlit as st
import plotly.express as px


#Crear pestañas
steps=st.tabs(["Start","Dashboard"])
with steps[0]:
    
    st.markdown("""
        ### Bienvenida al Panel de Control de Calidad y Servicio
        Este ecosistema de datos ha sido diseñado para transformar los registros de quejas en **decisiones estratégicas**. 
        A través de este dashboard, podrás monitorear en tiempo real la salud de nuestra operación, identificando:
        
        * **Patrones Temporales:** ¿En qué meses estamos recibiendo mayor volumen?
        * **Focos de Atención:** ¿Qué categorías concentran la mayor insatisfacción?
        * **Estrategia de Canales:** ¿Por dónde nos contactan más y cómo varía esa participación mes a mes?
        
        ---
        *Utiliza los filtros de la izquierda para segmentar la información por periodo o tipología.*
    """)
    
with steps[1]:
    

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
            
            # Mapeo de meses
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
            st.error(f"Error al cargar el archivo: {e}")
            return pd.DataFrame()

    df = load_data()

    # --- LÓGICA DE FILTRADO ---
    if not df.empty:
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

        # --- FILA 2: PARTICIPACIÓN PORCENTUAL (CORRECCIÓN DEFINITIVA) ---
        st.subheader("⚖️ Participación Porcentual de Canales por Mes")
        if not df_filtrado.empty:
            # Agrupamos y calculamos el porcentaje manualmente para que no haya errores de etiqueta
            df_part = df_filtrado.groupby(['Mes_Nombre', 'Canal de comunicación'], observed=True).size().reset_index(name='Conteo')
            
            # Calculamos el total por mes para sacar el % real
            df_part['Total_Mes'] = df_part.groupby('Mes_Nombre')['Conteo'].transform('sum')
            df_part['Porcentaje'] = (df_part['Conteo'] / df_part['Total_Mes']) * 100

            fig_percent = px.bar(
                df_part, 
                x='Mes_Nombre', 
                y='Porcentaje', # Usamos la columna de porcentaje ya calculada
                color='Canal de comunicación',
                text='Porcentaje',
                template="plotly_white",
                color_discrete_sequence=px.colors.qualitative.Pastel
            )

            fig_percent.update_traces(
                texttemplate='%{text:.1f}%', # Usamos el valor calculado
                textposition='inside'
            )

            fig_percent.update_layout(
                yaxis_title="Participación (%)",
                xaxis_title="",
                legend_title="Canal",
                hovermode="x unified",
                yaxis=dict(range=[0, 100])
            )
            
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
        st.error("Archivo no encontrado.")
