import unittest

from pydantic import ValidationError

from esquemas.pedidos import PedidoEntrada
from repositorios.pedidos import ProdutoDoCardapio
from servicos import pedidos as servico

CARDAPIO = {
    "calabresa": ProdutoDoCardapio(id=1, nome="Calabresa", precos_centavos={"broto": 2295, "grande": 4590}),
    "margherita": ProdutoDoCardapio(id=2, nome="Margherita", precos_centavos={"broto": 2600, "grande": 5200, "familia": 6240}),
}


def pedido(*itens):
    return PedidoEntrada.model_validate(
        {
            "contato_nome": "Ana",
            "contato_telefone": "(11) 91234-5678",
            "endereco_entrega": "Rua das Flores, 100",
            "itens": list(itens),
        }
    )


def inteira(produto, tamanho, quantidade=1):
    return {"tipo": "inteira", "produto": produto, "tamanho": tamanho, "quantidade": quantidade}


def meio(a, b, tamanho, quantidade=1):
    return {"tipo": "meio", "produto": a, "produto_metade": b, "tamanho": tamanho, "quantidade": quantidade}


class TestPrecificar(unittest.TestCase):
    def preco(self, *itens):
        feitos, total = servico.precificar(pedido(*itens).itens, CARDAPIO)
        return [(p.nome, p.preco_unitario_centavos) for p in feitos], total

    def test_inteira_usa_o_preco_do_tamanho(self):
        self.assertEqual(self.preco(inteira("calabresa", "broto")), ([("Calabresa", 2295)], 2295))

    def test_quantidade_multiplica(self):
        self.assertEqual(self.preco(inteira("calabresa", "grande", 3))[1], 3 * 4590)

    def test_meio_a_meio_cobra_o_sabor_mais_caro_em_qualquer_ordem(self):
        for a, b in (("calabresa", "margherita"), ("margherita", "calabresa")):
            with self.subTest(a=a):
                itens, total = self.preco(meio(a, b, "grande"))
                self.assertEqual(total, 5200)
                self.assertEqual(itens[0][1], 5200)

    def test_total_soma_todos_os_itens(self):
        _, total = self.preco(inteira("calabresa", "grande"), meio("calabresa", "margherita", "grande", 2))
        self.assertEqual(total, 4590 + 2 * 5200)

    def test_sabor_fora_do_cardapio_recusa_e_nomeia_o_sabor(self):
        with self.assertRaises(servico.ProdutoIndisponivel) as erro:
            self.preco(inteira("fantasma", "grande"))
        self.assertIn("fantasma", str(erro.exception))

    def test_meio_a_meio_exige_preco_nos_dois_sabores(self):
        with self.assertRaises(servico.ProdutoIndisponivel):
            self.preco(meio("calabresa", "margherita", "familia"))

    def test_o_cliente_nao_consegue_mandar_preco_nem_total(self):
        for campo in ("preco_centavos", "total_centavos", "preco_unitario_centavos"):
            with self.subTest(campo=campo):
                with self.assertRaises(ValidationError):
                    pedido({**inteira("calabresa", "grande"), campo: 1})
