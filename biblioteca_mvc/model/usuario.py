from model.database import Database

class Usuario:
	def criar_tabela():
		conn=Database.conectar()
		cursor=conn.cursor()
		cursor.execute("""
		CREATE TABLE IF NOT EXISTS usuarios(
			
		id INTEGER PRIMARY KEY,	
	
		login TEXT,

		senha TEXT

		)
		""")

		conn.commit()

	def cadastrar(login,senha):
		conn=Database.conectar()
		cursor=conn.cursor()
		cursor.execute(
		"""
	
		INSERT INTO usuarios
		VALUES(
		NULL,
		?,
		?
		)
		""",
		(login,senha)
		)
		
		conn.commit()
