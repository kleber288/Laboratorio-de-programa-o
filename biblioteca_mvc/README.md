# Sistema de Gerenciamento de Biblioteca

Um sistema de gerenciamento de biblioteca desenvolvido em Python com interface no terminal. Este projeto foi iniciado na disciplina de Laboratório de Programação e aprimorado em casa com a integração à API do Google Sheets para exportação de dados diretamente para a nuvem.

## Funcionalidades

- Cadastro de novos usuários e sistema de autenticação (login).
- Cadastro detalhado de livros (título, autores, ISBN, assunto, edição, editora, ano).
- Listagem de todos os livros cadastrados no sistema.
- Exclusão de livros utilizando o ID.
- **Integração Cloud:** Exportação automática do banco de dados direto para o Google Sheets.

## Tecnologias Utilizadas

- **Linguagem:** Python
- **Banco de Dados Local:** SQLite3
- **Manipulação de Dados:** Pandas e Openpyxl
- **Integração na Nuvem:** `gspread` e `google-auth` (Google Cloud APIs)
- **Arquitetura:** Baseado no padrão MVC (Model, View, Controller)

## Como executar o projeto na sua máquina

### 1. Clonar e Instalar Dependências
Primeiro, faça o clone deste repositório. Certifique-se de ter o Python instalado e instale as bibliotecas necessárias executando o comando abaixo no seu terminal:

```bash
pip install pandas openpyxl gspread google-auth
