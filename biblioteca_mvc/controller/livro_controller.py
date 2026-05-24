from model.livro import Livro

class LivroController:
	@staticmethod
	def cadastrar():
		titulo = input("Titulo: ")
		autores = []
		for i in range(3):
			autores.append(
				input(f"Autor {i+1}: ")
			)
		isbn =  input("ISBN: ")
		assunto = input("Assunto: ")
		edicao = input("Edicao: ")
		editora = input("Editora: ")
		ano = input("Ano: ")
		Livro.inserir(
			titulo, 
			autores[0], 
			autores[1], 
			autores[2], 
			isbn, 
			assunto, 
			edicao, 
			editora,
			ano
		)
		print("Livro cadastrado com sucesso!")
	@staticmethod
	def consultar():
		livros = Livro.consultar()
		print("\n=== LISTA DE LIVROS ===")
		for livro in livros:
			print(livro)
	@staticmethod
	def excluir():
		id_livro = input("ID do livro para excluir: ")
		Livro.excluir(id_livro)
		print("Livro excluido!")
