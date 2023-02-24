import biomapy as bp
import networkx as nx
import pandas as pd
import numpy as np
import warnings
from gprofiler import GProfiler
import igraph as ig 


warnings.filterwarnings('ignore')
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input,Output
import dash_cytoscape as cyto
import argparse

parser=argparse.ArgumentParser(description='Functional Enrichment viualization tool')
parser.add_argument('-l','--list',help='list of genes separator must be specified')
parser.add_argument('-id','--id',help='format of the id')
parser.add_argument('-s','--sep',help='type of separator')
args=parser.parse_args()




def LoadFile():
    Interactome=pd.read_csv('data/hippie_interactome.sif',header=None,sep=' ',usecols=[0,2])
    Interactome.columns=['source','target']
    # if ((args.sep=='space') & (args.id=='symbol')):
    Interactome.source=bp.gene_mapping_many(Interactome.source.tolist(),'entrez','symbol')
    Interactome.target=bp.gene_mapping_many(Interactome.target.tolist(),'entrez','symbol')
    with open(args.list,'r') as file:
        ListOfGenes=file.read()
    ListOfGenes=ListOfGenes.split(' ')
    Interactome.dropna(inplace=True)
    return Interactome,list(filter(None,ListOfGenes))



def EnrichmentAnalisys(ListOfGenes):
    ## PERFORM ENRICHMENT ANALISYS##
    gp = GProfiler(return_dataframe=True)
    Enrichment=gp.profile(organism='hsapiens',
                query=ListOfGenes,
                significance_threshold_method='bonferroni',
                no_iea=True,
                no_evidences=False)
    return Enrichment



def BuildGraph(SubGraph,EnrichmentDataframe):
    ## implement the possibility to make different layouts and to add attributes to the edges and to the nodes
    EnrichmentDataframe.dropna(subset = 'p_value',inplace = True)
    ig_subgraph=ig.Graph.from_networkx(SubGraph)
    pos_= dict(zip([v['_nx_name'] for v in ig_subgraph.vs],[coord for coord in ig_subgraph.layout_auto()]))
    app=dash.Dash(__name__)
    cyto_node_data=list(
                        zip(
                                pos_.keys(),
                                [coord[0] for coord in pos_.values()],
                                [coord[1] for coord in pos_.values()]
                                
                                
                            )
                    )
    nodes = [
    {
        'data': {'id': str(_id), 'label':str(_id)},
        'position': {'x': 120*x, 'y': 120*y}
    }
    for _id, x, y, in cyto_node_data
    ]



    edges = [
        {'data': {'source': source, 'target': target}}
        for source, target in SubGraph.edges()
        ]

    elements = nodes + edges




    default_stylesheet = [
        {
            'selector': 'node',
            'style': {
                'background-color': '#F5CEC5',
                'border-color':'black',
                'border-width':'1',
                'label': 'data(label)',
                'width':'60',
                'height':'60'
            }
        },
        {
            'selector': 'edge',
            'style': {
                'line-color': 'red',
                'width':'1'
            }
        }
    ]

    app.layout=html.Div([
                        html.Header(html.H1(['Function enrichment analysis topology visualization'],
                        style={'textAlign':'center','paddingBottom':'50px','border':'2px solid','borderRadius':'5px'})),

                        html.Main([html.Div([html.Label('P-value Slider'),
                                            dcc.Slider(id='pvalue_slider',
                                                    min=round(-np.log10(EnrichmentDataframe['p_value'].max())),
                                                    max=round(-np.log10(EnrichmentDataframe['p_value'].min())),
                                                    value=round(-np.log10(EnrichmentDataframe['p_value'].max())),
                                                    marks=dict(list(zip(set(sorted([round(el) for el in -np.log10(EnrichmentDataframe.p_value.tolist())])),
                                                    [{} for value in set([round(el) for el in -np.log10(EnrichmentDataframe.p_value.tolist())])]))),
                                                        step=None),
                                                
                                                html.Div(id='updatemode-output-container', style={'marginTop': 20}),
                                                
                                                html.Br(style={'lineHeight':'4'}),
                                                html.Label('Sources'),
                                                dcc.RadioItems(id='sources',
                                                                labelStyle={'display': 'flex'}
                                                                ),
                                                html.Br(style={'lineHeight':'4'}), 
                                                html.Label('Function'),
                                                dcc.Dropdown(id='function_dropdown'),
                                                html.P(id='cytoscape-mouseoverNodeData-output')
                                                


                                                
                                                
                                            ],
                                            style={'width':'20%','display':'inline-block','float':'left','paddingTop':'20px','paddingLeft':'50px'}
                                        ),
                                
                                
                                
                                html.Div([cyto.Cytoscape(id='cytoscape_network',
                                                        layout={'name': 'preset'},
                                                        style={'width': '100%', 'height': '800px'},
                                                        stylesheet=default_stylesheet,
                                                        elements=elements,
                                                        autoRefreshLayout=True
                                                        )
                                            
                                            ],
                                style={'width':'75%','float':'right','position':'relative','top':'20px'}
                                        
                                        )])
                        
                        ])





    @app.callback(Output('updatemode-output-container', 'children'),
                Input('pvalue_slider', 'value'))
    def display_value(value):
        return '-log10(P_Value): %s' %value  

    @app.callback(
        Output('sources', 'options'),
        Input('pvalue_slider', 'value'))
    def set_sources(selected_pvalue):
        return [{'label': i, 'value': i} for i in set(EnrichmentDataframe[-np.log10(EnrichmentDataframe.p_value)>=selected_pvalue].source.tolist())]


    @app.callback(Output('function_dropdown', 'options'),
                Input('pvalue_slider', 'value'),
                Input('sources', 'value'))
    def set_functions(p_value,source):
        return [{'label': i, 'value': i} for i in set(EnrichmentDataframe[(-np.log10(EnrichmentDataframe.p_value)>=p_value)&(EnrichmentDataframe.source==source)].name.tolist())]


    @app.callback(Output('cytoscape_network', 'stylesheet'),
                Input('sources', 'value'),
                Input('function_dropdown', 'value'))



    def update_network(fsource,ffunction):
        """Filter the functions in the dataset"""
        try:
            filt_enrich=EnrichmentDataframe[(EnrichmentDataframe.name==ffunction)&(EnrichmentDataframe.source==fsource)].intersections.values[0]

            new_stylesheet=[{
                                'selector':"[id='%s']"%ele ,
                                'style': {
                                    'background-color': 'black',
                                    'line-color': 'black'
                                }
                                } for ele in filt_enrich]
        
            return default_stylesheet+new_stylesheet
        except:
            return default_stylesheet
    

    
    
    app.run_server(debug=True)




def Main():
    EdgeFile,Lof=LoadFile()
    HippieNet=nx.from_pandas_edgelist(EdgeFile)
    SubG=HippieNet.subgraph(Lof)
    Enrichment= EnrichmentAnalisys(Lof)
    BuildGraph(SubG,Enrichment)


if __name__=='__main__':
    Main()
        
