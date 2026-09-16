from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


def asset(*partes):
    return BASE_DIR.joinpath("assets", *partes)