import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

# 1. Chargement des données unifiées (votre base de 4 078 points)
@st.cache_data
def charger_donnees():
  df = pd.read_excel('infrastructures_unifiees.xlsx')
  return df


df = charger_donnees()
import math
import streamlit as st

# ==========================================
# MODULE GPS & CALCUL DE DISTANCE FRONTIÈRE
# ==========================================
st.sidebar.markdown('---')
st.sidebar.subheader('📍 Géolocalisation & Terrain')

# Coordonnées approximatives de la frontière malienne proche (ex: région d'Adel Bagrou / Bassikounou)
# Vous pouvez ajuster ces coordonnées selon votre point de repère frontalier exact
LAT_FRONTIERE = 15.35  # Latitude indicative de la frontière
LON_FRONTIERE = -5.50  # Longitude indicative de la frontière
NOM_FRONTIERE = 'Frontière Mali'


# Fonction mathématique pour calculer la distance (en km) entre deux points GPS (Formule de Haversine)
def calculer_distance_km(lat1, lon1, lat2, lon2):
  R = 6371  # Rayon de la Terre en km
  dlat = math.radians(lat2 - lat1)
  dlon = math.radians(lon2 - lon1)
  a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(
      math.radians(lat2)
  ) * math.sin(dlon / 2) ** 2
  c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
  return R * c


# Simulation de saisie ou récupération GPS mobile
# Sur Streamlit, on peut proposer un petit sélecteur ou un bouton de géolocalisation navigateur
mode_gps = st.sidebar.radio(
    'Mode de position', ['Saisie manuelle / Par défaut', 'Activer mon GPS']
)

if mode_gps == 'Activer mon GPS':
  st.sidebar.info(
      "Autorisez l'accès à la position sur votre navigateur/téléphone."
  )
  # Utilisation d'un composant HTML/JS pour récupérer la position réelle du téléphone
  from streamlit_folium import st_folium

  # Note : Le composant de géolocalisation HTML5 s'intègre via un script dédié ou un composant Streamlit spécial.
  # Pour l'instant, simulons la position actuelle ou entrons les coordonnées GPS de terrain :
  lat_user = st.sidebar.number_input(
      'Votre Latitude actuelle', value=16.3333, format='%.4f'
  )
  lon_user = st.sidebar.number_input(
      'Votre Longitude actuelle', value=-5.7000, format='%.4f'
  )
else:
  # Position par défaut (ex: Adel Bagrou)
  lat_user = 16.3333
  lon_user = -5.7000
  st.sidebar.text('Position par défaut : Adel Bagrou')

# Calcul de la distance vers la frontière
distance_frontiere = calculer_distance_km(
    lat_user, lon_user, LAT_FRONTIERE, LON_FRONTIERE
)

# Affichage de l'indicateur de distance dans l'application
st.sidebar.metric(
    label=f'📏 Distance vers {NOM_FRONTIERE}',
    value=f'{distance_frontiere:.1f} km',
)
# ==========================================
# 2. COLREZ LE CODE DES FILTRES ET DES KPIs ICI :
# ==========================================
st.sidebar.header('🔍 Filtres Avancés - Piste 1')

# Filtres géographiques
if 'wilaya' in df.columns:
  wilayas = ['Toutes'] + sorted(df['wilaya'].dropna().unique().tolist())
  choix_wilaya = st.sidebar.selectbox('Sélectionner la Wilaya', wilayas)
  if choix_wilaya != 'Toutes':
    df = df[df['wilaya'] == choix_wilaya]

if 'Moughataa' in df.columns:
  moughataas = ['Toutes'] + sorted(df['Moughataa'].dropna().unique().tolist())
  choix_moughataa = st.sidebar.selectbox('Sélectionner la Moughataa', moughataas)
  if choix_moughataa != 'Toutes':
    df = df[df['Moughataa'] == choix_moughataa]

if 'Commune' in df.columns:
  communes = ['Toutes'] + sorted(df['Commune'].dropna().unique().tolist())
  choix_commune = st.sidebar.selectbox('Sélectionner la Commune', communes)
  if choix_commune != 'Toutes':
    df = df[df['Commune'] == choix_commune]
