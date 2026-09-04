"""Carrinho de livros, empréstimos, devoluções e exportação."""

from datetime import date
from io import BytesIO

from flask import Blueprint, abort, flash, redirect, render_template, request, send_file, session, url_for
from openpyxl import Workbook
from openpyxl.styles import Font

from models import emprestimo as emprestimo_model
from models import livro as livro_model

emprestimo_bp = Blueprint("emprestimo", __name__, url_prefix="/emprestimos")


def _carrinho():
    return session.setdefault("carrinho_livros", [])


@emprestimo_bp.get("")
def listar():
    return render_template("emprestimos.html", emprestimos=emprestimo_model.listar(), hoje=date.today().isoformat())


@emprestimo_bp.get("/novo")
def novo():
    return render_template("novo_emprestimo.html", livros=livro_model.listar(), carrinho=_carrinho(), hoje=date.today().isoformat())


@emprestimo_bp.post("/carrinho/adicionar")
def adicionar():
    try:
        livro_id = int(request.form.get("livro_id", ""))
        quantidade = int(request.form.get("quantidade", ""))
    except ValueError:
        livro_id, quantidade = 0, 0
    livro = livro_model.buscar(livro_id)
    if livro is None or quantidade <= 0:
        flash("Selecione um livro e uma quantidade válida.", "erro")
    elif quantidade > livro["exemplares_disponiveis"]:
        flash("A quantidade supera os exemplares disponíveis.", "erro")
    else:
        carrinho = _carrinho()
        existente = next((item for item in carrinho if item["livro_id"] == livro_id), None)
        nova_quantidade = quantidade + (existente["quantidade"] if existente else 0)
        if nova_quantidade > livro["exemplares_disponiveis"]:
            flash("A quantidade total supera os exemplares disponíveis.", "erro")
            return redirect(url_for("emprestimo.novo"))
        if existente:
            existente["quantidade"] = nova_quantidade
        else:
            carrinho.append({"livro_id": livro["id"], "titulo": livro["titulo"], "autor": livro["autor"], "quantidade": quantidade})
        session["carrinho_livros"] = carrinho
        flash("Livro adicionado ao empréstimo.", "sucesso")
    return redirect(url_for("emprestimo.novo"))


@emprestimo_bp.post("/carrinho/<int:indice>/remover")
def remover(indice):
    carrinho = _carrinho()
    if indice < 0 or indice >= len(carrinho):
        abort(404)
    carrinho.pop(indice)
    session["carrinho_livros"] = carrinho
    return redirect(url_for("emprestimo.novo"))


@emprestimo_bp.post("/carrinho/limpar")
def limpar():
    session.pop("carrinho_livros", None)
    flash("Seleção de livros esvaziada.", "sucesso")
    return redirect(url_for("emprestimo.novo"))


@emprestimo_bp.post("/finalizar")
def finalizar():
    carrinho = _carrinho()
    leitor = request.form.get("leitor", "").strip()
    data_prevista = request.form.get("data_prevista", "").strip()
    try:
        prazo = date.fromisoformat(data_prevista)
    except ValueError:
        prazo = None
    if not carrinho:
        flash("Nenhum livro foi selecionado.", "erro")
    elif len(leitor) < 2:
        flash("Informe o nome do leitor.", "erro")
    elif prazo is None or prazo < date.today():
        flash("Informe uma data de devolução válida.", "erro")
    else:
        try:
            emprestimo_id = emprestimo_model.finalizar(session["usuario_id"], leitor, data_prevista, carrinho)
            session.pop("carrinho_livros", None)
            flash("Empréstimo registrado com sucesso.", "sucesso")
            return redirect(url_for("emprestimo.detalhes", emprestimo_id=emprestimo_id))
        except ValueError as erro:
            flash(str(erro), "erro")
    return redirect(url_for("emprestimo.novo"))


@emprestimo_bp.get("/<int:emprestimo_id>")
def detalhes(emprestimo_id):
    emprestimo = emprestimo_model.buscar(emprestimo_id)
    if emprestimo is None:
        abort(404)
    return render_template("detalhes_emprestimo.html", emprestimo=emprestimo, itens=emprestimo_model.listar_itens(emprestimo_id), hoje=date.today().isoformat())


@emprestimo_bp.post("/<int:emprestimo_id>/devolver")
def devolver(emprestimo_id):
    try:
        emprestimo_model.devolver(emprestimo_id)
        flash("Devolução registrada e exemplares liberados.", "sucesso")
    except LookupError:
        abort(404)
    except ValueError as erro:
        flash(str(erro), "erro")
    return redirect(url_for("emprestimo.detalhes", emprestimo_id=emprestimo_id))


@emprestimo_bp.get("/exportar")
def exportar():
    wb = Workbook()
    ws = wb.active
    ws.title = "Empréstimos"
    ws.append(["Código", "Data", "Leitor", "Prazo", "Status", "Responsável", "Devolvido em"])
    for cell in ws[1]:
        cell.font = Font(bold=True)
    for emprestimo in emprestimo_model.listar():
        ws.append([emprestimo["id"], emprestimo["criado_em"], emprestimo["leitor"], emprestimo["data_prevista"], emprestimo["status"], emprestimo["usuario_nome"], emprestimo["devolvido_em"]])
    ws.column_dimensions["B"].width = 22
    ws.column_dimensions["C"].width = 26
    ws.column_dimensions["F"].width = 24
    arquivo = BytesIO()
    wb.save(arquivo)
    arquivo.seek(0)
    return send_file(arquivo, as_attachment=True, download_name="emprestimos_biblioteca.xlsx", mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
