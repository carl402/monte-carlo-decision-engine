import dash
from dash import dcc, html, Input, Output, State, dash_table, callback_context
import plotly.graph_objs as go
import pandas as pd
import numpy as np
from ..simulation.monte_carlo_engine import MonteCarloEngine
from ..models.business_scenario import BusinessScenario
from ..utils.statistics import StatisticsCalculator

class MonteCarloApp:
    def __init__(self):
        self.app = dash.Dash(__name__)
        self.engine = MonteCarloEngine(n_simulations=5000)
        self.current_user = {'id': 1, 'username': 'admin', 'role': 'admin'}
        self.logged_in = False
        self.setup_layout()
        self.setup_callbacks()
    
    def setup_layout(self):
        self.app.layout = html.Div([
            dcc.Store(id='login-state', data=False),
            dcc.Store(id='current-page', data='login'),
            html.Div(id='app-content')
        ])
    
    def login_page(self):
        return html.Div([
            html.Div([
                html.H1("🎯 Monte Carlo Decision Engine", 
                       style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': 40}),
                html.Div([
                    html.H3("Iniciar Sesión", style={'textAlign': 'center', 'marginBottom': 30}),
                    dcc.Input(
                        id='login-username',
                        placeholder='Usuario',
                        type='text',
                        value='admin',
                        style={'width': '100%', 'padding': '12px', 'margin': '10px 0', 'borderRadius': '5px', 'border': '1px solid #ddd'}
                    ),
                    dcc.Input(
                        id='login-password',
                        placeholder='Contraseña',
                        type='password',
                        value='admin123',
                        style={'width': '100%', 'padding': '12px', 'margin': '10px 0', 'borderRadius': '5px', 'border': '1px solid #ddd'}
                    ),
                    html.Button(
                        'Iniciar Sesión',
                        id='login-button',
                        style={
                            'width': '100%', 'padding': '12px', 'backgroundColor': '#3498db',
                            'color': 'white', 'border': 'none', 'borderRadius': '5px',
                            'fontSize': '16px', 'cursor': 'pointer', 'marginTop': '10px'
                        }
                    ),
                    html.Div(id='login-message', style={'textAlign': 'center', 'marginTop': '15px', 'color': 'red'})
                ], style={
                    'maxWidth': '400px', 'margin': '0 auto', 'padding': '40px',
                    'backgroundColor': 'white', 'borderRadius': '10px',
                    'boxShadow': '0 4px 6px rgba(0,0,0,0.1)'
                })
            ], style={
                'minHeight': '100vh', 'backgroundColor': '#ecf0f1',
                'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center'
            })
        ])
    
    def main_layout(self):
        return html.Div([
            # Header
            html.Div([
                html.H1("🎯 Monte Carlo Decision Engine", 
                       style={'display': 'inline-block', 'color': 'white', 'margin': 0}),
                html.Div([
                    dcc.Dropdown(
                        id='main-menu',
                        options=[
                            {'label': '📊 Dashboard', 'value': 'dashboard'},
                            {'label': '📁 Proyectos', 'value': 'projects'},
                            {'label': '🧮 Simulaciones', 'value': 'simulations'},
                            {'label': '📈 Visualizaciones', 'value': 'visualizations'},
                            {'label': '👥 Gestión Usuarios', 'value': 'users'},
                            {'label': '🚪 Cerrar Sesión', 'value': 'logout'}
                        ],
                        value='dashboard',
                        style={'width': '200px', 'color': 'black'}
                    )
                ], style={'display': 'inline-block', 'float': 'right'})
            ], style={
                'padding': '15px 30px', 'backgroundColor': '#2c3e50',
                'marginBottom': '0px', 'overflow': 'hidden'
            }),
            
            # Content
            html.Div(id='page-content', style={'padding': '20px'})
        ])
    
    def dashboard_page(self):
        return html.Div([
            html.H2("📊 Dashboard Principal", style={'color': '#2c3e50', 'marginBottom': 30}),
            
            # Proyectos Recientes
            html.Div([
                html.H3("📁 Proyectos Recientes"),
                html.Div([
                    html.Div([
                        html.H4("Proyecto Alpha"),
                        html.P("Lanzamiento de producto premium"),
                        html.Small("Creado: 2024-01-15")
                    ], className='project-card', style={
                        'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '8px',
                        'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'margin': '10px'
                    }),
                    html.Div([
                        html.H4("Proyecto Beta"),
                        html.P("Expansión mercado local"),
                        html.Small("Creado: 2024-01-10")
                    ], style={
                        'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '8px',
                        'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'margin': '10px'
                    })
                ], style={'display': 'flex', 'flexWrap': 'wrap'})
            ], style={'marginBottom': 30}),
            
            # Buscador
            html.Div([
                html.H3("🔍 Buscar Proyectos"),
                dcc.Input(
                    id='project-search',
                    placeholder='Buscar proyectos...',
                    style={'width': '100%', 'padding': '10px', 'borderRadius': '5px', 'border': '1px solid #ddd'}
                )
            ])
        ])
    
    def projects_page(self):
        return html.Div([
            html.H2("📁 Gestión de Proyectos", style={'color': '#2c3e50'}),
            html.Button(
                "+ Nuevo Proyecto",
                id='new-project-btn',
                style={
                    'padding': '10px 20px', 'backgroundColor': '#27ae60',
                    'color': 'white', 'border': 'none', 'borderRadius': '5px',
                    'marginBottom': '20px', 'cursor': 'pointer'
                }
            ),
            html.Div(id='projects-list', children=[
                html.Div([
                    html.H4("Proyecto Alpha"),
                    html.P("Descripción: Lanzamiento de producto premium"),
                    html.P("Escenarios: 3 | Última simulación: 2024-01-15"),
                    html.Button("Ver Detalles", style={'padding': '5px 15px', 'backgroundColor': '#3498db', 'color': 'white', 'border': 'none', 'borderRadius': '3px'})
                ], style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '8px', 'marginBottom': '15px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'})
            ])
        ])
    
    def simulations_page(self):
        return html.Div([
            html.H2("🧮 Simulaciones Monte Carlo", style={'color': '#2c3e50'}),
            
            # Configuración de Escenario
            html.Div([
                html.H3("📊 Configurar Escenario"),
                html.Div([
                    html.Div([
                        html.Label("Nombre del Escenario:"),
                        dcc.Input(id='scenario-name', value='Nuevo Escenario', type='text', style={'width': '100%', 'padding': '8px'})
                    ], style={'width': '48%', 'display': 'inline-block', 'marginRight': '4%'}),
                    
                    html.Div([
                        html.Label("Inversión Inicial ($):"),
                        dcc.Input(id='initial-investment', value=100000, type='number', style={'width': '100%', 'padding': '8px'})
                    ], style={'width': '48%', 'display': 'inline-block'}),
                ]),
                
                html.Div([
                    html.Div([
                        html.Label("Ingresos Mensuales - Media ($):"),
                        dcc.Input(id='revenue-mean', value=25000, type='number', style={'width': '100%', 'padding': '8px'})
                    ], style={'width': '48%', 'display': 'inline-block', 'marginRight': '4%'}),
                    
                    html.Div([
                        html.Label("Ingresos - Desv. Estándar ($):"),
                        dcc.Input(id='revenue-std', value=5000, type='number', style={'width': '100%', 'padding': '8px'})
                    ], style={'width': '48%', 'display': 'inline-block'}),
                ], style={'marginTop': '15px'}),
                
                html.Button(
                    "🚀 Ejecutar Simulación",
                    id='run-simulation',
                    style={
                        'marginTop': '20px', 'padding': '12px 30px',
                        'backgroundColor': '#e74c3c', 'color': 'white',
                        'border': 'none', 'borderRadius': '5px', 'fontSize': '16px'
                    }
                )
            ], style={'backgroundColor': '#f8f9fa', 'padding': '20px', 'borderRadius': '8px', 'marginBottom': '20px'}),
            
            # Resultados
            html.Div(id='simulation-results')
        ])
    
    def visualizations_page(self):
        return html.Div([
            html.H2("📈 Visualizaciones", style={'color': '#2c3e50'}),
            html.P("Visualizaciones recientes de simulaciones Monte Carlo"),
            html.Div([
                html.Div("Gráfico NPV - Proyecto Alpha", style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '8px', 'margin': '10px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
                html.Div("Análisis de Riesgo - Proyecto Beta", style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '8px', 'margin': '10px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'})
            ])
        ])
    
    def users_page(self):
        return html.Div([
            html.H2("👥 Gestión de Usuarios", style={'color': '#2c3e50'}),
            html.P("Panel de administración de usuarios"),
            html.Button("+ Nuevo Usuario", style={'padding': '10px 20px', 'backgroundColor': '#9b59b6', 'color': 'white', 'border': 'none', 'borderRadius': '5px'})
        ])
    
    def setup_callbacks(self):
        @self.app.callback(
            [Output('login-state', 'data'), Output('login-message', 'children')],
            Input('login-button', 'n_clicks'),
            [State('login-username', 'value'), State('login-password', 'value')]
        )
        def handle_login(n_clicks, username, password):
            if n_clicks and username == 'admin' and password == 'admin123':
                return True, ""
            elif n_clicks:
                return False, "Credenciales incorrectas"
            return False, ""
        
        @self.app.callback(
            Output('app-content', 'children'),
            Input('login-state', 'data')
        )
        def display_app(logged_in):
            if logged_in:
                return self.main_layout()
            return self.login_page()
        
        @self.app.callback(
            Output('page-content', 'children'),
            Input('main-menu', 'value')
        )
        def display_page(selected_page):
            if selected_page == 'dashboard':
                return self.dashboard_page()
            elif selected_page == 'projects':
                return self.projects_page()
            elif selected_page == 'simulations':
                return self.simulations_page()
            elif selected_page == 'visualizations':
                return self.visualizations_page()
            elif selected_page == 'users':
                return self.users_page()
            elif selected_page == 'logout':
                return self.login_page()
            return self.dashboard_page()
        
        @self.app.callback(
            Output('simulation-results', 'children'),
            Input('run-simulation', 'n_clicks'),
            [State('scenario-name', 'value'), State('initial-investment', 'value'),
             State('revenue-mean', 'value'), State('revenue-std', 'value')]
        )
        def run_simulation(n_clicks, name, investment, revenue_mean, revenue_std):
            if not n_clicks:
                return html.Div("👆 Configure los parámetros y ejecute la simulación")
            
            # Crear escenario
            scenario = BusinessScenario(
                name=name or "Escenario Test",
                initial_investment=investment or 100000,
                revenue_mean=revenue_mean or 25000,
                revenue_std=revenue_std or 5000,
                cost_mean=15000,
                cost_std=3000
            )
            
            # Ejecutar simulación
            result = self.engine.simulate_scenario(scenario)
            metrics = StatisticsCalculator.calculate_risk_metrics(result)
            
            return html.Div([
                html.H3("📈 Resultados de la Simulación"),
                html.Div([
                    html.Div([
                        html.H4(f"${metrics['media_npv']:,.0f}"),
                        html.P("NPV Promedio")
                    ], style={'backgroundColor': '#2ecc71', 'color': 'white', 'padding': '20px', 'borderRadius': '8px', 'textAlign': 'center', 'margin': '10px'}),
                    
                    html.Div([
                        html.H4(f"{metrics['probabilidad_exito']:.1f}%"),
                        html.P("Probabilidad de Éxito")
                    ], style={'backgroundColor': '#3498db', 'color': 'white', 'padding': '20px', 'borderRadius': '8px', 'textAlign': 'center', 'margin': '10px'}),
                    
                    html.Div([
                        html.H4(f"{metrics['roi_medio']:.1f}%"),
                        html.P("ROI Promedio")
                    ], style={'backgroundColor': '#e74c3c', 'color': 'white', 'padding': '20px', 'borderRadius': '8px', 'textAlign': 'center', 'margin': '10px'})
                ], style={'display': 'flex', 'justifyContent': 'space-around'})
            ])
    
    def run_server(self, debug=False, port=8050):
        self.app.run(debug=debug, port=port, host='0.0.0.0')