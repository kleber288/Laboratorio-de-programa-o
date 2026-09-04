# Biblioteca Viva

Versão do projeto Flask MVC adaptada para uma biblioteca. O sistema possui:

- autenticação e cadastro de funcionários;
- cadastro, edição, pesquisa e exclusão de livros;
- controle do total e da disponibilidade de exemplares;
- empréstimos com leitor e data prevista de devolução;
- devolução com reposição automática dos exemplares;
- histórico, indicação de atraso e exportação para Excel;
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

O banco é criado automaticamente em `instance/biblioteca.db`.
