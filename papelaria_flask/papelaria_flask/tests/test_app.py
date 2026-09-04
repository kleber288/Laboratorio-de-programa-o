import io
import sqlite3

from openpyxl import load_workbook


def login(client):
    return client.post("/login", data={"usuario": "admin", "senha": "admin123"}, follow_redirects=True)


def test_visitante_e_redirecionado(client):
    resposta = client.get("/produtos")
    assert resposta.status_code == 302
    assert "/login" in resposta.headers["Location"]


def test_fluxo_de_venda(client, app):
    assert "Olá, Administrador" in login(client).get_data(as_text=True)
    resposta = client.post("/produtos/novo", data={"nome": "Caderno", "marca": "Tilibra", "categoria": "Cadernos", "preco": "24,90", "estoque": "10"}, follow_redirects=True)
    assert "Produto cadastrado" in resposta.get_data(as_text=True)
    resposta = client.post("/vendas/carrinho/adicionar", data={"produto_id": "1", "quantidade": "2"}, follow_redirects=True)
    assert "R$ 49,80" in resposta.get_data(as_text=True)
    resposta = client.post("/vendas/finalizar", data={"cliente": "Ana Souza"}, follow_redirects=True)
    pagina = resposta.get_data(as_text=True)
    assert "Venda #1" in pagina
    assert "Ana Souza" in pagina
    with sqlite3.connect(app.config["DATABASE"]) as db:
        assert db.execute("SELECT estoque FROM produtos WHERE id=1").fetchone()[0] == 8
        assert db.execute("SELECT total_centavos FROM vendas WHERE id=1").fetchone()[0] == 4980


def test_exportacoes(client):
    login(client)
    for rota, aba in [("/produtos/exportar", "Produtos"), ("/vendas/exportar", "Vendas")]:
        resposta = client.get(rota)
        assert resposta.status_code == 200
        assert load_workbook(io.BytesIO(resposta.data)).active.title == aba


def test_cadastro(client):
    resposta = client.post("/cadastro", data={"nome": "Maria Silva", "usuario": "maria", "senha": "senha123"}, follow_redirects=True)
    assert "Cadastro realizado" in resposta.get_data(as_text=True)
    resposta = client.post("/login", data={"usuario": "maria", "senha": "senha123"}, follow_redirects=True)
    assert "Olá, Maria Silva" in resposta.get_data(as_text=True)
