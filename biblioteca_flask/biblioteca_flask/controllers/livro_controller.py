"""CRUD, pesquisa e exportação do acervo."""

import sqlite3
from datetime import date
from io import BytesIO

from flask import Blueprint, abort, flash, redirect, render_template, request, send_file, url_for
from openpyxl import Workbook
from openpyxl.styles import Font

from models import livro as livro_model

livro_bp = Blueprint("livro", __name__, url_prefix="/livros")


def _dados_formulario():
    titulo = request.form.get("titulo", "").strip()
    autor = request.form.get("autor", "").strip()
    isbn = request.form.get("isbn", "").strip()
    categoria = request.form.get("categoria", "").strip()
    ano = int(request.form.get("ano_publicacao", "0"))
    exemplares = int(request.form.get("exemplares_total", "0"))
    if not titulo or not autor or not isbn or not categoria or ano < 1 or ano > date.today().year + 1 or exemplares < 0:
        raise ValueError("Preencha todos os campos corretamente.")
    return titulo, autor, isbn, categoria, ano, exemplares


@livro_bp.get("")
def listar():
    busca = request.args.get("busca", "")
    return render_template("livros.html", livros=livro_model.listar(busca), busca=busca)


@livro_bp.route("/novo", methods=("GET", "POST"))
def novo():
    if request.method == "POST":
        try:
            livro_model.criar(*_dados_formulario())
            flash("Livro cadastrado.", "sucesso")
            return redirect(url_for("livro.listar"))
        except sqlite3.IntegrityError:
            flash("Já existe um livro com esse ISBN.", "erro")
        except (ValueError, TypeError):
            flash("Preencha ano e exemplares com valores válidos.", "erro")
    return render_template("livro_form.html", livro=None)


@livro_bp.route("/<int:livro_id>/editar", methods=("GET", "POST"))
def editar(livro_id):
    livro = livro_model.buscar(livro_id)
    if livro is None:
        abort(404)
    if request.method == "POST":
        try:
            livro_model.atualizar(livro_id, *_dados_formulario())
            flash("Livro atualizado.", "sucesso")
            return redirect(url_for("livro.listar"))
        except sqlite3.IntegrityError:
            flash("Já existe outro livro com esse ISBN.", "erro")
        except (ValueError, TypeError) as erro:
            flash(str(erro) if str(erro) else "Preencha os dados corretamente.", "erro")
    return render_template("livro_form.html", livro=livro)


@livro_bp.post("/<int:livro_id>/excluir")
def excluir(livro_id):
    if livro_model.buscar(livro_id) is None:
        abort(404)
    try:
        livro_model.excluir(livro_id)
        flash("Livro excluído. O histórico de empréstimos foi preservado.", "sucesso")
    except ValueError as erro:
        flash(str(erro), "erro")
    return redirect(url_for("livro.listar"))


@livro_bp.get("/exportar")
def exportar():
    wb = Workbook()
    ws = wb.active
    ws.title = "Livros"
    ws.append(["Código", "Título", "Autor", "ISBN", "Categoria", "Ano", "Total", "Disponíveis"])
    for cell in ws[1]:
        cell.font = Font(bold=True)
    for livro in livro_model.listar():
        ws.append([livro["id"], livro["titulo"], livro["autor"], livro["isbn"], livro["categoria"], livro["ano_publicacao"], livro["exemplares_total"], livro["exemplares_disponiveis"]])
    ws.column_dimensions["B"].width = 32
    ws.column_dimensions["C"].width = 26
    ws.column_dimensions["D"].width = 20
    arquivo = BytesIO()
    wb.save(arquivo)
    arquivo.seek(0)
    return send_file(arquivo, as_attachment=True, download_name="acervo_biblioteca.xlsx", mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