# ==========================================
# MODULE GPS & CALCUL DE DISTANCE FRONTIÈRE
# ==========================================
st.sidebar.markdown("---")
st.sidebar.subheader("📍 Géolocalisation & Terrain")

LAT_FRONTIERE = 16.3265
LON_FRONTIERE = -5.0683
NOM_FRONTIERE = "Frontière Mali (Adel Bagrou)"


def calculer_distance_km(lat1, lon1, lat2, lon2):
  R = 6371
  dlat = math.radians(lat2 - lat1)
  dlon = math.radians(lon2 - lon1)
  a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(
      math.radians(lat2)
  ) * math.sin(dlon / 2) ** 2
  c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
  return R * c


mode_gps = st.sidebar.radio(
    "Mode de position", ["Position par défaut (Adel Bagrou)", "Saisir mes coordonnées GPS"]
)

if mode_gps == "Saisir mes coordonnées GPS":
  lat_user = st.sidebar.number_input("Votre Latitude actuelle", value=16.3265, format="%.4f")
  lon_user = st.sidebar.number_input("Votre Longitude actuelle", value=-5.0683, format="%.4f")
else:
  lat_user = 16.3265
  lon_user = -5.0683
  st.sidebar.text("Zone : Adel Bagrou")

distance_frontiere = calculer_distance_km(lat_user, lon_user, LAT_FRONTIERE, LON_FRONTIERE)

st.sidebar.metric(
    label=f"📏 Distance vers {NOM_FRONTIERE}",
    value=f"{distance_frontiere:.1f} km",
)
# ==========================================
# MODULE ITINÉRAIRE & DÉTAILS DE L'OUVRAGE
# ==========================================
st.sidebar.markdown("---")
st.sidebar.subheader("🚗 Itinéraire vers une Infrastructure")

if not df.empty and "nom" in df.columns:
  # Création d'une étiquette unique combinant le nom, la commune et la moughataa
  df["label_affichage"] = (
      df["nom"].astype(str)
      + " ("
      + df["Commune"].astype(str)
      + " - "
      + df["Moughataa"].astype(str)
      + ")"
  )

  labels_ouvrages = sorted(df["label_affichage"].dropna().unique().tolist())
  choix_label = st.sidebar.selectbox("Choisir un ouvrage cible", labels_ouvrages)

  if choix_label:
    # Récupérer exactement la ligne correspondante
    ouvrage_cible = df[df["label_affichage"] == choix_label].iloc[0]

    # Extraire les informations propres à cette ligne
    nom_infra = ouvrage_cible.get("nom", "")
    lat_cible = ouvrage_cible.get("latitude")
    lon_cible = ouvrage_cible.get("longitude")
    moughataa_cible = ouvrage_cible.get("Moughataa", "Non renseignée")
    commune_cible = ouvrage_cible.get("Commune", "Non renseignée")
    type_ouvrage = ouvrage_cible.get("type_ouvrage", "")

    if pd.notnull(lat_cible) and pd.notnull(lon_cible):
      # Calcul de la distance depuis votre position
      distance_ouvrage = calculer_distance_km(lat_user, lon_user, lat_cible, lon_cible)

      # Affichage clair
      st.sidebar.success(f"📍 **{nom_infra}** ({type_ouvrage})")
      st.sidebar.markdown(f"- 🏛️ **Moughataa :** {moughataa_cible}")
      st.sidebar.markdown(f"- 🏘️ **Commune :** {commune_cible}")
      st.sidebar.metric(label="Distance estimée", value=f"{distance_ouvrage:.2f} km")

      tracer_ligne = st.sidebar.checkbox(
          "Afficher l'itinéraire direct sur la carte", value=True
      )
    else:
      st.sidebar.warning("Coordonnées GPS absentes pour cet ouvrage.")
