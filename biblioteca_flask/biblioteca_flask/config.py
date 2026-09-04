"""Configurações centralizadas da aplicação."""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "troque-esta-chave-em-producao")
    DATABASE = os.environ.get("DATABASE", str(BASE_DIR / "instance" / "biblioteca.db"))
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
