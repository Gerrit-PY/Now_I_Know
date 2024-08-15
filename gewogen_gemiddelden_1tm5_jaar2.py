import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Laad de nieuwe data
available_supply_data = pd.read_csv('available_supply_2024.csv')

# Zorg ervoor dat de 'date' kolom wordt herkend als een datetime object
available_supply_data['date'] = pd.to_datetime(available_supply_data['date'])

# Bereken de dagelijkse verandering in de available supply
available_supply_data['daily_change'] = available_supply_data['available_supply'].diff()

# Bereken het gewogen gemiddelde voor 1, 2, 3, 4, 5 jaar op basis van de dagelijkse verandering
available_supply_data.set_index('date', inplace=True)
weighted_1yr = available_supply_data['daily_change'].rolling(window=365, min_periods=365).mean()
weighted_2yr = available_supply_data['daily_change'].rolling(window=730, min_periods=730).mean()
weighted_3yr = available_supply_data['daily_change'].rolling(window=1095, min_periods=1095).mean()
weighted_4yr = available_supply_data['daily_change'].rolling(window=1460, min_periods=1460).mean()
weighted_5yr = available_supply_data['daily_change'].rolling(window=1825, min_periods=1825).mean()

# Zet de index terug naar een kolom
available_supply_data.reset_index(inplace=True)

# Voeg de gewogen gemiddelden toe aan de dataframe
available_supply_data['weighted_1yr'] = weighted_1yr.values
available_supply_data['weighted_2yr'] = weighted_2yr.values
available_supply_data['weighted_3yr'] = weighted_3yr.values
available_supply_data['weighted_4yr'] = weighted_4yr.values
available_supply_data['weighted_5yr'] = weighted_5yr.values

# Haal de laatste waardes op voor de titel (een dag terug)
latest_date = available_supply_data['date'].iloc[-2].strftime('%d-%m-%Y')
latest_1yr = available_supply_data['weighted_1yr'].iloc[-2]
latest_2yr = available_supply_data['weighted_2yr'].iloc[-2]
latest_3yr = available_supply_data['weighted_3yr'].iloc[-2]
latest_4yr = available_supply_data['weighted_4yr'].iloc[-2]
latest_5yr = available_supply_data['weighted_5yr'].iloc[-2]


# Creëer de interactieve grafiek met Plotly
fig = go.Figure()

# Viridis kleuren
colors = px.colors.sequential.Viridis

# Voeg het gewogen gemiddelde van 1 jaar toe
fig.add_trace(go.Scatter(
    x=available_supply_data['date'],
    y=available_supply_data['weighted_1yr'],
    mode='lines',
    name=f'1-Year Weighted Average: {latest_1yr:.2f}',
    line=dict(color=colors[0])
))

# Voeg het gewogen gemiddelde van 2 jaar toe
fig.add_trace(go.Scatter(
    x=available_supply_data['date'],
    y=available_supply_data['weighted_2yr'],
    mode='lines',
    name=f'2-Year Weighted Average: {latest_2yr:.2f}',
    line=dict(color=colors[1])
))

# Voeg het gewogen gemiddelde van 3 jaar toe
fig.add_trace(go.Scatter(
    x=available_supply_data['date'],
    y=available_supply_data['weighted_3yr'],
    mode='lines',
    name=f'3-Year Weighted Average: {latest_3yr:.2f}',
    line=dict(color=colors[2])
))

# Voeg het gewogen gemiddelde van 4 jaar toe
fig.add_trace(go.Scatter(
    x=available_supply_data['date'],
    y=available_supply_data['weighted_4yr'],
    mode='lines',
    name=f'4-Year Weighted Average: {latest_4yr:.2f}',
    line=dict(color=colors[3])
))

# Voeg het gewogen gemiddelde van 5 jaar toe
fig.add_trace(go.Scatter(
    x=available_supply_data['date'],
    y=available_supply_data['weighted_5yr'],
    mode='lines',
    name=f'5-Year Weighted Average: {latest_5yr:.2f}',
    line=dict(color=colors[4])
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

# Exporteer de plot naar een standalone HTML-bestand
fig.write_html('gewogen gemiddelden 1 tm 5 jaar.html')

# Exporteer de plot ook naar een PNG-bestand met de gewenste afmetingen en DPI
fig.write_image('/Users/kimgrifhorst/Desktop/final charts 2024/repository/Now_I_Know/gewogen gemiddelden 1 tm 5 jaar.png',
                width=1308, height=725, scale=1)
