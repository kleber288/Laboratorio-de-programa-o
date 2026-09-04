"""Consultas e inserções de usuários."""

from database import get_db


def buscar_por_usuario(usuario):
    return get_db().execute(
        "SELECT * FROM usuarios WHERE usuario = ? COLLATE NOCASE", (usuario,)
    ).fetchone()


def criar(nome, usuario, senha_hash):
    db = get_db()
    cursor = db.execute(
        "INSERT INTO usuarios (nome, usuario, senha_hash) VALUES (?, ?, ?)",
        (nome, usuario, senha_hash),
    )
    db.commit()
    return cursor.lastrowid
