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

CREATE TABLE IF NOT EXISTS produtos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    marca TEXT NOT NULL,
    categoria TEXT NOT NULL,
    preco_centavos INTEGER NOT NULL CHECK (preco_centavos >= 0),
    estoque INTEGER NOT NULL DEFAULT 0 CHECK (estoque >= 0),
    criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS vendas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    cliente TEXT NOT NULL,
    total_centavos INTEGER NOT NULL CHECK (total_centavos >= 0),
    criada_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

CREATE TABLE IF NOT EXISTS itens_venda (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    venda_id INTEGER NOT NULL,
    produto_id INTEGER,
    produto_nome TEXT NOT NULL,
    preco_unitario_centavos INTEGER NOT NULL,
    quantidade INTEGER NOT NULL CHECK (quantidade > 0),
    subtotal_centavos INTEGER NOT NULL,
    FOREIGN KEY (venda_id) REFERENCES vendas(id) ON DELETE CASCADE,
    FOREIGN KEY (produto_id) REFERENCES produtos(id) ON DELETE SET NULL
);
"""


def get_db():
    """Abre uma conexão por contexto de requisição e a reutiliza."""
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
    """Cria as tabelas e o administrador didático do primeiro acesso."""
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
