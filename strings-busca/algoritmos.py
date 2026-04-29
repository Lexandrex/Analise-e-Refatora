from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Tuple
import time

@dataclass
class PassoExecucao:
    numero_passo: int
    posicao_texto: int
    posicao_padrao: int
    descricao: str
    houve_match: bool
    destaque_texto: List[int] = field(default_factory=list)
    destaque_padrao: List[int] = field(default_factory=list)
    dados_extras: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResultadoBusca:
    algoritmo: str
    texto: str
    padrao: str
    posicoes: List[int]
    comparacoes: int
    passos: List[PassoExecucao]
    tempo_ms: float
    tabelas_extras: Dict[str, Any] = field(default_factory=dict)
    complexidade_melhor: str = ""
    complexidade_media: str = ""
    complexidade_pior: str = ""

class LoggerExecucao:
    def __init__(self):
        self.passos: List[PassoExecucao] = []
        self.numero_passo = 0
        self.comparacoes = 0

    def registrar(self, pos_texto, pos_padrao, descricao, match,
                  destaque_texto=None, destaque_padrao=None, extras=None):

        self.comparacoes += 1

        self.passos.append(PassoExecucao(
            numero_passo=self.numero_passo,
            posicao_texto=pos_texto,
            posicao_padrao=pos_padrao,
            descricao=descricao,
            houve_match=match,
            destaque_texto=destaque_texto or [],
            destaque_padrao=destaque_padrao or [],
            dados_extras=extras or {}
        ))

        self.numero_passo += 1

class EstrategiaDeBusca(ABC):
    nome: str = "Abstrato"
    complexidade_melhor: str = ""
    complexidade_media: str = ""
    complexidade_pior: str = ""

    def buscar(self, texto: str, padrao: str) -> ResultadoBusca:
        inicio = time.perf_counter()

        if self._entrada_invalida(texto, padrao):
            return self._resultado_vazio(texto, padrao, inicio)

        logger = LoggerExecucao()

        posicoes, tabelas = self._executar(texto, padrao, logger)

        tempo = (time.perf_counter() - inicio) * 1000

        return self._montar_resultado(
            texto,
            padrao,
            posicoes,
            logger.comparacoes,
            logger.passos,
            tempo,
            tabelas
        )

    @abstractmethod
    def _executar(self, texto: str, padrao: str, logger: LoggerExecucao) -> Tuple[List[int], Dict]:
        pass

    def _entrada_invalida(self, texto, padrao):
        return len(texto) == 0 or len(padrao) == 0 or len(padrao) > len(texto)

    def _resultado_vazio(self, texto, padrao, inicio):
        tempo = (time.perf_counter() - inicio) * 1000
        return self._montar_resultado(texto, padrao, [], 0, [], tempo)

    def _montar_resultado(self, texto, padrao, posicoes, comparacoes,
                          passos, tempo_ms, tabelas_extras=None) -> ResultadoBusca:
        return ResultadoBusca(
            algoritmo=self.nome,
            texto=texto,
            padrao=padrao,
            posicoes=posicoes,
            comparacoes=comparacoes,
            passos=passos,
            tempo_ms=tempo_ms,
            tabelas_extras=tabelas_extras or {},
            complexidade_melhor=self.complexidade_melhor,
            complexidade_media=self.complexidade_media,
            complexidade_pior=self.complexidade_pior,
        )

class BuscaNaive(EstrategiaDeBusca):
    nome = "Naive"
    complexidade_melhor = "O(n)"
    complexidade_media = "O(n·m)"
    complexidade_pior = "O(n·m)"

    def _executar(self, texto, padrao, logger):
        n, m = len(texto), len(padrao)
        posicoes = []

        for i in range(n - m + 1):
            if self._comparar_janela(texto, padrao, i, logger):
                posicoes.append(i)

        return posicoes, {}

    def _comparar_janela(self, texto, padrao, inicio, logger):
        m = len(padrao)

        for j in range(m):
            t = texto[inicio + j]
            p = padrao[j]
            match = t == p

            logger.registrar(
                inicio + j,
                j,
                f"texto[{inicio+j}]='{t}' vs padrão[{j}]='{p}'",
                match,
                destaque_texto=list(range(inicio, inicio + m)),
                destaque_padrao=list(range(j + 1)),
                extras={"inicio_janela": inicio}
            )

            if not match:
                return False

        return True

