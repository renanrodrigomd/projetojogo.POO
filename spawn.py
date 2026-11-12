"""Carregador de fases: transforma assets/fases/fase_*.json em objetos Fase.

Para criar uma fase nova basta copiar um arquivo .json e editar. Veja
assets/fases/LEIA-ME.txt. Erros de digitação viram mensagens claras
(com o nome do arquivo) em vez de travar o jogo no meio da partida.
"""

import json

from caminhos import asset
from Inimigos import (
    InimigoTerrestre, InimigoAereo, InimigoBlindado, InimigoExplosivo,
)
from mundo.elementos import (
    Plataforma, Barreira, PocaEnergia, PilarEletrico, Checkpoint,
    KitVida, Escudo, RelogioTempo,
)
from mundo.fase import Fase


class ErroDeFase(ValueError):
    """Problema encontrado ao ler um arquivo de fase."""


TIPOS_INIMIGO = {
    "terrestre": InimigoTerrestre,
    "aereo": InimigoAereo,
    "blindado": InimigoBlindado,
    "explosivo": InimigoExplosivo,
}

# categoria -> {tipo: classe}. None = categoria sem subtipos.
REGISTRO = {
    "plataformas": {None: Plataforma},
    "barreiras": {None: Barreira},
    "perigos": {"poca": PocaEnergia, "pilar": PilarEletrico},
    "checkpoints": {None: Checkpoint},
    "itens": {"vida": KitVida, "escudo": Escudo, "relogio": RelogioTempo},
}


def _exigir(dados, campo, contexto):
    if campo not in dados:
        raise ErroDeFase(f"{contexto}: falta o campo '{campo}'.")
    return dados[campo]


def _ler_inimigos(dados, largura, arquivo):
    inimigos = []

    for i, item in enumerate(dados.get("inimigos", []), start=1):
        contexto = f"{arquivo}, inimigos #{i}"
        tipo = _exigir(item, "tipo", contexto)

        if tipo not in TIPOS_INIMIGO:
            raise ErroDeFase(
                f"{contexto}: tipo '{tipo}' inválido "
                f"(use: {', '.join(TIPOS_INIMIGO)})."
            )

        x = _exigir(item, "x", contexto)

        if not 0 <= x <= largura:
            raise ErroDeFase(f"{contexto}: x={x} fora do mapa (0 a {largura}).")

        altura = item.get("altura", 220 if tipo == "aereo" else 0)
        inimigos.append((TIPOS_INIMIGO[tipo], x, altura))

    return inimigos


def _ler_elementos(dados, largura, arquivo):
    elementos = {}

    for categoria, tipos in REGISTRO.items():
        lista = []

        for i, item in enumerate(dados.get(categoria, []), start=1):
            contexto = f"{arquivo}, {categoria} #{i}"

            if None in tipos:
                classe = tipos[None]
            else:
                tipo = _exigir(item, "tipo", contexto)

                if tipo not in tipos:
                    raise ErroDeFase(
                        f"{contexto}: tipo '{tipo}' inválido "
                        f"(use: {', '.join(tipos)})."
                    )

                classe = tipos[tipo]

            x = _exigir(item, "x", contexto)

            if not 0 <= x <= largura:
                raise ErroDeFase(
                    f"{contexto}: x={x} fora do mapa (0 a {largura})."
                )

            try:
                classe.de_dados(item)  # teste: falha cedo se faltar campo
            except KeyError as erro:
                raise ErroDeFase(
                    f"{contexto}: falta o campo {erro}."
                ) from None
            except ValueError as erro:
                raise ErroDeFase(f"{contexto}: {erro}") from None

            lista.append((classe, item))

        elementos[categoria] = lista

    return elementos


def carregar_fase(caminho):
    arquivo = caminho.name

    try:
        with open(caminho, encoding="utf-8") as f:
            dados = json.load(f)
    except OSError as erro:
        raise ErroDeFase(f"{arquivo}: não consegui abrir ({erro}).") from None
    except ValueError as erro:
        raise ErroDeFase(f"{arquivo}: JSON inválido ({erro}).") from None

    numero = _exigir(dados, "numero", arquivo)
    nome = _exigir(dados, "nome", arquivo)
    largura = _exigir(dados, "largura", arquivo)
    final = _exigir(dados, "final", arquivo)

    if final >= largura:
        raise ErroDeFase(f"{arquivo}: 'final' precisa ser menor que 'largura'.")

    return Fase(
        numero, nome, largura, final,
        _ler_inimigos(dados, largura, arquivo),
        tempo_tres_estrelas=dados.get("tempo_tres_estrelas", 30),
        tempo_duas_estrelas=dados.get("tempo_duas_estrelas", 45),
        elementos=_ler_elementos(dados, largura, arquivo),
        intensidade_destrocos=dados.get("destrocos", 1.0),
    )


def carregar_fases(pasta=None):
    pasta = pasta or asset("fases")
    arquivos = sorted(pasta.glob("fase_*.json"))

    if not arquivos:
        raise ErroDeFase(f"Nenhuma fase encontrada em {pasta}.")

    fases = [carregar_fase(arquivo) for arquivo in arquivos]

    numeros = [fase.numero for fase in fases]
    if len(set(numeros)) != len(numeros):
        raise ErroDeFase("Há duas fases com o mesmo 'numero'.")

    return sorted(fases, key=lambda fase: fase.numero)
