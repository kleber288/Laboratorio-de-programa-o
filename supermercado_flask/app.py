"""Ponto de entrada e fábrica da aplicação web Mercado Fácil.

Este módulo pertence à camada de inicialização: cria o objeto Flask, carrega a
configuração, conecta os Blueprints (Controllers), registra recursos globais e
inicializa o banco. Os Models são alcançados indiretamente pelos Controllers e
os templates representam a camada View da organização MVC usada no projeto.
"""

# Flask é a classe principal; os demais objetos são proxies ligados à
# requisição atual. Eles só devem ser usados enquanto houver contexto Flask.
from flask import Flask, redirect, render_template, request, session, url_for
from config import Config
from database import init_app as init_database
# O projeto referencia ``utils`` como módulo utilitário. A distribuição atual
# contém ``util.py``; essa divergência preexistente é mantida para não alterar o
# comportamento solicitado e poderá aparecer como erro de importação nos testes.
from utils import formatar_moeda


def create_app(test_config=None):
    """Cria e configura uma instância isolada da aplicação Flask.

    Parâmetros:
        test_config: Mapeamento opcional que sobrescreve a configuração padrão,
            usado principalmente pelas fixtures para apontar a um banco
            temporário e ativar ``TESTING``.

    Retorno:
        A aplicação Flask pronta para receber requisições.

    Efeitos colaterais:
        Registra Blueprints, filtro Jinja, middleware, tratador de erro e hooks
        do SQLite; também inicializa o schema dentro de um contexto da aplicação.

    Possíveis erros:
        Imports ausentes, configuração inválida ou falhas SQL durante
        ``init_database`` impedem a criação. A função se relaciona com
        ``config.py``, ``database.py``, ``controllers/`` e ``util.py``.
    """
    # ``instance_relative_config=True`` faz o Flask reconhecer a pasta
    # ``instance`` como local apropriado para dados mutáveis, como o SQLite.
    app = Flask(__name__, instance_relative_config=True)
    # A classe centraliza valores que podem ser trocados por variáveis de ambiente.
    app.config.from_object(Config)

    # Nos testes, o dicionário fornecido tem precedência sobre ``Config``.
    if test_config:
        app.config.update(test_config)

    # Imports locais evitam carregar Controllers antes de existir uma aplicação
    # configurada e ajudam a reduzir dependências circulares durante a montagem.
    from controllers.auth_controller import auth_bp
    from controllers.compra_controller import compra_bp
    from controllers.main_controller import main_bp
    from controllers.produto_controller import produto_bp

    # Cada Blueprint agrupa rotas de um domínio. O registro transforma seus
    # decorators em URLs efetivamente conhecidas pela aplicação.
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(produto_bp)
    app.register_blueprint(compra_bp)

    # Disponibiliza ``|moeda`` a todos os templates Jinja2.
    app.jinja_env.filters["moeda"] = formatar_moeda

    @app.before_request
    def exigir_login():
        """Protege globalmente as páginas privadas antes de cada requisição.

        Parâmetros:
            Nenhum explícito; consulta os proxies ``request`` e ``session``.

        Retorno:
            Um redirecionamento para o login quando a rota é privada e não há
            ``usuario_id`` na sessão; caso contrário, ``None`` implícito permite
            que o Flask continue até a função da rota solicitada.

        Efeitos colaterais:
            Não altera a sessão. Pode encerrar antecipadamente o fluxo normal.

        Possíveis erros:
            O uso fora de contexto Flask gera erro de contexto. A proteção se
            conecta às rotas do Blueprint ``auth`` e à sessão criada no login.
        """
        # ``request.endpoint`` usa o formato ``blueprint.funcao``. A rota de
        # arquivos estáticos também é pública para que a tela de login tenha CSS.
        rotas_publicas = {"auth.login", "auth.cadastro", "static"}

        if request.endpoint not in rotas_publicas and "usuario_id" not in session:
            # ``url_for`` evita codificar a URL manualmente; ``proxima`` preserva
            # o caminho desejado como query string, embora o login atual não o use.
            return redirect(
                url_for("auth.login", proxima=request.path)
            )

    @app.errorhandler(404)
    def pagina_nao_encontrada(_erro):
        """Renderiza uma página amigável para recursos inexistentes.

        Parâmetros:
            _erro: Exceção HTTP 404 entregue pelo Flask; o prefixo indica que o
                objeto não precisa ser consultado para montar esta resposta.

        Retorno:
            Tupla com o HTML de ``404.html`` e o status HTTP 404.

        Efeitos colaterais:
            Renderiza um template, sem modificar banco ou sessão.

        Possíveis erros:
            Falhas no template podem interromper a resposta. Relaciona-se às
            chamadas ``abort(404)`` existentes nos Controllers.
        """
        return render_template("404.html"), 404

    # Associa abertura/fechamento da conexão à aplicação e cria o schema.
    init_database(app)

    return app


# Instância usada por servidores WSGI e por ``flask --app app``.
app = create_app()

# Este bloco só executa quando o arquivo é iniciado diretamente, não ao importar.
if __name__ == "__main__":
    # ``debug=True`` oferece recarga e diagnóstico e deve ficar restrito ao estudo local.
    app.run(debug=True)
