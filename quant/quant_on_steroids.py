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

# Functie om pieken te detecteren
def detect_peaks(series, distance=180, prominence=None):
    # Verwijder NaN waarden voor piekdetectie
    series_clean = series.dropna()
    peaks, _ = find_peaks(series_clean, distance=distance, prominence=prominence)
    # Map de pieken terug naar de originele index
    return series_clean.iloc[peaks].index

# Pad naar data
base_dir = '/Users/kimgrifhorst/Desktop/final charts 2024/repository/Now_I_Know/quant/'

# Definieer de oscillatoren
oscillators = {
    'price': {
        'file': os.path.join(base_dir, 'Price.json'),
        'column': 'Price',  # Hoofdlettergevoelig: 'Price'
    },
    'SOPR': {
        'file': os.path.join(base_dir, 'SOPR.json'),
        'column': 'SOPR',  # Hoofdlettergevoelig: 'SOPR'
    },
    # Voeg hier meer oscillatoren toe indien nodig
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

# Voeg de logaritmische prijs toe
combined_df['log_price'] = np.log(combined_df['Price'])

# Pas piekdetectie toe op de logaritmische prijs
price_prominence = 0.6  # Pas dit aan op basis van je data
price_distance = 180

price_peaks = detect_peaks(combined_df['log_price'], distance=price_distance, prominence=price_prominence)
combined_df['price_peak'] = False
combined_df.loc[price_peaks, 'price_peak'] = True

# Piekdetectie voor SOPR
sopr_prominence = 0.5  # Pas dit aan op basis van je data
sopr_distance = 180

sopr_peaks = detect_peaks(combined_df['SOPR'], distance=sopr_distance, prominence=sopr_prominence)
combined_df['SOPR_peak'] = False
combined_df.loc[sopr_peaks, 'SOPR_peak'] = True

# Bereken de closeness_score gebaseerd op SOPR
combined_df['max_sopr_since_peak'] = combined_df['SOPR'].groupby((combined_df['SOPR_peak']).cumsum()).cummax()
combined_df['closeness_score'] = (combined_df['SOPR'] / combined_df['max_sopr_since_peak']) * 100
combined_df['closeness_score'] = combined_df['closeness_score'].clip(upper=100)

# Selecteer alleen prijs pieken voor verdere analyse
peaks_df = combined_df[combined_df['price_peak']].copy()
peaks_df['closeness_score'] = combined_df.loc[peaks_df.index, 'closeness_score']

# Opslaan als CSV
output_csv = os.path.join(base_dir, 'bitcoin_peaks_scores.csv')
peaks_df.to_csv(output_csv, index=False)
print(f"\nResultaten opgeslagen in {output_csv}")

# Visualisaties
# Logaritmische Prijs met Pieken
plt.figure(figsize=(14,7))
plt.plot(combined_df['timestamp'], combined_df['log_price'], label='Logaritmische Prijs')
plt.scatter(combined_df.loc[price_peaks, 'timestamp'], combined_df.loc[price_peaks, 'log_price'], color='red', label='Prijs Toppen')
plt.xlabel('Datum')
plt.ylabel('Logaritmische Prijs')
plt.title('Bitcoin Logaritmische Prijs met Toppen Gemarkeerd')
plt.legend()
plt.show()

# Originele Prijs met Pieken
plt.figure(figsize=(14,7))
plt.plot(combined_df['timestamp'], combined_df['Price'], label='Prijs')
plt.scatter(peaks_df['timestamp'], peaks_df['Price'], color='red', label='Prijs Toppen')
plt.xlabel('Datum')
plt.ylabel('Prijs in USD')
plt.title('Bitcoin Prijs met Toppen Gemarkeerd')
plt.legend()
plt.show()

# SOPR met Pieken
plt.figure(figsize=(14,7))
plt.plot(combined_df['timestamp'], combined_df['SOPR'], label='SOPR')
plt.scatter(combined_df.loc[sopr_peaks, 'timestamp'], combined_df.loc[sopr_peaks, 'SOPR'], color='orange', label='SOPR Toppen')
plt.xlabel('Datum')
plt.ylabel('SOPR')
plt.title('SOPR met Toppen Gemarkeerd')
plt.legend()
plt.show()

# Closeness Score
plt.figure(figsize=(14,7))
plt.plot(peaks_df['timestamp'], peaks_df['closeness_score'], marker='o', linestyle='-', color='green')
plt.xlabel('Datum')
plt.ylabel('Closeness Score (1-100)')
plt.title('Closeness Score op Prijs Toppen volgens SOPR')
plt.ylim(0, 100)
plt.show()
