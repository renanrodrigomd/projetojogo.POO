import os
import pygame

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__))
IMAGES_DIR = os.path.join(
    BASE_DIR, "assets","images"
)

_cache={}
_warn = set()

def _placeholder(size,color=(255,0,255)):
    surf = pygame.Surface(size,pygame.SRCALPHA)
    surf.fill(*color,180)
    pygame.draw.rect(surf,(255,255,255),
                     surf.get_rect(),2)
    return surf

def load_image(relative_path, tamanho=None,
               fallback_color=(255,0,255)):
    chave = (relative_path,tamanho)
    if chave in _cache:
        return _cache[chave]
    full_path = os.path.join(IMAGES_DIR,
                             relative_path)
    if not os.path.isfile(full_path):
        if relative_path not in _warn:
            _warn.add(relative_path)
        image = _placeholder(tamanho or (32,32),
                             fallback_color)
    else:
        image = pygame.image.load(full_path)
        image = image.convert_alpha()
        if tamanho is not None and image.get_size() != tamanho:
            image = pygame.transform.smoothscale(image,tamanho)
    
    