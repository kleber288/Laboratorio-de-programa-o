from model.database import Database

class LoginController:
	def autenticar(login, senha):
		conn=Database.conectar()
		cursor=conn.cursor()
		cursor.execute(
		"""
		SELECT * 
		FROM usuarios
		
		WHERE
		login=?
		AND
		senha=?
		""",
		
		(
			login, 
			senha
		)
		)
		return cursor.fetchone()

