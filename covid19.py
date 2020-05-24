import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import pandas as pd

covid19 = pd.read_csv("data/covid19.csv")
cols = ['Tanggal', 'Provinsi', 'Kasus_Terkonfirmasi_Akumulatif', 'Kasus_Sembuh_Akumulatif', 'Kasus_Meninggal_Akumulatif', 'Kasus_Aktif_Akumulatif']

covid19 = covid19[cols]
covid19.columns = ['tanggal', 'provinsi', 'konfirmasi', 'sembuh', 'meninggal', 'aktif']
covid19['sembuh'] = covid19['konfirmasi'] - covid19['meninggal'] - covid19['aktif']

covid19['tanggal'] = pd.to_datetime(covid19['tanggal'])
covid19['tanggal'] = covid19['tanggal'].dt.date

latest = covid19.groupby("tanggal").sum().reset_index()
case = latest.loc[latest['tanggal'] == max(latest['tanggal']),:].reset_index()

konfirmasi = case['konfirmasi'][0]
sembuh = case['sembuh'][0]
meninggal = case['meninggal'][0]
aktif = case['aktif'][0]

case_options = [{'label':'Semua', 'value':'all'}]
for case in covid19.columns[2:5]:
    case_options.append({'label':str(case.title()), 'value':str(case)})

provinces = covid19.loc[covid19['provinsi'] != "Indonesia","provinsi"].sort_values().unique()
province_options = [{'label':province, 'value':province} for province in provinces]

colors = ["#142850", "#27496d", "#00909e", "#dae1e7"]

app = dash.Dash(__name__)
server = app.server

app.layout = html.Div([
    #Header
    html.Div([
        html.H3("COVID-19 Dash Project"),
        html.H5("Indonesia"),
        html.H6("@farelyue")
    ],id = "header",className = "header"),

    #Left Side
    html.Div([
        html.H3(children = "Indonesia", className = "kasus"),
        html.Label(children = "Jenis Kasus:", className = "label"),
        dcc.Dropdown(
            id = 'select-case',
            options = case_options,
            value = 'all',
            style = {'width':'70%'}
        ),
        html.Div([
            html.Div([
                html.H5("Konfirmasi"),
                html.H3(str(konfirmasi))
            ],id = "confirm", className = "confirm"),
        
            html.Div([
                html.H5("Meninggal"),
                html.H3(str(meninggal))
            ],id = "death", className = "death"),

            html.Div([
                html.H5("Sembuh"),
                html.H3(str(sembuh))
            ],id = "recover", className = "recover"),

            html.Div([
                html.H5("Aktif"),
                html.H3(str(aktif))
            ],id = "active", className = "active")
        ],id = "left-container", className = "left-container"),

        html.Div([
            dcc.Graph(id = "ts-indo")
        ], id = "graph-1", className = "pretty-graph"),

        html.Div([
            dcc.Graph(id = "ts-diff-indo")
        ], id = "graph-2", className = "pretty-graph"),

        html.Div([
            dcc.Graph(id = "barplot-indo")
        ], id = "graph-3", className = "pretty-graph")

    ],id = "left-side", className = "left-side cf"),

    #Right-side
    html.Div([
        html.H3(children = "Provinsi", className = "kasus"),
        html.Label(children = "Provinsi:", className = "label"),
        dcc.Dropdown(
            id = "select-province",
            options = province_options,
            value = "DKI Jakarta",
            style = {'width':'70%'}
        ),

        html.Div([
            html.Div([
                html.H5("Konfirmasi"),
                html.H3(id = "confirm-r")
            ], className = "confirm"),
        
            html.Div([
                html.H5("Meninggal"),
                html.H3(id = "death-r")
            ], className = "death"),

            html.Div([
                html.H5("Sembuh"),
                html.H3(id = "recover-r")
            ], className = "recover"),

            html.Div([
                html.H5("Aktif"),
                html.H3(id = "active-r")
            ], className = "active")
        ],id = "right-container", className = "right-container"),

        html.Div([
            dcc.Graph(id = "ts-province")
        ], id = "graph-4", className = "pretty-graph"),

        html.Div([
            dcc.Graph(id = "ts-diff-province")
        ],id = "graph-5", className = "pretty-graph"),

        html.Div([
            dcc.Graph(id = "ts-percentage-province")
        ], id = "graph-6", className = "pretty-graph")

    ],id = "right-side", className = "right-side cf")
],id="mainContainer")

