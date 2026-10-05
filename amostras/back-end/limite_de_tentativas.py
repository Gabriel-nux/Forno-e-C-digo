import hashlib
import hmac

from config import jwt_segredo
from repositorios import limite

LOGIN_PAR = ("login_par", 5, 15 * 60)
LOGIN_IP = ("login_ip", 20, 15 * 60)
PEDIDO_IP = ("pedido_ip", 10, 60 * 60)


def _chave(*partes: str) -> str:
    # O banco nunca guarda e-mail nem IP em claro: só o HMAC. Se alguém levar a tabela, não descobre nada.
    return hmac.new(jwt_segredo().encode(), "\x1f".join(partes).encode(), hashlib.sha256).hexdigest()


def _espera(regra: tuple[str, int, int], chave: str) -> int:
    escopo, maximo, janela = regra
    return limite.segundos_ate_liberar(escopo, chave, maximo, janela)


def espera_do_login(email: str, ip: str) -> int:
    # Conta o par IP + e-mail, e não só o e-mail: assim um estranho não consegue trancar o dono fora da própria conta.
    # O teto por IP segura quem fica trocando de e-mail a cada tentativa.
    return max(_espera(LOGIN_PAR, _chave(ip, email)), _espera(LOGIN_IP, _chave(ip)))


def registrar_falha_de_login(email: str, ip: str) -> None:
    limite.registrar(LOGIN_PAR[0], _chave(ip, email))
    limite.registrar(LOGIN_IP[0], _chave(ip))


def limpar_falhas_do_par(email: str, ip: str) -> None:
    limite.limpar(LOGIN_PAR[0], _chave(ip, email))


def reservar_envio_de_pedido(ip: str) -> int:
    chave = _chave(ip)
    espera = _espera(PEDIDO_IP, chave)
    if espera == 0:
        limite.registrar(PEDIDO_IP[0], chave)
    return espera
