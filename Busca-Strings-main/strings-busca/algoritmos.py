from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any
import time

#  ESTRUTURAS DE DADOS
@dataclass
class PassoExecucao:

    numero_passo: int           # número sequencial do passo (0, 1, 2...)
    posicao_texto: int          # índice atual no texto
    posicao_padrao: int         # índice atual no padrão
    descricao: str              # texto legível: "texto[3]='a' vs padrão[0]='a'"
    houve_match: bool           # True se os caracteres são iguais
    destaque_texto: List[int] = field(default_factory=list)   # posições de destaque no texto
    destaque_padrao: List[int] = field(default_factory=list)  # posições de destaque no padrão
    dados_extras: Dict[str, Any] = field(default_factory=dict) # info específica do algoritmo


@dataclass
class ResultadoBusca:

    algoritmo: str              # nome do algoritmo usado
    texto: str                  # texto onde buscamos
    padrao: str                 # padrão que buscamos
    posicoes: List[int]         # onde o padrão foi encontrado
    comparacoes: int            # total de comparações feitas
    passos: List[PassoExecucao] # rastreamento completo do algoritmo
    tempo_ms: float             # tempo de execução em milissegundos
    tabelas_extras: Dict[str, Any] = field(default_factory=dict)  # LPS, mau-char, hashes
    complexidade_melhor: str = ""
    complexidade_media: str = ""
    complexidade_pior: str = ""


#  INTERFACE (STRATEGY)
class EstrategiaDeBusca(ABC):
    nome: str = "Abstrato"
    complexidade_melhor: str = ""
    complexidade_media: str = ""
    complexidade_pior: str = ""

    @abstractmethod
    def buscar(self, texto: str, padrao: str) -> ResultadoBusca:
        """Executa a busca e retorna o resultado completo."""
        ...

    def _montar_resultado(self, texto, padrao, posicoes, comparacoes,
                            passos, tempo_ms, tabelas_extras=None) -> ResultadoBusca:
        """Método auxiliar para montar o ResultadoBusca de forma padronizada."""
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



#  ALGORITMO 1: BUSCA NAIVE (FORÇA BRUTA)
class BuscaNaive(EstrategiaDeBusca):
    nome = "Naive"
    complexidade_melhor = "O(n)"
    complexidade_media = "O(n·m)"
    complexidade_pior = "O(n·m)"

    def buscar(self, texto: str, padrao: str) -> ResultadoBusca:
        n = len(texto)
        m = len(padrao)
        posicoes = []
        passos = []
        comparacoes = 0
        numero_passo = 0

        inicio = time.perf_counter()

        # Caso especial: texto ou padrão vazio → nada a buscar
        if m == 0 or n == 0:
            tempo = (time.perf_counter() - inicio) * 1000
            return self._montar_resultado(texto, padrao, [], 0, [], tempo)

        # Para cada posição possível de início no texto...
        for inicio_janela in range(n - m + 1):

            # ...tenta casar o padrão inteiro a partir daqui
            j = 0
            while j < m:
                comparacoes += 1
                char_texto = texto[inicio_janela + j]
                char_padrao = padrao[j]
                houve_match = (char_texto == char_padrao)

                passos.append(PassoExecucao(
                    numero_passo=numero_passo,
                    posicao_texto=inicio_janela + j,
                    posicao_padrao=j,
                    descricao=f"texto[{inicio_janela + j}]='{char_texto}' vs padrão[{j}]='{char_padrao}'",
                    houve_match=houve_match,
                    destaque_texto=list(range(inicio_janela, inicio_janela + m)),
                    destaque_padrao=list(range(j + 1)),
                    dados_extras={"inicio_janela": inicio_janela},
                ))
                numero_passo += 1

                if not houve_match:
                    break  # falhou → tenta próxima janela
                j += 1

            if j == m:
                posicoes.append(inicio_janela)  # chegou até o fim → encontrou!

        tempo = (time.perf_counter() - inicio) * 1000
        return self._montar_resultado(texto, padrao, posicoes, comparacoes, passos, tempo)


