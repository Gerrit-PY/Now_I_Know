import os
import json
import pandas as pd
from scipy.signal import find_peaks
import matplotlib.pyplot as plt
import numpy as np

# Functie om JSON-bestanden in te laden met foutafhandeling en debugging
def load_json(file_path):
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        # Verwerk data onder de sleutel 'data'
        if 'data' in data:
            df = pd.DataFrame(data['data'])
        else:
            df = pd.DataFrame(data)
        print(f"\nDataFrame geladen van {file_path}:")
        print(df.head())  # Print de eerste paar rijen voor inspectie
        print(f"Kolommen in de DataFrame: {df.columns.tolist()}")
        return df
    except FileNotFoundError:
        print(f"Fout: Bestand niet gevonden op pad: {file_path}")
        exit(1)
    except json.JSONDecodeError:
        print(f"Fout: Bestand is geen geldige JSON: {file_path}")
        exit(1)

# Functie om pieken te detecteren met dynamische prominences
def detect_peaks_dynamic(series, distance=180, prominence_percent=5):
    # Bereken de prominences als percentage van de maximale waarde in de serie
    max_val = series.max()
    if pd.isna(max_val) or max_val == 0:
        return []  # Geen pieken als de serie leeg is of max_val is 0
    prominence = (prominence_percent / 100) * max_val
    peaks, _ = find_peaks(series, distance=distance, prominence=prominence)
    return peaks

# Pad naar data
base_dir = '/Users/kimgrifhorst/Desktop/final charts 2024/repository/Now_I_Know/quant/'

# Definieer de oscillatoren inclusief Active_MVRV
oscillators = {
    'price': {
        'file': os.path.join(base_dir, 'Price.json'),
        'column': 'Price',  # Hoofdlettergevoelig: 'Price'
        'prominence_percent': 10,  # Verlaagd van 60 naar 10
        'distance': 180
    },
    'SOPR': {
        'file': os.path.join(base_dir, 'SOPR.json'),
        'column': 'SOPR',  # Hoofdlettergevoelig: 'SOPR'
        'prominence_percent': 20,  # Verlaagd van 60 naar 10
        'distance': 180
    },
    'Active_MVRV': {
        'file': os.path.join(base_dir, 'Active_MVRV.json'),
        'column': 'Active_MVRV',  # Hoofdlettergevoelig: 'Active_MVRV'
        'prominence_percent': 40,  # Verlaagd van 60 naar 10
        'distance': 180
    }
}

# Laad en combineer alle datasets
data_frames = {}
for name, props in oscillators.items():
    df = load_json(props['file'])
    # Zoek naar de tijdskolom
    possible_time_columns = ['timestamp', 'time', 'date', 'Timestamp', 'Date']
    for col in possible_time_columns:
        if col in df.columns:
            time_column = col
            break
    else:
        print(f"Fout: Geen tijdskolom gevonden in bestand {props['file']}.")
        exit(1)
    # Converteer tijdskolom naar datetime
    df['timestamp'] = pd.to_datetime(df[time_column], errors='coerce')
    df = df.drop(columns=[time_column])
    # Zet 'timestamp' als index en selecteer de relevante kolom
    data_frames[name] = df.set_index('timestamp')[props['column']]

# Combineer alle dataframes op timestamp
combined_df = pd.concat(data_frames.values(), axis=1, join='inner').reset_index()

# Filter data vanaf 2013-01-01
combined_df = combined_df[combined_df['timestamp'] >= '2013-01-01']
combined_df.sort_values('timestamp', inplace=True)
combined_df.reset_index(drop=True, inplace=True)

print("\nGecombineerde DataFrame:")
print(combined_df.head())

# Pas logaritmische transformatie toe op prijsgegevens
combined_df['log_price'] = np.log(combined_df['Price'])

# Dynamische piekdetectie voor elke oscillator op de logaritmische schaal
for name, props in oscillators.items():
    if name == 'price':
        series = combined_df['log_price']
    else:
        series = combined_df[props['column']]
    peaks = detect_peaks_dynamic(series, distance=props['distance'], prominence_percent=props['prominence_percent'])
    combined_df[f'{name}_peak'] = False
    combined_df.loc[peaks, f'{name}_peak'] = True

