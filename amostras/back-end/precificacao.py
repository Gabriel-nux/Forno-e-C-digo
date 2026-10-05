from dataclasses import dataclass

from esquemas.pedidos import ItemEntrada, ItemMeio
from repositorios.pedidos import ProdutoDoCardapio


class ProdutoIndisponivel(Exception):
    def __init__(self, descricao: str):
        super().__init__(descricao)
        self.descricao = descricao


@dataclass(frozen=True)
class ItemPrecificado:
    entrada: ItemEntrada
    produto_id: int
    produto_metade_id: int | None
    nome: str
    preco_unitario_centavos: int


def _preco(slug: str, tamanho: str, cardapio: dict[str, ProdutoDoCardapio]) -> tuple[ProdutoDoCardapio, int]:
    produto = cardapio.get(slug)
    if produto is None:
        raise ProdutoIndisponivel(f"O sabor '{slug}' não está disponível.")
    preco = produto.precos_centavos.get(tamanho)
    if preco is None:
        raise ProdutoIndisponivel(f"{produto.nome} não tem o tamanho {tamanho}.")
    return produto, preco


def precificar(itens: list[ItemEntrada], cardapio: dict[str, ProdutoDoCardapio]) -> tuple[list[ItemPrecificado], int]:
    # Quem manda o pedido nunca manda preço. O servidor olha o cardápio e faz a conta,
    # tudo em centavos inteiros pra não ter surpresa com ponto flutuante.
    precificados: list[ItemPrecificado] = []
    for item in itens:
        a, preco_a = _preco(item.produto, item.tamanho, cardapio)
        if isinstance(item, ItemMeio):
            b, preco_b = _preco(item.produto_metade, item.tamanho, cardapio)
            precificados.append(ItemPrecificado(item, a.id, b.id, f"{a.nome} / {b.nome}", max(preco_a, preco_b)))
        else:
            precificados.append(ItemPrecificado(item, a.id, None, a.nome, preco_a))
    total = sum(p.preco_unitario_centavos * p.entrada.quantidade for p in precificados)
    return precificados, total
