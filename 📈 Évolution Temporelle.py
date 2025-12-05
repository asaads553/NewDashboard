import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np

# --- PRÉPARATION ---
df_sim_filtered = pd.DataFrame({
    'Date': pd.date_range(start='2023-01-01', periods=30),
    'Taux_Regularite': np.random.uniform(90, 100, 30),
    'Ligne': ['1'] * 30
})
[tab1] = st.tabs(["📈 Évolution Temporelle"])

# --- TON CODE MODIFIÉ ---
with tab1:
    st.subheader("Suivi de la performance jour après jour")
    
    # Création du graphique linéaire
    fig_line = px.line(
        df_sim_filtered, 
        x='Date', 
        y='Taux_Regularite', 
        color='Ligne',
        title="Taux de régularité journalier par ligne (Thème Sombre)",
        labels={'Taux_Regularite': 'Régularité (%)'},
        template="plotly_dark",
        # 👇 C'EST ICI QUE ÇA CHANGE 👇
        # Avant : color_discrete_sequence=px.colors.sequential.Plasma
        # Après : On force la couleur rouge
        color_discrete_sequence=['red'] 
    )
    
    # Ajout de la ligne d'objectif (Je l'ai laissée en vert, dis-moi si tu veux la changer aussi)
    fig_line.add_hline(
        y=95, 
        line_dash="dash", 
        line_color="#22C55E", 
        annotation_text="Objectif 95%", 
        annotation_position="bottom right"
    )
    
    # Affichage
    st.plotly_chart(fig_line, use_container_width=True)