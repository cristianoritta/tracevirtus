from flask import Flask
from flask_cors import CORS
import os
import secrets
from dotenv import load_dotenv



app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.config['ENV'] = 'development'
app.config['DEBUG'] = True
CORS(app)

# import declared routes
from Lib.Functions.template_tags import format_cpf_cnpj, moeda
import routes

load_dotenv()

# *
# ********************
if __name__ == "__main__":

    # Verifica a variável de ambiente para definir o modo de execução
    modo_desenvolvimento = os.getenv('DEV', 'False').lower() in ('true', '1', 't')

    app.jinja_env.filters['cpf_cnpj'] = format_cpf_cnpj
    app.jinja_env.filters['moeda'] = moeda

    if modo_desenvolvimento:
        # Inicia o APP com Flask em modo debug
        app.run(port=8088, debug=True)
    else:
        from flaskwebgui import FlaskUI
        
        # Inicia o APP com FlaskUI
        FlaskUI(app=app,
                fullscreen=True,
                server="flask",
                port=8088).run()


#### https://brasilapi.com.br/api/cnpj/v1/{cnpj}