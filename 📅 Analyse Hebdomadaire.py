import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np

# --- 1. DONNÉES DE DÉMO ---
# On crée des dates et on extrait le jour de la semaine
dates = pd.date_range(start='2023-01-01', periods=100)
df_sim_filtered = pd.DataFrame({
    'Date': dates,
    'Ligne': np.random.choice(['1', '13', '14'], 100),
    'Taux_Regularite': np.random.uniform(90, 100, 100)
})
df_sim_filtered['Jour_Semaine'] = df_sim_filtered['Date'].dt.day_name()

# --- 2. CRÉATION DE L'ONGLET ---
[tab3] = st.tabs(["📅 Analyse Hebdomadaire"])

# --- 3. LE CODE DU GRAPHIQUE ---
with tab3:
    st.subheader("Visualisation des plages horaires et jours critiques")
    
    # Création de la matrice (Pivot Table)
    heatmap_data = df_sim_filtered.pivot_table(
        index='Ligne', 
        columns='Jour_Semaine', 
        values='Taux_Regularite', 
        aggfunc='mean'
    )
    
    # Graphique Heatmap
    fig_heat = px.imshow(
        heatmap_data,
        # 'Reds' pour des nuances de rouge
        color_continuous_scale='Reds', 
        aspect="auto",
        text_auto='.1f',
        title="Régularité moyenne par Ligne et Jour",
        template="plotly_dark"
    )
    
    st.plotly_chart(fig_heat, use_container_width=True)