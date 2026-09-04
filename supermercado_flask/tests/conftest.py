"""Fixtures compartilhadas pelos testes de integração do Mercado Fácil."""

import pytest

from app import create_app


@pytest.fixture()
def app(tmp_path):
    """Cria uma aplicação de teste isolada.

    Parâmetros:
        tmp_path: Fixture nativa do pytest que fornece diretório temporário único.

    Retorno:
        Aplicação Flask com ``TESTING`` ativo, chave própria e banco temporário.

    Efeitos colaterais:
        A Application Factory tenta inicializar ``teste.db`` dentro do diretório
        temporário, eliminado pelo pytest ao fim da sessão.

    Possíveis erros:
        Falhas de importação ou inicialização do schema interrompem a fixture e,
        por consequência, os testes que dependem dela.
    """
    # Sobrescrever DATABASE impede que os testes modifiquem o banco de desenvolvimento.
    return create_app({"TESTING": True, "DATABASE": str(tmp_path / "teste.db"),
                       "SECRET_KEY": "chave-de-testes"})


@pytest.fixture()
def client(app):
    """Fornece um cliente HTTP sem abrir servidor ou porta de rede.

    Recebe a fixture ``app`` e retorna ``app.test_client()``. Não altera o banco
    por si só; cada chamada feita pelos testes executa middleware e rotas reais.
    Erros de criação do cliente são propagados.
    """
    return app.test_client()
