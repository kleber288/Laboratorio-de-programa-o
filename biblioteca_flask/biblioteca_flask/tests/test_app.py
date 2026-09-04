import io
import sqlite3

from openpyxl import load_workbook


def login(client):
    return client.post("/login", data={"usuario": "admin", "senha": "admin123"}, follow_redirects=True)


def test_visitante_e_redirecionado(client):
    resposta = client.get("/livros")
    assert resposta.status_code == 302
    assert "/login" in resposta.headers["Location"]


def test_emprestimo_e_devolucao(client, app):
    assert "Olá, Administrador" in login(client).get_data(as_text=True)
    resposta = client.post("/livros/novo", data={"titulo": "Dom Casmurro", "autor": "Machado de Assis", "isbn": "978-85-000-0000-1", "categoria": "Romance", "ano_publicacao": "1899", "exemplares_total": "3"}, follow_redirects=True)
    assert "Livro cadastrado" in resposta.get_data(as_text=True)
    resposta = client.post("/emprestimos/carrinho/adicionar", data={"livro_id": "1", "quantidade": "1"}, follow_redirects=True)
    assert "Dom Casmurro" in resposta.get_data(as_text=True)
    resposta = client.post("/emprestimos/finalizar", data={"leitor": "Ana Souza", "data_prevista": "2099-12-31"}, follow_redirects=True)
    pagina = resposta.get_data(as_text=True)
    assert "Empréstimo #1" in pagina
    assert "Ana Souza" in pagina
    with sqlite3.connect(app.config["DATABASE"]) as db:
        assert db.execute("SELECT exemplares_disponiveis FROM livros WHERE id=1").fetchone()[0] == 2
    resposta = client.post("/emprestimos/1/devolver", follow_redirects=True)
    assert "Devolução registrada" in resposta.get_data(as_text=True)
    with sqlite3.connect(app.config["DATABASE"]) as db:
        assert db.execute("SELECT exemplares_disponiveis FROM livros WHERE id=1").fetchone()[0] == 3
        assert db.execute("SELECT status FROM emprestimos WHERE id=1").fetchone()[0] == "DEVOLVIDO"


def test_exportacoes(client):
    login(client)
    for rota, aba in [("/livros/exportar", "Livros"), ("/emprestimos/exportar", "Empréstimos")]:
        resposta = client.get(rota)
        assert resposta.status_code == 200
        assert load_workbook(io.BytesIO(resposta.data)).active.title == aba


def test_isbn_repetido(client):
    login(client)
    dados = {"titulo": "Livro A", "autor": "Autora", "isbn": "123", "categoria": "Conto", "ano_publicacao": "2020", "exemplares_total": "1"}
    client.post("/livros/novo", data=dados)
    resposta = client.post("/livros/novo", data=dados, follow_redirects=True)
    assert "Já existe um livro com esse ISBN" in resposta.get_data(as_text=True)
