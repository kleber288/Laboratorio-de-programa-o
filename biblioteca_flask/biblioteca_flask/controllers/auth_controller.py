"""Rotas de login, cadastro e logout."""

import sqlite3

from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from models import usuario as usuario_model

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        usuario = usuario_model.buscar_por_usuario(request.form.get("usuario", "").strip())
        if usuario and check_password_hash(usuario["senha_hash"], request.form.get("senha", "")):
            session.clear()
            session["usuario_id"] = usuario["id"]
            session["usuario_nome"] = usuario["nome"]
            return redirect(url_for("main.inicio"))
        flash("Usuário ou senha inválidos.", "erro")
    return render_template("login.html")


@auth_bp.route("/cadastro", methods=("GET", "POST"))
def cadastro():
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        nome_usuario = request.form.get("usuario", "").strip()
        senha = request.form.get("senha", "")
        if len(nome) < 2 or len(nome_usuario) < 3 or len(senha) < 6:
            flash("Informe nome, usuário com 3 caracteres e senha com 6 caracteres.", "erro")
        else:
            try:
                usuario_model.criar(nome, nome_usuario, generate_password_hash(senha))
                flash("Cadastro realizado. Agora faça o login.", "sucesso")
                return redirect(url_for("auth.login"))
            except sqlite3.IntegrityError:
                flash("Esse nome de usuário já está em uso.", "erro")
    return render_template("cadastro_usuario.html")


@auth_bp.post("/logout")
def logout():
    session.clear()
    flash("Sessão encerrada.", "sucesso")
    return redirect(url_for("auth.login"))