#  ALGORITMO 2: RABIN-KARP
class BuscaRabinKarp(EstrategiaDeBusca):
    nome = "Rabin-Karp"
    complexidade_melhor = "O(n+m)"
    complexidade_media = "O(n+m)"
    complexidade_pior = "O(n·m)"

    BASE = 256  # base do sistema posicional (tamanho do alfabeto)
    MOD  = 101  # módulo primo para manter o hash pequeno

    def buscar(self, texto: str, padrao: str) -> ResultadoBusca:
        n = len(texto)
        m = len(padrao)
        posicoes = []
        passos = []
        comparacoes = 0
        numero_passo = 0
        registro_hashes = []  # para exibir na aba "Tabelas Internas"

        inicio = time.perf_counter()

        if m == 0 or n == 0 or m > n:
            tempo = (time.perf_counter() - inicio) * 1000
            return self._montar_resultado(texto, padrao, [], 0, [], tempo)

        B = self.BASE
        MOD = self.MOD

        # h = B^(m-1) mod MOD → usado para remover o primeiro caractere da janela
        h = pow(B, m - 1, MOD)

        # Calcula o hash inicial do padrão e da primeira janela do texto
        hash_padrao = 0
        hash_janela = 0
        for i in range(m):
            hash_padrao = (B * hash_padrao + ord(padrao[i])) % MOD
            hash_janela = (B * hash_janela + ord(texto[i])) % MOD

        registro_hashes.append({"janela": 0, "hash_texto": hash_janela, "hash_padrao": hash_padrao})

        # Desliza a janela pelo texto
        for i in range(n - m + 1):
            hashes_iguais = (hash_janela == hash_padrao)

            info_extra = {
                "hash_texto": hash_janela,
                "hash_padrao": hash_padrao,
                "hashes_iguais": hashes_iguais,
                "inicio_janela": i,
            }

            if hashes_iguais:
                # Hashes batem → verifica caractere a caractere para confirmar
                for j in range(m):
                    comparacoes += 1
                    char_texto = texto[i + j]
                    char_padrao = padrao[j]
                    houve_match = (char_texto == char_padrao)

                    passos.append(PassoExecucao(
                        numero_passo=numero_passo,
                        posicao_texto=i + j,
                        posicao_padrao=j,
                        descricao=f"[Hash igual!] Confirmando: texto[{i+j}]='{char_texto}' vs padrão[{j}]='{char_padrao}'",
                        houve_match=houve_match,
                        destaque_texto=list(range(i, i + m)),
                        destaque_padrao=list(range(j + 1)),
                        dados_extras=info_extra,
                    ))
                    numero_passo += 1

                    if not houve_match:
                        break  # foi uma colisão de hash → falso positivo
                else:
                    posicoes.append(i)  # todos os chars batem → encontrou!
            else:
                # Hashes diferentes → podemos pular sem verificar os chars
                passos.append(PassoExecucao(
                    numero_passo=numero_passo,
                    posicao_texto=i,
                    posicao_padrao=0,
                    descricao=f"Hash diferente na janela {i}: texto={hash_janela} ≠ padrão={hash_padrao} → pula",
                    houve_match=False,
                    destaque_texto=list(range(i, i + m)),
                    destaque_padrao=[],
                    dados_extras=info_extra,
                ))
                numero_passo += 1

            # Atualiza o hash para a próxima janela (rolling hash em O(1))
            if i < n - m:
                hash_janela = (B * (hash_janela - ord(texto[i]) * h) + ord(texto[i + m])) % MOD
                if hash_janela < 0:
                    hash_janela += MOD
                registro_hashes.append({"janela": i + 1, "hash_texto": hash_janela, "hash_padrao": hash_padrao})

        tempo = (time.perf_counter() - inicio) * 1000
        tabelas = {
            "hashes": registro_hashes,
            "base": B,
            "mod": MOD,
            "hash_padrao": hash_padrao,
        }
        return self._montar_resultado(texto, padrao, posicoes, comparacoes, passos, tempo, tabelas)


#  ALGORITMO 3: KNUTH-MORRIS-PRATT (KMP)
class BuscaKMP(EstrategiaDeBusca):
    nome = "KMP"
    complexidade_melhor = "O(n)"
    complexidade_media = "O(n+m)"
    complexidade_pior = "O(n+m)"

    def _construir_tabela_lps(self, padrao: str) -> List[int]:
        """
        Constrói a tabela LPS (Longest Proper Prefix-Suffix).
        Esta é a pré-computação do KMP, feita em O(m).
        """
        m = len(padrao)
        lps = [0] * m  # lps[0] é sempre 0 (prefixo próprio de 1 char = vazio)

        comprimento = 0  # tamanho do prefixo atual
        i = 1

        while i < m:
            if padrao[i] == padrao[comprimento]:
                # Extendemos o prefixo-sufixo em mais um caractere
                comprimento += 1
                lps[i] = comprimento
                i += 1
            else:
                if comprimento != 0:
                    # Tentamos um prefixo menor (não retrocedem em i!)
                    comprimento = lps[comprimento - 1]
                else:
                    # Nenhum prefixo-sufixo possível
                    lps[i] = 0
                    i += 1

        return lps

    def buscar(self, texto: str, padrao: str) -> ResultadoBusca:
        n = len(texto)
        m = len(padrao)
        posicoes = []
        passos = []
        comparacoes = 0
        numero_passo = 0

        inicio = time.perf_counter()

        if m == 0 or n == 0:
            tempo = (time.perf_counter() - inicio) * 1000
            return self._montar_resultado(texto, padrao, [], 0, [], tempo)

        lps = self._construir_tabela_lps(padrao)

        i = 0  # cursor no texto  (nunca retrocede!)
        j = 0  # cursor no padrão

        while i < n:
            comparacoes += 1
            char_texto = texto[i]
            char_padrao = padrao[j]
            houve_match = (char_texto == char_padrao)

            # Calcula o salto que faríamos se falhar aqui
            salto_lps = lps[j - 1] if (not houve_match and j > 0) else None

            passos.append(PassoExecucao(
                numero_passo=numero_passo,
                posicao_texto=i,
                posicao_padrao=j,
                descricao=f"texto[{i}]='{char_texto}' vs padrão[{j}]='{char_padrao}' | LPS[{j}]={lps[j]}",
                houve_match=houve_match,
                destaque_texto=[i],
                destaque_padrao=[j],
                dados_extras={"lps": lps[:], "i": i, "j": j, "salto_lps": salto_lps},
            ))
            numero_passo += 1

            if houve_match:
                i += 1  # avança nos dois
                j += 1
            else:
                if j != 0:
                    # Usa o LPS para saltar → não retrocede i!
                    j = lps[j - 1]
                else:
                    i += 1  # nem o primeiro char casou → avança no texto

            # Chegou ao fim do padrão → encontrou!
            if j == m:
                posicoes.append(i - j)
                j = lps[j - 1]  # prepara para buscar a próxima ocorrência

        tempo = (time.perf_counter() - inicio) * 1000
        tabelas = {
            "lps": [
                {"indice": idx, "char": padrao[idx], "valor_lps": lps[idx]}
                for idx in range(m)
            ],
        }
        return self._montar_resultado(texto, padrao, posicoes, comparacoes, passos, tempo, tabelas)


