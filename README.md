# 🎮 SmachTech: Invasion Robotics
## Desenvolvedores do jogo:
Renan Rodrigo Medeios Dantas
Gustavo Medeiros Lucena
Juan Oliveira Fonseca

---
## 1. Título do Jogo

**SmachTech: Invasion Robotics**
Jogo de ação e plataforma em um mundo futurista dominado por robôs.

---

## 2. Descrição Geral

SmachTech: Invasion Robotics é um jogo de ação e plataforma com progressão por fases. O jogador enfrenta inimigos em uma cidade tecnológica destruída, exigindo movimentação constante e decisões rápidas para sobreviver.

---

## 3. Objetivo do Jogo

O jogador deve:

* Sobreviver durante a fase
* Derrotar inimigos
* Coletar itens
* Chegar ao final do mapa

Objetivo final: completar todas as fases e derrotar Romero Merito

---

## 4. Personagem Principal

**Nome:** Gepeto

**Descrição:**
Gebeto é um humano modificado criado por seu pai, um cientista obcecado pela criação de robôs autônomos. Após anos sendo usado como experimento, ele se rebela e parte em busca de vingança contra seu pai que agora, ja se transfomou em um ciborgue.

**Movimentação:**

* Esquerda e direita (eixo X)
* Pular (eixo Y)

**Atributos:**

* Vida
* Armas
* Tempo de fase

---

## 5. Inimigos e Obstáculos

**Tipos de inimigos:**

* Robôs terrestres
* Robôs aéreos

**Comportamentos:**

* Perseguem o jogador
* Permanecem parados como obstáculos

**Colisão:**

* O jogador perde vida ao encostar em inimigos, tiros ou explosões

---

## 6. Cenário (Mapa)

Cidade destruída/caótica.

**Elementos:**

* Prédios em ruínas
* Fogo
* Estruturas em ruínas

**Mapa:**

* Caminhos com obstáculos e plataformas
* Limites que não podem ser ultrapassados
* Final da fase localizado à direita

**Itens:**

* Dropados por inimigos
* Incluem armas e melhorias

---

## 7. Sistema de Pontuação

Baseado no tempo de conclusão da fase:

* ≤ 37 segundos → ⭐⭐⭐
* ≤ 42 segundos → ⭐⭐
* ≥ 50 segundos → ⭐

**Bônus:**

* Eliminar inimigos em sequência reduz o tempo (sistema de combo)

---

## 8. Sistema de Vida

* 3 vidas por fase

**Perde vida ao:**

* Encostar em inimigos
* Ser atingido por tiros
* Entrar em explosões

**Ao perder todas as vidas:**

* A fase reinicia
* Sem melhorias acumuladas

---

## 9. Controles

* A → esquerda
* D → direita
* Space → pular
* K → atirar

---

## 10. Fluxo do Jogo

1. Menu principal
2. Seleção de fase
3. Escolha de equipamentos
4. Início da fase
5. Durante o jogo:

   * Combate com inimigos
   * Coleta de itens
   * Progressão pelo mapa
6. Final:

   * Vitória: chegar ao final vivo
   * Derrota: perder todas as vidas

---

## 11. Regras do Jogo

* Não atravessar paredes ou o chão
* Respeitar os limites do mapa
* Itens coletados por contato
* Colisões causam dano
* O jogador deve chegar ao final da fase

---

## 12. Estrutura do Projeto

Organização sugerida:

* `Player.py` → personagem principal
* `Inimigos.py` → lógica dos inimigos
* `Mapa.py` → cenário
* `Jogo.py` → lógica principal
* `Menu.py` → interface
* `Fases.py` → controle de fases

---

## 13. Funcionalidades Mínimas

Primeira versão deve conter:

* Movimento do jogador
* Sistema de pulo
* Colisão
* Inimigos básicos
* Sistema de vida
* Final de fase
* Menu simples

---

## 14. Melhorias Futuras

* Agachar
* Tiros diagonais
* Novos tipos de inimigos
* Sistema de upgrades
* Mais armas
* Mais fases
* Chefes intermediários
* Melhorias visuais e sonoras
* Recarga de munição
* Trocar de arma durante a fase

---

## 🧠 Boss Final

**Nome:** Romero Merito

O chefe final representa o ápice do sistema robótico e será o maior desafio do jogo, exigindo habilidade e estratégia do jogador.
 
