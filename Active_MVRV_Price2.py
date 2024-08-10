import json
import pandas as pd
import plotly.graph_objects as go

# Load the JSON data for Active_MVRV, Active_Realized_Price, and BTC Price
with open('Active_MVRV.json', 'r') as file:
    active_mvrv_data = json.load(file)

with open('Active_Realized_Price.json', 'r') as file:
    active_realized_price_data = json.load(file)

with open('Price.json', 'r') as file:
    btc_price_data = json.load(file)

# Convert to DataFrames
df_active_mvrv = pd.DataFrame(active_mvrv_data['data'])
df_active_realized = pd.DataFrame(active_realized_price_data['data'])
df_btc_price = pd.DataFrame(btc_price_data['data'])

# Convert the 'date' column to datetime
df_active_mvrv['date'] = pd.to_datetime(df_active_mvrv['date'])
df_active_realized['date'] = pd.to_datetime(df_active_realized['date'])
df_btc_price['date'] = pd.to_datetime(df_btc_price['date'])

# Merge the DataFrames on the 'date' column
df_combined = pd.merge(df_active_mvrv, df_active_realized, on='date', how='inner')
df_combined = pd.merge(df_combined, df_btc_price, on='date', how='inner')

# Filter the combined DataFrame to start from 2013
df_combined = df_combined[df_combined['date'] >= '2013-01-01']

# Create the plot
fig = go.Figure()

# Add Active_MVRV trace with conditional coloring
fig.add_trace(go.Scatter(x=df_combined['date'], y=df_combined['Active_MVRV'], 
                         mode='lines', 
                         name='Active_MVRV<br>{:.2f}'.format(df_combined['Active_MVRV'].iloc[-1]), 
                         line=dict(color='green', width=2),
                         hovertemplate='%{y:.2f}'))

# Color fill for positive Active_MVRV (trace 2, not in legend)
fig.add_trace(go.Scatter(
    x=df_combined['date'], y=df_combined['Active_MVRV'].where(df_combined['Active_MVRV'] >= 0),
    mode='lines', line=dict(width=0),
    showlegend=False,
    fill='tozeroy', fillcolor='rgba(0,255,0,0.2)',
    hoverinfo='skip'
))

# Color fill for Active_MVRV from 0 to 5 (trace 3, not in legend)
fig.add_trace(go.Scatter(
    x=df_combined['date'], y=df_combined['Active_MVRV'].where((df_combined['Active_MVRV'] >= 0) & (df_combined['Active_MVRV'] <= 5)),
    mode='lines', line=dict(color='yellowgreen', width=2),
    showlegend=False,
    fill='tozeroy', fillcolor='rgba(255,255,0,0.2)',
    hoverinfo='skip'
))

# Color fill for negative Active_MVRV
fig.add_trace(go.Scatter(
    x=df_combined['date'], y=df_combined['Active_MVRV'].where(df_combined['Active_MVRV'] < 0),
    mode='lines', line=dict(color='red', width=2),
    showlegend=False,
    fill='tozeroy', fillcolor='rgba(255,0,0,0.2)',
    hovertemplate='%{y:.2f}',
    yaxis='y2'
))

# Add Active_Realized_Price trace
fig.add_trace(go.Scatter(x=df_combined['date'], y=df_combined['Active_Realized_Price'], 
                         mode='lines', 
                         name='Active_Realized_Price<br>{:.2f}'.format(df_combined['Active_Realized_Price'].iloc[-1]), 
                         line=dict(color='blue', width=2)))

# Add BTC_Price trace
fig.add_trace(go.Scatter(x=df_combined['date'], y=df_combined['Price'], 
                         mode='lines', 
                         name='BTC Price<br>{:.2f}'.format(df_combined['Price'].iloc[-1]), 
                         line=dict(color='orange', width=2)))

# Update layout to add a secondary y-axis and other customizations
fig.update_layout(
    title='Active_MVRV, Active_Realized_Price, and BTC Price',
    xaxis_title='Date',
    yaxis_title='BTC Price',
    yaxis=dict(
        type='log',
        tickvals=[1, 10, 100, 1000, 10000, 100000],
        ticktext=['1', '10', '100', '1k', '10k', '100k']
    ),
    yaxis2=dict(
        title='Active_MVRV',
        overlaying='y',
        side='right',
        range=[-2, 30]  # Adjust the range to accommodate the specified range
    ),
    legend_title='Metric',
    template='plotly_white'
)

# Update trace to use the secondary y-axis for Active_MVRV
fig.data[0].update(yaxis='y2')
fig.data[1].update(yaxis='y2')
fig.data[2].update(yaxis='y2')

# Exporteer de plot naar een standalone HTML-bestand
fig.write_html('/Users/kimgrifhorst/Desktop/final charts 2024/repository/Now_I_Know/Active_MVRV_Price.html')

# Exporteer de plot ook naar een PNG-bestand met de gewenste afmetingen en DPI
fig.write_image('/Users/kimgrifhorst/Desktop/final charts 2024/repository/Now_I_Know/active_mvrv_price.png',
                width=1308, height=725, scale=1)
