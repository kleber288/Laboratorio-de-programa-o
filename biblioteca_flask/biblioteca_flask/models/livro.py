"""CRUD e indicadores do acervo de livros."""

from database import get_db


def listar(busca=""):
    termo = f"%{busca.strip()}%"
    return get_db().execute(
        """SELECT * FROM livros
           WHERE titulo LIKE ? OR autor LIKE ? OR isbn LIKE ? OR categoria LIKE ?
           ORDER BY titulo COLLATE NOCASE""",
        (termo, termo, termo, termo),
    ).fetchall()


def buscar(livro_id):
    return get_db().execute("SELECT * FROM livros WHERE id=?", (livro_id,)).fetchone()


def criar(titulo, autor, isbn, categoria, ano_publicacao, exemplares_total):
    db = get_db()
    cursor = db.execute(
        """INSERT INTO livros
           (titulo, autor, isbn, categoria, ano_publicacao, exemplares_total, exemplares_disponiveis)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (titulo, autor, isbn, categoria, ano_publicacao, exemplares_total, exemplares_total),
    )
    db.commit()
    return cursor.lastrowid


def atualizar(livro_id, titulo, autor, isbn, categoria, ano_publicacao, exemplares_total):
    """Mantém emprestados e recalcula disponíveis ao alterar o total."""
    db = get_db()
    atual = buscar(livro_id)
    emprestados = atual["exemplares_total"] - atual["exemplares_disponiveis"]
    if exemplares_total < emprestados:
        raise ValueError(f"Existem {emprestados} exemplar(es) emprestado(s).")
    disponiveis = exemplares_total - emprestados
    db.execute(
        """UPDATE livros SET titulo=?, autor=?, isbn=?, categoria=?, ano_publicacao=?,
           exemplares_total=?, exemplares_disponiveis=? WHERE id=?""",
        (titulo, autor, isbn, categoria, ano_publicacao, exemplares_total, disponiveis, livro_id),
    )
    db.commit()


def excluir(livro_id):
    livro = buscar(livro_id)
    if livro["exemplares_disponiveis"] != livro["exemplares_total"]:
        raise ValueError("Não é possível excluir um livro com exemplares emprestados.")
    db = get_db()
    db.execute("DELETE FROM livros WHERE id=?", (livro_id,))
    db.commit()


def quantidade_titulos():
    return get_db().execute("SELECT COUNT(*) AS total FROM livros").fetchone()["total"]


def quantidade_disponivel():
    return get_db().execute("SELECT COALESCE(SUM(exemplares_disponiveis), 0) AS total FROM livros").fetchone()["total"]
