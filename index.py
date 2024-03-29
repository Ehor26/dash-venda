import dash
from dash import html, dcc
from dash.dependencies import Input, Output

import pandas as pd
import numpy as np

import plotly.express as px
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# ============ Ingestão e manipulação de dados =========== 

df_data = pd.read_csv("./assets/supermarket_sales.csv")
df_data["Date"] = pd.to_datetime(df_data["Date"])

# ============ Layout =========== 

app.layout = html.Div(children=[
    dbc.Row([
        dbc.Col([
            dbc.Card([
                html.H2("ESTEVAM", style={"font-family": "Voltaire", "font-size": "50px" }),
                html.Hr(),

                html.H5("Cidades:"),
                dcc.Checklist(
                    options=[
                        {'label': city, 'value': city} for city in df_data["City"].unique()
                    ],
                    value=df_data["City"].unique(),
                    id="check_city",
                    inline=True,
                    inputStyle={"margin-right": "5px", "margin-left": "20px"}
                ),

                html.H5("Variável de análise:", style={"margin-top": "30px"}),
                dcc.RadioItems(
                    options=[
                        {'label': 'Gross Income', 'value': 'gross income'},
                        {'label': 'Rating', 'value': 'Rating'}
                    ],
                    value='gross income',
                    id="main_variable",
                    inline=True,
                    inputStyle={"margin-right": "5px", "margin-left": "20px"}
                ),

            ], style={"height": "95vh", "margin": "5px", "padding": "5px"})
        ], sm=2),

        dbc.Col([
            dbc.Row([
                dbc.Col([dcc.Graph(id="city_fig")], sm=4),
                dbc.Col([dcc.Graph(id="gender_fig")], sm=4),
                dbc.Col([dcc.Graph(id="pay_fig")], sm=4)
            ]),
            dbc.Row([dcc.Graph(id="income_per_date_fig")]),
            dbc.Row([dcc.Graph(id="income_per_product_fig")]),
        ], sm=10)
    ])
])

# ============ Callbacks =========== 
@app.callback(
    [
        Output('city_fig', 'figure'),
        Output('pay_fig', 'figure'),
        Output('gender_fig', 'figure'),
        Output('income_per_date_fig', 'figure'),
        Output('income_per_product_fig', 'figure')
    ],
    [
        Input('check_city', 'value'),
        Input('main_variable', 'value')
    ]
)
def render_graphs(cities, main_variable):
    operation = np.sum if main_variable == "gross income" else np.mean

    df_filtro = df_data[df_data["City"].isin(cities)]

    df_city = df_filtro.groupby(["City"])[main_variable].apply(operation).reset_index()
    df_gender = df_filtro.groupby(["Gender", "City"])[main_variable].apply(operation).reset_index()
    df_payment = df_filtro.groupby("Payment")[main_variable].apply(operation).reset_index()

    df_income_time = df_filtro.groupby("Date")[main_variable].apply(operation).reset_index()
    df_product_income = df_filtro.groupby(["Product line", "City"])[main_variable].apply(operation).reset_index()

    # ======== Gráficos ==============
    fig_city = px.bar(df_city, x="City", y=main_variable)

    fig_payment = px.bar(df_payment, y="Payment", x=main_variable, orientation="h")

    fig_gender = px.bar(df_gender, x="Gender", y=main_variable, color="City", barmode="group")

    fig_product_income = px.bar(df_product_income, x=main_variable, y="Product line",
                                 color="City", orientation="h", barmode="group")

    fig_income_date = px.bar(df_income_time, y=main_variable, x="Date")

    for fig in [fig_city, fig_payment, fig_gender, fig_product_income, fig_income_date]:
        fig.update_layout(margin=dict(l=0, r=0, t=20, b=20), height=200, template="plotly_dark")

    fig_product_income.update_layout(margin=dict(l=0, r=0, t=20, b=10), height=300)

    return fig_city, fig_payment, fig_gender, fig_income_date, fig_product_income

# ============ Run server ===========
if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=80)

