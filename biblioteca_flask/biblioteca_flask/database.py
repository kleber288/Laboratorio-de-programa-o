"""Conexão, schema e carga inicial do banco SQLite."""

import sqlite3
from pathlib import Path

from flask import current_app, g
from werkzeug.security import generate_password_hash

SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    usuario TEXT NOT NULL UNIQUE COLLATE NOCASE,
    senha_hash TEXT NOT NULL,
    criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS livros (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    autor TEXT NOT NULL,
    isbn TEXT NOT NULL UNIQUE,
    categoria TEXT NOT NULL,
    ano_publicacao INTEGER NOT NULL CHECK (ano_publicacao BETWEEN 1 AND 9999),
    exemplares_total INTEGER NOT NULL CHECK (exemplares_total >= 0),
    exemplares_disponiveis INTEGER NOT NULL CHECK (
        exemplares_disponiveis >= 0 AND exemplares_disponiveis <= exemplares_total
    ),
    criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS emprestimos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    leitor TEXT NOT NULL,
    data_prevista TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'EM_ABERTO' CHECK (status IN ('EM_ABERTO', 'DEVOLVIDO')),
    criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    devolvido_em TEXT,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

CREATE TABLE IF NOT EXISTS itens_emprestimo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    emprestimo_id INTEGER NOT NULL,
    livro_id INTEGER,
    livro_titulo TEXT NOT NULL,
    quantidade INTEGER NOT NULL CHECK (quantidade > 0),
    FOREIGN KEY (emprestimo_id) REFERENCES emprestimos(id) ON DELETE CASCADE,
    FOREIGN KEY (livro_id) REFERENCES livros(id) ON DELETE SET NULL
);
"""


def get_db():
    if "db" not in g:
        caminho = Path(current_app.config["DATABASE"])
        caminho.parent.mkdir(parents=True, exist_ok=True)
        g.db = sqlite3.connect(caminho)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(_error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    db.executescript(SCHEMA)
    if db.execute("SELECT 1 FROM usuarios LIMIT 1").fetchone() is None:
        db.execute(
            "INSERT INTO usuarios (nome, usuario, senha_hash) VALUES (?, ?, ?)",
            ("Administrador", "admin", generate_password_hash("admin123")),
        )
    db.commit()


def init_app(app):
    app.teardown_appcontext(close_db)
    with app.app_context():
        init_db()