@app.callback(
    Output('ts-indo', 'figure'),
    [Input('select-case', 'value')]
)

def indo_ts(case_name):
    latest = covid19.groupby('tanggal').sum().reset_index()
    cases = ["konfirmasi","meninggal","sembuh"]
    if case_name == 'all':
        traces = []
        for case in cases:
            trace = go.Scatter(
                x = latest['tanggal'],
                y = latest.loc[:,case],
                mode = "lines",
                name = case.title()
            )
            traces.append(trace)
        
        layout = go.Layout(
            title = {'text':'Banyak Kasus Covid-19 di Indonesia',
                    'x':0.5,
                    'y':0.9,
                    'xanchor':'center',
                    'yanchor':'top',
                    'font':{'size':18}},
            xaxis = {'title':'Tanggal'},
            yaxis = {'title':'Banyak Kasus'},
            hovermode = "closest",
            template = "plotly_dark"
        )

        fig = go.Figure(data = traces, layout = layout)
        return fig
    
    else:
        if case_name == "konfirmasi":
            traces = [go.Scatter(
                x = latest['tanggal'],
                y = latest.loc[:,case_name],
                mode = "lines",
                name = case_name.title(),
                line = {'color':'#2B37B0'},
                type = "scatter",
            )]
        elif case_name == "meninggal":
            traces = [go.Scatter(
                x = latest['tanggal'],
                y = latest.loc[:,case_name],
                mode = "lines",
                name = case_name.title(),
                line = {'color':'#FF2520'},
                type = "scatter"
            )]
        else:
            traces = [go.Scatter(
                x = latest['tanggal'],
                y = latest.loc[:,case_name],
                mode = "lines",
                name = case_name.title(),
                line = {'color':'#17B65C'},
                type = "scatter"
            )]
        
        layout = go.Layout(
            title = {'text':"Banyak Pasien {} di Indonesia".format(case_name.title()),
                    'x':0.5,
                    'y':0.9,
                    'xanchor':'center',
                    'yanchor':'top',
                    'font':{'size':18}},
            xaxis = {'title':'Tanggal'},
            yaxis = {'title':'Banyak Kasus'},
            hovermode = "closest",
            template = "plotly_dark"
        )
        
        fig = go.Figure(data = traces, layout = layout)
        return fig

@app.callback(
    Output('ts-diff-indo', 'figure'),
    [Input('select-case', 'value')]
)

def indo_diff(case):
    global covid19
    indo = covid19.groupby('tanggal').sum().reset_index()
    indo = indo.sort_values('tanggal')

    if case == "all":

        def difference(kasus):
            diff = []
            for ind in range(len(indo[kasus])):
                if ind == 0:
                    diff.append(0)
                else:
                    res = indo[kasus].values[ind] - indo[kasus].values[ind-1]
                    diff.append(res)
            return diff
        
        indo["diff_konfirmasi"] = difference("konfirmasi")
        indo["diff_meninggal"] = difference("meninggal")
        indo["diff_sembuh"] = difference("sembuh")

        cases = ["diff_konfirmasi","diff_meninggal","diff_sembuh"]
        cols = ["#2B37B0", "#FF2520", "#17B65C"]

        traces = [go.Scatter(
            x = indo["tanggal"],
            y = indo[kasus],
            mode = "lines",
            name = kasus.title(),
            marker = {'color':cols[ind]}
        ) for ind,kasus in enumerate(cases)]

        layout = go.Layout(
            title = {'text':"Banyak Pertambahan Kasus Covid-19 di Indonesia",
                    'x':0.5,
                    'y':0.9,
                    'xanchor':'center',
                    'yanchor':'top',
                    'font':{'size':18}},
            xaxis = {'title':'Tanggal'},
            yaxis = {'title':'Banyak Pertambahan'},
            hovermode = "closest",
            template = "plotly_dark"
        )

        fig = go.Figure(data = traces, layout = layout)
        return fig

    else:
        diff = []
        for ind in range(len(indo[case])):
            if ind == 0:
                diff.append(0)
            else:
                res = indo[case].values[ind] - indo[case].values[ind-1]
                diff.append(res)
        
        if case == "konfirmasi":
            cols = "#2B37B0"
            kasus = "diff_konfirmasi"
        elif case == "meninggal":
            cols = "#FF2520"
            kasus = "diff_meninggal"
        else:
            cols = "#17B65C"
            kasus = "sembuh"

        traces = [go.Scatter(
            x = indo['tanggal'],
            y = indo[kasus],
            mode = "lines",
            name = case.title(),
            marker = {'color':cols}
        )]

        layout = go.Layout(
            title = {'text':"Pertambahan Pasien {} di Indonesia".format(case.title()),
                    'x':0.5,
                    'y':0.9,
                    'xanchor':'center',
                    'yanchor':'top',
                    'font':{'size':18}},
            xaxis = {'title':'Tanggal'},
            yaxis = {'title':'Banyak Pertambahan'},
            hovermode = "closest",
            template = "plotly_dark"
        )

        fig = go.Figure(data = traces, layout = layout)
        return fig

