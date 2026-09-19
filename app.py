import io
import math
import folium
from folium.plugins import MarkerCluster
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# ==========================================
# 1. CONFIGURATION ET CHARGEMENT DES DONNÉES
# ==========================================
st.set_page_config(
    page_title="SIG Pastoral Mauritanie", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

def calculer_distance_km(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def trouver_colonne(dataframe, nom_cherche):
    for col in dataframe.columns:
        if str(col).strip().lower() == nom_cherche.lower():
            return col
    return None

@st.cache_data
def charger_donnees():
    return pd.read_excel('infrastructures_unifiees.xlsx')

df_source = charger_donnees()
df = df_source.copy()

# ==========================================
# 2. NETTOYAGE PUISSANT DES COORDONNÉES GPS
# ==========================================
col_lat = trouver_colonne(df, 'latitude')
col_lon = trouver_colonne(df, 'longitude')

if col_lat and col_lon:
    # On remplace les virgules par des points, on enlève les espaces
    df[col_lat] = pd.to_numeric(df[col_lat].astype(str).str.replace(',', '.').str.replace(' ', '').str.replace('°', ''), errors='coerce')
    df[col_lon] = pd.to_numeric(df[col_lon].astype(str).str.replace(',', '.').str.replace(' ', '').str.replace('°', ''), errors='coerce')

# ==========================================
# 3. FILTRES DANS LA BARRE LATÉRALE
# ==========================================
st.sidebar.header("🔍 Filtres Avancés")

col_wilaya = trouver_colonne(df, 'wilaya')
col_moughataa = trouver_colonne(df, 'Moughataa')
col_commune = trouver_colonne(df, 'Commune')
col_etat = trouver_colonne(df, 'etat')
col_nom = trouver_colonne(df, 'nom')
col_type = trouver_colonne(df, 'type_ouvrage')

if col_wilaya:
    wilayas = ['Toutes'] + sorted(df[col_wilaya].dropna().unique().tolist())
    choix_wilaya = st.sidebar.selectbox('Sélectionner la Wilaya', wilayas)
    if choix_wilaya != 'Toutes':
        df = df[df[col_wilaya] == choix_wilaya]

if col_moughataa:
    moughataas = ['Toutes'] + sorted(df[col_moughataa].dropna().unique().tolist())
    choix_moughataa = st.sidebar.selectbox('Sélectionner la Moughataa', moughataas)
    if choix_moughataa != 'Toutes':
        df = df[df[col_moughataa] == choix_moughataa]

if col_commune:
    communes = ['Toutes'] + sorted(df[col_commune].dropna().unique().tolist())
    choix_commune = st.sidebar.selectbox('Sélectionner la Commune', communes)
    if choix_commune != 'Toutes':
        df = df[df[col_commune] == choix_commune]

if col_type:
    types_infra = sorted(df[col_type].dropna().astype(str).unique().tolist())
    choix_types = st.sidebar.multiselect("Type d'infrastructure", types_infra, default=types_infra)
    if choix_types:
        df = df[df[col_type].isin(choix_types)]

if col_etat:
    etats = sorted(df[col_etat].dropna().astype(str).unique().tolist())
    choix_etats = st.sidebar.multiselect("État de l'infrastructure", etats, default=etats)
    if choix_etats:
        df = df[df[col_etat].isin(choix_etats)]

# --- BOUCLIER GÉOGRAPHIQUE ---
# On ne garde que les coordonnées qui existent physiquement sur Terre !
if col_lat and col_lon:
    masque_valide = (
        df[col_lat].notna() & 
        df[col_lon].notna() & 
        (df[col_lat] >= -90) & 
        (df[col_lat] <= 90) & 
        (df[col_lon] >= -180) & 
        (df[col_lon] <= 180)
    )
    df_valide = df[masque_valide].copy()
    erreurs_gps = len(df) - len(df_valide)
else:
    df_valide = pd.DataFrame()
    erreurs_gps = 0

# ==========================================
# 4. GÉOLOCALISATION ET ITINÉRAIRE
# ==========================================
st.sidebar.markdown("---")
st.sidebar.subheader("📍 Position / Base de départ")

bases_terrain = {
    "Adel Bagrou": (15.5339, -7.0304),
    "Bassikounou": (15.7500, -5.9167),
    "Néma": (16.6167, -7.2500),
    "Kiffa": (16.6167, -11.4000),
    "Autre (Saisie manuelle)": (0.0, 0.0),
}

choix_base = st.sidebar.selectbox("Choisir votre zone / base", list(bases_terrain.keys()))

if choix_base == "Autre (Saisie manuelle)":
    lat_user = st.sidebar.number_input("Votre Latitude", value=15.5339, format="%.4f")
    lon_user = st.sidebar.number_input("Votre Longitude", value=-7.0304, format="%.4f")
else:
    lat_user, lon_user = bases_terrain[choix_base]

st.sidebar.markdown("---")
st.sidebar.subheader("🚗 Itinéraire vers une Infrastructure")
tracer_ligne = False

if not df.empty and col_nom:
    val_commune = df_valide[col_commune].astype(str) if col_commune else "Inconnue"
    val_moughataa = df_valide[col_moughataa].astype(str) if col_moughataa else "Inconnue"
    
    df_valide["label_affichage"] = df_valide[col_nom].astype(str) + " (" + val_commune + " - " + val_moughataa + ")"
    labels_ouvrages = sorted(df_valide["label_affichage"].dropna().unique().tolist())
    
    choix_label = st.sidebar.selectbox("Choisir un ouvrage cible", ["Aucun"] + labels_ouvrages)

    if choix_label != "Aucun":
        ouvrage_cible = df_valide[df_valide["label_affichage"] == choix_label].iloc[0]
        lat_cible = ouvrage_cible.get(col_lat)
        lon_cible = ouvrage_cible.get(col_lon)
        nom_infra = ouvrage_cible.get(col_nom, "")
        
        if pd.notnull(lat_cible) and pd.notnull(lon_cible):
            distance_ouvrage = calculer_distance_km(lat_user, lon_user, lat_cible, lon_cible)
            st.sidebar.success(f"📍 **{nom_infra}**")
            st.sidebar.metric(label="Distance estimée", value=f"{distance_ouvrage:.2f} km")
            tracer_ligne = st.sidebar.checkbox("Afficher l'itinéraire sur la carte", value=True)
        else:
            st.sidebar.warning("Coordonnées GPS absentes.")

# ==========================================
# 5. INDICATEURS CLÉS DE SYNTHÈSE (KPIS)
# ==========================================
st.subheader("📊 Indicateurs de Synthèse & Couverture Pastorale")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(label="Ouvrages filtrés", value=f"{len(df)}")
with col2:
    st.metric(label="✅ GPS Valides", value=f"{len(df_valide)}") 
with col3:
    if erreurs_gps > 0:
        st.metric(label="❌ Erreurs GPS", value=f"{erreurs_gps}") # Alerte les erreurs Excel !
    else:
        if col_wilaya: st.metric(label="Wilayas", value=df[col_wilaya].nunique())
with col4:
    if col_commune: st.metric(label="Communes", value=df_valide[col_commune].nunique())
with col5:
    if col_etat:
        fonctionnels = len(df_valide[df_valide[col_etat].astype(str).str.lower().str.contains('fonctionnel|bon', na=False)])
        st.metric(label="Opérationnels", value=fonctionnels)

st.markdown("---")

# ==========================================
# 6. CARTE INTERACTIVE FOLIUM
# ==========================================
st.markdown("### 🗺️ Carte d'intervention")

with st.spinner("Génération de la carte en cours..."):
    carte_zone = folium.Map(location=[lat_user, lon_user], zoom_start=8)

    folium.TileLayer(
        tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
        attr='Google',
        name='Satellite Hybride',
        overlay=False,
        control=True
    ).add_to(carte_zone)
    folium.LayerControl().add_to(carte_zone)

    marker_cluster = MarkerCluster().add_to(carte_zone)

    if not df_valide.empty:
        for index, row in df_valide.iterrows():
            # Ultra sécurisation des textes pour ne jamais faire planter la carte
            nom_o = str(row.get(col_nom, 'Inconnu')).replace("'", " ").replace('"', ' ').replace('<', '').replace('>', '')
            type_o = str(row.get(col_type, 'N/A')).replace("'", " ").replace('"', ' ')
            etat_o = str(row.get(col_etat, 'N/A')).replace("'", " ").replace('"', ' ')
            
            couleur = "green" if "fonctionnel" in etat_o.lower() or "bon" in etat_o.lower() else "red"
            
            folium.Marker(
                location=[row[col_lat], row[col_lon]],
                popup=f"<b>{nom_o}</b><br>Type: {type_o}<br>État: {etat_o}",
                icon=folium.Icon(color=couleur, icon="tint")
            ).add_to(marker_cluster)

    # Marqueur de votre position
    folium.Marker(
        location=[lat_user, lon_user],
        popup=f"📍 Ma Base : {choix_base}",
        icon=folium.Icon(color="darkred", icon="user", prefix="fa"),
    ).add_to(carte_zone)

    # Tracé de l'itinéraire
    if tracer_ligne and "lat_cible" in locals() and "lon_cible" in locals():
        if pd.notnull(lat_cible) and pd.notnull(lon_cible):
            folium.PolyLine(
                locations=[[lat_user, lon_user], [lat_cible, lon_cible]],
                color="blue",
                weight=5,
                opacity=0.8,
                tooltip="Itinéraire cible"
            ).add_to(carte_zone)

    # Affichage de la carte
    html_data = carte_zone.get_root().render()
    components.html(html_data, height=600)

    st.download_button(
        label="🌍 Télécharger la carte en Satellite_Hybride.html",
        data=html_data,
        file_name="Satellite_Hybride.html",
        mime="text/html"
    )

# ==========================================
# 7. BASE DE DONNÉES & TÉLÉCHARGEMENTS
# ==========================================
st.markdown("### 📋 Base d'inventaire tabulaire")

if col_lat and col_lon and col_nom:
    df["Lien_GPS_Mobile"] = (
        "geo:" + df[col_lat].astype(str) + "," + df[col_lon].astype(str) 
        + "?q=" + df[col_lat].astype(str) + "," + df[col_lon].astype(str) 
        + "(" + df[col_nom].astype(str).str.replace(' ', '%20') + ")"
    )

st.dataframe(
    df, 
    use_container_width=True,
    column_config={
        "Lien_GPS_Mobile": st.column_config.LinkColumn("🗺️ Ouvrir dans Organic Maps / Maps.me")
    }
)

col_dl1, col_dl2 = st.columns(2)

with col_dl1:
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Télécharger la sélection en CSV", data=csv, file_name="selection_pastorale.csv", mime="text/csv")

with col_dl2:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Ouvrages')
    st.download_button("📥 Télécharger la sélection en Excel", data=buffer, file_name="selection_pastorale.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
