"""
servidor.py
===========
Servidor web Flask que conecta o frontend (index.html) aos algoritmos de busca.

Endpoints disponíveis:
  GET  /                  → Serve a interface (index.html)
  GET  /api/algoritmos    → Lista os algoritmos disponíveis
  POST /api/buscar        → Executa um algoritmo específico
  POST /api/comparar      → Executa todos os algoritmos e compara

Como usar:
  pip install flask
  python servidor.py
  Abrir http://127.0.0.1:5000 no navegador
"""

import sys
import os

# Garante que os módulos da mesma pasta sejam encontrados
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, request, jsonify, send_from_directory
from controlador import executar_busca, executar_todos, listar_algoritmos

# Cria a aplicação Flask apontando para a pasta atual (onde está o index.html)
app = Flask(__name__, static_folder=".")


# ──────────────────────────────────────────────────────────────
#  ROTAS
# ──────────────────────────────────────────────────────────────

@app.route("/")
def pagina_inicial():
    """Serve o arquivo index.html da interface."""
    return send_from_directory(".", "index.html")


@app.route("/api/algoritmos")
def rota_algoritmos():
    """Retorna a lista de algoritmos com nome e complexidades."""
    return jsonify(listar_algoritmos())


@app.route("/api/buscar", methods=["POST"])
def rota_buscar():
    """
    Executa um algoritmo de busca.

    Corpo da requisição (JSON):
      {
        "texto":     "AABAACAADAABAABA",
        "padrao":    "AABA",
        "algoritmo": "kmp"
      }

    Algoritmos válidos: naive, rabin-karp, kmp, boyer-moore
    """
    dados = request.json or {}
    texto     = dados.get("texto", "")
    padrao    = dados.get("padrao", "")
    algoritmo = dados.get("algoritmo", "naive")

    resultado = executar_busca(algoritmo, texto, padrao)
    return jsonify(resultado)


@app.route("/api/comparar", methods=["POST"])
def rota_comparar():
    """
    Executa todos os algoritmos sobre o mesmo texto e padrão.
    Retorna uma lista com os resultados de cada um.

    Corpo da requisição (JSON):
      {
        "texto":  "AABAACAADAABAABA",
        "padrao": "AABA"
      }
    """
    dados  = request.json or {}
    texto  = dados.get("texto", "")
    padrao = dados.get("padrao", "")

    resultados = executar_todos(texto, padrao)
    return jsonify(resultados)


# ──────────────────────────────────────────────────────────────
#  INICIALIZAÇÃO
# ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n" + "═" * 50)
    print("  String Search Lab — Servidor iniciado")
    print("  Acesse: http://127.0.0.1:5000")
    print("═" * 50 + "\n")
    app.run(debug=True, port=5000)
