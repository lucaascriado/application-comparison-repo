from http.server import BaseHTTPRequestHandler
from db.dbOperations import select_user, select_all_users
import json
import datetime
from pybars import Compiler
import os
import jwt
import http.cookies

def datetime_converter(o):
    if isinstance(o, datetime.datetime):
        return o.isoformat()

class GetRoutes(BaseHTTPRequestHandler):

    def do_GET(self):
        routes = {
            '/login': self.render_login,
            '/register': self.render_register,
            '/home': self.render_home,
            '/404': self.render_404,
        }
        if self.path in routes:
            routes[self.path]()
        else:
            self.render_404()

    def render_home(self):
        try:
            # Verifica se o token JWT está presente nos cookies
            if 'Cookie' in self.headers:
                cookies = http.cookies.SimpleCookie(self.headers['Cookie'])
                if 'jwt_token' in cookies:
                    token = cookies['jwt_token'].value
                    try:
                        # Decodifica o token JWT
                        decoded_token = jwt.decode(token, os.getenv('JWT_SECRET'), algorithms=['HS256'])
                        # Se o token for válido, permite o acesso à página home
                        if decoded_token.get('name_user'):
                            user_data = select_all_users()
                            self.send_response(200)
                            self.send_header('Content-type', 'application/json')
                            self.end_headers()
                            self.wfile.write(json.dumps(user_data, default=datetime_converter).encode())
                        else:
                            # Token inválido
                            self.send_error_response(401, "Unauthorized: Invalid token")
                    except jwt.ExpiredSignatureError:
                        # Token expirado
                        self.send_error_response(401, "Unauthorized: Token expired")
                    except jwt.InvalidTokenError:
                        # Token inválido
                        self.send_error_response(401, "Unauthorized: Invalid token")
                else:
                    # Nenhum token JWT presente nos cookies
                    self.send_error_response(401, "Unauthorized: Missing token")
            else:
                # Nenhum cookie presente na requisição
                self.send_error_response(401, "Unauthorized: No cookies")
        except Exception as e:
            self.send_error_response(500, "Server Error")

    def render_404(self):
        self.send_error_response(404, "Rota nao encontrada.")

    def send_error_response(self, code, message):
        self.send_error(code, message)

    def render_login(self):
        compiler = Compiler()

        with open(os.path.join('templates', 'login.hbs'), 'r') as file:
            source = file.read()
        template = compiler.compile(source)
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(template({}).encode())

    def render_register(self):
        compiler = Compiler()

        # Lendo o conteúdo do arquivo style.css
        with open(os.path.join('public', 'style.css'), 'r') as file:
            css_source = file.read()

        with open(os.path.join('templates', 'register.hbs'), 'r') as file:
            html_source = file.read()

        html_template = compiler.compile(html_source)

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        self.wfile.write(html_template({ 'css_content': css_source }).encode())