#  ALGORITMO 4: BOYER-MOORE
class BuscaBoyerMoore(EstrategiaDeBusca):
    nome = "Boyer-Moore"
    complexidade_melhor = "O(n/m)"
    complexidade_media = "O(n)"
    complexidade_pior = "O(n·m)"

    def _construir_tabela_mau_caractere(self, padrao: str) -> Dict[str, int]:
        """
        Tabela de mau caractere: char → último índice no padrão.
        Chars ausentes retornam -1 quando consultados com .get(char, -1).
        """
        tabela = {}
        for i, char in enumerate(padrao):
            tabela[char] = i  # sobrescreve → fica só o último índice
        return tabela

    def buscar(self, texto: str, padrao: str) -> ResultadoBusca:
        n = len(texto)
        m = len(padrao)
        posicoes = []
        passos = []
        comparacoes = 0
        numero_passo = 0

        inicio = time.perf_counter()

        if m == 0 or n == 0 or m > n:
            tempo = (time.perf_counter() - inicio) * 1000
            return self._montar_resultado(texto, padrao, [], 0, [], tempo)

        tabela_mc = self._construir_tabela_mau_caractere(padrao)

        deslocamento = 0  # quantas posições o padrão está deslocado sobre o texto

        while deslocamento <= n - m:

            # Compara da direita para a esquerda
            j = m - 1

            while j >= 0:
                comparacoes += 1
                char_texto = texto[deslocamento + j]
                char_padrao = padrao[j]
                houve_match = (char_padrao == char_texto)

                # Índice do mau caractere no padrão (-1 se não existir)
                indice_mc = tabela_mc.get(char_texto, -1)
                salto = max(1, j - indice_mc) if not houve_match else 0

                passos.append(PassoExecucao(
                    numero_passo=numero_passo,
                    posicao_texto=deslocamento + j,
                    posicao_padrao=j,
                    descricao=(
                        f"texto[{deslocamento+j}]='{char_texto}' vs padrão[{j}]='{char_padrao}' "
                        f"(direita→esquerda)"
                    ),
                    houve_match=houve_match,
                    destaque_texto=list(range(deslocamento, deslocamento + m)),
                    destaque_padrao=[j],
                    dados_extras={
                        "deslocamento": deslocamento,
                        "indice_mc": indice_mc,
                        "salto": salto,
                        "mau_caractere": char_texto,
                    },
                ))
                numero_passo += 1

                if not houve_match:
                    break  # achou o mau caractere → calcula salto e pula
                j -= 1

            if j < 0:
                # j chegou a -1 → casou tudo → encontrou!
                posicoes.append(deslocamento)
                prox = tabela_mc.get(texto[deslocamento + m], -1) if deslocamento + m < n else -1
                deslocamento += m - prox
            else:
                # Aplica a heurística do mau caractere
                indice_mc = tabela_mc.get(texto[deslocamento + j], -1)
                deslocamento += max(1, j - indice_mc)

        tempo = (time.perf_counter() - inicio) * 1000
        tabelas = {
            "mau_caractere": [
                {"char": char, "ultimo_indice": idx}
                for char, idx in sorted(tabela_mc.items())
            ],
        }
        return self._montar_resultado(texto, padrao, posicoes, comparacoes, passos, tempo, tabelas)