class BuscaRabinKarp(EstrategiaDeBusca):
    nome = "Rabin-Karp"
    complexidade_melhor = "O(n+m)"
    complexidade_media = "O(n+m)"
    complexidade_pior = "O(n·m)"

    BASE = 256
    MOD = 101

    def _executar(self, texto, padrao, logger):
        n, m = len(texto), len(padrao)
        posicoes = []
        hashes = []

        B, MOD = self.BASE, self.MOD

        h = pow(B, m - 1, MOD)

        hash_p = 0
        hash_t = 0

        for i in range(m):
            hash_p = (B * hash_p + ord(padrao[i])) % MOD
            hash_t = (B * hash_t + ord(texto[i])) % MOD

        for i in range(n - m + 1):

            if hash_p == hash_t:
                if self._confirmar(texto, padrao, i, logger):
                    posicoes.append(i)
            else:
                logger.registrar(
                    i, 0,
                    f"Hash diferente → pula",
                    False,
                    destaque_texto=list(range(i, i + m)),
                    extras={"hash_texto": hash_t, "hash_padrao": hash_p}
                )

            if i < n - m:
                hash_t = (B * (hash_t - ord(texto[i]) * h) + ord(texto[i + m])) % MOD

            hashes.append(hash_t)

        return posicoes, {"hashes": hashes}

    def _confirmar(self, texto, padrao, inicio, logger):
        for j in range(len(padrao)):
            t = texto[inicio + j]
            p = padrao[j]
            match = t == p

            logger.registrar(
                inicio + j, j,
                f"[Confirmando] {t} == {p}",
                match
            )

            if not match:
                return False

        return True

class BuscaKMP(EstrategiaDeBusca):
    nome = "KMP"
    complexidade_melhor = "O(n)"
    complexidade_media = "O(n+m)"
    complexidade_pior = "O(n+m)"

    def _executar(self, texto, padrao, logger):
        n, m = len(texto), len(padrao)
        lps = self._lps(padrao)

        posicoes = []
        i = j = 0

        while i < n:
            t, p = texto[i], padrao[j]
            match = t == p

            logger.registrar(i, j, f"{t} == {p}", match, extras={"lps": lps})

            if match:
                i += 1
                j += 1
            else:
                if j != 0:
                    j = lps[j - 1]
                else:
                    i += 1

            if j == m:
                posicoes.append(i - j)
                j = lps[j - 1]

        return posicoes, {"lps": lps}

    def _lps(self, padrao):
        lps = [0] * len(padrao)
        j = 0

        for i in range(1, len(padrao)):
            while j > 0 and padrao[i] != padrao[j]:
                j = lps[j - 1]

            if padrao[i] == padrao[j]:
                j += 1
                lps[i] = j

        return lps

class BuscaBoyerMoore(EstrategiaDeBusca):
    nome = "Boyer-Moore"

    def _executar(self, texto, padrao, logger):
        n, m = len(texto), len(padrao)
        tabela = self._tabela_mc(padrao)

        posicoes = []
        shift = 0

        while shift <= n - m:
            j = m - 1

            while j >= 0:
                t = texto[shift + j]
                p = padrao[j]
                match = t == p

                logger.registrar(shift + j, j, f"{t} == {p}", match)

                if not match:
                    break
                j -= 1

            if j < 0:
                posicoes.append(shift)
                shift += m
            else:
                shift += max(1, j - tabela.get(texto[shift + j], -1))

        return posicoes, {"mau_caractere": tabela}

    def _tabela_mc(self, padrao):
        return {c: i for i, c in enumerate(padrao)}
