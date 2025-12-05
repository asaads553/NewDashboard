import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime, timedelta

# Configuration de la page
st.set_page_config(
    page_title="Dashboard Qualité RATP & Services",
    page_icon="🚇",
    layout="wide"
)

# --- 1. CHARGEMENT DES DONNÉES ---

@st.cache_data
def load_simulation_data():
    """
    Génère des données simulées pour la régularité (car le CSV ne contient pas d'historique).
    """
    # Génération des dates pour l'année 2023
    dates = pd.date_range(start="2023-01-01", end="2023-12-31", freq='D')
    lignes = [str(i) for i in range(1, 15)]  # Lignes 1 à 14
    
    data = []
    for ligne in lignes:
        # Simulation de la fiabilité : Lignes automatiques (1, 14) meilleures
        base_reg = 98.0 if ligne in ['1', '14'] else (92.0 if ligne == '13' else 95.0)
        
        for date in dates:
            variation = np.random.normal(0, 1.5)
            # Week-end souvent plus calme ou travaux
            is_weekend = date.weekday() >= 5
            factor = 0.5 if is_weekend else 0.0
            
            taux = min(100, max(0, base_reg + variation - factor))
            
            data.append({
                'Date': date,
                'Ligne': ligne, 
                'Taux_Regularite': round(taux, 2),
                'Trafic': int(np.random.normal(500000, 50000))
            })
            
    df = pd.DataFrame(data)
    
    # Ajout colonnes temporelles
    df['Mois'] = df['Date'].dt.month_name()
    df['Jour_Semaine'] = df['Date'].dt.day_name()
    
    # Ordre des jours pour affichage propre
    ordre_jours = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    df['Jour_Semaine'] = pd.Categorical(df['Jour_Semaine'], categories=ordre_jours, ordered=True)
    
    return df

@st.cache_data
def load_real_csv_data(): # <--- CORRECTION APPORTÉE ICI
    """
    Charge le fichier CSV 'fontaines-a-eau-dans-le-reseau-ratp.csv'
    """
    try:
        # Lecture du fichier avec le séparateur point-virgule
        # Le nom du fichier est une chaîne de caractères entre guillemets.
        df = pd.read_csv(r"C:\Users\rayan.rami\Desktop\data viz web\fontaines-a-eau-dans-le-reseau-ratp.csv", sep=';')
        
        # Conversion de la colonne Ligne en texte pour matcher avec la simulation
        df['Ligne'] = df['Ligne'].astype(str)
        
        # Renommage des colonnes pour que st.map fonctionne (latitude, longitude en minuscules)
        df = df.rename(columns={'Latitude': 'latitude', 'Longitude': 'longitude'})
        
        return df
    except FileNotFoundError:
        return None
    except Exception as e:
        st.error(f"Erreur lors de la lecture du CSV : {e}")
        return None

# Chargement des données au lancement
df_sim = load_simulation_data()
df_real = load_real_csv_data()

# --- 2. BARRE LATÉRALE (SIDEBAR) ---

st.title("🚇 RATP : Qualité & Services")
st.markdown("""
Analyse hybride combinant :
* 📊 **Données Simulées** pour l'historique de régularité.
* 🗺️ **Fichier CSV Réel** pour la localisation des fontaines à eau.
""")

st.sidebar.header("🔍 Filtres")

# Définition de la liste des lignes disponibles
if df_real is not None:
    liste_lignes = sorted(df_real['Ligne'].unique())
else:
    liste_lignes = sorted(df_sim['Ligne'].unique())

# Sélecteur de lignes
choix_lignes = st.sidebar.multiselect(
    "Choisir les lignes :",
    options=liste_lignes,
    default=['1', '4', '13']
)

