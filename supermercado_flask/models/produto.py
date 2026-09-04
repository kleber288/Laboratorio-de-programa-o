"""Model do catálogo: SELECTs, INSERT, UPDATE, DELETE e contagem."""

from database import get_db


def listar(busca=""):
    """Lista produtos cujo nome ou fabricante contém o termo informado.

    ``busca`` é texto opcional. Retorna todas as linhas via ``fetchall``; não há
    alteração de dados. Pode propagar erros SQLite/contexto. Os ``%`` criam uma
    busca por trecho com LIKE, e a função atende a listagem e as exportações.
    """
    # O termo continua sendo parâmetro, não concatenação de SQL; ``strip`` apenas
    # remove espaços das extremidades. Com busca vazia, ``%%`` encontra tudo.
    termo = f"%{busca.strip()}%"

    return get_db().execute(
        """
        SELECT * FROM produtos
        WHERE nome LIKE ? OR fabricante LIKE ?
        ORDER BY nome COLLATE NOCASE
        """,
        # Há dois placeholders, portanto a tupla repete o termo duas vezes.
        # ORDER BY com NOCASE fornece ordem alfabética sem distinguir caixa ASCII.
        (termo, termo),
    ).fetchall()


def buscar(produto_id):
    """Busca um produto por chave primária.

    ``produto_id`` é o id inteiro. Retorna uma ``sqlite3.Row`` ou ``None`` por
    ``fetchone``; apenas lê o banco e pode propagar erros. É usado pelos
    Controllers de edição, exclusão e carrinho.
    """
    return get_db().execute(
        "SELECT * FROM produtos WHERE id = ?",
        # A vírgula transforma o único parâmetro em tupla de um item.
        (produto_id,),
    ).fetchone()


def criar(nome, fabricante, unidade, preco_centavos, estoque):
    """Insere um produto validado pelo Controller.

    Recebe nome, fabricante, unidade, preço inteiro em centavos e estoque
    inteiro; retorna ``None``. Executa INSERT e commit. Pode propagar erros de
    restrição, tipo, contexto ou SQLite para ``produto_controller.py``.
    """
    db = get_db()

    # Cada ``?`` corresponde, na mesma ordem, a um valor da tupla abaixo.
    db.execute(
        """
        INSERT INTO produtos (
            nome,
            fabricante,
            unidade,
            preco_centavos,
            estoque
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (nome, fabricante, unidade, preco_centavos, estoque),
    )

    # Confirma a transação para que o novo produto sobreviva ao fechamento.
    db.commit()


def atualizar(
    produto_id,
    nome,
    fabricante,
    unidade,
    preco_centavos,
    estoque
):
    """Atualiza todos os campos editáveis de um produto existente.

    Recebe ``produto_id`` e os mesmos cinco dados de ``criar``; retorna ``None``.
    Executa UPDATE/commit e pode propagar erros SQLite. O ``WHERE id = ?`` limita
    a alteração ao registro solicitado pelo Controller.
    """
    db = get_db()

    db.execute(
        """
        UPDATE produtos
        SET nome = ?,
            fabricante = ?,
            unidade = ?,
            preco_centavos = ?,
            estoque = ?
        WHERE id = ?
        """,
        # A ordem da tupla acompanha os cinco SETs e, por último, o WHERE.
        (
            nome,
            fabricante,
            unidade,
            preco_centavos,
            estoque,
            produto_id,
        ),
    )

    db.commit()


def excluir(produto_id):
    """Exclui o produto identificado por ``produto_id``.

    Retorna ``None``; executa DELETE e commit. Pode propagar erros de chave
    estrangeira/SQLite. O Controller verifica a existência antes, e o schema
    pretende aplicar ``ON DELETE SET NULL`` nos itens históricos.
    """
    db = get_db()

    db.execute(
        "DELETE FROM produtos WHERE id = ?",
        # Placeholder impede que o id seja interpretado como trecho de SQL.
        (produto_id,),
    )

    db.commit()


def quantidade_total():
    """Conta os produtos para o card do painel.

    Não recebe parâmetros. Retorna um inteiro, sem efeitos de escrita, e pode
    propagar erros SQLite/contexto. ``COUNT(*)`` agrega todas as linhas em uma,
    ``AS total`` dá o nome acessado graças a ``sqlite3.Row``.
    """
    return get_db().execute(
        "SELECT COUNT(*) AS total FROM produtos"
    ).fetchone()["total"]