# Bereken de closeness_score gebaseerd op SOPR
if 'SOPR' in oscillators:
    combined_df['max_sopr_since_peak'] = combined_df['SOPR'].groupby((combined_df['SOPR_peak']).cumsum()).cummax()
    combined_df['closeness_score'] = (combined_df['SOPR'] / combined_df['max_sopr_since_peak']) * 100
    combined_df['closeness_score'] = combined_df['closeness_score'].clip(upper=100)

# Bereken de closeness_score voor Active_MVRV
if 'Active_MVRV' in oscillators:
    combined_df['max_active_mvrv_since_peak'] = combined_df['Active_MVRV'].groupby((combined_df['Active_MVRV_peak']).cumsum()).cummax()
    combined_df['closeness_score_active_mvrv'] = (combined_df['Active_MVRV'] / combined_df['max_active_mvrv_since_peak']) * 100
    combined_df['closeness_score_active_mvrv'] = combined_df['closeness_score_active_mvrv'].clip(upper=100)

# Selecteer alleen prijs pieken voor verdere analyse en verwijder NaN's in Price
peaks_df = combined_df[combined_df['price_peak']].copy()
peaks_df = peaks_df[~peaks_df['Price'].isna()]

# Verwijder eventuele rijen met NaN in kritieke kolommen
critical_columns = ['Price', 'SOPR', 'Active_MVRV']
peaks_df = peaks_df.dropna(subset=critical_columns + ['closeness_score', 'closeness_score_active_mvrv'])

# Opslaan als CSV
output_csv = os.path.join(base_dir, 'bitcoin_peaks_scores_cleaned_log.csv')
peaks_df.to_csv(output_csv, index=False)
print(f"\nGereinigde resultaten opgeslagen in {output_csv}")

# Visualisaties (optioneel, kan worden uitgeschakeld indien niet nodig)
# Prijs met Pieken (Logarithmische Schaal)
plt.figure(figsize=(14,7))
plt.plot(combined_df['timestamp'], combined_df['log_price'], label='Log Prijs')
plt.scatter(peaks_df['timestamp'], np.log(peaks_df['Price']), color='red', label='Prijs Toppen')
plt.xlabel('Datum')
plt.ylabel('Log Prijs in USD')
plt.title('Bitcoin Log Prijs met Toppen Gemarkeerd')
plt.legend()
plt.show()

# SOPR met Pieken
plt.figure(figsize=(14,7))
plt.plot(combined_df['timestamp'], combined_df['SOPR'], label='SOPR')
plt.scatter(combined_df.loc[combined_df['SOPR_peak'], 'timestamp'], combined_df.loc[combined_df['SOPR_peak'], 'SOPR'], color='orange', label='SOPR Toppen')
plt.xlabel('Datum')
plt.ylabel('SOPR')
plt.title('SOPR met Toppen Gemarkeerd')
plt.legend()
plt.show()

# Active_MVRV met Pieken
plt.figure(figsize=(14,7))
plt.plot(combined_df['timestamp'], combined_df['Active_MVRV'], label='Active MVRV')
plt.scatter(combined_df.loc[combined_df['Active_MVRV_peak'], 'timestamp'], combined_df.loc[combined_df['Active_MVRV_peak'], 'Active_MVRV'], color='purple', label='Active MVRV Toppen')
plt.xlabel('Datum')
plt.ylabel('Active MVRV')
plt.title('Active MVRV met Toppen Gemarkeerd')
plt.legend()
plt.show()

# Closeness Score voor SOPR
if 'closeness_score' in combined_df.columns:
    plt.figure(figsize=(14,7))
    plt.plot(peaks_df['timestamp'], peaks_df['closeness_score'], marker='o', linestyle='-', color='green')
    plt.xlabel('Datum')
    plt.ylabel('Closeness Score (1-100)')
    plt.title('Closeness Score op Prijs Toppen volgens SOPR')
    plt.ylim(0, 100)
    plt.show()

# Closeness Score voor Active_MVRV
if 'closeness_score_active_mvrv' in combined_df.columns:
    plt.figure(figsize=(14,7))
    plt.plot(peaks_df['timestamp'], peaks_df['closeness_score_active_mvrv'], marker='o', linestyle='-', color='blue')
    plt.xlabel('Datum')
    plt.ylabel('Closeness Score Active MVRV (1-100)')
    plt.title('Closeness Score Active MVRV op Prijs Toppen')
    plt.ylim(0, 100)
    plt.show()
