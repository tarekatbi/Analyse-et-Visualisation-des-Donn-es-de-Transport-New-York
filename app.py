import streamlit as st
import pandas as pd
import pydeck as pdk
import datetime

# Chargement des données
yellow_data = pd.read_parquet("data_cleaned/yellow_data.parquet")
green_data = pd.read_parquet("data_cleaned/green_data.parquet")
vtc_data = pd.read_parquet("data_cleaned/vtc_data.parquet")

# Renommer les colonnes pour uniformiser le nom des colonnes de date
yellow_data.rename(columns={'pickup_time': 'pickup_time', 'dropoff_time': 'dropoff_time'}, inplace=True)
green_data.rename(columns={'pickup_time': 'pickup_time', 'dropoff_time': 'dropoff_time'}, inplace=True)
vtc_data.rename(columns={'pickup_time': 'pickup_time'}, inplace=True)

# Convertir les timestamps en datetime
yellow_data['pickup_time'] = pd.to_datetime(yellow_data['pickup_time'], unit='ms')
yellow_data['dropoff_time'] = pd.to_datetime(yellow_data['dropoff_time'], unit='ms')

green_data['pickup_time'] = pd.to_datetime(green_data['pickup_time'], unit='ms')
green_data['dropoff_time'] = pd.to_datetime(green_data['dropoff_time'], unit='ms')

vtc_data['pickup_time'] = pd.to_datetime(vtc_data['pickup_time'], unit='ms')

# Fusionner les datasets
yellow_data['type'] = 'yellow'
green_data['type'] = 'green'
vtc_data['type'] = 'vtc'

vtc_data['passenger_count'] = 0  # Ajoute une colonne avec une valeur par défaut

green_data.rename(columns={'Passenger_count': 'passenger_count'}, inplace=True)
green_data.rename(columns={'Payment_type': 'payment_type'}, inplace=True)
green_data.rename(columns={'Tip_amount': 'tip_amount'}, inplace=True)

# Fusionner les datasets
all_data = pd.concat([
    yellow_data[['pickup_lat', 'pickup_lon', 'dropoff_lat', 'dropoff_lon', 'pickup_time', 'dropoff_time', 'type', 'passenger_count', 'distance', 'total_fare', 'payment_type', 'tip_amount']],
    green_data[['pickup_lat', 'pickup_lon', 'dropoff_lat', 'dropoff_lon', 'pickup_time', 'dropoff_time', 'type', 'passenger_count', 'distance', 'total_fare', 'payment_type', 'tip_amount']],
    vtc_data[['pickup_lat', 'pickup_lon', 'pickup_time', 'type', 'passenger_count']]
], ignore_index=True)


# Filtrer les données par date et type de véhicule
st.title("Analyse des Pickups et Drop-offs à New York")
st.sidebar.title("Filtres")

# Filtres par date
start_date = st.sidebar.date_input('Date de début', value=datetime.date(2015, 1, 1))
end_date = st.sidebar.date_input('Date de fin', value=datetime.date(2015, 1, 18))

# Filtres par type de véhicule
vehicle_type = st.sidebar.multiselect(
    'Sélectionner les types de véhicules',
    options=['yellow', 'green', 'vtc'],
    default=['yellow', 'green', 'vtc']
)

# Filtres pour Pickups/Drop-offs (uniquement pour Yellow et Green)
pickup_dropoff_choice = st.sidebar.selectbox(
    'Sélectionner Pickup ou Drop-off (Yellow et Green uniquement)',
    options=['Pickups', 'Drop-offs']
)

# Filtrer les données en fonction de la date, du type de véhicule et du choix Pickup/Drop-off
filtered_data = all_data[
    (all_data['pickup_time'] >= pd.to_datetime(start_date)) & 
    (all_data['pickup_time'] <= pd.to_datetime(end_date)) &
    (all_data['type'].isin(vehicle_type))
]

# Appliquer le filtre supplémentaire Pickup/Drop-off uniquement pour Yellow et Green
if 'yellow' in vehicle_type or 'green' in vehicle_type:
    if pickup_dropoff_choice == 'Pickups':
        filtered_data = filtered_data.dropna(subset=['pickup_lat', 'pickup_lon'])
    elif pickup_dropoff_choice == 'Drop-offs':
        filtered_data = filtered_data.dropna(subset=['dropoff_lat', 'dropoff_lon'])

# Afficher un aperçu des données filtrées
st.write(f"Nombre de trajets entre {start_date} et {end_date} pour les types sélectionnés: {filtered_data.shape[0]}")
st.write(filtered_data.head())

# Carte interactive avec Kepler.gl via Pydeck
st.header("Carte des Pickups et Drop-offs")

# Définir les couleurs pour chaque type de véhicule
vehicle_colors = {
    'yellow': [255, 255, 0],  # Jaune
    'green': [0, 255, 0],     # Vert
    'vtc': [0, 0, 255]        # Bleu
}

