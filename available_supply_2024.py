import pandas as pd
import yfinance as yf
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Laad de samengevoegde data
merged_data = pd.read_csv('available_supply_2024.csv')

# Haal Bitcoin-prijzen op van de yfinance API
ticker = 'BTC-USD'
btc_data = yf.download(ticker, start=merged_data['date'].min(), end=merged_data['date'].max())

# Lijn Bitcoin-prijzen uit met de data in merged_data
btc_data = btc_data.reindex(merged_data['date']).ffill()
merged_data['price'] = btc_data['Adj Close'].values

# Bereken de beschikbare supply in dollars
merged_data['available_supply_dollars'] = merged_data['available_supply'] * merged_data['price']

# Verwijder rijen die NaN-waarden bevatten in 'available_supply_dollars'
merged_data = merged_data.dropna(subset=['available_supply_dollars'])

# Haal de laatste datum waarbij een waarde beschikbaar is voor 'available_supply'
last_date = merged_data.dropna(subset=['available_supply'])['date'].max()
last_date_str = datetime.strptime(last_date, '%Y-%m-%d').strftime('%d-%m-%Y')

# Haal de laatste waarden voor de legenda
last_available_supply = merged_data.loc[merged_data['date'] == last_date, 'available_supply'].values[0]
last_available_supply_dollars = merged_data.loc[merged_data['date'] == last_date, 'available_supply_dollars'].values[0]

# Creëer de interactieve grafiek met Plotly
fig = make_subplots(specs=[[{"secondary_y": True}]])

# Voeg beschikbare supply toe als een gevuld gebied
scatter_supply = go.Scatter(
    x=merged_data['date'],
    y=merged_data['available_supply'],
    mode='lines',
    name=f'Available Supply ({int(last_available_supply):,} BTC)',
    line=dict(color='blue'),
    fill='tozeroy'
)
fig.add_trace(scatter_supply)

# Voeg beschikbare supply in dollars toe
scatter_dollars = go.Scatter(
    x=merged_data['date'],
    y=merged_data['available_supply_dollars'],
    mode='lines',
    name=f'Available Supply in Dollars (${int(last_available_supply_dollars):,})',
    line=dict(color='#F7931A'),  # Kleur van het Bitcoin-logo
    yaxis="y2"
)
fig.add_trace(scatter_dollars)

# Werk de layout bij met dubbele y-assen en verplaats de legenda
fig.update_layout(
    title=f'Available BTC Supply in Dollars vs Available BTC Supply ({last_date_str})',
    xaxis_title='Date',
    yaxis=dict(
        title='Available BTC Supply',
        showgrid=False,
        tickformat=',.1f',
        ticksuffix=' BTC',
        rangemode='tozero',
        linecolor='blue'
    ),
    yaxis2=dict(
        title='Available BTC Supply in Dollars',
        overlaying='y',
        side='right',
        showgrid=False,
        tickformat='$,.0f',
        rangemode='tozero',
        linecolor='#F7931A'
    ),
    legend=dict(
        x=0, 
        y=1,
        xanchor='left',
        yanchor='top',
        itemsizing='constant'
    )
)

# Functie om annotaties toe te voegen of te verwijderen
def add_or_remove_annotation(trace, points, state):
    if points.point_inds:
        ind = points.point_inds[0]
        date = merged_data['date'][ind]
        value = points.ys[0]
        yref = 'y' if trace.name == 'Available Supply' else 'y2'
        existing_annotations = list(fig.layout.annotations)

        # Controleer of er al een annotatie bestaat op dezelfde locatie
        annotation_exists = False
        for i, annotation in enumerate(existing_annotations):
            if annotation['x'] == date and annotation['y'] == value:
                # Verwijder de annotatie
                existing_annotations.pop(i)
                annotation_exists = True
                break
        
        # Voeg een nieuwe annotatie toe als er geen bestaat
        if not annotation_exists:
            annotation = {
                'x': date,
                'y': value,
                'xref': 'x',
                'yref': yref,
                'text': f"Date: {date}<br>Value: {value:.1f}",
                'showarrow': True,
                'arrowhead': 2,
                'bgcolor': 'white'
            }
            existing_annotations.append(annotation)
        
        fig.update_layout(annotations=existing_annotations)

# Voeg klik event toe aan beide traces
fig.data[0].on_click(add_or_remove_annotation)
fig.data[1].on_click(add_or_remove_annotation)

# Toon de interactieve grafiek
fig.show()
