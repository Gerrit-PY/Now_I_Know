import pandas as pd
import json
from datetime import datetime, timedelta

# Stap 1: JSON-data inladen
def load_json_data(sopr_path, mvrv_path, price_path):
    with open(sopr_path, 'r') as sopr_file:
        sopr_data = json.load(sopr_file)['data']
    with open(mvrv_path, 'r') as mvrv_file:
        mvrv_data = json.load(mvrv_file)['data']
    with open(price_path, 'r') as price_file:
        price_data = json.load(price_file)['data']
    
    # Dataframes aanmaken
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
    
    return combined_df

# Stap 2: Signalen genereren op basis van variabele drempels
def generate_signals(df, sopr_buy_thresh, sopr_sell_thresh, mvrv_buy_thresh, mvrv_sell_thresh):
    df['buy_signal'] = (df['SOPR'] < sopr_buy_thresh) & (df['Active_MVRV'] < mvrv_buy_thresh)
    df['sell_signal'] = (df['SOPR'] > sopr_sell_thresh) & (df['Active_MVRV'] > mvrv_sell_thresh)
    return df

# Stap 3: Responstijden meten
def measure_response_times(df, signal_col, days_to_check=30):
    signals = df[df[signal_col]]  # Filter op de kolom met koop/verkoop signalen
    
    response_times = []
    
    for index, row in signals.iterrows():
        future_price = df.loc[(df['date'] > row['date']) & (df['date'] <= row['date'] + timedelta(days=days_to_check))]
        if signal_col == 'buy_signal':
            first_increase = future_price[future_price['price'] > row['price']].head(1)
            if not first_increase.empty:
                response_time = (first_increase['date'].iloc[0] - row['date']).days
                response_times.append(response_time)
        elif signal_col == 'sell_signal':
            first_decrease = future_price[future_price['price'] < row['price']].head(1)
            if not first_decrease.empty:
                response_time = (first_decrease['date'].iloc[0] - row['date']).days
                response_times.append(response_time)
    
    return response_times

# Stap 4: Gemiddelde responstijden berekenen
def calculate_average_response_times(response_times):
    avg_time = sum(response_times) / len(response_times) if response_times else None
    return avg_time

# Stap 5: Automatische drempelwaardes testen
def test_thresholds(df, sopr_buy_range, sopr_sell_range, mvrv_buy_range, mvrv_sell_range, days_to_check=30):
    results = []
    for sopr_buy in sopr_buy_range:
        for sopr_sell in sopr_sell_range:
            for mvrv_buy in mvrv_buy_range:
                for mvrv_sell in mvrv_sell_range:
                    # Genereer signalen met de huidige drempels
                    df_with_signals = generate_signals(df, sopr_buy, sopr_sell, mvrv_buy, mvrv_sell)
                    
                    # Meet de responstijden
                    buy_times = measure_response_times(df_with_signals, 'buy_signal', days_to_check=days_to_check)
                    sell_times = measure_response_times(df_with_signals, 'sell_signal', days_to_check=days_to_check)
                    
                    # Bereken de gemiddelde responstijden
                    avg_buy_time = calculate_average_response_times(buy_times)
                    avg_sell_time = calculate_average_response_times(sell_times)
                    
                    # Voeg de resultaten toe aan de lijst
                    results.append({
                        'sopr_buy_thresh': round(sopr_buy, 1),
                        'sopr_sell_thresh': round(sopr_sell, 1),
                        'mvrv_buy_thresh': round(mvrv_buy, 1),
                        'mvrv_sell_thresh': round(mvrv_sell, 1),
                        'avg_buy_time': avg_buy_time,
                        'avg_sell_time': avg_sell_time
                    })
    
    # Zet de resultaten in een DataFrame en sorteer op basis van responstijd
    results_df = pd.DataFrame(results)
    results_df = results_df.dropna(subset=['avg_buy_time', 'avg_sell_time'])  # Verwijder resultaten zonder respons
    results_df['combined_score'] = (results_df['avg_buy_time'] + results_df['avg_sell_time']) / 2
    results_df = results_df.sort_values(by='combined_score')
    
    return results_df.head(10)  # Return de top 10 resultaten

# Stap 6: Automatisch gewichten toekennen op basis van prestaties
def assign_weights(results_df):
    # Hoe lager de responstijd, hoe hoger het gewicht
    results_df['sopr_buy_weight'] = 100 / results_df['avg_buy_time'] if results_df['avg_buy_time'].notna().any() else 0
    results_df['sopr_sell_weight'] = 100 / results_df['avg_sell_time'] if results_df['avg_sell_time'].notna().any() else 0
    
    results_df['mvrv_buy_weight'] = 100 / results_df['avg_buy_time'] if results_df['avg_buy_time'].notna().any() else 0
    results_df['mvrv_sell_weight'] = 100 / results_df['avg_sell_time'] if results_df['avg_sell_time'].notna().any() else 0
    
    return results_df

# Uitvoeren van het volledige proces
def run_analysis(sopr_path, mvrv_path, price_path):
    # Data inladen
    combined_df = load_json_data(sopr_path, mvrv_path, price_path)
    
    # Drempelwaarderanges instellen
    sopr_buy_range = [x / 10.0 for x in range(8, 21)]  # Drempel voor koop tussen 0.8 en 2.0
    sopr_sell_range = [x / 10.0 for x in range(15, 31)]  # Drempel voor verkoop tussen 1.5 en 3.0
    mvrv_buy_range = [x / 10.0 for x in range(8, 21)]  # Drempel voor koop tussen 0.8 en 2.0
    mvrv_sell_range = [x / 10.0 for x in range(15, 31)]  # Drempel voor verkoop tussen 1.5 en 3.0
    
    # Test de drempelwaarden en haal de top 10 resultaten op
    top_10_thresholds = test_thresholds(combined_df, sopr_buy_range, sopr_sell_range, mvrv_buy_range, mvrv_sell_range)
    
    # Automatisch gewichten toekennen op basis van prestaties
    top_10_with_weights = assign_weights(top_10_thresholds)
    
    # Resultaten weergeven
    print(top_10_with_weights)

# Voorbeeld aanroepen (vervang paden door de werkelijke paden van je bestanden)
sopr_path = 'SOPR.json'
mvrv_path = 'Active_MVRV.json'
price_path = 'Price.json'

run_analysis(sopr_path, mvrv_path, price_path)
