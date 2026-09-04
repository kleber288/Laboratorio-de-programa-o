"""Fábrica da aplicação Biblioteca Viva."""

from flask import Flask, redirect, render_template, request, session, url_for

from config import Config
from database import init_app as init_database


def create_app(test_config=None):
    """Cria e configura uma instância isolada da aplicação Flask."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)

    from controllers.auth_controller import auth_bp
    from controllers.emprestimo_controller import emprestimo_bp
    from controllers.livro_controller import livro_bp
    from controllers.main_controller import main_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(livro_bp)
    app.register_blueprint(emprestimo_bp)

    @app.before_request
    def exigir_login():
        rotas_publicas = {"auth.login", "auth.cadastro", "static"}
        if request.endpoint not in rotas_publicas and "usuario_id" not in session:
            return redirect(url_for("auth.login", proxima=request.path))

    @app.errorhandler(404)
    def pagina_nao_encontrada(_erro):
        return render_template("404.html"), 404

    init_database(app)
    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
