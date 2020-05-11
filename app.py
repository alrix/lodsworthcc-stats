# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import requests
import os
import logging
import plotly.graph_objects as go

# Setup Logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
# add the handler to the root logger
logging.getLogger().addHandler(console)

# Minimum innings for batting
min_bat = 5

# Minimum overs for bowling
min_bowl = 25

# Minimum no of boundaries
min_boundaries = 2

api_uri = os.environ['API_URI']
batting_json = api_uri + "?discipline=batting"
bowling_json = api_uri + "?discipline=bowling"
fielding_json = api_uri + "?discipline=fielding"

# Dataframes
global_bat_df = pd.read_json(
    requests.get(batting_json).content,
    orient='columns')
global_bowl_df = pd.read_json(
    requests.get(bowling_json).content,
    orient='columns')
global_field_df = pd.read_json(
    requests.get(fielding_json).content,
    orient='columns')

# Innings dataframe
innings = global_bat_df[['name', 'score', 'innings']].groupby(
    'name').sum().sort_values(by=['score'], ascending=False)
names = innings[innings['innings'] >= min_bat].index
scores = []
for name in names:
    scores.append(global_bat_df[['name', 'score']]
                  [global_bat_df['name'] == name]['score'].values)
# Total runs
total_runs = global_bat_df[['name', 'score']].groupby(
    ['name']).sum().sort_values(by=['score'], ascending=False)

# Individual batting
ind_bat_df = global_bat_df[['name', 'score', 'not_out',
                            'innings', 'retired']].groupby('name').sum()
ind_bat_df = ind_bat_df[ind_bat_df['innings'] >= min_bat]
ind_bat_df['average'] = ind_bat_df['score'] / (
    ind_bat_df['innings'] - ind_bat_df['not_out'] - ind_bat_df['retired'])
ind_bat_df = ind_bat_df.sort_values(by=['average'], ascending=False)

# Ducks
ducks_df = global_bat_df.query('score == 0 and not_out == 0 and retired == 0')[
                               ['name', 'innings']].groupby('name').sum().sort_values(by='innings', ascending=False)

# Individual batting - highest score
top_scores = global_bat_df[['name', 'score']].groupby(
    'name').max().sort_values(by='score', ascending=False)

# Boundaries
boundaries = global_bat_df[['name', 'fours', 'sixes']].groupby(
    'name').sum().sort_values(by='fours', ascending=False)
boundaries = boundaries[boundaries['fours'] >= min_boundaries ]

# Bowling averages
bowling_averages = global_bowl_df.groupby('name').sum()
bowling_averages['economy'] = bowling_averages['runs'] / (
    ((bowling_averages['overs'] * 6) + bowling_averages['balls']) / 6)
bowling_averages['average'] = bowling_averages['runs'] / bowling_averages['wickets']
bowling_average_df = bowling_averages[bowling_averages['overs'] >= min_bowl].sort_values(
    by='average')
bowling_economy_df = bowling_averages.sort_values(by='economy')

# Fielding
fielding = global_field_df.groupby('name').sum(
).sort_values(by=['catches'], ascending=False)

# Charts
batting_averages = go.Figure()
batting_averages.add_trace(go.Bar(x=ind_bat_df.index,
                                  y=ind_bat_df['average'],
                                  name='Batting average'
                                  ))
batting_averages.update_layout(
    title='Batting averages (min ' + str(min_bat) + ' innings)',
    yaxis=dict(
        autorange=True,
        showgrid=True,
        zeroline=True,
        dtick=5,
        gridcolor='rgb(255, 255, 255)',
        gridwidth=1,
        zerolinecolor='rgb(255, 255, 255)',
        zerolinewidth=2,
    ),
    margin=dict(
        l=40,
        r=30,
        b=80,
        t=100,
    ),
    paper_bgcolor='rgb(243, 243, 243)',
    plot_bgcolor='rgb(243, 243, 243)',
    showlegend=False
)


total_runs_chart = go.Figure()
total_runs_chart.add_trace(go.Bar(x=total_runs.index,
                                  y=total_runs.score,
                                  name='Total Runs'
                                  ))
total_runs_chart.update_layout(
    title='Total runs',
    yaxis=dict(
        autorange=True,
        showgrid=True,
        zeroline=True,
        dtick=25,
        gridcolor='rgb(255, 255, 255)',
        gridwidth=1,
        zerolinecolor='rgb(255, 255, 255)',
        zerolinewidth=2,
    ),
    margin=dict(
        l=40,
        r=30,
        b=80,
        t=100,
    ),
    paper_bgcolor='rgb(243, 243, 243)',
    plot_bgcolor='rgb(243, 243, 243)',
    showlegend=False
)

top_scores_chart = go.Figure()
top_scores_chart.add_trace(go.Bar(x=top_scores.index,
                                  y=top_scores.score,
                                  name='Highest score'
                                  ))
top_scores_chart.update_layout(
    title='Highest score',
    yaxis=dict(
        autorange=True,
        showgrid=True,
        zeroline=True,
        dtick=25,
        gridcolor='rgb(255, 255, 255)',
        gridwidth=1,
        zerolinecolor='rgb(255, 255, 255)',
        zerolinewidth=2,
    ),
    margin=dict(
        l=40,
        r=30,
        b=80,
        t=100,
    ),
    paper_bgcolor='rgb(243, 243, 243)',
    plot_bgcolor='rgb(243, 243, 243)',
    showlegend=False
)

boundaries_chart = go.Figure(data=[
    go.Bar(x=boundaries.index, y=boundaries.fours, name='Fours'),
    go.Bar(x=boundaries.index, y=boundaries.sixes, name='Sixes')])
