import streamlit as st
import pandas as pd
import numpy as np

# --- 1. DONNÉES DE DÉMO (Faux points GPS à Paris) ---
df_real_filtered = pd.DataFrame({
    'Ligne': np.random.choice(['1', '4'], 50),
    'latitude': 48.8566 + np.random.normal(0, 0.02, 50),  # Autour de Paris
    'longitude': 2.3522 + np.random.normal(0, 0.02, 50),
    'Station': [f'Station {i}' for i in range(50)]
})

# --- 2. CRÉATION DE L'ONGLET ---
[tab4] = st.tabs(["🗺️ Carte des Services"])

# --- 3. LE CODE DE LA CARTE ---
with tab4:
    st.subheader("🗺️ Localisation des Services (Rouge)")
    
    if df_real_filtered.empty:
        st.info("Aucune donnée à afficher.")
    else:
        st.markdown(f"Affichage des **{len(df_real_filtered)}** points.")
        
        # Nettoyage des coordonnées vides
        map_data = df_real_filtered.dropna(subset=['latitude', 'longitude'])
        
        # Affichage de la carte avec des points ROUGES
        st.map(map_data, zoom=11, size=20, color='#FF0000') # <-- Code Hexa pour Rouge pur
        
        with st.expander("Voir le détail des stations"):
            st.dataframe(df_real_filtered)