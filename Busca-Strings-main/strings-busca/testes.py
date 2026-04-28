"""
testes.py
=========
Testes automatizados para todos os algoritmos de busca.

Como rodar:
  python testes.py

Cada algoritmo é testado com os mesmos casos, garantindo que todos
retornam exatamente as mesmas posições (a interface é a mesma, Strategy!).
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from algoritmos import BuscaIngenua, BuscaRabinKarp, BuscaKMP, BuscaBoyerMoore

# Lista de algoritmos a testar
ALGORITMOS = [
    BuscaIngenua(),
    BuscaRabinKarp(),
    BuscaKMP(),
    BuscaBoyerMoore(),
]

# Casos de teste: (texto, padrão, posições_esperadas)
CASOS_DE_TESTE = [
    # Casos básicos
    ("AABAACAADAABAABA", "AABA",   [0, 9, 12]),
    ("abcabcabc",        "abc",    [0, 3, 6]),
    ("hello mundo",      "mundo",  [6]),

    # Padrão no fim
    ("abcdef",           "ef",     [4]),

    # Muitas ocorrências sobrepostas
    ("aaaaaaa",          "aaa",    [0, 1, 2, 3, 4]),

    # Sem ocorrência
    ("abcdef",           "xyz",    []),

    # Entradas vazias
    ("",                 "abc",    []),
    ("abc",              "",       []),

    # Padrão igual ao texto
    ("abc",              "abc",    [0]),

    # Clássico de algoritmos
    ("GEEKS FOR GEEKS",  "GEEKS",  [0, 10]),

    # Sobreposição parcial
    ("aabaabaab",        "aab",    [0, 3, 6]),

    # Padrão quase certo mas falha no fim
    ("abcabdabc",        "abc",    [0, 6]),
]


def executar_testes():
    total = 0
    passou = 0

    print("\n" + "═" * 65)
    print("  String Search Lab — Suite de Testes")
    print("═" * 65)

    for algoritmo in ALGORITMOS:
        print(f"\n── {algoritmo.nome} " + "─" * (50 - len(algoritmo.nome)))

        for texto, padrao, esperado in CASOS_DE_TESTE:
            resultado = algoritmo.buscar(texto, padrao)
            encontrado = sorted(resultado.posicoes)
            correto = (encontrado == sorted(esperado))

            total += 1
            if correto:
                passou += 1

            # Formata a linha de saída
            simbolo = "✅" if correto else "❌"
            texto_curto = f'"{texto[:22]}{"…" if len(texto) > 22 else ""}"'
            padrao_curto = f'"{padrao}"'
            label = f"{texto_curto} / {padrao_curto}"

            print(f"  {simbolo}  {label:<40}  pos={encontrado}")

            if not correto:
                print(f"       Esperado: {esperado}")

    # Resumo final
    percentual = int(passou / total * 100) if total else 0
    print("\n" + "═" * 65)
    if passou == total:
        print(f"  ✅ Todos os testes passaram! {passou}/{total} (100%)")
    else:
        print(f"  ⚠️  {passou}/{total} testes passaram ({percentual}%)")
    print("═" * 65 + "\n")


if __name__ == "__main__":
    executar_testes()
