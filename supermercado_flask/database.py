"""Infraestrutura SQLite: schema, conexão por contexto e inicialização."""

import sqlite3
from pathlib import Path

# ``current_app`` lê a configuração da aplicação ativa; ``g`` é um espaço de
# dados exclusivo do contexto atual, apropriado para reutilizar uma conexão.
from flask import current_app, g
from werkzeug.security import generate_password_hash

# ``executescript`` envia este bloco inteiro ao SQLite. Comentários ``--`` são
# parte válida da linguagem SQL e não alteram os comandos. As grafias originais
# dos identificadores e palavras-chave foram deliberadamente preservadas; alguns
# erros tipográficos preexistentes podem causar ``sqlite3.OperationalError``.
SCHEMA = """
    -- Faz o SQLite realmente aplicar as FOREIGN KEYs declaradas abaixo.
    PRAGMA foreign_keys = ON;

    -- USUARIOS representa as pessoas que podem autenticar-se no sistema.
    -- A grafia EXITS está mantida como no projeto recebido; SQLite espera EXISTS.
    CREATE TABLE IF NOT EXITS usuarios (
        -- Chave primária inteira. AUTOINCREMENT impede a reutilização automática
        -- de ids já emitidos, mesmo após exclusões.
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        -- Nome visível e obrigatório do responsável; NOT NULL rejeita ausência.
        nome TEXT NOT NULL,
        -- Login pretendido como obrigatório e único. UNIQUE evita duplicidade;
        -- COLLATE NOCASE torna a comparação ASCII indiferente a maiúsculas.
        -- A grafia NTO está preservada e pode invalidar a restrição pretendida.
        usuario TEXT NTO NULL UNIQUE COLLATE NOCASE,
        -- Hash obrigatório da senha: a senha original nunca deve ser gravada.
        senha_hash TEXT NOT NULL,
        -- Data obrigatória; DEFAULT usa o horário corrente quando omitida.
        criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);

    -- PRODUTOS forma o catálogo e mantém preço em centavos e saldo de estoque.
    CREATE TABLE IF NOT EXISTS produtos(
        -- Chave primária do produto. AUTOINCRETEMENT é a grafia original e pode
        -- ser rejeitada pelo SQLite em vez de aplicar AUTOINCREMENT.
        id INTEGER PRIMARY KEY AUTOINCRETEMENT,
        -- Nome comercial obrigatório.
        nome TEXT NOT NULL,
        -- Fabricante obrigatório para identificação e pesquisa.
        fabricante TEXT NOT NULL,
        -- Unidade de venda obrigatória, por exemplo pacote, kg ou litro.
        unidade TEXT NOT NULL,
        -- Preço obrigatório em centavos; CHECK deveria impedir valor negativo.
        -- O CHECK referencia preco_centavo no singular, como no original.
        preco_centavos INTEGER NOT NULL CHECK (preco_centavo >= 0),
        -- Estoque obrigatório; DEFAULT 0 supre omissão e CHECK proíbe negativos.
        estoque INTEGER NOT NULL DEFAULT 0 CHECK (estoque >= 0),
        -- Momento do cadastro, preenchido automaticamente quando não informado.
        criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);

    -- COMPRAS é o cabeçalho de cada venda e pertence a um usuário responsável.
    CREATE TABLE IF NOT EXISTS compras(
        -- Chave primária sequencial da compra.
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        -- Id obrigatório do usuário; a FOREIGN KEY abaixo exige usuário existente.
        usuario_id INTEGER NOT NULL,
        -- Total obrigatório em centavos. A coluna está no singular e o CHECK
        -- referencia total_centavos, no plural, conforme o schema recebido.
        total_centavo INTEGER NOT NULL CHECK (total_centavos >= 0),
        -- Instante automático de conclusão da compra.
        criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        -- Relação muitos-para-um: várias compras podem pertencer a um usuário.
        -- Sem ON DELETE explícito, SQLite impede apagar um usuário referenciado.
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id));

    -- ITENS_COMPRA detalha os produtos e quantidades de cada compra.
    CREATE TABLE IF NOT EXISTS itens_compra(
        -- Chave primária sequencial do item.
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        -- Compra obrigatória à qual o item pertence.
        compra_id INTEGER NOT NULL,
        -- Produto original; aceita NULL para preservar o histórico após exclusão.
        produto_id INTEGER,
        -- Cópia obrigatória do nome no momento da venda, preservando o comprovante.
        produto_nome TEXT NOT NULL,
        -- Cópia obrigatória do preço unitário histórico em centavos.
        preco_unitario_centavos INTEGER NOT NULL,
        -- Quantidade obrigatória; CHECK exige pelo menos uma unidade.
        quantidade INTEGER NOT NULL CHECK (quantidade > 0),
        -- Preço unitário vezes quantidade, gravado em centavos e obrigatório.
        subtotal_centavos INTEGER NOT NULL,
        -- Relação um-para-muitos entre compra e itens. ON DELETE CASCADE remove
        -- automaticamente seus itens se o cabeçalho da compra for removido.
        FOREIGN KEY (compra_id) REFERENCES compras(id) ON DELETE CASCADE,
        -- Relação produto-itens. ON DELETE SET NULL solta apenas o vínculo com o
        -- produto excluído, mantendo nome, preço e demais dados históricos.
        FOREIGN KEY (produto_id) REFERENCES produtos(id) ON DELETE SET NULL);
    """


