"""Controller da página inicial privada e de seus indicadores."""

from flask import Blueprint, render_template

# Estes Models executam COUNTs usados nos cards do painel.
from models import compra, produto


main_bp = Blueprint("main", __name__)


@main_bp.get("/")
def inicio():
    """Atende ``GET /`` e monta o painel da área autenticada.

    Parâmetros:
        Nenhum.

    Retorno:
        HTML de ``menu.html`` com ``total_produtos`` e ``total_compras``.

    Efeitos colaterais:
        Executa duas consultas de leitura; não altera banco nem sessão.

    Possíveis erros:
        Falhas SQLite/Jinja são propagadas. Antes desta rota, o ``before_request``
        de ``app.py`` redireciona visitantes sem ``usuario_id``.
    """
    # Argumentos nomeados viram variáveis disponíveis diretamente no template.
    return render_template(
        "menu.html", total_produtos=produto.quantidade_total(), total_compras=compra.quantidade_total()
    )