# Créer les couches de données pour la carte (Pickups et Dropoffs)
pickup_layers = []
dropoff_layers = []

# Créer des couches pour chaque type de véhicule
for vehicle in vehicle_type:
    vehicle_data = filtered_data[filtered_data['type'] == vehicle]
    
    if pickup_dropoff_choice == 'Pickups':  # Afficher uniquement les pickups
        pickup_layer = pdk.Layer(
            "ScatterplotLayer",
            vehicle_data[['pickup_lon', 'pickup_lat']],
            get_position=["pickup_lon", "pickup_lat"],
            get_radius=100,
            get_color=vehicle_colors[vehicle],
            radius_min_pixels=5,
            pickable=True,
            opacity=0.7,
            auto_highlight=True,
            tooltip={"html": f"Pick-up - {vehicle}", "style": {"color": "black"}}
        )
        pickup_layers.append(pickup_layer)
    elif pickup_dropoff_choice == 'Drop-offs':  # Afficher uniquement les drop-offs
        dropoff_layer = pdk.Layer(
            "ScatterplotLayer",
            vehicle_data[['dropoff_lon', 'dropoff_lat']].dropna(),
            get_position=["dropoff_lon", "dropoff_lat"],
            get_radius=100,
            get_color=vehicle_colors[vehicle],
            radius_min_pixels=5,
            pickable=True,
            opacity=0.7,
            auto_highlight=True,
            tooltip={"html": f"Drop-off - {vehicle}", "style": {"color": "black"}}
        )
        dropoff_layers.append(dropoff_layer)

# Configurer la vue
view_state = pdk.ViewState(
    longitude=-73.935242, latitude=40.730610, zoom=12, pitch=50
)

# Créer la carte
deck = pdk.Deck(
    layers=pickup_layers + dropoff_layers,
    initial_view_state=view_state,
    map_style='mapbox://styles/mapbox/light-v9'
)

# Afficher la carte dans Streamlit
st.pydeck_chart(deck)

# Filtrer les données pour exclure VTC dans les statistiques
stats_data = all_data[all_data['type'] != 'vtc']

# Calcul des nouvelles statistiques
# 1. Revenus totaux par type de véhicule
revenus_par_type = stats_data.groupby('type')['total_fare'].sum()

# 2. Pourcentage des paiements par type
pourcentage_paiement_par_type = stats_data.groupby('payment_type').size() / stats_data.shape[0] * 100

# 3. Nombre moyen de passagers par course
nombre_moyen_passagers = stats_data.groupby('type')['passenger_count'].mean()

# 4. Distance moyenne par course
distance_moyenne = stats_data.groupby('type')['distance'].mean()

# 5. Pourcentage de paiements avec pourboire
paiement_avec_pourboire = (stats_data['tip_amount'] > 0).mean() * 100

# 6. Temps moyen des trajets en minutes
# Conversion des timestamps en minutes
stats_data['pickup_time'] = pd.to_datetime(stats_data['pickup_time'], unit='ms')
stats_data['dropoff_time'] = pd.to_datetime(stats_data['dropoff_time'], unit='ms')
stats_data['temps_trajet'] = (stats_data['dropoff_time'] - stats_data['pickup_time']).dt.total_seconds() / 60
temps_moyen_trajet = stats_data.groupby('type')['temps_trajet'].mean()


# Afficher les statistiques
st.header("Statistiques")
if st.checkbox("Afficher les statistiques détaillées"):
    st.write("### Nombre de passagers par type de véhicule (hors VTC)")
    st.bar_chart(stats_data.groupby('type')['passenger_count'].sum())

    st.write("### Distance totale parcourue par type de véhicule (hors VTC)")
    if 'distance' in stats_data.columns:
        st.bar_chart(stats_data.groupby('type')['distance'].sum())
    else:
        st.write("La colonne 'trip_distance' n'existe pas dans les données filtrées.")

    # 1. Revenus totaux par type de véhicule
    st.write("### Revenus totaux par type de véhicule")
    st.bar_chart(revenus_par_type)

    # 2. Pourcentage des paiements par type
    st.write("### Pourcentage des paiements par type")
    st.bar_chart(pourcentage_paiement_par_type)

    # 3. Nombre moyen de passagers par course
    st.write("### Nombre moyen de passagers par course")
    st.bar_chart(nombre_moyen_passagers)

    # 4. Distance moyenne par course
    st.write("### Distance moyenne par course")
    st.bar_chart(distance_moyenne)

    # 5. Pourcentage de paiements avec pourboire
    st.write("### Pourcentage de paiements avec pourboire")
    st.write(f"{paiement_avec_pourboire:.2f}% des paiements incluent un pourboire")

    # 6. Temps moyen des trajets en minutes
    st.write("### Temps moyen des trajets (en minutes)")
    st.bar_chart(temps_moyen_trajet)
