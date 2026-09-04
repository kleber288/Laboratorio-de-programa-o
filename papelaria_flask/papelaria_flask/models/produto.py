"""CRUD dos produtos da papelaria."""

from database import get_db


def listar(busca=""):
    termo = f"%{busca.strip()}%"
    return get_db().execute(
        """SELECT * FROM produtos
           WHERE nome LIKE ? OR marca LIKE ? OR categoria LIKE ?
           ORDER BY nome COLLATE NOCASE""",
        (termo, termo, termo),
    ).fetchall()


def buscar(produto_id):
    return get_db().execute("SELECT * FROM produtos WHERE id = ?", (produto_id,)).fetchone()


def criar(nome, marca, categoria, preco_centavos, estoque):
    db = get_db()
    cursor = db.execute(
        """INSERT INTO produtos (nome, marca, categoria, preco_centavos, estoque)
           VALUES (?, ?, ?, ?, ?)""",
        (nome, marca, categoria, preco_centavos, estoque),
    )
    db.commit()
    return cursor.lastrowid


def atualizar(produto_id, nome, marca, categoria, preco_centavos, estoque):
    db = get_db()
    db.execute(
        """UPDATE produtos SET nome=?, marca=?, categoria=?, preco_centavos=?, estoque=?
           WHERE id=?""",
        (nome, marca, categoria, preco_centavos, estoque, produto_id),
    )
    db.commit()


def excluir(produto_id):
    db = get_db()
    db.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))
    db.commit()


def quantidade_total():
    return get_db().execute("SELECT COUNT(*) AS total FROM produtos").fetchone()["total"]


def estoque_total():
    return get_db().execute("SELECT COALESCE(SUM(estoque), 0) AS total FROM produtos").fetchone()["total"]
