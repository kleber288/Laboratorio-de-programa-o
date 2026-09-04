"""Rota do painel inicial."""

from flask import Blueprint, render_template

from models import emprestimo, livro

main_bp = Blueprint("main", __name__)


@main_bp.get("/")
def inicio():
    return render_template(
        "menu.html",
        total_titulos=livro.quantidade_titulos(),
        total_disponiveis=livro.quantidade_disponivel(),
        emprestimos_abertos=emprestimo.quantidade_em_aberto(),
    )
