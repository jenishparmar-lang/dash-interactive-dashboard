import dash
from dash import dcc, html, Input, Output, State
import plotly.express as px
import pandas as pd

# Sample data (replace with pd.read_csv("data/yourfile.csv") as needed)
df = px.data.tips()

# Helper lists
days = sorted(df['day'].unique())
sexes = sorted(df['sex'].unique())
smokers = sorted(df['smoker'].unique())
min_bill, max_bill = df['total_bill'].min(), df['total_bill'].max()

app = dash.Dash(__name__)
server = app.server  # expose the Flask server for gunicorn / deployment

app.layout = html.Div(style={'fontFamily': 'Arial, sans-serif', 'margin': '20px'}, children=[
    html.H2("Interactive Dashboard — Demo (tips dataset)"),
    html.Div(style={'display': 'flex', 'gap': '20px'}, children=[
        html.Div(style={'flex': '0 0 300px'}, children=[
            html.Label("Days (multi-select)"),
            dcc.Dropdown(id='day-dropdown', options=[{'label': d, 'value': d} for d in days],
                         value=days, multi=True),
            html.Br(),
            html.Label("Sex"),
            dcc.Checklist(id='sex-checklist', options=[{'label': s, 'value': s} for s in sexes],
                          value=sexes, inline=True),
            html.Br(),
            html.Label("Smoker"),
            dcc.Checklist(id='smoker-checklist', options=[{'label': s, 'value': s} for s in smokers],
                          value=smokers, inline=True),
            html.Br(),
            html.Label("Total bill range"),
            dcc.RangeSlider(id='bill-range', min=min_bill, max=max_bill,
                            step=0.5, value=[min_bill, max_bill],
                            tooltip={"placement": "bottom", "always_visible": False}),
            html.Br(),
            html.Button("Clear bar selection", id='clear-btn'),
            html.Div(style={'marginTop': '8px', 'color': '#666', 'fontSize': '12px'},
                     children="Click a bar in the left chart to filter the right chart by that day.")
        ]),
        html.Div(style={'flex': '1 1 auto'}, children=[
            dcc.Graph(id='bar-chart'),
            dcc.Graph(id='scatter-chart'),
            html.H4("Selected rows (table)"),
            html.Div(id='table-container')
        ])
    ]),
    # store clicked day (from bar click)
    dcc.Store(id='clicked-day-store', data=None)
])


def filter_df(values):
    days_sel, sexes_sel, smokers_sel, bill_range, clicked_day = values
    if not days_sel:
        days_sel = []
    dff = df[df['day'].isin(days_sel)]
    dff = dff[dff['sex'].isin(sexes_sel)]
    dff = dff[dff['smoker'].isin(smokers_sel)]
    dff = dff[(dff['total_bill'] >= bill_range[0]) & (dff['total_bill'] <= bill_range[1])]
    if clicked_day:
        dff = dff[dff['day'] == clicked_day]
    return dff


@app.callback(
    Output('clicked-day-store', 'data'),
    Input('bar-chart', 'clickData'),
    Input('clear-btn', 'n_clicks'),
    prevent_initial_call=True
)
def capture_bar_click(clickData, clear_clicks):
    # If clear button pressed, clear selection
    ctx = dash.callback_context
    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if triggered_id == 'clear-btn':
        return None
    if clickData and 'points' in clickData and clickData['points']:
        # bar x (day) is in point['x']
        return clickData['points'][0].get('x')
    return None


@app.callback(
    Output('bar-chart', 'figure'),
    Output('scatter-chart', 'figure'),
    Output('table-container', 'children'),
    Input('day-dropdown', 'value'),
    Input('sex-checklist', 'value'),
    Input('smoker-checklist', 'value'),
    Input('bill-range', 'value'),
    Input('clicked-day-store', 'data'),
)
def update_charts(days_sel, sexes_sel, smokers_sel, bill_range, clicked_day):
    # master filtering (bar shows counts for current filters excluding clicked_day focus)
    master_df = df[df['day'].isin(days_sel)]
    master_df = master_df[master_df['sex'].isin(sexes_sel)]
    master_df = master_df[master_df['smoker'].isin(smokers_sel)]
    master_df = master_df[(master_df['total_bill'] >= bill_range[0]) & (master_df['total_bill'] <= bill_range[1])]

    bar_fig = px.histogram(master_df, x='day', title='Rows by day (click a bar to focus)',
                           labels={'count': 'rows', 'day': 'Day'})
    bar_fig.update_layout(clickmode='event+select')

    # Detail df: apply clicked_day filter if present
    detail_df = filter_df((days_sel, sexes_sel, smokers_sel, bill_range, clicked_day))

    scatter_title = 'Total bill vs Tip' + (f" — focused on {clicked_day}" if clicked_day else "")
    scatter_fig = px.scatter(detail_df, x='total_bill', y='tip', color='sex', hover_data=['day', 'smoker', 'size'],
                             title=scatter_title, labels={'total_bill': 'Total bill', 'tip': 'Tip'})

    # small table
    if detail_df.empty:
        table_html = html.Div("No rows match the filters", style={'padding': '8px'})
    else:
        # show first 10 rows
        table_html = html.Table(
            [html.Tr([html.Th(c) for c in detail_df.columns[:6]])] +
            [html.Tr([html.Td(str(detail_df.iloc[i][c])) for c in detail_df.columns[:6]])
             for i in range(min(10, len(detail_df)))]
        )

    return bar_fig, scatter_fig, table_html


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)
