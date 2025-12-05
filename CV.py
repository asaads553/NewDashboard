import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime, timedelta
from PIL import Image
import os

# --- CONFIGURATION INITIALE & THÈME GLOBAL ---
st.set_page_config(
    page_title="Asaad Saadi | Portefeuille Data & CV",
    page_icon="⚡",
    layout="wide"
)

# --- CSS GLOBAL STYLÉ (Dark Mode Overlays) ---
st.markdown("""
<style>
    /* Import d'une police moderne */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Couleurs du thème */
    :root {
        --primary-color: #00FFFF; /* Cyan Électrique */
        --background-color: #050711; /* Fond sombre global renforcé */
        --secondary-background-color: rgba(31, 36, 48, 0.95); /* Cartes sombres légèrement translucides */
        --text-color: #FAFAFA;
        --accent-color: #FF8C00;
        --danger-color: #FF6347;
    }

    /* Fond global de l'app */
    .stApp {
        background: radial-gradient(circle at top left, #1f2933 0, #050711 45%, #000000 100%);
        color: var(--text-color);
    }

    /* Barre latérale */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #050711 0%, #111827 100%);
        border-right: 1px solid rgba(255, 255, 255, 0.06);
    }
    section[data-testid="stSidebar"] * {
        color: #e5e7eb !important;
    }

    /* Titres */
    h1, h2, h3, h4 {
        font-family: 'Inter', sans-serif;
        letter-spacing: 0.03em;
    }
    h1 { font-weight: 700; }
    h2, h3 { font-weight: 600; }

    /* Styles pour le CV */
    .cv-header-card {
        background: linear-gradient(135deg, rgba(31, 36, 48, 0.96), rgba(15, 23, 42, 0.96));
        padding: 30px;
        border-radius: 18px;
        border: 1px solid rgba(255, 255, 255, 0.06);
        box-shadow: 0 20px 45px rgba(0, 0, 0, 0.65);
        margin-bottom: 30px;
    }

    /* Cartes pour les projets */
    .project-card {
        background: var(--secondary-background-color);
        border-left: 4px solid var(--primary-color);
        border-radius: 12px;
        padding: 20px 22px;
        margin-bottom: 18px;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.45);
        transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
    }
    .project-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 16px 35px rgba(0, 0, 0, 0.6);
        border-left-color: var(--accent-color);
    }

    /* Styles pour les KPIs du Dashboard */
    .kpi-card {
        background: linear-gradient(145deg, rgba(31, 36, 48, 0.97), rgba(15, 23, 42, 0.97));
        border-radius: 14px;
        padding: 20px 18px;
        text-align: center;
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.55);
        border: 1px solid rgba(255, 255, 255, 0.05);
        transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
    }
    .kpi-card:hover {
        transform: translateY(-3px) scale(1.01);
        box-shadow: 0 18px 40px rgba(0, 0, 0, 0.7);
        border-color: rgba(0, 255, 255, 0.4);
    }
    .kpi-value {
        font-size: 2.4em;
        font-weight: 700;
        color: var(--accent-color);
    }
    .kpi-label {
        font-size: 0.9em;
        color: #9CA3AF;
        margin-top: 5px;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }

    /* Style des barres de progression */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, var(--primary-color), #00C896);
    }

    /* Bouton principal */
    .stButton button {
        border-radius: 999px;
        padding: 0.6rem 1.4rem;
        border: 1px solid rgba(255, 255, 255, 0.16);
        background: radial-gradient(circle at top left, #22d3ee 0, #0ea5e9 40%, #0369a1 100%);
        color: white;
        font-weight: 600;
        letter-spacing: 0.03em;
        box-shadow: 0 12px 30px rgba(34, 211, 238, 0.4);
        transition: transform 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;
    }
    .stButton button:hover {
        transform: translateY(-1px);
        box-shadow: 0 18px 40px rgba(56, 189, 248, 0.55);
        background: radial-gradient(circle at top left, #22c55e 0, #16a34a 40%, #15803d 100%);
    }

    /* Onglets */
    button[data-baseweb="tab"] {
        border-radius: 999px !important;
        background-color: transparent !important;
        color: #9CA3AF !important;
        border: 1px solid transparent !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        background: rgba(31, 41, 55, 0.9) !important;
        color : #F9FAFB !important;
        border-color: rgba(148, 163, 184, 0.6) !important;
    }

    /* Petits séparateurs plus discrets */
    hr {
        border-color: rgba(148, 163, 184, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# --- FONCTIONS DE CHARGEMENT ET DE PRÉPARATION DES DONNEES (Pour le Dashboard) ---
@st.cache_data
def load_simulation_data():
    dates = pd.date_range(start="2023-01-01", end="2023-12-31", freq='D')
    lignes = [str(i) for i in range(1, 15)]
    data = []
    
    for ligne in lignes:
        base_reg = 98.0 if ligne in ['1', '14'] else (92.0 if ligne == '13' else 95.0)
        for date in dates:
            variation = np.random.normal(0, 1.5)
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
    df['Mois'] = df['Date'].dt.month_name()
    df['Jour_Semaine'] = df['Date'].dt.day_name()
    
    ordre_jours = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    df['Jour_Semaine'] = pd.Categorical(df['Jour_Semaine'], categories=ordre_jours, ordered=True)
    
    return df

@st.cache_data
def load_real_csv_data():
    file_path = "fontaines-a-eau-dans-le-reseau-ratp.csv"
    try:
        df = pd.read_csv(file_path, sep=';')
        df['Ligne'] = df['Ligne'].astype(str)
        df = df.rename(columns={'Latitude': 'latitude', 'Longitude': 'longitude'})
        return df
    except FileNotFoundError:
        return None
    except Exception as e:
        st.error(f"Erreur lors de la lecture du CSV ({file_path}): {e}. Vérifiez le chemin et le format du fichier.")
        return None

df_sim = load_simulation_data()
df_real = load_real_csv_data()

# --- BLOCS DE RENDU DES PAGES ---
def render_cv_page():
    img = None
    try:
        image_path = "profile.jpg"
        img = Image.open(image_path)
    except FileNotFoundError:
        st.warning("L'image 'profile.jpg' est introuvable. Veuillez la placer dans le même répertoire que app.py.")

    # EN-TÊTE
    st.markdown('<div class="cv-header-card">', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 4], gap="medium")
    
    with col1:
        if img:
            # CORRECTION ICI: suppression de use_column_width=False
            st.image(img, width=200)
            
    with col2:
        st.title("Asaad Saadi")
        st.subheader("Étudiant en BUT Sciences des Données | Data Analyst Junior")
        st.markdown(
            '<p style="color:#E5E7EB;">📍 Le Bourget (France) | 📧 '
            '<a href="mailto:saadi_asaad@outlook.fr" style="color:#38BDF8;text-decoration:none;">'
            'saadi_asaad@outlook.fr</a> | 📞 07 52 07 70 35</p>',unsafe_allow_html=True
        )
        st.markdown(
            '<a href="https://www.linkedin.com/in/Asaad%20Saadi" style="color:#00FFFF;font-weight:600;">'
            '🔗 LinkedIn Professionnel</a>', unsafe_allow_html=True
        )
    st.markdown('</div>', unsafe_allow_html=True)

    # À PROPOS
    st.subheader("🔥 À propos de moi")
    st.write(
        """
        Étudiant en BUT Sciences des Données à l'IUT de Paris Rives de Seine (2023-2026), je recherche une alternance en chargé d'étude.
        Passionné par la modélisation et la visualisation, j'ai développé des compétences solides en statistiques,
        en programmation (Python/R) et en gestion de bases de données, cherchant toujours à transformer la donnée brute en information stratégique.
        """
    )

    # COMPÉTENCES
    st.subheader("💡 Compétences Techniques")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Langages & Outils Data :**")
        st.write("`Python` (Pandas, Numpy, Plotly, Streamlit) / `R` / `SAS` / `SQL`")
        st.write("`Excel` (VBA) / `Access`")
    with col2:
        st.markdown("**Analyse & Visualization :**")
        st.write("`Power BI` / Data Storytelling / Statistiques Descriptives")
        st.write("Modélisation de données / Analyse d'enquêtes")

    # PROJETS
    st.subheader("💻 Projets Data & Développement")
    st.markdown("""
    <div class="project-card">
        <b>Tableau de Bord RATP (Streamlit Data Viz)</b><br>
        - Objectif : Créer une preuve de concept pour suivre la ponctualité du métro.<br>
        - Réalisation : Application Streamlit intégrant des données simulées de régularité et des données réelles de services (fontaines). Visualisation de KPIs, courbes temporelles, et cartographie interactive (Plotly).<br>
        - Compétences : Python, Streamlit, Pandas, Plotly.
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚀 Accéder au Tableau de Bord RATP (Voir la Data Viz)", type="primary"):
        st.session_state.page = "Dashboard RATP"
        st.rerun()

    st.markdown("---")
    
    st.markdown("""
    <div class="project-card">
        <b>Étude sur les Jeux Olympiques (2023-2024)</b><br>
        - Collecte, nettoyage et création de bases de données volumineuses.<br>
        - Réalisation de statistiques et graphiques complexes
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="project-card">
        <b>Traitement de fichiers CSV (2023)</b><br>
        - Nettoyage et transformation des données avec Python pour préparer l'analyse.
    </div>
    """, unsafe_allow_html=True)

    # FORMATION
    st.subheader("🎓 Formation")
    st.write("---")
    st.markdown("**BUT Sciences des Données** - IUT Rives de Seine Paris (2023 - 2026)")
    st.markdown("**Baccalauréat Général** - Lycée Germain Tillon, Le Bourget (2022)")

    # LANGUES
    st.subheader("🌐 Langues")
    st.write("Français : Langue maternelle")
    st.progress(1.0)
    st.write("Arabe : Niveau C1")
    st.progress(0.85)
    st.write("Anglais : Niveau B1")
    st.progress(0.6)
    
    st.caption("Fait avec Streamlit pour un affichage dynamique et moderne.")


def render_dashboard_page(df_sim, df_real):
    st.title("🚇 Tableau de Bord RATP : Qualité de Service (POC)")
    st.markdown("Analyse combinée de la **Régularité (Simulée)** et des **Services (Réels)**. Thème sombre pour un impact maximal.")

    # FILTRES
    liste_lignes = sorted(df_sim['Ligne'].unique())
    st.sidebar.header("🔍 Filtres d'Analyse")
    
    choix_lignes = st.sidebar.multiselect(
        "Choisir les lignes :",
        options=liste_lignes,
        default=['1', '14', '13']
    )

    min_date = df_sim['Date'].min()
    max_date = df_sim['Date'].max()
    
    date_range = st.sidebar.date_input(
        "Période d'analyse (Ponctualité) :",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    if not choix_lignes:
        st.warning("Veuillez sélectionner au moins une ligne.")
        return

    mask_sim = (
        (df_sim['Date'].dt.date >= date_range[0]) & 
        (df_sim['Date'].dt.date <= date_range[1]) & 
        (df_sim['Ligne'].isin(choix_lignes))
    )
    df_sim_filtered = df_sim[mask_sim]

    if df_real is not None:
        df_real_filtered = df_real[df_real['Ligne'].isin(choix_lignes)]
    else:
        df_real_filtered = None

    # KPI
    col1, col2, col3 = st.columns(3)
    
    avg_reg = df_sim_filtered['Taux_Regularite'].mean()
    min_reg = df_sim_filtered['Taux_Regularite'].min()
    nb_fontaines = len(df_real_filtered) if df_real_filtered is not None else 0

    col1.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">RÉGULARITÉ MOYENNE (Sim.)</div>
        <div class="kpi-value" style="color:#22C55E;">{avg_reg:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

    col2.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">PIRE PERFORMANCE JOURNALIÈRE (Sim.)</div>
        <div class="kpi-value" style="color:#F97373;">{min_reg:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

    col3.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">SERVICES RÉELS (Fontaines)</div>
        <div class="kpi-value">{nb_fontaines} 🚰</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Onglets
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Évolution Temporelle",
        "🏆 Comparaison Lignes",
        "📅 Analyse Hebdomadaire",
        "🗺️ Carte des Services (CSV)"
    ])

    with tab1:
        st.subheader("Suivi de la performance jour après jour")
        fig_line = px.line(
            df_sim_filtered, 
            x='Date', 
            y='Taux_Regularite', 
            color='Ligne',
            title="Taux de régularité journalier par ligne (Thème Sombre)",
            labels={'Taux_Regularite': 'Régularité (%)'},
            template="plotly_dark",
            color_discrete_sequence=px.colors.sequential.Plasma
        )
        fig_line.add_hline(
            y=95, 
            line_dash="dash", 
            line_color="#22C55E", 
            annotation_text="Objectif 95%", 
            annotation_position="bottom right"
        )
        st.plotly_chart(fig_line, use_container_width=True)

    with tab2:
        st.subheader("Classement des lignes sur la période sélectionnée")
        df_grouped = df_sim_filtered.groupby('Ligne')['Taux_Regularite'].mean().reset_index()
        df_grouped = df_grouped.sort_values(by='Taux_Regularite', ascending=False)
        
        fig_bar = px.bar(
            df_grouped,
            x='Taux_Regularite',
            y='Ligne',
            orientation='h',
            color='Taux_Regularite',
            color_continuous_scale='Reds',
            range_color=[90, 100],
            text_auto='.1f',
            labels={'Taux_Regularite': 'Régularité Moyenne (%)'},
            template="plotly_dark"
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with tab3:
        st.subheader("Visualisation des plages horaires et jours critiques")
        heatmap_data = df_sim_filtered.pivot_table(
            index='Ligne', 
            columns='Jour_Semaine', 
            values='Taux_Regularite', 
            aggfunc='mean'
        )
        fig_heat = px.imshow(
            heatmap_data,
            color_continuous_scale='Viridis',
            aspect="auto",
            text_auto='.1f',
            title="Régularité moyenne par Ligne et Jour de la semaine (Plus le chiffre est élevé, mieux c'est)",
            template="plotly_dark"
        )
        st.plotly_chart(fig_heat, use_container_width=True)

    with tab4:
        st.subheader("🗺️ Localisation des Fontaines à eau (Services Réels)")
        if df_real is None:
            file_path_display = r"fontaines-a-eau-dans-le-reseau-ratp.csv"
            st.error(f"⚠️ Fichier CSV introuvable ou illisible. Vérifiez qu'il est bien à côté de app.py.")
        elif df_real_filtered.empty:
            st.info("Aucune fontaine n'est répertoriée pour les lignes sélectionnés.")
        else:
            st.markdown(f"Affichage des **{len(df_real_filtered)}** fontaines disponibles pour ces lignes.")
            map_data = df_real_filtered.dropna(subset=['latitude', 'longitude'])
            st.map(map_data, zoom=11, size=20, color='#00C080')
            
            with st.expander("Voir le détail des stations (Tableau)"):
                st.dataframe(df_real_filtered[['Ligne', 'Station ou Gare', 'Adresse', 'Commune', 'En zone contrôlée ou non']])

    st.divider()
    st.caption("Projet Streamlit (POC Data Viz).")


# --- FONCTION PRINCIPALE DE L'APPLICATION ---
def main():
    if 'page' not in st.session_state:
        st.session_state.page = "Mon CV"

    page_selection = st.sidebar.radio(
        "Navigation Principale", 
        ["Mon CV", "Dashboard RATP"],
        index=0 if st.session_state.page == "Mon CV" else 1
    )
    
    st.session_state.page = page_selection

    if st.session_state.page == "Mon CV":
        render_cv_page()
    elif st.session_state.page == "Dashboard RATP":
        render_dashboard_page(df_sim, df_real)

if __name__ == "__main__":
    main()