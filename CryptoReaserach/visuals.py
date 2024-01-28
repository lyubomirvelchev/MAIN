import pandas as pd
import plotly.graph_objects as go

df = pd.read_csv('btc1D.csv')
df['date'] = pd.to_datetime(df['time'], unit='s').dt.date

fig = go.Figure(data=[go.Candlestick(
    x=df['date'],
    open=df['open'],
    high=df['high'],
    low=df['low'],
    close=df['close']
)])

fig.update_layout(
    yaxis=dict(
        type='log',
        title='Logarithmic Scale for Price'
    ),
    xaxis=dict(
        title='Date'
    )
)

fig.show()
