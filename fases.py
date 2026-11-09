"""Lista de fases do jogo (lidas de assets/fases/*.json)."""

from mundo.fase import Fase  # noqa: F401  (reexportada para os outros arquivos)
from spawn import carregar_fases

FASES = carregar_fases()