@app.callback(
    Output('barplot-indo', 'figure'),
    [Input('select-case', 'value')]
)

def indo_barplot(case):
    covid_max = covid19.loc[covid19['tanggal'] == max(covid19['tanggal']),:]
    latest_sorted = covid_max.sort_values('konfirmasi', ascending = False)
    top_10 = latest_sorted[:10]
    if case == "all":
        traces = []
        case_name = ['konfirmasi', 'meninggal', 'sembuh']
        colors = ["#2B37B0", "#FF2520", "#17B65C"]
        for ind,case in enumerate(covid19.columns[2:5]):
            trace = go.Bar(
                x = top_10['provinsi'],
                y = top_10['konfirmasi'],
                name = case_name[ind].title(),
                marker = {'color':colors[ind]}
            )
            traces.append(trace)
        
        layout = go.Layout(
            title = {'text':"Banyak Kasus Covid19 tiap Provinsi",
                    'x':0.5,
                    'y':0.9,
                    'xanchor':'center',
                    'yanchor':'top',
                    'font':{'size':18}},
            barmode = "stack",
            hovermode = "closest",
            template = "plotly_dark"
        )

        fig = go.Figure(data = traces, layout = layout)
        return fig

    else:
        traces = [go.Bar(
            x = top_10['provinsi'],
            y = top_10[case],
            name = case.title()
        )]

        layout = go.Layout(
            title = {'text':"Banyak Pasien {} tiap Provinsi".format(case.title()),
                    'x':0.5,
                    'y':0.9,
                    'xanchor':'center',
                    'yanchor':'top',
                    'font':{'size':18}},
            hovermode = "closest",
            template = "plotly_dark"
        )

        fig = go.Figure(data = traces, layout = layout)

        if case == "konfirmasi":
            fig.update_traces(marker = {'color':'#2B37B0'})
        elif case == "meninggal":
            fig.update_traces(marker = {'color':'#FF2520'})
        else:
            fig.update_traces(marker = {'color':'#17B65C'})

        return fig

@app.callback(
    Output('confirm-r','children'),
    [Input('select-province', 'value')]
)

def confirm_province(province):
    prov = covid19.loc[covid19['provinsi'] == province,:]
    prov = prov.sort_values('tanggal')

    prov_date = prov.groupby('tanggal').sum().reset_index()
    update = prov_date.loc[prov_date['tanggal'] == max(prov_date['tanggal']),:]

    konfirmasi = update['konfirmasi'].values[0]
    return str(konfirmasi)

@app.callback(
    Output('death-r','children'),
    [Input('select-province', 'value')]
)

def death_province(province):
    prov = covid19.loc[covid19['provinsi'] == province,:]
    prov = prov.sort_values('tanggal')

    prov_date = prov.groupby('tanggal').sum().reset_index()
    update = prov_date.loc[prov_date['tanggal'] == max(prov_date['tanggal']),:]

    meninggal = update['meninggal'].values[0]
    return str(meninggal)

@app.callback(
    Output('recover-r','children'),
    [Input('select-province', 'value')]
)

def recover_province(province):
    prov = covid19.loc[covid19['provinsi'] == province,:]
    prov = prov.sort_values('tanggal')

    prov_date = prov.groupby('tanggal').sum().reset_index()
    update = prov_date.loc[prov_date['tanggal'] == max(prov_date['tanggal']),:]

    sembuh = update['sembuh'].values[0]
    return str(sembuh)

@app.callback(
    Output('active-r','children'),
    [Input('select-province', 'value')]
)

