from model.database import Database
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials


class Livro:
    @staticmethod
    def criar():
        conn = Database.conectar()
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS livros(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT,
                autor1 TEXT,
                autor2 TEXT,
                autor3 TEXT,
                isbn TEXT,
                assunto TEXT,
                edicao TEXT,
                editora TEXT,
                ano INTEGER
            )
            """
        )
        conn.commit()
        conn.close()

    @staticmethod
    def inserir(titulo, autor1, autor2, autor3, isbn, assunto, edicao, editora, ano):
        conn = Database.conectar()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO livros(
                titulo,
                autor1,
                autor2,
                autor3,
                isbn,
                assunto,
                edicao,
                editora,
                ano
            )
            VALUES(
                ?,?,?,?,?,?,?,?,?
            )
            """,
            (
                titulo,
                autor1,
                autor2,
                autor3,
                isbn,
                assunto,
                edicao,
                editora,
                ano,
            ),
        )
        conn.commit()
        conn.close()

    @staticmethod
    def consultar():
        conn = Database.conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM livros")
        resultado = cursor.fetchall()
        conn.close()
        return resultado

    @staticmethod
    def excluir(id_livro):
        conn = Database.conectar()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM livros WHERE id=?", (id_livro,))
        conn.commit()
        conn.close()

    @staticmethod
    def exportar():
        try:
            # 1. Pega os dados do seu banco SQLite
            conn = Database.conectar()
            df = pd.read_sql("SELECT * FROM livros", conn)
            conn.close()

            # 2. Configura as permissões para a API do Google
            escopos = [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive",
            ]

            # Lê o arquivo de chaves que você vai baixar do Google
            credenciais = Credentials.from_service_account_file(
                "credenciais.json",
                scopes=escopos,
            )
            cliente = gspread.authorize(credenciais)

            # 3. Abre a planilha no Google Sheets pelo nome
            # ATENÇÃO: Substitua pelo nome exato da sua planilha
            planilha = cliente.open("Minha Biblioteca Python")
            aba = planilha.sheet1

            # 4. Transforma o DataFrame do Pandas em uma lista para o Google Sheets entender
            dados = [df.columns.values.tolist()] + df.values.tolist()

            # 5. Limpa a aba antiga e escreve os dados novos
            aba.clear()
            aba.update(values=dados, range_name="A1")

            print("Exportação para o Google Sheets concluída com sucesso!")
        except FileNotFoundError:
            print("Erro: O arquivo 'credenciais.json' não foi encontrado na pasta do projeto.")
        except gspread.exceptions.SpreadsheetNotFound:
            print("Erro: A planilha não foi encontrada. Verifique o nome e se ela foi compartilhada com o bot.")
        except Exception as erro:
            print(f"Erro inesperado: {erro}")
