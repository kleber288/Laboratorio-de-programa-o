"""Funções de conversão e apresentação de dinheiro."""

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP


def moeda_para_centavos(valor):
    texto = str(valor).strip().replace("R$", "").replace(" ", "")
    if "," in texto:
        texto = texto.replace(".", "").replace(",", ".")
    try:
        return int((Decimal(texto) * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    except InvalidOperation as erro:
        raise ValueError("Valor monetário inválido") from erro


def formatar_moeda(centavos):
    valor = Decimal(int(centavos)) / 100
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
