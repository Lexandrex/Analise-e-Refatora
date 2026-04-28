# String Busca Lab 🔍

Aplicação completa para **exploração, visualização e comparação** de algoritmos de busca em strings,
implementados com o padrão de projeto **Strategy** em Python.

---

## Estrutura de arquivos

```
strings-busca/
├── algoritmos.py   # Padrão Strategy + Algoritmos Obrigatórios
├── controlador.py   # Orquestração, serialização JSON
├── servidor.py       # Servidor Flask (endpoints da API)
├── index.html      # Front-end completo (HTML/CSS/JS)
└── testes.py        # Suite de testes automatizados

```

---

## Como rodar

#### 1. Instalar dependências
```bash
pip install flask
```

#### 2. Iniciar o servidor
```bash
cd strings-busca
python servidor.py
```

#### 3. Abrir no navegador
```
http://127.0.0.1:5000
```

---

### Para rodar os testes
```bash
python testes.py
```

---

## Padrão Strategy

```
SearchStrategy  (ABC)
├── NaiveSearch          → O(n·m) brute force
├── RabinKarpSearch      → O(n+m) rolling hash
├── KMPSearch            → O(n+m) LPS table
└── BoyerMooreSearch     → O(n/m) bad character
```

---

## API Endpoints

| Método | Endpoint       | Descrição                              |
|--------|---------------|----------------------------------------|
| GET    | `/`           | Serve o frontend (index.html)          |
| GET    | `/api/algorithms` | Lista algoritmos disponíveis      |
| POST   | `/api/search` | Executa um algoritmo específico        |
| POST   | `/api/compare`| Executa todos os algoritmos e compara  |

### POST /api/search
```json
{
  "text":      "AABAACAADAABAABA",
  "pattern":   "AABA",
  "algorithm": "kmp"
}
```
Algoritmos: `naive`, `rabin-karp`, `kmp`, `boyer-moore`

---

## Funcionalidades da Interface

- **Upload de arquivos .txt** (um ou múltiplos, suporte a drag & drop)
- **Digitação manual** do texto
- **Seleção visual** do algoritmo
- **Execução normal** → posições encontradas + métricas
- **Passo a passo** → slider interativo, reprodução automática,
  texto e padrão coloridos em tempo real, log detalhado
- **Tabelas internas**:
  - KMP → tabela LPS completa
  - Boyer-Moore → tabela Bad Character
  - Rabin-Karp → hashes de cada janela
- **Comparação** → gráficos de barras animados, tabela completa,
  dicas de uso para cada algoritmo
