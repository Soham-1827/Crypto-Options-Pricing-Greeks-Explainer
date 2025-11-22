import dash
from dash import html, dcc, Input, Output, State, callback
import plotly.graph_objects as go
import pandas as pd
import datetime
from src.workflow import create_workflow

# Initialize LangGraph
workflow_app = create_workflow()

# Initialize Dash App
app = dash.Dash(__name__, title="Crypto Options Terminal")
server = app.server

# Styles
DARK_BG = "#1e1e1e"
TEXT_COLOR = "#00ff00" # Terminal Green
CARD_BG = "#2d2d2d"

style_container = {
    "backgroundColor": DARK_BG,
    "color": TEXT_COLOR,
    "fontFamily": "Consolas, monospace",
    "minHeight": "100vh",
    "padding": "20px"
}

style_card = {
    "backgroundColor": CARD_BG,
    "padding": "15px",
    "borderRadius": "5px",
    "marginBottom": "20px",
    "border": "1px solid #444"
}

style_input = {
    "backgroundColor": "#333",
    "color": "white",
    "border": "1px solid #555",
    "padding": "5px",
    "width": "100%"
}

app.layout = html.Div(style=style_container, children=[
    html.H1("ANTIGRAVITY // CRYPTO OPTIONS SIMULATOR", style={"textAlign": "center", "borderBottom": "2px solid #00ff00", "paddingBottom": "10px"}),
    
    html.Div(style={"display": "grid", "gridTemplateColumns": "1fr 2fr", "gap": "20px"}, children=[
        # Left Column: Controls
        html.Div(style=style_card, children=[
            html.H3("PARAMETERS"),
            
            html.Label("Asset (CoinGecko ID)"),
            dcc.Input(id="input-coin", type="text", value="bitcoin", style=style_input),
            html.Br(), html.Br(),
            
            html.Label("Target Date (Days from now)"),
            dcc.Slider(id="input-days", min=7, max=365, step=7, value=30, 
                       marks={7: '1W', 30: '1M', 90: '3M', 180: '6M', 365: '1Y'}),
            html.Br(), html.Br(),
            
            html.Label("Strike Price ($)"),
            dcc.Input(id="input-strike", type="number", value=100000, style=style_input),
            html.Br(), html.Br(),
            
            html.Label("Option Type"),
            dcc.RadioItems(id="input-type", options=[
                {'label': 'Call', 'value': 'call'},
                {'label': 'Put', 'value': 'put'}
            ], value='call', labelStyle={'display': 'block'}),
            html.Br(),
            
            html.Button("RUN SIMULATION", id="btn-run", n_clicks=0, 
                        style={"backgroundColor": "#00ff00", "color": "black", "fontWeight": "bold", "width": "100%", "padding": "10px", "cursor": "pointer"})
        ]),
        
        # Right Column: Output
        html.Div(children=[
            # Top Row: Stats
            html.Div(style={"display": "grid", "gridTemplateColumns": "repeat(4, 1fr)", "gap": "10px"}, children=[
                html.Div(style=style_card, children=[html.H4("PRICE"), html.Div(id="out-price", children="-")]),
                html.Div(style=style_card, children=[html.H4("DELTA"), html.Div(id="out-delta", children="-")]),
                html.Div(style=style_card, children=[html.H4("GAMMA"), html.Div(id="out-gamma", children="-")]),
                html.Div(style=style_card, children=[html.H4("THETA"), html.Div(id="out-theta", children="-")])
            ]),
            
            # Middle Row: Explanation
            html.Div(style=style_card, children=[
                html.H3("TEACHER'S ANALYSIS"),
                dcc.Markdown(id="out-explanation", children="Run simulation to see analysis...")
            ]),
            
            # Bottom Row: Chart
            html.Div(style=style_card, children=[
                dcc.Graph(id="out-chart")
            ])
        ])
    ])
])

@callback(
    [Output("out-price", "children"),
     Output("out-delta", "children"),
     Output("out-gamma", "children"),
     Output("out-theta", "children"),
     Output("out-explanation", "children"),
     Output("out-chart", "figure")],
    [Input("btn-run", "n_clicks")],
    [State("input-coin", "value"),
     State("input-days", "value"),
     State("input-strike", "value"),
     State("input-type", "value")]
)
def run_simulation(n_clicks, coin_id, days, strike, option_type):
    if n_clicks == 0:
        return "-", "-", "-", "-", "Ready to simulate.", {}
    
    # Run LangGraph Workflow
    inputs = {
        "coin_id": coin_id,
        "target_date_days": days,
        "strike_price": float(strike),
        "option_type": option_type
    }
    
    try:
        result = workflow_app.invoke(inputs)
        
        res = result["results"]
        explanation = result["explanation"]
        current_price = result["current_price"]
        
        # Format outputs
        price_fmt = f"${res['price']:.2f}"
        delta_fmt = f"{res['delta']:.4f}"
        gamma_fmt = f"{res['gamma']:.4f}"
        theta_fmt = f"{res['theta']:.4f}"
        
        # Create a simple chart (Payoff diagram)
        # Spot price range +/- 20%
        spots = list(range(int(current_price * 0.8), int(current_price * 1.2), int(current_price * 0.01)))
        payoffs = []
        for s in spots:
            if option_type == "call":
                payoffs.append(max(s - strike, 0))
            else:
                payoffs.append(max(strike - s, 0))
                
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=spots, y=payoffs, mode='lines', name='Payoff at Expiry', line=dict(color='#00ff00')))
        fig.add_vline(x=current_price, line_dash="dash", line_color="white", annotation_text="Current Price")
        fig.add_vline(x=strike, line_dash="dash", line_color="red", annotation_text="Strike Price")
        
        fig.update_layout(
            title=f"Option Payoff at Expiry (Strike: ${strike})",
            paper_bgcolor=CARD_BG,
            plot_bgcolor=CARD_BG,
            font=dict(color="white"),
            xaxis_title="Spot Price",
            yaxis_title="Payoff"
        )
        
        return price_fmt, delta_fmt, gamma_fmt, theta_fmt, explanation, fig
        
    except Exception as e:
        return "Err", "Err", "Err", "Err", f"Simulation failed: {str(e)}", {}

if __name__ == '__main__':
    app.run_server(debug=True)
