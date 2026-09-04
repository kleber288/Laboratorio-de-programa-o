"""Conversões monetárias compartilhadas entre Controllers e templates."""

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP


def moeda_para_centavos(valor):
    """Converte uma entrada monetária textual para centavos inteiros.

    Parâmetros:
        valor: Texto ou objeto convertível em texto, como ``"12,90"``.

    Retorno:
        Número inteiro de centavos, arredondado para a unidade mais próxima com
        ``ROUND_HALF_UP``.

    Efeitos colaterais:
        Nenhum; a função apenas cria valores temporários.

    Possíveis erros:
        Levanta ``ValueError`` encadeado de ``InvalidOperation`` quando o texto
        não representa um decimal. É usada pelo Controller de produtos antes de
        chamar o Model.
    """
    # Remove símbolo e espaços; se houver vírgula, interpreta pontos como
    # separadores de milhar e troca a vírgula decimal pelo ponto do ``Decimal``.
    texto = str(valor).strip().replace("R$", "").replace(" ", "")
    if "," in texto:
        texto = texto.replace(".", "").replace(",", ".")
    try:
        # Trabalhar em centavos evita erros binários de ``float`` no banco.
        return int(
            (Decimal(texto) * 100).quantize(
                Decimal("1"),
                rounding=ROUND_HALF_UP
            )
        )
    except InvalidOperation as erro:
        # O encadeamento ``from erro`` mantém a causa técnica para depuração.
        raise ValueError("Valor monetário inválido") from erro


def formatar_moeda(centavos):
    """Formata centavos inteiros no padrão monetário brasileiro.

    Parâmetros:
        centavos: Valor compatível com ``int`` armazenado pelos Models.

    Retorno:
        Texto como ``"R$ 1.234,56"``, usado pelo filtro Jinja ``moeda``.

    Efeitos colaterais:
        Nenhum.

    Possíveis erros:
        ``TypeError`` ou ``ValueError`` se ``centavos`` não puder ser convertido
        para inteiro. O filtro é registrado globalmente em ``app.py``.
    """
    valor = Decimal(int(centavos)) / 100
    # A formatação Python nasce no padrão anglófono; o marcador temporário evita
    # que a troca dos separadores de milhar e decimal conflite.
    return (
        f"R$ {valor:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )
