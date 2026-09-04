class LivroView:
	@staticmethod
	def menu():
		print("\n===== MENU =====")
		print("1 - Cadastrar livro")
		print("2 - Consultar livros")
		print("3 - Excluir livro")
		print("4 - Exportar Excel")
		print("0 - Sair")
		return input("Escolha: ")