boundaries_chart.update_layout(
    barmode='group',
    title='Boundaries',
    yaxis=dict(
        autorange=True,
        showgrid=True,
        zeroline=True,
        dtick=5,
        gridcolor='rgb(255, 255, 255)',
        gridwidth=1,
        zerolinecolor='rgb(255, 255, 255)',
        zerolinewidth=2,
    ),
    margin=dict(
        l=40,
        r=30,
        b=80,
        t=100,
    ),
    paper_bgcolor='rgb(243, 243, 243)',
    plot_bgcolor='rgb(243, 243, 243)',
    showlegend=True
)

ind_bat_box_chart = go.Figure()
for xd, yd in zip(names, scores):
    ind_bat_box_chart.add_trace(go.Box(
            y=yd,
            name=xd,
            boxpoints='all',
            jitter=0.5,
            whiskerwidth=0.2,
            boxmean=True,
            marker_size=2,
            line_width=1)
        )
ind_bat_box_chart.update_layout(
    title='Runs scored (min ' + str(min_bat) + ' innings)',
    yaxis=dict(
        autorange=True,
        showgrid=True,
        zeroline=True,
        dtick=5,
        gridcolor='rgb(255, 255, 255)',
        gridwidth=1,
        zerolinecolor='rgb(255, 255, 255)',
        zerolinewidth=2,
    ),
    margin=dict(
        l=40,
        r=30,
        b=80,
        t=100,
    ),
    paper_bgcolor='rgb(243, 243, 243)',
    plot_bgcolor='rgb(243, 243, 243)',
    showlegend=False
)

ducks = go.Figure()
ducks.add_trace(go.Bar(x=ducks_df.index,
                       y=ducks_df['innings'],
                       name='Ducks'
                       ))
ducks.update_layout(
    title='Ducks',
    yaxis=dict(
        autorange=True,
        showgrid=True,
        zeroline=True,
        dtick=1,
        gridcolor='rgb(255, 255, 255)',
        gridwidth=1,
        zerolinecolor='rgb(255, 255, 255)',
        zerolinewidth=2,
    ),
    margin=dict(
        l=40,
        r=30,
        b=80,
        t=100,
    ),
    paper_bgcolor='rgb(243, 243, 243)',
    plot_bgcolor='rgb(243, 243, 243)',
    showlegend=False
)

bowling_averages = go.Figure()
bowling_averages.add_trace(go.Bar(x=bowling_average_df.index,
                                  y=bowling_average_df['average'],
                                  name='Bowling average'
                                  ))
bowling_averages.update_layout(
    title='Bowling averages (min ' + str(min_bowl) + ' overs)',
    yaxis=dict(
        autorange=True,
        showgrid=True,
        zeroline=True,
        dtick=10,
        gridcolor='rgb(255, 255, 255)',
        gridwidth=1,
        zerolinecolor='rgb(255, 255, 255)',
        zerolinewidth=2,
    ),
    margin=dict(
        l=40,
        r=30,
        b=80,
        t=100,
    ),
    paper_bgcolor='rgb(243, 243, 243)',
    plot_bgcolor='rgb(243, 243, 243)',
    showlegend=False
)

bowling_economy = go.Figure()
bowling_economy.add_trace(go.Bar(x=bowling_economy_df.index,
                                 y=bowling_economy_df['economy'],
                                 name='Bowling economy'
                                 ))
bowling_economy.update_layout(
    title='Bowling Economy',
    yaxis=dict(
        autorange=True,
        showgrid=True,
        zeroline=True,
        dtick=1,
        gridcolor='rgb(255, 255, 255)',
        gridwidth=1,
        zerolinecolor='rgb(255, 255, 255)',
        zerolinewidth=2,
    ),
    margin=dict(
        l=40,
        r=30,
        b=80,
        t=100,
    ),
    paper_bgcolor='rgb(243, 243, 243)',
    plot_bgcolor='rgb(243, 243, 243)',
    showlegend=False
)

fielding_chart = go.Figure(data=[
    go.Bar(x=fielding.index, y=fielding.catches, name='Catches'),
    go.Bar(x=fielding.index, y=fielding.run_outs, name='Run Outs')])
fielding_chart.update_layout(
    barmode='stack',
    title='Fielding',
    yaxis=dict(
        autorange=True,
        showgrid=True,
        zeroline=True,
        dtick=2,
        gridcolor='rgb(255, 255, 255)',
        gridwidth=1,
        zerolinecolor='rgb(255, 255, 255)',
        zerolinewidth=2,
    ),
    margin=dict(
        l=40,
        r=30,
        b=80,
        t=100,
    ),
    paper_bgcolor='rgb(243, 243, 243)',
    plot_bgcolor='rgb(243, 243, 243)',
    showlegend=True
)

# Main Dash Layout
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

colors = {
    'background': '#E2E6EB',
    'text': '#05336B'
}

app.layout = html.Div(
    style={'backgroundColor': colors['background']},
    children=[
        html.H1(
            children='Lodsworth Cricket Club Stats',
            style={
                'textAlign': 'center',
                'color': colors['text']
                }
            ),

        html.Div(
            children='Stats for the 2019 Season.',
            style={
                'textAlign': 'center',
                'color': colors['text']
                }
            ),

        dcc.Graph(figure=batting_averages),
        dcc.Graph(figure=total_runs_chart),
        dcc.Graph(figure=top_scores_chart),
        dcc.Graph(figure=ind_bat_box_chart),
        dcc.Graph(figure=boundaries_chart),
        dcc.Graph(figure=ducks),
        dcc.Graph(figure=bowling_averages),
        dcc.Graph(figure=bowling_economy),
        dcc.Graph(figure=fielding_chart)
        ])

if __name__ == '__main__':
    app.run_server(debug=True)
