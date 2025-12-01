#!/usr/bin/env python3
"""
Punto de entrada alternativo para Heroku
"""
import os
from dotenv import load_dotenv
load_dotenv()

# Importar después de cargar variables
from src.ui.new_dashboard import MonteCarloApp

if __name__ == "__main__":
    app = MonteCarloApp()
    port = int(os.environ.get('PORT', 8050))
    app.run_server(debug=False, port=port)