# ==========================================
# LA CARTE FOLIUM ET LES ONGLETS DE LA SUITE
# ==========================================
# (Ici tu mets le reste de ton code pour afficher la carte interactive)
# Filtres thématiques
st.sidebar.markdown('---')
if 'categorie' in df.columns:
  categories = df['categorie'].dropna().unique().tolist()
  choix_categories = st.sidebar.multiselect(
      'Filtrer par Catégorie', categories, default=categories
  )
  if choix_categories:
    df = df[df['categorie'].isin(choix_categories)]

if 'type_ouvrage' in df.columns:
  types_ouvrages = df['type_ouvrage'].dropna().unique().tolist()
  choix_types = st.sidebar.multiselect(
      'Type d’ouvrage', types_ouvrages, default=types_ouvrages
  )
  if choix_types:
    df = df[df['type_ouvrage'].isin(choix_types)]

if 'etat' in df.columns:
  etats = df['etat'].dropna().unique().tolist()
  choix_etats = st.sidebar.multiselect(
      "État de l'infrastructure", etats, default=etats
  )
  if choix_etats:
    df = df[df['etat'].isin(choix_etats)]

# Affichage des Indicateurs Clés de Synthèse (KPIs)
st.subheader('📊 Indicateurs de Synthèse & Couverture Pastorale')
col1, col2, col3, col4 = st.columns(4)

with col1:
  st.metric(label='Ouvrages filtrés', value=f'{len(df)}')

with col2:
  if 'wilaya' in df.columns:
    st.metric(label='Wilayas concernées', value=df['wilaya'].nunique())
  else:
    st.metric(label='Wilayas', value='-')

with col3:
  if 'Commune' in df.columns:
    st.metric(label='Communes couvertes', value=df['Commune'].nunique())
  else:
    st.metric(label='Communes', value='-')

with col4:
  if 'etat' in df.columns:
    fonctionnels = len(
        df[df['etat'].astype(str).str.lower().str.contains('fonctionnel|bon', na=False)]
    )
    st.metric(label='Opérationnels / Bons', value=fonctionnels)
  else:
    st.metric(label='Statut', value='Actif')

st.markdown('---')
# ==========================================
# 3. LA SUITE DE VOTRE CODE EXISTANT (la carte Folium, les onglets, etc.)
# CONTINUE ICI EN UTILISANT LA VARIABLE `df` FILTRÉE :
# ==========================================
# (Votre code de carte s'affichera dynamiquement en fonction des filtres choisis ci-dessus)
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import math
import io