def active_province(province):
    prov = covid19.loc[covid19['provinsi'] == province,:]
    prov = prov.sort_values('tanggal')

    prov_date = prov.groupby('tanggal').sum().reset_index()
    update = prov_date.loc[prov_date['tanggal'] == max(prov_date['tanggal']),:]

    aktif = update['aktif'].values[0]
    return str(aktif)

@app.callback(
    Output('ts-province', 'figure'),
    [Input('select-province', 'value')]
)

def province_ts(province):
    prov = covid19.loc[covid19['provinsi'] == province, :]
    prov = prov.sort_values('tanggal')
    cases = ["konfirmasi","meninggal", "sembuh"]
    cols = ["#2B37B0", "#FF2520", "#17B65C"]
    
    traces = [go.Scatter(
        x = prov['tanggal'],
        y = prov[kasus],
        mode = "lines",
        name = kasus.title(),
        marker = {"color":cols[ind]}
    ) for ind,kasus in enumerate(cases)]

    layout = go.Layout(
        title = {'text':"Banyak Kasus Covid-19 di Provinsi {}".format(province),
                'x':0.5,
                'y':0.9,
                'xanchor':'center',
                'yanchor':'top',
                'font':{'size':18}},
        xaxis = {'title':'Tanggal'},
        yaxis = {'title':'Banyak Kasus'},
        hovermode = "closest",
        template = "plotly_dark"
    )

    fig = go.Figure(data = traces, layout = layout)
    return fig

@app.callback(
    Output("ts-diff-province", "figure"),
    [Input("select-province", "value")]
)

def province_diff(province):
    prov = covid19.loc[covid19["provinsi"] == province, :]
    prov = prov.sort_values('tanggal')
    
    def difference(kasus):
        diff = []
        for ind in range(len(prov[kasus])):
            if ind == 0:
                diff.append(0)
            else:
                res = prov[kasus].values[ind] - prov[kasus].values[ind-1]
                diff.append(res)
        return diff
    
    prov["diff_konfirmasi"] = difference("konfirmasi")
    prov["diff_meninggal"] = difference("meninggal")
    prov["diff_sembuh"] = difference("sembuh")

    cases = ["diff_konfirmasi","diff_meninggal","diff_sembuh"]
    cols = ["#2B37B0", "#FF2520", "#17B65C"]

    traces = [go.Scatter(
        x = prov["tanggal"],
        y = prov[kasus],
        mode = "lines",
        name = kasus.title(),
        marker = {'color':cols[ind]}
    ) for ind,kasus in enumerate(cases)]

    layout = go.Layout(
        title = {'text':"Pertambahan Pasien di Provinsi {}".format(province),
                'x':0.5,
                'y':0.9,
                'xanchor':'center',
                'yanchor':'top',
                'font':{'size':18}},
        xaxis = {'title':'Tanggal'},
        yaxis = {'title':'Banyak Pertambahan'},
        hovermode = "closest",
        template = "plotly_dark"
    )

    fig = go.Figure(data = traces, layout = layout)
    return fig

@app.callback(
    Output('ts-percentage-province','figure'),
    [Input('select-province', 'value')]
)

def province_percentage(province):
    prov = covid19.loc[covid19['provinsi'] == province, :]
    prov = prov.sort_values('tanggal')

    prov["perc_meninggal"] = 100 * prov["meninggal"]/prov["konfirmasi"]
    prov["perc_sembuh"] = 100 * prov["sembuh"]/prov["konfirmasi"]

    cases = ["perc_meninggal", "perc_sembuh"]
    names = ["Persentase Meninggal", "Persentase Sembuh"]
    cols = ["#FF2520", "#17B65C"]
    
    traces = [go.Scatter(
        x = prov["tanggal"],
        y = prov[kasus],
        mode = "lines",
        name = names[ind],
        marker = {'color':cols[ind]}
    ) for ind,kasus in enumerate(cases)]

    layout = go.Layout(
        title = {'text':"Persentase Kasus di Provinsi {}".format(province),
                'x':0.5,
                'y':0.9,
                'xanchor':'center',
                'yanchor':'top',
                'font':{'size':18}},
        xaxis = {'title':'Tanggal'},
        yaxis = {'title':'Persentase'},
        hovermode = "closest",
        template = "plotly_dark"
    )

    fig = go.Figure(data = traces, layout = layout)
    return fig

if __name__ == "__main__":
    app.run_server(debug = False)