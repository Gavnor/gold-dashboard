import os
import pandas as pd
import dash
from dash import dcc, html, dash_table
import plotly.express as px

# CSV file path (adjust path if needed in Railway deployment)
LOG_FILE = 'data/trade_log.csv'

# Initialize Dash app
app = dash.Dash(__name__)
app.title = "Gold Trading Bot Monitor"

# Load trade data
def load_data():
    if not os.path.exists(LOG_FILE):
        return pd.DataFrame(columns=[
            "time", "current_price", "predicted_price", "contract", "stake", "balance"
        ])
    
    df = pd.read_csv(LOG_FILE, names=[
        "time", "current_price", "predicted_price", "contract", "stake", "balance"
    ])
    
    # Translate CALL/PUT → BUY/SELL
    df['direction'] = df['contract'].map({'CALL': 'BUY', 'PUT': 'SELL'})
    df['time'] = pd.to_datetime(df['time'])
    df = df.sort_values('time')
    return df

# Layout
app.layout = html.Div([
    html.H1("📊 Gold Trading Bot Dashboard", style={'textAlign': 'center'}),

    dcc.Interval(id='update_interval', interval=60*1000, n_intervals=0),

    html.Div(id='stats', style={'padding': '20px'}),

    dash_table.DataTable(
        id='table',
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'center'},
        page_size=20
    ),

    dcc.Graph(id='prediction_scatter')
])

# Callbacks
@app.callback(
    [dash.dependencies.Output('stats', 'children'),
     dash.dependencies.Output('table', 'data'),
     dash.dependencies.Output('table', 'columns'),
     dash.dependencies.Output('prediction_scatter', 'figure')],
    [dash.dependencies.Input('update_interval', 'n_intervals')]
)
def update_dashboard(n):
    df = load_data()

    if df.empty:
        return html.Div("No trades logged yet."), [], [], {}

    total_trades = len(df)
    avg_stake = df['stake'].mean()
    avg_balance = df['balance'].mean()

    stats = html.Div([
        html.H3(f"Total Trades: {total_trades}"),
        html.H4(f"Average Stake: ${avg_stake:.2f}"),
        html.H4(f"Average Account Balance: ${avg_balance:.2f}")
    ])

    columns = [{"name": i, "id": i} for i in df.columns]
    data = df.to_dict('records')

    scatter = px.scatter(
        df, x="time", y="current_price", color="direction",
        hover_data=["predicted_price", "stake", "balance"],
        title="Trade Entries Over Time"
    )

    return stats, data, columns, scatter

# Run server
if __name__ == '__main__':
    app.run_server(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
