"""Histórico e finalização transacional das vendas."""

from database import get_db


def listar():
    return get_db().execute(
        """SELECT v.*, u.nome AS usuario_nome FROM vendas v
           JOIN usuarios u ON u.id = v.usuario_id
           ORDER BY v.criada_em DESC, v.id DESC"""
    ).fetchall()


def buscar(venda_id):
    return get_db().execute(
        """SELECT v.*, u.nome AS usuario_nome FROM vendas v
           JOIN usuarios u ON u.id = v.usuario_id WHERE v.id = ?""",
        (venda_id,),
    ).fetchone()


def listar_itens(venda_id):
    return get_db().execute(
        "SELECT * FROM itens_venda WHERE venda_id = ? ORDER BY id", (venda_id,)
    ).fetchall()


def finalizar(usuario_id, cliente, carrinho):
    """Revalida estoque e grava cabeçalho, itens e baixas em uma transação."""
    db = get_db()
    try:
        itens = []
        for item in carrinho:
            produto = db.execute("SELECT * FROM produtos WHERE id=?", (item["produto_id"],)).fetchone()
            if produto is None:
                raise ValueError(f"O produto {item['nome']} não existe mais.")
            if produto["estoque"] < item["quantidade"]:
                raise ValueError(f"Estoque insuficiente para {produto['nome']}.")
            itens.append((produto, item["quantidade"]))

        total = sum(produto["preco_centavos"] * quantidade for produto, quantidade in itens)
        cursor = db.execute(
            "INSERT INTO vendas (usuario_id, cliente, total_centavos) VALUES (?, ?, ?)",
            (usuario_id, cliente, total),
        )
        venda_id = cursor.lastrowid
        for produto, quantidade in itens:
            subtotal = produto["preco_centavos"] * quantidade
            db.execute(
                """INSERT INTO itens_venda
                   (venda_id, produto_id, produto_nome, preco_unitario_centavos,
                    quantidade, subtotal_centavos) VALUES (?, ?, ?, ?, ?, ?)""",
                (venda_id, produto["id"], produto["nome"], produto["preco_centavos"], quantidade, subtotal),
            )
            db.execute("UPDATE produtos SET estoque=estoque-? WHERE id=?", (quantidade, produto["id"]))
        db.commit()
        return venda_id
    except Exception:
        db.rollback()
        raise


def quantidade_total():
    return get_db().execute("SELECT COUNT(*) AS total FROM vendas").fetchone()["total"]