# Sélecteur de dates (impacte seulement la simulation)
min_date = df_sim['Date'].min()
max_date = df_sim['Date'].max()
date_range = st.sidebar.date_input(
    "Période d'analyse :",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Arrêt si aucune ligne sélectionnée
if not choix_lignes:
    st.warning("Veuillez sélectionner au moins une ligne dans la barre latérale.")
    st.stop()

# --- FILTRAGE ---

# Filtrage simulation
mask_sim = (df_sim['Date'].dt.date >= date_range[0]) & \
           (df_sim['Date'].dt.date <= date_range[1]) & \
           (df_sim['Ligne'].isin(choix_lignes))
df_sim_filtered = df_sim[mask_sim]

# Filtrage CSV réel
if df_real is not None:
    df_real_filtered = df_real[df_real['Ligne'].isin(choix_lignes)]
else:
    df_real_filtered = None

# --- 3. TABLEAU DE BORD ---

# KPIs
col1, col2, col3 = st.columns(3)
avg_reg = df_sim_filtered['Taux_Regularite'].mean()
nb_fontaines = len(df_real_filtered) if df_real_filtered is not None else 0

col1.metric("Régularité Moyenne", f"{avg_reg:.1f}%")
col2.metric("Fontaines détectées", f"{nb_fontaines} 🚰")
col3.metric("Lignes affichées", len(choix_lignes))

st.divider()

# Onglets
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Évolution (Sim)", 
    "🏆 Classement (Sim)", 
    "📅 Heatmap (Sim)", 
    "🗺️ Carte Services (CSV)"
])

# Onglet 1 : Évolution
with tab1:
    st.subheader("Évolution de la régularité")
    fig_line = px.line(
        df_sim_filtered, x='Date', y='Taux_Regularite', color='Ligne',
        title="Régularité journalière par ligne",
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    fig_line.add_hline(y=95, line_dash="dot", line_color="green", annotation_text="Objectif 95%")
    st.plotly_chart(fig_line, use_container_width=True)

# Onglet 2 : Classement
with tab2:
    st.subheader("Classement par fiabilité")
    df_grouped = df_sim_filtered.groupby('Ligne')['Taux_Regularite'].mean().reset_index()
    df_grouped = df_grouped.sort_values(by='Taux_Regularite', ascending=False)
    
    fig_bar = px.bar(
        df_grouped, x='Taux_Regularite', y='Ligne', orientation='h',
        color='Taux_Regularite', color_continuous_scale='RdYlGn',
        range_color=[90, 100], text_auto='.1f'
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# Onglet 3 : Heatmap
with tab3:
    st.subheader("Performance par jour de la semaine")
    heatmap_data = df_sim_filtered.pivot_table(
        index='Ligne', columns='Jour_Semaine', values='Taux_Regularite', aggfunc='mean'
    )
    fig_heat = px.imshow(
        heatmap_data, color_continuous_scale='RdYlGn', aspect="auto", text_auto='.1f',
        title="Régularité moyenne par Ligne et Jour de la semaine"
    )
    st.plotly_chart(fig_heat, use_container_width=True)

# Onglet 4 : Carte (Données CSV réelles)
with tab4:
    st.subheader("📍 Localisation des Fontaines à eau")
    
    if df_real_filtered is not None and not df_real_filtered.empty:
        st.markdown(f"Affichage des fontaines pour les lignes : **{', '.join(choix_lignes)}**")
        
        # Vérification des coordonnées
        map_data = df_real_filtered.dropna(subset=['latitude', 'longitude'])
        
        if not map_data.empty:
            st.map(map_data, size=20, color='#0044ff')
            
            with st.expander("Voir le détail des adresses"):
                st.dataframe(df_real_filtered[['Ligne', 'Station ou Gare', 'Adresse', 'Commune']])
        else:
            st.warning("Données géographiques manquantes pour ces lignes (vérifiez les colonnes 'Latitude' et 'Longitude' dans votre fichier CSV).")
            
    elif df_real is None:
        st.error("⚠️ Fichier 'fontaines-a-eau-dans-le-reseau-ratp.csv' introuvable. Assurez-vous qu'il est dans le même dossier que D.py.")
    else:
        st.info("Aucune fontaine trouvée pour les lignes sélectionnées.")

# Footer
st.divider()
st.caption("Application Streamlit générée pour exercice POC.")