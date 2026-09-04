"""Controller de autenticação: login, cadastro e encerramento da sessão."""

import sqlite3

# Blueprint agrupa as rotas; request lê a requisição; session mantém o estado
# assinado no cookie; flash envia uma mensagem para a próxima página;
# redirect/url_for aplicam o padrão Post/Redirect/Get; render_template chama a View.
from flask import (Blueprint, flash, redirect, render_template, request, session, url_for)
# O Werkzeug gera hashes com salt e verifica a senha sem armazená-la em texto puro.
from werkzeug.security import check_password_hash, generate_password_hash
from models import usuario as usuario_model

# O nome ``auth`` compõe endpoints como ``auth.login`` usados por ``url_for``.
auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=("GET", "POST"))
def login():
    """Exibe o login em GET e autentica credenciais em POST na URL ``/login``.

    Parâmetros:
        Nenhum explícito; os campos ``usuario`` e ``senha`` vêm de
        ``request.form`` e correspondem aos atributos ``name`` de ``login.html``.

    Retorno:
        Em sucesso, redireciona para ``main.inicio``; em GET ou falha, devolve o
        template de login.

    Efeitos colaterais:
        Consulta o Model de usuário, limpa/cria dados de sessão e pode registrar
        uma mensagem ``flash``.

    Possíveis erros:
        Erros do banco ou acesso incorreto à linha retornada são propagados. O
        middleware de ``app.py`` considera ``usuario_id`` a prova de autenticação.
    """
    # GET apenas apresenta o formulário; POST processa dados enviados no corpo.
    if request.method == "POST":
        # ``get`` com padrão evita KeyError; o login remove espaços nas pontas,
        # enquanto a senha é preservada exatamente como digitada.
        nome_usuario = request.form.get("usuario", "").strip()
        senha = request.form.get("senha", "")
        usuario = usuario_model.buscar_por_usuario(nome_usuario)

        # O hash armazenado inclui os parâmetros necessários à comparação segura.
        if usuario and check_password_hash(usuario["senha_hash"], senha):
            # Limpar primeiro evita carregar carrinho ou identidade de sessão anterior.
            session.clear()
            session["usuario_id"] = usuario["id"]
            # Esta expressão original apenas lê a chave, sem atribuir o nome, e
            # pode causar KeyError; foi mantida para não modificar a lógica.
            session["usuario_nome"]
            # ``url_for`` resolve o endpoint mesmo que sua URL mude futuramente.
            return redirect(url_for("main.inicio"))

        # A categoria ``erro`` vira uma classe CSS em ``base.html``.
        flash("Usuário ou senha inválidos.", "erro")
    return render_template("login.html")


@auth_bp.route("/cadastro", methods=("GET", "POST"))
def cadastro():
    """Exibe e processa o cadastro na URL ``/cadastro`` por GET e POST.

    Parâmetros:
        Nenhum explícito; lê ``nome``, ``usuario`` e ``senha`` de
        ``request.form``, ligados aos ``name`` de ``cadastro_usuario.html``.

    Retorno:
        Redirecionamento ao login após inserir; caso contrário, o formulário.

    Efeitos colaterais:
        Gera hash de senha, insere via ``models/usuario.py``, faz commit no Model
        e grava mensagens flash de sucesso ou erro.

    Possíveis erros:
        ``sqlite3.IntegrityError`` por login repetido é convertido em mensagem;
        outras falhas do banco são propagadas.
    """
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        nome_usuario = request.form.get("usuario", "").strip()
        senha = request.form.get("senha", "")

        # A validação do servidor é indispensável: atributos HTML podem ser
        # ignorados por clientes que enviam requisições diretamente.
        if len(nome) < 2 or len(nome_usuario) < 3 or len(senha) < 6:
            flash("Informa nome, usuário com 3 caracteres e senha com 6 caracteres.", "erro")
        else:
            try:
                # Só o hash com salt atravessa a fronteira até o Model.
                usuario_model.criar(nome, nome_usuario, generate_password_hash(senha),)
                flash("Cadastro realizado. Agora faça o login.", "sucesso")
                return redirect(url_for("auth.login"))
            except sqlite3.IntegrityError:
                # A restrição UNIQUE do schema é a autoridade final contra duplicidade.
                flash("Esse nome de usuário já está em uso.", "erro")

    return render_template("cadastro_usuario.html")


@auth_bp.post("/logout")
def logout():
    """Encerra a autenticação exclusivamente por POST na URL ``/logout``.

    Parâmetros:
        Nenhum.

    Retorno:
        Redirecionamento para ``auth.login``.

    Efeitos colaterais:
        ``session.clear`` remove identidade e carrinho; ``flash`` cria uma nova
        sessão mínima para transportar a confirmação do logout.

    Possíveis erros:
        Falhas ao assinar a sessão podem ser propagadas. Usar POST evita que um
        simples link ou pré-carregamento de GET encerre a sessão.
    """
    session.clear()
    flash("Sessão encerrada.", "sucesso")
    return redirect(url_for("auth.login"))