st.set_page_config(
    page_title="SIG Pastoral Mauritanie",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style CSS personnalisé
st.markdown("""
<style>
    .main-header {
        font-size: 24px;
        font-weight: bold;
        color: #1b4332;
        margin-bottom: 2px;
    }
    .sub-header {
        font-size: 14px;
        color: #52796f;
        margin-bottom: 15px;
    }
    .metric-card {
        background: #f8f9fa;
        border-left: 5px solid #2d6a4f;
        padding: 10px 14px;
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def charger_donnees():
    try:
        return pd.read_excel('infrastructures_unifiees.xlsx')
    except Exception as e:
        return None

df = charger_donnees()

if df is None:
    st.error("Le fichier 'infrastructures_unifiees.xlsx' n'a pas été trouvé dans le répertoire de travail.")
    st.info("Assurez-vous que 'infrastructures_unifiees.xlsx' se trouve dans le même dossier que 'app.py'.")
    st.stop()

# Barre latérale : Filtres
st.sidebar.image("https://img.icons8.com/color/96/oasis.png", width=60)
st.sidebar.title("SIG Pastoral")
st.sidebar.caption("Plateforme d'aide à la décision et de zonage")

st.sidebar.subheader("Filtrage Géographique")
wilayas_dispos = sorted(df['wilaya'].dropna().unique())
sel_wilayas = st.sidebar.multiselect("Wilaya", options=wilayas_dispos, default=[])

df_zone = df[df['wilaya'].isin(sel_wilayas)] if sel_wilayas else df

moughataas_dispos = sorted(df_zone['moughataa'].dropna().unique())
sel_moughataas = st.sidebar.multiselect("Moughataa", options=moughataas_dispos, default=[])
if sel_moughataas:
    df_zone = df_zone[df_zone['moughataa'].isin(sel_moughataas)]

st.sidebar.subheader("Filtrage Thématique")
categories_dispos = sorted(df['categorie'].dropna().unique())
sel_cats = st.sidebar.multiselect("Catégorie d'infrastructure", options=categories_dispos, default=[])
if sel_cats:
    df_zone = df_zone[df_zone['categorie'].isin(sel_cats)]

etats_dispos = sorted(df['etat'].dropna().unique())
sel_etats = st.sidebar.multiselect("État physique", options=etats_dispos, default=[])
if sel_etats:
    df_zone = df_zone[df_zone['etat'].isin(sel_etats)]

st.sidebar.markdown("---")
st.sidebar.subheader("Paramètres de l'Analyse Pastorale")
rayon_buffer = st.sidebar.slider("Rayon d'action pastorale (km)", min_value=3, max_value=25, value=15, step=1,
                                 help="Norme sahélienne standard : 5 km (petits ruminants), 15 km (bovins en saison sèche).")
montrer_degrades = st.sidebar.checkbox("Afficher le potentiel des puits à réhabiliter", value=True)

# En-tête principal
st.markdown('<div class="main-header">Système d\'Information Géographique Pastoral — Mauritanie</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Identification, analyse spatiale et planification des interventions d\'urgence pastorale</div>', unsafe_allow_html=True)

# Indicateurs de bord
col1, col2, col3, col4, col5 = st.columns(5)

total_pts = len(df_zone)
df_puits = df_zone[df_zone['categorie'] == 'Hydraulique pastorale']
puits_actifs = df_puits[~df_puits['etat'].str.contains('hors|réhab', case=False, na=False)]
puits_degrades = df_puits[df_puits['etat'].str.contains('hors|réhab', case=False, na=False)]

surface_unitaire = math.pi * (rayon_buffer ** 2)
surface_active_km2 = len(puits_actifs) * surface_unitaire
potentiel_rehab_km2 = len(puits_degrades) * surface_unitaire

col1.metric("Ouvrages sélectionnés", f"{total_pts:,}")
col2.metric("Puits fonctionnels", f"{len(puits_actifs):,}")
col3.metric("Puits à réhabiliter", f"{len(puits_degrades):,}")
col4.metric(f"Desserte active (R={rayon_buffer}km)", f"{surface_active_km2:,.0f} km²")
col5.metric(f"Potentiel déblocable", f"{potentiel_rehab_km2:,.0f} km²")

# Onglets
tab_carte, tab_zonage, tab_donnees = st.tabs([
    "🗺️ Carte Globale & Répartition",
    "🛰️ Analyse de Couverture & Pâturages (Buffers)",
    "📋 Données & Exports"
])

def get_color(etat):
    e = str(etat).lower()
    if 'bon' in e: return '#2d6a4f'
    if 'lég' in e or 'leger' in e: return '#f39c12'
    return '#d62828'

with tab_carte:
    if total_pts > 0:
        moy_lat = df_zone['latitude'].mean()
        moy_lon = df_zone['longitude'].mean()
        carte_inv = folium.Map(location=[moy_lat, moy_lon], zoom_start=8, tiles='OpenStreetMap')
        cluster = MarkerCluster(name="Regroupements d'ouvrages").add_to(carte_inv)

        for _, r in df_zone.head(1500).iterrows():
            txt_pop = f"""
            <b>{r['nom']}</b><br>
            <b>Type :</b> {r['type_ouvrage']}<br>
            <b>Localité :</b> {r['localite']} ({r['moughataa']}, {r['wilaya']})<br>
            <b>État :</b> {r['etat']}<br>
            <b>Gestion :</b> {r['responsable'] or r['gestion']}
            """
            folium.CircleMarker(
                location=[r['latitude'], r['longitude']],
                radius=5,
                color=get_color(r['etat']),
                fill=True,
                fill_opacity=0.85,
                popup=folium.Popup(txt_pop, max_width=280)
            ).add_to(cluster)

        folium.LayerControl().add_to(carte_inv)
        st_folium(carte_inv, width="100%", height=550)
        if total_pts > 1500:
            st.caption(f"ℹ️ Affichage optimisé à 1 500 points sur {total_pts} pour garantir une réactivité maximale.")
    else:
        st.warning("Aucune infrastructure ne correspond aux critères de filtre.")

with tab_zonage:
    st.subheader(f"Modélisation de l'empreinte pastorale ({rayon_buffer} km autour des points d'eau)")
    st.caption("Cercles verts : zones pâturables sécurisées par un point d'eau opérationnel. Cercles rouges en pointillés : pâturages enclavés ou sous-exploités dont l'accès dépend de la réhabilitation du point d'eau.")
    
    if len(df_puits) > 0:
        moy_lat = df_puits['latitude'].mean()
        moy_lon = df_puits['longitude'].mean()
        carte_zone = folium.Map(location=[moy_lat, moy_lon], zoom_start=9, tiles='OpenStreetMap')

        fg_verts = folium.FeatureGroup(name="Zones couvertes (Puits fonctionnels)")
        fg_rouges = folium.FeatureGroup(name="Zones à débloquer (À réhabiliter)")

        for _, p in puits_actifs.head(500).iterrows():
            folium.Circle(
                location=[p['latitude'], p['longitude']],
                radius=rayon_buffer * 1000,
                color='#2d6a4f',
                weight=1,
                fill=True,
                fill_color='#52b788',
                fill_opacity=0.15
            ).add_to(fg_verts)
            folium.CircleMarker(
                location=[p['latitude'], p['longitude']],
                radius=4,
                color='#1b4332',
                fill=True,
                fill_opacity=1,
                popup=f"<b>{p['nom']}</b> ({p['localite']})<br>État: {p['etat']}"
            ).add_to(fg_verts)

        if montrer_degrades:
            for _, p in puits_degrades.head(500).iterrows():
                folium.Circle(
                    location=[p['latitude'], p['longitude']],
                    radius=rayon_buffer * 1000,
                    color='#d62828',
                    weight=1.5,
                    dash_array='4, 6',
                    fill=True,
                    fill_color='#e63946',
                    fill_opacity=0.10
                ).add_to(fg_rouges)
                folium.CircleMarker(
                    location=[p['latitude'], p['longitude']],
                    radius=4,
                    color='#a4161a',
                    fill=True,
                    fill_opacity=1,
                    popup=f"<b>{p['nom']} (À RÉHABILITER)</b> ({p['localite']})<br>État: {p['etat']}"
                ).add_to(fg_rouges)

        fg_verts.add_to(carte_zone)
        if montrer_degrades:
            fg_rouges.add_to(carte_zone)

        folium.LayerControl().add_to(carte_zone)
        st_folium(carte_zone, width="100%", height=550)
    else:
        st.warning("Aucun point d'eau présent dans la sélection actuelle.")

with tab_donnees:
    st.subheader("Base d'inventaire tabulaire")
    st.dataframe(
        df_zone[['id', 'categorie', 'type_ouvrage', 'nom', 'localite', 'wilaya', 'moughataa', 'commune', 'etat', 'profondeur_m', 'latitude', 'longitude']],
        use_container_width=True,
        hide_index=True
    )

    col_dl1, col_dl2 = st.columns(2)
    with col_dl1:
        csv_bytes = df_zone.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Télécharger la sélection en CSV",
            data=csv_bytes,
            file_name="selection_pastorale.csv",
            mime="text/csv"
        )
    with col_dl2:
        # Export Excel direct
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_zone.to_excel(writer, index=False, sheet_name='Ouvrages')
        excel_data = output.getvalue()
        st.download_button(
            label="📊 Télécharger la sélection en Excel (.xlsx)",
            data=excel_data,
            file_name="selection_pastorale.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
