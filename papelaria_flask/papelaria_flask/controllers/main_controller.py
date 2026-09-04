"""Rota do painel inicial."""

from flask import Blueprint, render_template

from models import produto, venda

main_bp = Blueprint("main", __name__)


@main_bp.get("/")
def inicio():
    return render_template(
        "menu.html",
        total_produtos=produto.quantidade_total(),
        total_estoque=produto.estoque_total(),
        total_vendas=venda.quantidade_total(),
    )
