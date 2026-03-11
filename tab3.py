from dash import dcc, html

def render_tab(df):

    layout = html.Div([html.H1('Kanały sprzedaży',style={'text-align':'center'}),
                        html.Div([dcc.DatePickerRange(id='sales-range',
                        start_date=df['tran_date'].min(),
                        end_date=df['tran_date'].max(),
                        display_format='YYYY-MM-DD')],style={'width':'100%','text-align':'center'}),
                        dcc.Graph(id="weekday-storetype"),
                        html.H4("Profil klientów wg kanału"),
                        dcc.Graph(id="customers-storetype")
                        ])

    return layout
