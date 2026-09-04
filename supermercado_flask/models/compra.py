"""Model de compras, itens, consultas históricas e transação de estoque."""
from database import get_db


def listar():
    """Lista compras com o nome do usuário responsável.

    Não recebe parâmetros. Retorna todas as linhas com ``fetchall`` e não altera
    dados; erros SQLite/contexto são propagados. O JOIN relaciona
    ``compras.usuario_id`` a ``usuarios.id``; o alias ``usuario_nome`` evita
    ambiguidade. ORDER BY mostra primeiro data e id mais recentes.
    """
    return get_db().execute(
        """SELECT c.*, u.nome AS usuario_nome
           FROM compras c JOIN usuarios u ON u.id = c.usuario_id
           ORDER BY c.criada_em DESC, c.id DESC"""
    ).fetchall()


def buscar(compra_id):
    """Busca uma compra e seu responsável pela chave primária.

    ``compra_id`` é inteiro. Retorna uma linha ou ``None`` por ``fetchone``;
    executa apenas SELECT e pode propagar erros. O placeholder recebe uma tupla
    de um elemento e protege a consulta usada na rota de detalhes.
    """
    return get_db().execute(
        """SELECT c.*, u.nome AS usuario_nome
           FROM compras c JOIN usuarios u ON u.id = c.usuario_id WHERE c.id = ?""",
        (compra_id,),
    ).fetchone()


def listar_itens(compra_id):
    """Lista, na ordem de id, os itens pertencentes a uma compra.

    Recebe o id da compra e retorna lista de linhas via ``fetchall``; não escreve.
    Pode propagar erros SQL/contexto. ``WHERE compra_id = ?`` implementa o lado
    muitos da relação e a tupla separa o valor do comando.
    """
    return get_db().execute(
        "SELECT * FROM itens_compra WHERE compra_id = ? ORDER BY id", (compra_id,)
    ).fetchall()


def finalizar(usuario_id, carrinho):
    """Grava compra/itens e baixa estoque como uma única transação.

    Parâmetros:
        usuario_id: Id do responsável armazenado na sessão autenticada.
        carrinho: Lista de itens com ``produto_id``, nome, preço e quantidade.

    Retorno:
        Id da compra criada, obtido de ``cursor.lastrowid``.

    Efeitos colaterais:
        Faz SELECTs de revalidação, INSERT no cabeçalho, INSERTs de itens, UPDATEs
        de estoque e um único commit. Qualquer exceção executa rollback e é
        relançada, evitando uma venda parcialmente gravada.

    Possíveis erros:
        ``ValueError`` quando o produto sumiu ou o estoque mudou; erros de
        restrição/SQLite também causam rollback. É chamado pelo Controller após a
        validação preliminar do carrinho.
    """
    db = get_db()
    try:
        # A primeira passagem relê todos os produtos do banco. Não se confia no
        # preço/estoque guardado na sessão, que pode estar desatualizado.
        itens = []
        for item in carrinho:
            produto = db.execute(
                "SELECT * FROM produtos WHERE id = ?", (item["produto_id"],)
            ).fetchone()
            # ``fetchone`` produz ``None`` quando o id deixou de existir.
            if produto is None:
                raise ValueError(f"O produto {item['nome']} não existe mais.")
            if produto["estoque"] < item["quantidade"]:
                raise ValueError(f"Estoque insuficiente para {produto['nome']}.")
            itens.append((produto, item["quantidade"]))

        # O total é recalculado com preços atuais vindos do banco.
        total = sum(p["preco_centavos"] * qtd for p, qtd in itens)
        # O INSERT usa placeholders e inicia o cabeçalho da venda.
        cursor = db.execute(
            "INSERT INTO compras (usuario_id, total_centavos) VALUES (?, ?)",
            (usuario_id, total),
        )
        # ``lastrowid`` liga todos os itens à chave gerada para o cabeçalho.
        compra_id = cursor.lastrowid
        for produto, quantidade in itens:
            subtotal = produto["preco_centavos"] * quantidade
            # O item guarda nome e preço como fotografia histórica da venda.
            db.execute(
                """INSERT INTO itens_compra
                   (compra_id, produto_id, produto_nome, preco_unitario_centavos,
                    quantidade, subtotal_centavos) VALUES (?, ?, ?, ?, ?, ?)""",
                (compra_id, produto["id"], produto["nome"],
                 produto["preco_centavos"], quantidade, subtotal),
            )
            # O UPDATE subtrai no próprio banco e limita a baixa ao produto atual.
            db.execute(
                "UPDATE produtos SET estoque = estoque - ? WHERE id = ?",
                (quantidade, produto["id"]),
            )
        # Um único commit confirma cabeçalho, itens e todas as baixas juntos.
        db.commit()
        return compra_id
    except Exception:
        # Rollback desfaz toda a unidade de trabalho; ``raise`` preserva tipo e traceback.
        db.rollback()
        raise


def quantidade_total():
    """Conta compras concluídas para o painel.

    Não recebe parâmetros; retorna inteiro lido do alias ``total``. Executa apenas
    SELECT com ``COUNT(*)`` e pode propagar erros SQLite/contexto.
    """
    return get_db().execute("SELECT COUNT(*) AS total FROM compras").fetchone()["total"]
