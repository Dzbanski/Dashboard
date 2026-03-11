import pandas as pd
import dash
import dash_auth
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
from db import db
import tab1
import tab2
import tab3

df = db()
df.merge()

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
USERNAME_PASSWORD = [['user','pass']]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)

auth = dash_auth.BasicAuth(app,USERNAME_PASSWORD)

app.layout = html.Div([html.Div([dcc.Tabs(id='tabs',value='tab-1',children=[
                            dcc.Tab(label='Sprzedaż globalna',value='tab-1'),
                            dcc.Tab(label='Produkty',value='tab-2'),
                            dcc.Tab(label='Kanały sprzedaży',value='tab-3')
                            ]),
                            html.Div(id='tabs-content')
                    ],style={'width':'80%','margin':'auto'})],
                    style={'height':'100%'})

@app.callback(Output('tabs-content','children'),[Input('tabs','value')])
def render_content(tab):

    if tab == 'tab-1':
        return tab1.render_tab(df.merged)
    elif tab == 'tab-2':
        return tab2.render_tab(df.merged)
    elif tab == 'tab-3':
        return tab3.render_tab(df.merged)
    
# tab1 callbacks
@app.callback(Output('bar-sales','figure'),
    [Input('sales-range','start_date'),Input('sales-range','end_date')])

def tab1_bar_sales(start_date,end_date):

    truncated = df.merged_df(start_date, end_date)
    grouped = truncated[truncated['total_amt']>0].groupby([pd.Grouper(key='tran_date',freq='M'),'Store_type'])['total_amt'].sum().round(2).unstack()

    traces = []
    for col in grouped.columns:
        traces.append(go.Bar(x=grouped.index,y=grouped[col],name=col,hoverinfo='text',
        hovertext=[f'{y/1e3:.2f}k' for y in grouped[col].values]))

    data = traces
    fig = go.Figure(data=data,layout=go.Layout(title='Przychody',barmode='stack',legend=dict(x=0,y=-0.5)))

    return fig

@app.callback(Output('choropleth-sales','figure'),
            [Input('sales-range','start_date'),Input('sales-range','end_date')])
def tab1_choropleth_sales(start_date,end_date):

    truncated = df.merged_df(start_date, end_date)
    grouped = truncated[truncated['total_amt']>0].groupby('country')['total_amt'].sum().round(2)

    trace0 = go.Choropleth(colorscale='Viridis',reversescale=True,
                            locations=grouped.index,locationmode='country names',
                            z = grouped.values, colorbar=dict(title='Sales'))
    data = [trace0]
    fig = go.Figure(data=data,layout=go.Layout(title='Mapa',geo=dict(showframe=False,projection={'type':'natural earth'})))

    return fig

# tab2 callbacks
@app.callback(Output('barh-prod-subcat','figure'),
            [Input('prod_dropdown','value')])
def tab2_barh_prod_subcat(chosen_cat):

    grouped = df.merged[(df.merged['total_amt']>0)&(df.merged['prod_cat']==chosen_cat)].pivot_table(index='prod_subcat',columns='Gender',values='total_amt',aggfunc='sum').assign(_sum=lambda x: x['F']+x['M']).sort_values(by='_sum').round(2)

    traces = []
    for col in ['F','M']:
        traces.append(go.Bar(x=grouped[col],y=grouped.index,orientation='h',name=col))

    data = traces
    fig = go.Figure(data=data,layout=go.Layout(barmode='stack',margin={'t':20,}))
    return fig



# tab3 callbacks
@app.callback(Output("weekday-storetype", "figure"),
              [Input("sales-range", "start_date"),
               Input("sales-range", "end_date")])

def weekday_sales(start_date, end_date):

    dff = df.merged_df(start_date, end_date)

    dff["weekday"] = dff["tran_date"].dt.day_name()

    order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]

    grouped = (
        dff.groupby(["weekday","Store_type"])["total_amt"]
        .sum()
        .unstack()
        .reindex(order)
    )

    fig = go.Figure()

    for col in grouped.columns:
        fig.add_bar(x=grouped.index, y=grouped[col], name=col)

    fig.update_layout(
        title="Sprzedaż wg dni tygodnia i kanału",
        barmode="group"
    )

    return fig

@app.callback(Output("customers-storetype", "figure"),
              [Input("sales-range", "start_date"),
               Input("sales-range", "end_date")])
def customers_profile(start_date, end_date):

    dff = df.merged_df(start_date, end_date)

    dff["DOB"] = pd.to_datetime(dff["DOB"], errors="coerce")
    dff["age"] = (dff["tran_date"] - dff["DOB"]).dt.days / 365

    grouped = dff.groupby("Store_type").agg(
        avg_spend=("total_amt", "mean"),
        avg_age=("age", "mean")
    ).round(2)

    fig = go.Figure()

    fig.add_bar(
        x=grouped.index,
        y=grouped["avg_spend"],
        name="Średnia wartość zakupu"
    )

    fig.add_scatter(
        x=grouped.index,
        y=grouped["avg_age"],
        name="Średni wiek",
        yaxis="y2",
        mode="lines+markers"
    )

    fig.update_layout(
        title="Profil klientów wg kanału",
        yaxis=dict(title="Średnia wartość"),
        yaxis2=dict(title="Wiek", overlaying="y", side="right")
    )

    return fig

if __name__ == '__main__':

    app.run(debug=True)



