import pandas as pd
import json
from datetime import datetime, timedelta

# Stap 1: JSON-data inladen
def load_json_data(sopr_path, mvrv_path, price_path):
    # Gebruik json.load() om de JSON-bestanden in te laden
    with open(sopr_path, 'r') as sopr_file:
        sopr_data = json.load(sopr_file)['data']
    with open(mvrv_path, 'r') as mvrv_file:
        mvrv_data = json.load(mvrv_file)['data']
    with open(price_path, 'r') as price_file:
        price_data = json.load(price_file)['data']
    
    # Zet de ingelezen JSON om naar DataFrames
    sopr_df = pd.DataFrame(sopr_data)
    mvrv_df = pd.DataFrame(mvrv_data)
    price_df = pd.DataFrame(price_data)
    
    # Datumvelden omzetten naar datetime objecten
    sopr_df['date'] = pd.to_datetime(sopr_df['date'])
    mvrv_df['date'] = pd.to_datetime(mvrv_df['date'])
    price_df['date'] = pd.to_datetime(price_df['date'])
    
    # Dataframes combineren op basis van de 'date' kolom
    combined_df = pd.merge(sopr_df, mvrv_df, on='date', how='inner')
    combined_df = pd.merge(combined_df, price_df, on='date', how='inner')
    
    # Data filteren vanaf 1 januari 2013
    start_date = pd.to_datetime('2013-01-01')
    combined_df = combined_df[combined_df['date'] >= start_date]
    
    return combined_df

# Stap 2: Bereken 10% van het verschil tussen de laagste en hoogste waarde
def calculate_percentage_threshold(df, col_name, percentage=0.1):
    min_value = df[col_name].min()
    max_value = df[col_name].max()
    threshold = round(min_value + (percentage * (max_value - min_value)), 2)  # Bereken de drempel met 2 decimalen
    return threshold

# Stap 3: Bereken de dagen tot een prijsstijging
def calculate_days_to_increase(df, threshold_col, days_to_check=30):
    days_to_increase = []
    for index, row in df.iterrows():
        future_data = df[(df['date'] > row['date']) & (df['date'] <= row['date'] + timedelta(days=days_to_check))]
        price_increase = future_data[future_data['Price'] > row['Price']]
        if not price_increase.empty:
            first_increase_day = (price_increase['date'].iloc[0] - row['date']).days
            days_to_increase.append(first_increase_day)
        else:
            days_to_increase.append(days_to_check)  # Geen stijging gevonden binnen de days_to_check
    return pd.Series(days_to_increase)

# Stap 4: Bereken dagelijkse koop/verkoop score op basis van gewichten en dagen tot stijging
def calculate_daily_score(df, sopr_weight, mvrv_weight, sopr_days, mvrv_days, sopr_threshold, mvrv_threshold):
    # Aanpassen van gewichten op basis van tijd tot prijsstijging
    adjusted_sopr_weight = sopr_weight / sopr_days
    adjusted_mvrv_weight = mvrv_weight / mvrv_days

    # Gebruik pandas vectorized operations om de koopscore en verkoopscore te berekenen
    df['buy_score'] = (
        (adjusted_sopr_weight * (1 - df['SOPR'])).where(df['SOPR'] <= sopr_threshold, 0) +
        (adjusted_mvrv_weight * (1 - df['Active_MVRV'])).where(df['Active_MVRV'] <= mvrv_threshold, 0)
    )
    
    df['sell_score'] = (
        (adjusted_sopr_weight * df['SOPR']).where(df['SOPR'] >= sopr_threshold, 0) +
        (adjusted_mvrv_weight * df['Active_MVRV']).where(df['Active_MVRV'] >= mvrv_threshold, 0)
    )

    return df

# Stap 5: Toekenning van gewichten en dagen berekening
def assign_historical_weights_and_days(df):
    # Historisch gewogen score gebaseerd op eerdere prestatie
    sopr_weight = 0.6  # Dit is een fictieve waarde gebaseerd op eerdere prestaties
    mvrv_weight = 0.4  # Dit is een fictieve waarde gebaseerd op eerdere prestaties

    # Bereken de dagen tot prijsstijging voor SOPR en Active_MVRV
    sopr_days = calculate_days_to_increase(df, 'SOPR')
    mvrv_days = calculate_days_to_increase(df, 'Active_MVRV')

    # Gemiddelde dagen voor prijsstijging berekenen
    sopr_avg_days = sopr_days.mean()
    mvrv_avg_days = mvrv_days.mean()

    return sopr_weight, mvrv_weight, sopr_avg_days, mvrv_avg_days

# Stap 6: Resultaten naar CSV opslaan
def save_to_csv(df, file_name='resultaten.csv'):
    df.to_csv(file_name, index=False)
    print(f'Resultaten opgeslagen in {file_name}')

# Uitvoeren van het volledige proces
def run_analysis(sopr_path, mvrv_path, price_path):
    # Data inladen
    combined_df = load_json_data(sopr_path, mvrv_path, price_path)

    # Historische gewichten instellen en dagen tot prijsstijging berekenen
    sopr_weight, mvrv_weight, sopr_avg_days, mvrv_avg_days = assign_historical_weights_and_days(combined_df)

    # Bereken de drempels op basis van procentuele verschillen
    sopr_threshold = calculate_percentage_threshold(combined_df, 'SOPR', 0.1)
    mvrv_threshold = calculate_percentage_threshold(combined_df, 'Active_MVRV', 0.1)

    # Bereken de dagelijkse score (koop/verkoop) met aangepaste gewichten
    combined_df_with_scores = calculate_daily_score(combined_df, sopr_weight, mvrv_weight, sopr_avg_days, mvrv_avg_days, sopr_threshold, mvrv_threshold)

    # Resultaten naar CSV opslaan
    save_to_csv(combined_df_with_scores)

# Voorbeeld aanroepen (vervang paden door de werkelijke paden van je bestanden)
sopr_path = 'SOPR.json'
mvrv_path = 'Active_MVRV.json'
price_path = 'Price.json'

run_analysis(sopr_path, mvrv_path, price_path)
