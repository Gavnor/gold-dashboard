import dash
from dash import dcc, html
import pandas as pd
import plotly.express as px
from flask import send_file

app = dash.Dash(__name__)
server = app.server

CSV_PATH = "data/trade_log.csv"

def load_data():
    try:
        df = pd.read_csv(CSV_PATH, names=[
            "timestamp", "type", "current_price",
            "predicted_price", "stake", "contract"
        ])
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        return df
    except:
        return pd.DataFrame()

df = load_data()
fig = px.line(df, x="timestamp", y=["current_price", "predicted_price"],
              title="Gold Bot: Predicted vs Actual")

app.layout = html.Div([
    html.H1("📊 Gold LSTM Bot Dashboard"),
    html.A("📥 Download Log CSV", href="/download", target="_blank",
           style={"fontSize": 18, "marginBottom": "20px", "display": "inline-block"}),
    dcc.Graph(figure=fig),
    html.H3("Trade Log Table"),
    html.Table(
        [html.Tr([html.Th(col) for col in df.columns])] +
        [html.Tr([html.Td(df.iloc[i][col]) for col in df.columns])
         for i in range(len(df))]
    )
])

@server.route("/download")
def download_csv():
    return send_file(CSV_PATH, mimetype="text/csv",
                     as_attachment=True, download_name="trade_log.csv")

if __name__ == "__main__":
    app.run_server(debug=True, port=8080)