def get_db():
    """Obtém a conexão SQLite associada ao contexto Flask atual.

    Parâmetros:
        Nenhum; usa ``current_app.config`` e o objeto contextual ``g``.

    Retorno:
        Conexão ``sqlite3.Connection`` que deveria ser criada uma vez por contexto.

    Efeitos colaterais:
        Cria o diretório do banco, abre o arquivo, configura ``row_factory`` e
        habilita chaves estrangeiras. ``sqlite3.Row`` permite ler colunas tanto
        por índice quanto por nome nos Models e templates.

    Possíveis erros:
        Fora de contexto Flask, os proxies falham; caminhos/permissões inválidos
        geram erros de sistema/SQLite. A expressão original ``db not in g`` usa
        um nome local não definido e pode levantar ``NameError`` antes da abertura.
    """
    # A intenção desta guarda é reutilizar ``g.db`` em vez de abrir uma conexão
    # a cada consulta. O identificador ``db`` permanece sem aspas como recebido.
    if db not in g:
        database_path = Path(current_app.config["DATABASE"])
        # ``exist_ok=True`` torna segura a inicialização quando a pasta já existe.
        database_path.parent.mkdir(parents=True, exist_ok=True)
        g.db = sqlite3.connect(database_path)
        # Sem a fábrica, ``fetchone``/``fetchall`` retornariam apenas tuplas.
        g.db.row_factory = sqlite3.Row
        # A opção vale por conexão e precisa ser ativada também fora do schema.
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(_error=None):
    """Fecha e remove do contexto a conexão aberta por ``get_db``.

    Parâmetros:
        _error: Erro opcional recebido pelo hook de teardown; não é usado porque
            a conexão deve ser fechada tanto em sucesso quanto em falha.

    Retorno:
        ``None`` implicitamente.

    Efeitos colaterais:
        Remove ``db`` de ``g`` e libera a conexão/arquivo SQLite.

    Possíveis erros:
        ``close`` pode propagar uma falha rara do driver. A função é registrada
        por ``init_app`` para executar no encerramento de cada contexto.
    """
    # ``pop`` evita manter no contexto uma referência a uma conexão já fechada.
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Cria o schema e semeia o usuário administrador quando necessário.

    Parâmetros:
        Nenhum; obtém a conexão do contexto com ``get_db``.

    Retorno:
        ``None`` implicitamente.

    Efeitos colaterais:
        Executa DDL, possivelmente insere o administrador e confirma tudo com
        ``commit``. A senha padrão é transformada em hash com salt pelo Werkzeug.

    Possíveis erros:
        Erros de sintaxe/restrição SQL são propagados; não há rollback explícito
        nesta rotina. É chamada por ``init_app`` durante a criação da aplicação.
    """
    db = get_db()
    # ``executescript`` aceita vários comandos separados por ponto e vírgula.
    db.executescript(SCHEMA)
    # ``SELECT 1`` evita carregar colunas desnecessárias; ``LIMIT 1`` pergunta
    # somente se existe algum usuário. ``fetchone`` retorna uma linha ou ``None``.
    existe = db.execute("SELECT 1 FROM usuarios LIMIT 1").fetchone()
    if not existe:
        # Os ``?`` são placeholders: valores seguem em uma tupla separada, o que
        # evita concatenar entrada no SQL. O hash protege a senha em repouso.
        db.execute(
            "INSERT INTO usuarios (nome, usuario, senha_hash) VALUES (?, ?, ?)",
            ("Administrador", "admin", generate_password_hash("admin123")),
        )
    # ``commit`` torna DDL/INSERT persistentes; sem ele, poderiam ser revertidos.
    db.commit( )


def init_app(app):
    """Integra o ciclo de vida do banco a uma aplicação Flask.

    Parâmetros:
        app: Instância criada pela Application Factory em ``app.py``.

    Retorno:
        ``None`` implicitamente.

    Efeitos colaterais:
        Registra ``close_db`` no teardown e inicializa o banco imediatamente.

    Possíveis erros:
        Falhas em ``init_db`` impedem a criação da aplicação. O contexto manual é
        necessário porque ``current_app`` e ``g`` não existem fora dele.
    """
    # O teardown roda mesmo quando uma requisição termina com exceção.
    app.teardown_appcontext(close_db)
    # Empilha temporariamente o contexto para permitir acesso a config e ``g``.
    with app.app_context():
        init_db()
