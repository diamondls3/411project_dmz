import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.express as px
from db.mysql_utils import *
from db.mongodb_utils import *
# from db.neo4j_utils import *
import pandas as pd
from dash import dash_table
import plotly.graph_objects as go
from plotly.graph_objects import Layout
from plotly.validator_cache import ValidatorCache


app = dash.Dash(__name__)

min_year = 2010
max_year = 2021

#app layout
app.layout = html.Div([
    #bar chart
    html.Div([
            html.H4('Top 8 popular keywords for selected years:'),
            html.P("Year:"),
            dcc.RangeSlider(
                                id='year-slider',
                                min=min_year,
                                max=max_year,
                                value=[min_year, min_year],  
                                marks={str(year): str(year) for year in range(min_year, max_year+1)},
                                step=1
                            ),
            dcc.Graph(id="top_keywords_for_selected_years"),
        ], style={'marginLeft': '10px', 'width': '50%','display': 'inline-block'}),
    #bubble chart
    html.Div([
            html.H4('Top 10 Professors with highest KRC'),   
            html.P("Keywords:"),
            dcc.Dropdown(id='keyword-dropdown',
                options=[keyword['name'] for keyword in get_keyword_names()],
                value='data mining',
                clearable=False
            ),
            dcc.Graph(id="bubble-chart")
    ], style={'marginLeft': '10px', 'width': '47%','display': 'inline-block'}),
    #sunburst chart
    html.Div([
            html.H4('Professor top3 research interest and related publications'),   
            html.P("Professors:"),
            dcc.Dropdown(id='professor-dropdown',
                options=[professor['name'] for professor in get_professor_names()],
                value='A. Ali Yanik',
                clearable=False
            ),
            dcc.Graph(id="sunburst-chart"),
    ], style={'marginLeft': '10px', 'width': '50%','display': 'inline-block'}),
    #scatter plot
    html.Div([
            html.H4('Professor all publications and its most related keyword'),   
            html.P("Professors:"),
            dcc.Dropdown(id='professor-dropdown2',
                options=[professor['name'] for professor in get_professor_names()],
                value='A. Ali Yanik',
                clearable=False
            ),
            dcc.Graph(id="scatter-plot"),
    ], style={'marginLeft': '10px', 'width': '47%','display': 'inline-block'}),
], style={'width': '100%', 'display': 'inline-block'})

#bubble chart callback
@app.callback(
        Output('bubble-chart', 'figure'),
        Input('keyword-dropdown', 'value')
        )
def generate_bubble_chart(keyword):
    df = pd.DataFrame(get_top_researchers_by_KRC(keyword))

    fig = px.scatter(df, x="pub_cnt", y="cit_sum",
                    size="KRC", color="professor",
                    hover_name="professor", hover_data=["university"],
                    log_x=False, size_max=60)
    return fig

#sunburst chart callback
@app.callback(
        Output('sunburst-chart', 'figure'),
        Input('professor-dropdown', 'value')
        )
def generate_bubble_chart(professor):
    df = pd.DataFrame(get_professor_research_interest(professor))

    fig = px.sunburst(df, path=['research_interest', 'year','venue_short'], values='score',
                      hover_data=["venue","publication_title"])
    
    return fig

#top_keywords_for_selected_years
@app.callback(
		Output('top_keywords_for_selected_years', 'figure'),
		[Input('year-slider', 'value')]
)
def update_top_keywords_for_selected_years(selected_years):
		start_year, end_year = selected_years
		df = pd.DataFrame(get_top_keywords_for_selected_years(start_year, end_year))
		fig = px.bar(df, x='_id', y='pub_cnt', text_auto=True)
		return fig

# scatter_plot
@app.callback(
		Output('scatter-plot', 'figure'),
		Input('professor-dropdown2', 'value')
)
def generate_scatter_plot(professor):
    df = pd.DataFrame(get_professor_publications(professor))
    fig = px.scatter(df, y="num_citations", x="keyword_score", 
                     color="most_related_publication_keyword",
                     hover_data=["publications"])
    return fig

if __name__ == '__main__':
    app.run_server(debug=True, dev_tools_hot_reload=False)

# app = dash.Dash(__name__)

# app.layout = html.Div([
# 	        html.H4('Professor all publications'),   
#             html.P("Professors:"),
#             dcc.Dropdown(id='professor-dropdown',
#                 options=[professor['name'] for professor in get_professor_names()],
#                 value='A. Ali Yanik',
#                 clearable=False
#             ),
#             dcc.Graph(id="scatter-plot"),
# ])

# # scatter_plot
# @app.callback(
# 		Output('scatter-plot', 'figure'),
# 		Input('professor-dropdown', 'value')
# )
# def generate_scatter_plot(professor):
#     df = pd.DataFrame(get_professor_publications(professor))
#     fig = px.scatter(df, y="num_citations", x="keyword_score", 
#                      color="most_related_publication_keyword")
#     return fig

# if __name__ == '__main__':
# 	app.run_server(debug=True, dev_tools_hot_reload=False)