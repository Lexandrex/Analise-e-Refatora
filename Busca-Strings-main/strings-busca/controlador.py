"""
controlador.py
==============
Camada intermediária entre a interface web e os algoritmos de busca.

Responsabilidades:
  - Manter o registro de algoritmos disponíveis
  - Executar o algoritmo escolhido
  - Converter o resultado (objetos Python) em dicionários JSON-serializáveis
  - Expor funções simples para o servidor chamar
"""

from typing import List, Dict, Any
from algoritmos import (
    EstrategiaDeBusca, ResultadoBusca,
    BuscaNaive, BuscaRabinKarp, BuscaKMP, BuscaBoyerMoore,
)


# ──────────────────────────────────────────────────────────────
#  REGISTRO DE ALGORITMOS
#  Adicionar um novo algoritmo aqui é suficiente para que
#  apareça automaticamente na interface.
# ──────────────────────────────────────────────────────────────

ALGORITMOS: Dict[str, EstrategiaDeBusca] = {
    "naive":        BuscaNaive(),
    "rabin-karp":   BuscaRabinKarp(),
    "kmp":          BuscaKMP(),
    "boyer-moore":  BuscaBoyerMoore(),
}


# ──────────────────────────────────────────────────────────────
#  FUNÇÕES PÚBLICAS
# ──────────────────────────────────────────────────────────────

def executar_busca(algoritmo: str, texto: str, padrao: str) -> Dict[str, Any]:
    """
    Executa um único algoritmo e retorna o resultado como dicionário.
    Chamada pelo endpoint POST /api/buscar.
    """
    estrategia = ALGORITMOS.get(algoritmo)

    if estrategia is None:
        return {"erro": f"Algoritmo desconhecido: '{algoritmo}'"}

    resultado = estrategia.buscar(texto, padrao)
    return _para_dict(resultado)


def executar_todos(texto: str, padrao: str) -> List[Dict[str, Any]]:
    """
    Executa TODOS os algoritmos sobre o mesmo texto/padrão.
    Chamada pelo endpoint POST /api/comparar.
    Útil para a aba de comparação da interface.
    """
    return [_para_dict(estrategia.buscar(texto, padrao)) for estrategia in ALGORITMOS.values()]


def listar_algoritmos() -> List[Dict[str, str]]:
    """
    Retorna a lista de algoritmos disponíveis com seus metadados.
    Chamada pelo endpoint GET /api/algoritmos.
    """
    return [
        {
            "id":      chave,
            "nome":    estrategia.nome,
            "melhor":  estrategia.complexidade_melhor,
            "medio":   estrategia.complexidade_media,
            "pior":    estrategia.complexidade_pior,
        }
        for chave, estrategia in ALGORITMOS.items()
    ]


# ──────────────────────────────────────────────────────────────
#  SERIALIZAÇÃO
#  Converte os dataclasses Python em dicionários simples
#  que podem ser enviados como JSON para o frontend.
# ──────────────────────────────────────────────────────────────

def _para_dict(resultado: ResultadoBusca) -> Dict[str, Any]:
    """Converte um ResultadoBusca em dicionário JSON-serializável."""
    return {
        "algoritmo":       resultado.algoritmo,
        "posicoes":        resultado.posicoes,
        "comparacoes":     resultado.comparacoes,
        "tempo_ms":        round(resultado.tempo_ms, 4),
        "tamanho_texto":   len(resultado.texto),
        "tamanho_padrao":  len(resultado.padrao),
        "complexidade": {
            "melhor": resultado.complexidade_melhor,
            "medio":  resultado.complexidade_media,
            "pior":   resultado.complexidade_pior,
        },
        "tabelas_extras": resultado.tabelas_extras,
        "passos": [
            {
                "numero":          passo.numero_passo,
                "posicao_texto":   passo.posicao_texto,
                "posicao_padrao":  passo.posicao_padrao,
                "descricao":       passo.descricao,
                "houve_match":     passo.houve_match,
                "destaque_texto":  passo.destaque_texto,
                "destaque_padrao": passo.destaque_padrao,
                "dados_extras":    passo.dados_extras,
            }
            for passo in resultado.passos
        ],
    }
