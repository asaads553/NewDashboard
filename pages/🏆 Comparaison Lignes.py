import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np

# --- 1. DONNÉES DE DÉMO ---
df_sim_filtered = pd.DataFrame({
    'Ligne': np.random.choice(['1', '4', '13', '14'], 100),
    'Taux_Regularite': np.random.uniform(85, 100, 100)
})

# --- 2. CRÉATION DE L'ONGLET ---
# On met les crochets [] pour récupérer l'onglet unique
[tab2] = st.tabs(["🏆 Comparaison Lignes"])

# --- 3. LE CODE DU GRAPHIQUE ---
with tab2:
    st.subheader("Classement des lignes sur la période sélectionnée")
    
    # Calcul de la moyenne par ligne
    df_grouped = df_sim_filtered.groupby('Ligne')['Taux_Regularite'].mean().reset_index()
    # Tri du meilleur au moins bon
    df_grouped = df_grouped.sort_values(by='Taux_Regularite', ascending=False)
    
    # Graphique en barres
    fig_bar = px.bar(
        df_grouped,
        x='Taux_Regularite',
        y='Ligne',
        orientation='h',
        # On utilise la colonne Taux pour colorer (plus c'est haut, plus c'est foncé)
        color='Taux_Regularite', 
        # Palette de Rouges
        color_continuous_scale='Reds', 
        range_color=[85, 100], # Ajuste l'échelle pour bien voir les différences de rouge
        text_auto='.1f',
        labels={'Taux_Regularite': 'Régularité Moyenne (%)'},
        template="plotly_dark"
    )
    
    st.plotly_chart(fig_bar, use_container_width=True)
