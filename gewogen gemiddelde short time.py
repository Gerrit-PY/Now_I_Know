import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Laad de nieuwe data
available_supply_data = pd.read_csv('available_supply_2024.csv')

# Zorg ervoor dat de 'date' kolom wordt herkend als een datetime object
available_supply_data['date'] = pd.to_datetime(available_supply_data['date'])

# Bereken de dagelijkse verandering in de available supply
available_supply_data['daily_change'] = available_supply_data['available_supply'].diff()

# Bereken het gewogen gemiddelde voor 1 week, 1 maand, 3 maanden en 6 maanden op basis van de dagelijkse verandering
available_supply_data.set_index('date', inplace=True)
weighted_1w = available_supply_data['daily_change'].rolling(window=7, min_periods=7).mean()
weighted_1m = available_supply_data['daily_change'].rolling(window=30, min_periods=30).mean()
weighted_3m = available_supply_data['daily_change'].rolling(window=90, min_periods=90).mean()
weighted_6m = available_supply_data['daily_change'].rolling(window=180, min_periods=180).mean()

# Zet de index terug naar een kolom
available_supply_data.reset_index(inplace=True)

# Voeg de gewogen gemiddelden toe aan de dataframe
available_supply_data['weighted_1w'] = weighted_1w.values
available_supply_data['weighted_1m'] = weighted_1m.values
available_supply_data['weighted_3m'] = weighted_3m.values
available_supply_data['weighted_6m'] = weighted_6m.values

# Haal de laatste waardes op voor de titel (een dag terug)
latest_date = available_supply_data['date'].iloc[-2].strftime('%d-%m-%Y')
latest_1w = available_supply_data['weighted_1w'].iloc[-2]
latest_1m = available_supply_data['weighted_1m'].iloc[-2]
latest_3m = available_supply_data['weighted_3m'].iloc[-2]
latest_6m = available_supply_data['weighted_6m'].iloc[-2]

# Creëer de interactieve grafiek met Plotly
fig = go.Figure()

# Viridis kleuren
colors = px.colors.sequential.Viridis

# Voeg het gewogen gemiddelde van 1 week toe
fig.add_trace(go.Scatter(
    x=available_supply_data['date'],
    y=available_supply_data['weighted_1w'],
    mode='lines',
    name=f'1-Week Weighted Average: {latest_1w:.2f}',
    line=dict(color=colors[0])
))

# Voeg het gewogen gemiddelde van 1 maand toe
fig.add_trace(go.Scatter(
    x=available_supply_data['date'],
    y=available_supply_data['weighted_1m'],
    mode='lines',
    name=f'1-Month Weighted Average: {latest_1m:.2f}',
    line=dict(color=colors[1])
))

# Voeg het gewogen gemiddelde van 3 maanden toe
fig.add_trace(go.Scatter(
    x=available_supply_data['date'],
    y=available_supply_data['weighted_3m'],
    mode='lines',
    name=f'3-Month Weighted Average: {latest_3m:.2f}',
    line=dict(color=colors[2])
))

# Voeg het gewogen gemiddelde van 6 maanden toe
fig.add_trace(go.Scatter(
    x=available_supply_data['date'],
    y=available_supply_data['weighted_6m'],
    mode='lines',
    name=f'6-Month Weighted Average: {latest_6m:.2f}',
    line=dict(color=colors[3])
))

# Werk de layout bij met lineaire y-as en nieuwe titel
fig.update_layout(
    title=f'Weighted Averages of Daily Change in Available Supply\n({latest_date})',
    xaxis_title='Date',
    yaxis_title='Weighted Average of Daily Change in Available Supply',
    yaxis=dict(
        showgrid=True,
        tickformat=',.0f',
        linecolor='blue'
    ),
    xaxis=dict(
        tickformat='%d-%m-%Y',
        tickangle=45
    ),
    legend=dict(
        x=0.01,  # Legenda meer naar links
        y=0.99,  # Legenda meer omhoog
        bgcolor='rgba(255, 255, 255, 0.8)',
        bordercolor='Black',
        borderwidth=1
    )
)

# Toon de interactieve grafiek
fig.show()
