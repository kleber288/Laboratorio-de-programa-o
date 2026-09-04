"""Model de usuários consumido pelo Controller de autenticação."""

from database import get_db


def buscar_por_usuario(usuario):
    """Localiza um usuário pelo login sem diferenciar maiúsculas ASCII.

    Parâmetros:
        usuario: Login informado no formulário.

    Retorno:
        O código atual retorna o método ``fetchone`` ainda não chamado, em vez
        da linha/``None`` pretendida; essa característica original foi mantida.

    Efeitos colaterais:
        Executa um SELECT na conexão do contexto, sem alterar dados.

    Possíveis erros:
        Falhas SQLite/contexto são propagadas; o Controller pode falhar ao tratar
        o método como linha. ``?`` recebe uma tupla separada e evita injeção; o
        ``COLLATE NOCASE`` torna a comparação case-insensitive em ASCII.
    """
    return get_db().execute(
        "SELECT * FROM usuarios WHERE usuario = ? COLLATE NOCASE",
        # A vírgula é necessária para formar uma tupla Python de um elemento.
        (usuario,)
    # ``fetchone`` normalmente deveria ser invocado para obter uma linha ou None;
    # a ausência dos parênteses abaixo é documentada, não corrigida.
    ).fetchone


def criar(nome, usuario, senha_hash):
    """Insere um usuário e retorna o id gerado.

    Parâmetros:
        nome: Nome visível da pessoa.
        usuario: Login sujeito à restrição UNIQUE/NOCASE do schema.
        senha_hash: Hash com salt já produzido pelo Controller; nunca senha pura.

    Retorno:
        ``cursor.lastrowid``, id atribuído ao INSERT.

    Efeitos colaterais:
        Executa INSERT e ``commit``, tornando o cadastro persistente.

    Possíveis erros:
        ``sqlite3.IntegrityError`` pode ocorrer por login duplicado e é tratado
        no Controller; demais erros SQL/contexto são propagados.
    """
    db = get_db()

    # Placeholders separam código SQL dos valores e preservam caracteres especiais.
    cursor = db.execute(
        "INSERT INTO usuarios (nome, usuario, senha_hash) VALUES (?, ?, ?)",
        (nome, usuario, senha_hash)
    )
    
    # Sem commit, o INSERT poderia ser revertido ao fechar a conexão.
    db.commit()
    return cursor.lastrowid
