"""Configuração central da aplicação, com valores substituíveis pelo ambiente."""

import os
from pathlib import Path

# Parte do caminho absoluto deste arquivo para que o banco não dependa do
# diretório a partir do qual o comando Flask foi executado.
BASE_DIR = Path(__file__).resolve().parent


class Config:
    """Valores padrão carregados por ``create_app`` em ``app.py``.

    Não recebe parâmetros nem possui métodos. A leitura da classe não retorna
    valores diretamente, mas expõe atributos ao dicionário ``app.config``.
    Como efeito colateral de importação, consulta variáveis de ambiente. Não há
    tratamento local para caminhos inválidos; eventuais erros surgem ao abrir o
    banco em ``database.py``.
    """

    # A chave assina criptograficamente o cookie de sessão. Este fallback é
    # somente didático/local e DEVE ser substituído por um segredo forte em produção.
    SECRET_KEY = os.environ.get("SECRET_KEY", "troque-esta-chave-em-producao")
    # Permite indicar outro arquivo SQLite; na ausência, usa ``instance/``.
    DATABASE = os.environ.get("DATABASE", str(BASE_DIR / "instance" / "supermercado.db"))

    # Impede JavaScript do navegador de ler o cookie, reduzindo exposição em XSS.
    SESSION_COOKIE_HTTPONLY = True
    # ``Lax`` limita o envio entre sites e ajuda contra CSRF em navegações comuns.
    SESSION_COOKIE_SAMESITE = "Lax"
