"""Empréstimos, itens e devoluções transacionais."""

from database import get_db


def listar():
    return get_db().execute(
        """SELECT e.*, u.nome AS usuario_nome FROM emprestimos e
           JOIN usuarios u ON u.id=e.usuario_id
           ORDER BY e.criado_em DESC, e.id DESC"""
    ).fetchall()


def buscar(emprestimo_id):
    return get_db().execute(
        """SELECT e.*, u.nome AS usuario_nome FROM emprestimos e
           JOIN usuarios u ON u.id=e.usuario_id WHERE e.id=?""",
        (emprestimo_id,),
    ).fetchone()


def listar_itens(emprestimo_id):
    return get_db().execute(
        "SELECT * FROM itens_emprestimo WHERE emprestimo_id=? ORDER BY id", (emprestimo_id,)
    ).fetchall()


def finalizar(usuario_id, leitor, data_prevista, carrinho):
    db = get_db()
    try:
        itens = []
        for item in carrinho:
            livro = db.execute("SELECT * FROM livros WHERE id=?", (item["livro_id"],)).fetchone()
            if livro is None:
                raise ValueError(f"O livro {item['titulo']} não existe mais.")
            if livro["exemplares_disponiveis"] < item["quantidade"]:
                raise ValueError(f"Não há exemplares suficientes de {livro['titulo']}.")
            itens.append((livro, item["quantidade"]))
        cursor = db.execute(
            "INSERT INTO emprestimos (usuario_id, leitor, data_prevista) VALUES (?, ?, ?)",
            (usuario_id, leitor, data_prevista),
        )
        emprestimo_id = cursor.lastrowid
        for livro, quantidade in itens:
            db.execute(
                """INSERT INTO itens_emprestimo (emprestimo_id, livro_id, livro_titulo, quantidade)
                   VALUES (?, ?, ?, ?)""",
                (emprestimo_id, livro["id"], livro["titulo"], quantidade),
            )
            db.execute(
                "UPDATE livros SET exemplares_disponiveis=exemplares_disponiveis-? WHERE id=?",
                (quantidade, livro["id"]),
            )
        db.commit()
        return emprestimo_id
    except Exception:
        db.rollback()
        raise


def devolver(emprestimo_id):
    db = get_db()
    emprestimo = db.execute("SELECT * FROM emprestimos WHERE id=?", (emprestimo_id,)).fetchone()
    if emprestimo is None:
        raise LookupError("Empréstimo não encontrado.")
    if emprestimo["status"] == "DEVOLVIDO":
        raise ValueError("Este empréstimo já foi devolvido.")
    try:
        itens = db.execute("SELECT * FROM itens_emprestimo WHERE emprestimo_id=?", (emprestimo_id,)).fetchall()
        for item in itens:
            if item["livro_id"] is not None:
                db.execute(
                    "UPDATE livros SET exemplares_disponiveis=exemplares_disponiveis+? WHERE id=?",
                    (item["quantidade"], item["livro_id"]),
                )
        db.execute(
            "UPDATE emprestimos SET status='DEVOLVIDO', devolvido_em=CURRENT_TIMESTAMP WHERE id=?",
            (emprestimo_id,),
        )
        db.commit()
    except Exception:
        db.rollback()
        raise


def quantidade_em_aberto():
    return get_db().execute(
        "SELECT COUNT(*) AS total FROM emprestimos WHERE status='EM_ABERTO'"
    ).fetchone()["total"]
