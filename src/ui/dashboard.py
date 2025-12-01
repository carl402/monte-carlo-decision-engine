import dash
from dash import dcc, html, Input, Output, State, dash_table, callback_context
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import numpy as np
from ..simulation.monte_carlo_engine import MonteCarloEngine
from ..models.business_scenario import BusinessScenario
from ..utils.statistics import StatisticsCalculator
from ..auth.auth_manager import AuthManager
from .projects_manager import ProjectsManager

class DecisionDashboard:
    """Dashboard interactivo para análisis de decisiones empresariales"""
    
    def __init__(self):
        self.app = dash.Dash(__name__)
        self.engine = MonteCarloEngine(n_simulations=5000)
        try:
            self.auth = AuthManager()
            self.projects_manager = ProjectsManager(self.auth)
            self.auth_enabled = True
        except Exception as e:
            print(f"⚠️ Autenticación deshabilitada: {e}")
            self.auth = None
            self.projects_manager = None
            self.auth_enabled = False
        
        self.current_user = None
        self.setup_layout()
        self.setup_callbacks()
    
    def setup_layout(self):
        """Configura el layout del dashboard"""
        
        self.app.layout = html.Div([
            dcc.Store(id='session-store'),
            html.Div(id='main-content')
        ])
    
    def login_layout(self):
        """Layout de login"""
        return html.Div([
            html.Div([
                html.H1("🎯 Monte Carlo Decision Engine", 
                       style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': 30}),
                html.Div([
                    html.H3("Iniciar Sesión", style={'textAlign': 'center'}),
                    dcc.Input(id='username', placeholder='Usuario', type='text', 
                             style={'width': '100%', 'padding': '10px', 'margin': '10px 0'}),
                    dcc.Input(id='password', placeholder='Contraseña', type='password',
                             style={'width': '100%', 'padding': '10px', 'margin': '10px 0'}),
                    html.Button('Iniciar Sesión', id='login-btn', 
                               style={'width': '100%', 'padding': '10px', 'backgroundColor': '#3498db', 'color': 'white', 'border': 'none'}),
                    html.Div(id='login-message', style={'textAlign': 'center', 'marginTop': '10px'})
                ], style={'maxWidth': '400px', 'margin': '0 auto', 'padding': '20px', 
                         'backgroundColor': '#f8f9fa', 'borderRadius': '10px'})
            ], style={'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center', 
                     'minHeight': '100vh', 'backgroundColor': '#ecf0f1'})
        ])
    
    def main_dashboard_layout(self):
        """Layout principal del dashboard"""
        return html.Div([
            # Header con menú
            html.Div([
                html.H1("🎯 Monte Carlo Decision Engine", 
                       style={'display': 'inline-block', 'color': '#2c3e50', 'margin': 0}),
                html.Div([
                    dcc.Dropdown(
                        id='menu-dropdown',
                        options=[
                            {'label': '📊 Dashboard', 'value': 'dashboard'},
                            {'label': '📁 Mis Proyectos', 'value': 'projects'},
                            {'label': '👥 Gestión Usuarios', 'value': 'users'},
                            {'label': '🚪 Cerrar Sesión', 'value': 'logout'}
                        ],
                        value='dashboard',
                        style={'width': '200px'}
                    )
                ], style={'display': 'inline-block', 'float': 'right'})
            ], style={'padding': '20px', 'backgroundColor': '#34495e', 'color': 'white', 'marginBottom': '20px'}),
            
            # Contenido dinámico
            html.Div(id='page-content')
        ])
    
    def dashboard_content(self):
        """Contenido del dashboard de simulación"""
        return html.Div([
            html.H1("📊 Simulación Monte Carlo", 
                   style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': 30}),
            
            # Panel de configuración
            html.Div([
                html.H3("📊 Configuración del Escenario"),
                html.Div([
                    html.Div([
                        html.Label("Nombre del Escenario:"),
                        dcc.Input(id='scenario-name', value='Lanzamiento Producto A', type='text', style={'width': '100%'})
                    ], className='input-group'),
                    
                    html.Div([
                        html.Label("Inversión Inicial ($):"),
                        dcc.Input(id='initial-investment', value=100000, type='number', style={'width': '100%'})
                    ], className='input-group'),
                    
                    html.Div([
                        html.Label("Ingresos Mensuales - Media ($):"),
                        dcc.Input(id='revenue-mean', value=25000, type='number', style={'width': '100%'})
                    ], className='input-group'),
                    
                    html.Div([
                        html.Label("Ingresos - Desv. Estándar ($):"),
                        dcc.Input(id='revenue-std', value=5000, type='number', style={'width': '100%'})
                    ], className='input-group'),
                ], style={'display': 'flex', 'flexWrap': 'wrap', 'gap': '15px'}),
                
                html.Div([
                    html.Div([
                        html.Label("Costos Mensuales - Media ($):"),
                        dcc.Input(id='cost-mean', value=15000, type='number', style={'width': '100%'})
                    ], className='input-group'),
                    
                    html.Div([
                        html.Label("Costos - Desv. Estándar ($):"),
                        dcc.Input(id='cost-std', value=3000, type='number', style={'width': '100%'})
                    ], className='input-group'),
                    
                    html.Div([
                        html.Label("Tasa de Inflación:"),
                        dcc.Input(id='inflation-rate', value=0.03, type='number', step=0.01, style={'width': '100%'})
                    ], className='input-group'),
                    
                    html.Div([
                        html.Label("Volatilidad del Mercado:"),
                        dcc.Input(id='market-volatility', value=0.15, type='number', step=0.01, style={'width': '100%'})
                    ], className='input-group'),
                ], style={'display': 'flex', 'flexWrap': 'wrap', 'gap': '15px', 'marginTop': '15px'}),
                
                html.Button("🚀 Ejecutar Simulación", id='run-simulation', 
                           style={'marginTop': '20px', 'padding': '10px 20px', 'fontSize': '16px'})
            ], style={'backgroundColor': '#ecf0f1', 'padding': '20px', 'borderRadius': '10px', 'marginBottom': '20px'}),
            
            # Resultados
            html.Div(id='results-container'),
            
        ], style={'maxWidth': '1200px', 'margin': '0 auto', 'padding': '20px'})
    
    def projects_content(self):
        """Contenido de proyectos"""
        if self.current_user:
            return self.projects_manager.projects_content(self.current_user['id'])
        return html.Div("Error: Usuario no autenticado")
    
    def users_content(self):
        """Contenido de usuarios"""
        return self.projects_manager.users_content()
    
    def setup_callbacks(self):
        """Configura los callbacks del dashboard"""
        
        @self.app.callback(
            Output('main-content', 'children'),
            Input('session-store', 'data')
        )
        def display_page(session_data):
            if not self.auth_enabled:
                return self.dashboard_content()  # Modo sin autenticación
            if not session_data:
                return self.login_layout()
            return self.main_dashboard_layout()
        
        @self.app.callback(
            Output('session-store', 'data'),
            Input('login-btn', 'n_clicks'),
            [State('username', 'value'), State('password', 'value')]
        )
        def login(n_clicks, username, password):
            if n_clicks and username and password:
                result = self.auth.login(username, password)
                if result:
                    self.current_user = result['user']
                    return result
            return None
        
        @self.app.callback(
            Output('page-content', 'children'),
            Input('menu-dropdown', 'value')
        )
        def display_content(selected_page):
            if selected_page == 'dashboard':
                return self.dashboard_content()
            elif selected_page == 'projects':
                return self.projects_content()
            elif selected_page == 'users':
                return self.users_content()
            return self.dashboard_content()
        
        @self.app.callback(
            Output('results-container', 'children'),
            Input('run-simulation', 'n_clicks'),
            [State('scenario-name', 'value'),
             State('initial-investment', 'value'),
             State('revenue-mean', 'value'),
             State('revenue-std', 'value'),
             State('cost-mean', 'value'),
             State('cost-std', 'value'),
             State('inflation-rate', 'value'),
             State('market-volatility', 'value')]
        )
        def run_simulation(n_clicks, name, investment, rev_mean, rev_std, 
                          cost_mean, cost_std, inflation, volatility):
            
            if not n_clicks:
                return html.Div("👆 Configure los parámetros y ejecute la simulación", 
                               style={'textAlign': 'center', 'color': '#7f8c8d', 'fontSize': '18px'})
            
            # Crear escenario
            scenario = BusinessScenario(
                name=name,
                initial_investment=investment,
                revenue_mean=rev_mean,
                revenue_std=rev_std,
                cost_mean=cost_mean,
                cost_std=cost_std,
                inflation_rate=inflation,
                market_volatility=volatility
            )
            
            # Ejecutar simulación
            result = self.engine.simulate_scenario(scenario)
            metrics = StatisticsCalculator.calculate_risk_metrics(result)
            
            return self.create_results_layout(result, metrics)
    
    def create_results_layout(self, result, metrics):
        """Crea el layout de resultados"""
        
        return html.Div([
            # Métricas principales
            html.H3("📈 Resultados de la Simulación"),
            html.Div([
                self.create_metric_card("NPV Promedio", f"${metrics['media_npv']:,.0f}", 
                                       "green" if metrics['media_npv'] > 0 else "red"),
                self.create_metric_card("Probabilidad de Éxito", f"{metrics['probabilidad_exito']:.1f}%", 
                                       "green" if metrics['probabilidad_exito'] > 50 else "orange"),
                self.create_metric_card("ROI Promedio", f"{metrics['roi_medio']:.1f}%", 
                                       "green" if metrics['roi_medio'] > 0 else "red"),
                self.create_metric_card("Break-even Promedio", f"{metrics['break_even_medio']:.1f} meses", "blue"),
            ], style={'display': 'flex', 'gap': '15px', 'marginBottom': '20px'}),
            
            # Gráficos
            html.Div([
                html.Div([
                    dcc.Graph(figure=self.create_npv_histogram(result))
                ], style={'width': '50%'}),
                html.Div([
                    dcc.Graph(figure=self.create_risk_metrics_chart(metrics))
                ], style={'width': '50%'}),
            ], style={'display': 'flex', 'gap': '20px', 'marginBottom': '20px'}),
            
            # Tabla de estadísticas detalladas
            html.H4("📊 Estadísticas Detalladas"),
            self.create_statistics_table(metrics)
        ])
    
    def create_metric_card(self, title, value, color):
        """Crea una tarjeta de métrica"""
        return html.Div([
            html.H4(title, style={'margin': '0', 'color': '#2c3e50'}),
            html.H2(value, style={'margin': '10px 0', 'color': color})
        ], style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '8px', 
                 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'textAlign': 'center', 'flex': '1'})
    
    def create_npv_histogram(self, result):
        """Crea histograma de distribución NPV"""
        fig = go.Figure()
        fig.add_trace(go.Histogram(
            x=result.net_present_values,
            nbinsx=50,
            name='Distribución NPV',
            marker_color='rgba(55, 128, 191, 0.7)'
        ))
        
        # Líneas de percentiles
        fig.add_vline(x=result.percentile_5, line_dash="dash", line_color="red", 
                     annotation_text=f"P5: ${result.percentile_5:,.0f}")
        fig.add_vline(x=result.percentile_95, line_dash="dash", line_color="green", 
                     annotation_text=f"P95: ${result.percentile_95:,.0f}")
        
        fig.update_layout(
            title="Distribución de Valor Presente Neto (NPV)",
            xaxis_title="NPV ($)",
            yaxis_title="Frecuencia",
            showlegend=False
        )
        return fig
    
    def create_risk_metrics_chart(self, metrics):
        """Crea gráfico de métricas de riesgo"""
        categories = ['Prob. Éxito', 'ROI > 0%', 'Break-even 6m', 'Break-even 12m']
        values = [
            metrics['probabilidad_exito'],
            metrics['prob_roi_positivo'],
            metrics['prob_break_even_6m'],
            metrics['prob_break_even_12m']
        ]
        
        fig = go.Figure(data=[
            go.Bar(x=categories, y=values, marker_color=['green', 'blue', 'orange', 'purple'])
        ])
        
        fig.update_layout(
            title="Métricas de Probabilidad (%)",
            yaxis_title="Probabilidad (%)",
            yaxis=dict(range=[0, 100])
        )
        return fig
    
    def create_statistics_table(self, metrics):
        """Crea tabla de estadísticas"""
        data = [
            {"Métrica": "NPV Promedio", "Valor": f"${metrics['media_npv']:,.0f}"},
            {"Métrica": "Desviación Estándar", "Valor": f"${metrics['desviacion_std']:,.0f}"},
            {"Métrica": "VaR 95%", "Valor": f"${metrics['var_95']:,.0f}"},
            {"Métrica": "CVaR 95%", "Valor": f"${metrics['cvar_95']:,.0f}"},
            {"Métrica": "Coef. Variación", "Valor": f"{metrics['coeficiente_variacion']:.2f}"},
            {"Métrica": "Asimetría", "Valor": f"{metrics['asimetria']:.2f}"},
            {"Métrica": "Curtosis", "Valor": f"{metrics['curtosis']:.2f}"},
        ]
        
        return dash_table.DataTable(
            data=data,
            columns=[{"name": i, "id": i} for i in data[0].keys()],
            style_cell={'textAlign': 'left', 'padding': '10px'},
            style_header={'backgroundColor': '#3498db', 'color': 'white', 'fontWeight': 'bold'},
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': '#f8f9fa'
                }
            ]
        )
    
    def run_server(self, debug=True, port=8050):
        """Ejecuta el servidor del dashboard"""
        self.app.run(debug=debug, port=port, host='0.0.0.0')