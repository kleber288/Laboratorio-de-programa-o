# Papelaria Criativa

Versão do projeto Flask MVC adaptada para uma papelaria. O sistema possui:

- autenticação e cadastro de funcionários;
- cadastro, edição, pesquisa e exclusão de produtos;
- controle de estoque;
- carrinho e finalização de vendas com identificação do cliente;
- comprovante, histórico e exportação para Excel;
- testes de integração.

## Como executar

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Acesse `http://127.0.0.1:5000`. Primeiro login: `admin` / `admin123`.

## Testes

```bash
pytest -q
```

O banco é criado automaticamente em `instance/papelaria.db`.
