import io
import math
import folium
from folium.plugins import MarkerCluster
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

# ==========================================
# 1. CONFIGURATION ET CHARGEMENT DES DONNÉES
# ==========================================
st.set_page_config(
    page_title="SIG Pastoral Mauritanie", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# Fonction de calcul de distance (Haversine)
def calculer_distance_km(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# Fonction pour trouver les colonnes sans erreur de majuscule/minuscule
def trouver_colonne(dataframe, nom_cherche):
    for col in dataframe.columns:
        if col.strip().lower() == nom_cherche.lower():
            return col
    return None

@st.cache_data
def charger_donnees():
    # Remplacez par le nom exact de votre fichier si besoin
    return pd.read_excel('infrastructures_unifiees.xlsx')

df_source = charger_donnees()
df = df_source.copy()

# ==========================================
# 2. FILTRES DANS LA BARRE LATÉRALE
# ==========================================
st.sidebar.header("🔍 Filtres Avancés")

# Sécurisation des noms de colonnes
col_wilaya = trouver_colonne(df, 'wilaya')
col_moughataa = trouver_colonne(df, 'moughataa')
col_commune = trouver_colonne(df, 'commune')
col_etat = trouver_colonne(df, 'etat')
col_nom = trouver_colonne(df, 'nom')
col_lat = trouver_colonne(df, 'latitude')
col_lon = trouver_colonne(df, 'longitude')
col_type = trouver_colonne(df, 'type_ouvrage')

if col_wilaya:
    wilayas = ['Toutes'] + sorted(df[col_wilaya].dropna().unique().tolist())
    choix_wilaya = st.sidebar.selectbox('Sélectionner la Wilaya', wilayas)
    if choix_wilaya != 'Toutes':
        df = df[df[col_wilaya] == choix_wilaya]

if col_moughataa:
    moughataas = ['Toutes'] + sorted(df[col_moughataa].dropna().unique().tolist())
    choix_moughataa = st.sidebar.selectbox('Sélectionner la moughataa', moughataas)
    if choix_moughataa != 'Toutes':
        df = df[df[col_moughataa] == choix_moughataa]

if col_commune:
    communes = ['Toutes'] + sorted(df[col_commune].dropna().unique().tolist())
    choix_commune = st.sidebar.selectbox('Sélectionner la commune', communes)
    if choix_commune != 'Toutes':
        df = df[df[col_commune] == choix_commune]

if col_etat:
    etats = df[col_etat].dropna().unique().tolist()
    choix_etats = st.sidebar.multiselect("État de l'infrastructure", etats, default=etats)
    if choix_etats:
        df = df[df[col_etat].isin(choix_etats)]

# ==========================================
# 3. GÉOLOCALISATION ET ITINÉRAIRE (BARRE LATÉRALE)
# ==========================================
st.sidebar.markdown("---")
st.sidebar.subheader("📍 Position / Base de départ")

bases_terrain = {
    "Adel Bagrou": (15.5358, -7.0256),
    "Bassikounou": (15.7500, -5.9167),
    "Néma": (16.6167, -7.2500),
    "Kiffa": (16.6167, -11.4000),
    "Autre (Saisie manuelle)": (0.0, 0.0),
}

choix_base = st.sidebar.selectbox("Choisir votre zone / base", list(bases_terrain.keys()))

if choix_base == "Autre (Saisie manuelle)":
    lat_user = st.sidebar.number_input("Votre Latitude", value=15.5358, format="%.4f")
    lon_user = st.sidebar.number_input("Votre Longitude", value=-7.0256, format="%.4f")
else:
    lat_user, lon_user = bases_terrain[choix_base]

# Choix de la destination
st.sidebar.markdown("---")
st.sidebar.subheader("🚗 Itinéraire vers une Infrastructure")
tracer_ligne = False

if not df.empty and col_nom:
    val_commune = df[col_commune].astype(str) if col_commune else "Inconnue"
    val_moughataa = df[col_moughataa].astype(str) if col_moughataa else "Inconnue"
    
    df["label_affichage"] = df[col_nom].astype(str) + " (" + val_commune + " - " + val_moughataa + ")"
    labels_ouvrages = sorted(df["label_affichage"].dropna().unique().tolist())
    
    # On ajoute une option vide pour ne pas tracer par défaut
    choix_label = st.sidebar.selectbox("Choisir un ouvrage cible", ["Aucun"] + labels_ouvrages)

    if choix_label != "Aucun":
        ouvrage_cible = df[df["label_affichage"] == choix_label].iloc[0]
        lat_cible = ouvrage_cible.get(col_lat)
        lon_cible = ouvrage_cible.get(col_lon)
        nom_infra = ouvrage_cible.get(col_nom, "")
        
        if pd.notnull(lat_cible) and pd.notnull(lon_cible):
            distance_ouvrage = calculer_distance_km(lat_user, lon_user, lat_cible, lon_cible)
            
            st.sidebar.success(f"📍 **{nom_infra}**")
            st.sidebar.metric(label="Distance estimée (vol d'oiseau)", value=f"{distance_ouvrage:.2f} km")
            tracer_ligne = st.sidebar.checkbox("Afficher l'itinéraire sur la carte", value=True)
        else:
            st.sidebar.warning("Coordonnées GPS absentes pour cet ouvrage.")

# ==========================================
# 4. INDICATEURS CLÉS DE SYNTHÈSE (KPIS)
# ==========================================
st.subheader("📊 Indicateurs de Synthèse & Couverture Pastorale")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="Ouvrages filtrés", value=f"{len(df)}")
with col2:
    if col_wilaya: st.metric(label="Wilayas", value=df[col_wilaya].nunique())
with col3:
    if col_commune: st.metric(label="Communes", value=df[col_commune].nunique())
with col4:
    if col_etat:
        fonctionnels = len(df[df[col_etat].astype(str).str.lower().str.contains('fonctionnel|bon', na=False)])
        st.metric(label="Opérationnels / Bons", value=fonctionnels)

st.markdown("---")

# ==========================================
# 5. CARTE INTERACTIVE FOLIUM
# ==========================================
st.markdown("### 🗺️ Carte d'intervention")

# Initialiser la carte centrée sur la zone de départ
carte_zone = folium.Map(location=[lat_user, lon_user], zoom_start=8)
marker_cluster = MarkerCluster().add_to(carte_zone)

# Ajouter les points d'eau filtrés sur la carte
if col_lat and col_lon and col_nom:
    for index, row in df.dropna(subset=[col_lat, col_lon]).iterrows():
        etat_ouvrage = str(row.get(col_etat, 'Inconnu')).lower()
        couleur = "green" if "fonctionnel" in etat_ouvrage or "bon" in etat_ouvrage else "red"
        
        folium.Marker(
            location=[row[col_lat], row[col_lon]],
            popup=f"<b>{row[col_nom]}</b><br>État: {row.get(col_etat, 'N/A')}",
            icon=folium.Icon(color=couleur, icon="tint")
        ).add_to(marker_cluster)

# Ajouter VOTRE position (Marqueur Rouge)
folium.Marker(
    location=[lat_user, lon_user],
    popup=f"📍 Ma Base : {choix_base}",
    icon=folium.Icon(color="darkred", icon="user", prefix="fa"),
).add_to(carte_zone)

# Tracer l'itinéraire si demandé
if tracer_ligne and "lat_cible" in locals() and "lon_cible" in locals():
    folium.PolyLine(
        locations=[[lat_user, lon_user], [lat_cible, lon_cible]],
        color="blue",
        weight=5,
        opacity=0.8,
        tooltip="Itinéraire cible"
    ).add_to(carte_zone)

# Affichage final de la carte dans Streamlit
st_folium(carte_zone, width="100%", height=550)

# ==========================================
# 6. BASE DE DONNÉES ET TÉLÉCHARGEMENTS
# ==========================================
st.markdown("### 📋 Base d'inventaire tabulaire")
st.dataframe(df, use_container_width=True)

col_dl1, col_dl2 = st.columns(2)

with col_dl1:
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Télécharger la sélection en CSV", data=csv, file_name="selection_pastorale.csv", mime="text/csv")

with col_dl2:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Ouvrages')
    st.download_button("📥 Télécharger la sélection en Excel", data=buffer, file_name="selection_pastorale.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
