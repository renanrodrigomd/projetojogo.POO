"""Recordes salvos em arquivo (dados/recordes.json), um por fase."""

import json

from caminhos import BASE_DIR


class Recordes:
    ARQUIVO = BASE_DIR / "dados" / "recordes.json"

    def __init__(self):
        self._dados = self._carregar()

    def _carregar(self):
        try:
            with open(self.ARQUIVO, encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
            return dados if isinstance(dados, dict) else {}
        except (OSError, ValueError):
            return {}

    def _salvar(self):
        try:
            self.ARQUIVO.parent.mkdir(parents=True, exist_ok=True)
            with open(self.ARQUIVO, "w", encoding="utf-8") as arquivo:
                json.dump(self._dados, arquivo, indent=2)
        except OSError:
            pass  # sem permissão de escrita: o jogo segue normalmente

    def melhor(self, numero_fase):
        """Devolve {'pontos','tempo','estrelas'} ou None."""
        return self._dados.get(str(numero_fase))

    def registrar(self, numero_fase, pontos, tempo, estrelas):
        """Guarda os melhores valores. Devolve True se bateu o recorde
        de pontos (ou se foi a primeira vez que a fase foi concluída)."""
        anterior = self.melhor(numero_fase)

        if anterior is None:
            novo = {"pontos": pontos, "tempo": tempo, "estrelas": estrelas}
            recorde = True
        else:
            novo = {
                "pontos": max(anterior["pontos"], pontos),
                "tempo": min(anterior["tempo"], tempo),
                "estrelas": max(anterior["estrelas"], estrelas),
            }
            recorde = pontos > anterior["pontos"]

        self._dados[str(numero_fase)] = novo
        self._salvar()

        return recorde
