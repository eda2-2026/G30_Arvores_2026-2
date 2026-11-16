import math
import time

from filmes import carregar_filmes
from buscas import (
    busca_sequencial,
    busca_binaria,
    busca_interpolacao,
    ArvoreBusca,
    montar_arvore_balanceada,
    TabelaHash,
    tamanho_recomendado_para_hash,
)
from arvores import (
    ArvoreAVL,
    ArvoreRubroNegra,
    montar_arvore_avl,
    montar_arvore_rubro_negra,
    desenhar_arvore,
    VERMELHO,
)
from ordenacoes import (
    selection_sort,
    insertion_sort,
    bubble_sort,
    counting_sort,
    radix_sort,
    heap_sort,
)

# quantas ocorrências uma busca por trecho (título/gênero) devolve no
# máximo -- ela para de procurar assim que atingir esse número.
LIMITE_BUSCA_POR_TRECHO = 10

CAMPOS = {
    "1": {
        "id": "codigo",
        "nome": "Código",
        "chave": lambda f: f.codigo,
        "conversor": int,
        "unico": True,
        "numerico": True,
        "modo": "igual",
        "limite": None,
    },
    "2": {
        "id": "titulo",
        "nome": "Título",
        "chave": lambda f: f.titulo.casefold(),
        "conversor": lambda texto: texto.casefold(),
        "unico": False,
        "numerico": False,
        "modo": "contem",
        "limite": LIMITE_BUSCA_POR_TRECHO,
    },
    "3": {
        "id": "ano",
        "nome": "Ano",
        "chave": lambda f: f.ano,
        "conversor": int,
        "unico": False,
        "numerico": True,
        "modo": "igual",
        "limite": None,
    },
    "4": {
        "id": "genero",
        "nome": "Gênero",
        "chave": lambda f: f.genero.casefold(),
        "conversor": lambda texto: texto.casefold(),
        "unico": False,
        "numerico": False,
        "modo": "contem",
        "limite": LIMITE_BUSCA_POR_TRECHO,
    },
}

METODOS = {
    "1": "Busca Sequencial",
    "2": "Busca Binária",
    "3": "Busca por Interpolação",
    "4": "Busca em Árvore Binária",
    "5": "Busca por Hashing",
    "6": "Busca em Árvore AVL",
    "7": "Busca em Árvore Rubro-Negra",
}

# métodos de busca que usam uma árvore já montada em montar_estruturas
ARVORES_DE_BUSCA = {"4": "arvore", "6": "avl", "7": "rubro_negra"}

# "apenas_numerico": counting/radix indexam um vetor pelo valor da chave,
# então só funcionam com chaves inteiras (código e ano).
ALGORITMOS_ORDENACAO = {
    "1": {"nome": "Selection Sort", "funcao": selection_sort, "apenas_numerico": False},
    "2": {"nome": "Insertion Sort", "funcao": insertion_sort, "apenas_numerico": False},
    "3": {"nome": "Bubble Sort", "funcao": bubble_sort, "apenas_numerico": False},
    "4": {"nome": "Counting Sort", "funcao": counting_sort, "apenas_numerico": True},
    "5": {"nome": "Radix Sort", "funcao": radix_sort, "apenas_numerico": True},
    "6": {"nome": "Heap Sort", "funcao": heap_sort, "apenas_numerico": False},
}


def campos_disponiveis(metodo_id):
    return CAMPOS


def montar_estruturas(filmes):
    estruturas = {}
    tamanho_hash = tamanho_recomendado_para_hash(len(filmes))
    for campo in CAMPOS.values():
        chave = campo["chave"]
        # vetor ordenado usado pela busca binária / interpolação, agora
        # gerado pelo nosso Heap Sort (O(n log n)) em vez do sorted() do Python
        ordenados, _, _ = heap_sort(filmes, chave=chave)

        arvore = montar_arvore_balanceada(ordenados, chave=chave)

        tabela_hash = TabelaHash(tamanho=tamanho_hash, chave=chave)
        for filme in filmes:
            tabela_hash.inserir(filme)

        # AVL e rubro-negra se balanceiam sozinhas: inserimos na ordem do CSV,
        # sem precisar ordenar antes como na árvore binária acima
        estruturas[campo["id"]] = {
            "ordenados": ordenados,
            "arvore": arvore,
            "avl": montar_arvore_avl(filmes, chave=chave),
            "rubro_negra": montar_arvore_rubro_negra(filmes, chave=chave),
            "hash": tabela_hash,
        }
    return estruturas


def executar_busca(metodo_id, campo, valor, filmes, estruturas):
    chave = campo["chave"]
    dados = estruturas[campo["id"]]

    if campo["modo"] == "contem":
        limite = campo["limite"]
        if metodo_id == "1":
            return busca_sequencial(filmes, valor, chave=chave, modo="contem", limite=limite)
        if metodo_id in ("2", "3"):
            return busca_sequencial(dados["ordenados"], valor, chave=chave, modo="contem", limite=limite)
        if metodo_id in ARVORES_DE_BUSCA:
            return dados[ARVORES_DE_BUSCA[metodo_id]].buscar_por_trecho(valor, limite=limite)
        if metodo_id == "5":
            return dados["hash"].buscar_por_trecho(valor, limite=limite)
        raise ValueError(f"Método de busca desconhecido: {metodo_id}")

    if metodo_id == "1":
        return busca_sequencial(filmes, valor, chave=chave, chave_unica=campo["unico"])
    if metodo_id == "2":
        return busca_binaria(dados["ordenados"], valor, chave=chave)
    if metodo_id == "3":
        return busca_interpolacao(dados["ordenados"], valor, chave=chave)
    if metodo_id in ARVORES_DE_BUSCA:
        return dados[ARVORES_DE_BUSCA[metodo_id]].buscar(valor)
    if metodo_id == "5":
        return dados["hash"].buscar(valor)
    raise ValueError(f"Método de busca desconhecido: {metodo_id}")


def listar_catalogo(filmes):
    print("\n--- Catálogo de filmes (ordenado por código) ---")
    for filme in sorted(filmes, key=lambda f: f.codigo):
        print(" ", filme)
    print()


def ler_valor_busca(campo):
    rotulo = campo["nome"] + (" (contém)" if campo["modo"] == "contem" else "")
    while True:
        entrada = input(f"{rotulo} (Enter para voltar): ").strip()
        if entrada == "":
            return None
        try:
            return campo["conversor"](entrada)
        except ValueError:
            print("Valor inválido para este campo.\n")


LIMITE_RESULTADOS_EXIBIDOS = 20


def buscar_no_submenu(metodo_id, metodo_nome, campo, filmes, estruturas):
    print(f"\n--- {metodo_nome} | Campo: {campo['nome']} ---")
    print(f"({len(filmes)} filmes no catálogo -- use a opção 8 do menu principal pra ver a lista completa)\n")

    while True:
        valor = ler_valor_busca(campo)
        if valor is None:
            break

        inicio = time.perf_counter()
        encontrados, comparacoes = executar_busca(metodo_id, campo, valor, filmes, estruturas)
        fim = time.perf_counter()

        if encontrados:
            print(f"{len(encontrados)} filme(s) encontrado(s):")
            for filme in encontrados[:LIMITE_RESULTADOS_EXIBIDOS]:
                print(" ", filme)
            excedente = len(encontrados) - LIMITE_RESULTADOS_EXIBIDOS
            if excedente > 0:
                print(f"  ... e mais {excedente} filme(s) (não exibidos).")
        else:
            print("Nenhum filme encontrado.")
        print(f"Comparações: {comparacoes} | Tempo: {(fim - inicio) * 1000:.4f} ms\n")


def comparar_metodos(filmes, estruturas):
    campo = CAMPOS["1"]
    codigos_existentes = [f.codigo for f in filmes]
    codigo_inexistente = max(codigos_existentes) + 1

    print("\n--- Comparativo de desempenho (busca por código) ---")
    print(f"{len(codigos_existentes)} buscas bem-sucedidas (uma por filme do catálogo)\n")
    cabecalho = (f"{'Método':<30}{'Melhor':>8}{'Pior':>8}{'Médio':>10}"
                 f"{'Malsucedida':>13}{'Tempo total (ms)':>18}")
    print(cabecalho)
    print("-" * len(cabecalho))

    for metodo_id, nome in METODOS.items():
        comparacoes_lista = []

        inicio = time.perf_counter()
        for codigo in codigos_existentes:
            _, comparacoes = executar_busca(metodo_id, campo, codigo, filmes, estruturas)
            comparacoes_lista.append(comparacoes)
        _, comparacoes_ausente = executar_busca(metodo_id, campo, codigo_inexistente, filmes, estruturas)
        fim = time.perf_counter()

        melhor = min(comparacoes_lista)
        pior = max(comparacoes_lista)
        media = sum(comparacoes_lista) / len(comparacoes_lista)
        tempo_total_ms = (fim - inicio) * 1000

        print(f"{nome:<30}{melhor:>8}{pior:>8}{media:>10.2f}"
              f"{comparacoes_ausente:>13}{tempo_total_ms:>18.4f}")
    print()


def menu_campo(metodo_id, metodo_nome, filmes, estruturas):
    campos = campos_disponiveis(metodo_id)

    while True:
        print(f"\n--- {metodo_nome}: buscar por qual campo? ---")
        for chave_menu, campo in campos.items():
            print(f"{chave_menu} - {campo['nome']}")
        print("0 - Voltar ao menu principal")

        escolha = input("Escolha uma opção: ").strip()
        if escolha == "0":
            return
        if escolha not in campos:
            print("Opção inválida!\n")
            continue

        buscar_no_submenu(metodo_id, metodo_nome, campos[escolha], filmes, estruturas)


def campos_para_ordenacao(algoritmo):
    if algoritmo["apenas_numerico"]:
        return {k: c for k, c in CAMPOS.items() if c["numerico"]}
    return CAMPOS


def ordenar_catalogo(algoritmo, campo, filmes):
    print(f"\n--- {algoritmo['nome']} | Campo: {campo['nome']} ---")
    inicio = time.perf_counter()
    ordenados, comparacoes, movimentacoes = algoritmo["funcao"](filmes, chave=campo["chave"])
    fim = time.perf_counter()

    print(f"Primeiros {LIMITE_RESULTADOS_EXIBIDOS} de {len(ordenados)} filmes ordenados:")
    for filme in ordenados[:LIMITE_RESULTADOS_EXIBIDOS]:
        print(" ", filme)
    print(f"Comparações: {comparacoes} | Movimentações: {movimentacoes} | "
          f"Tempo: {(fim - inicio) * 1000:.4f} ms\n")


def menu_ordenacao(filmes):
    while True:
        print("\n--- Ordenar catálogo: qual algoritmo? ---")
        for chave_menu, algoritmo in ALGORITMOS_ORDENACAO.items():
            print(f"{chave_menu} - {algoritmo['nome']}")
        print("0 - Voltar ao menu principal")

        escolha = input("Escolha uma opção: ").strip()
        if escolha == "0":
            return
        if escolha not in ALGORITMOS_ORDENACAO:
            print("Opção inválida!\n")
            continue

        algoritmo = ALGORITMOS_ORDENACAO[escolha]
        campos = campos_para_ordenacao(algoritmo)
        if algoritmo["apenas_numerico"]:
            print(f"({algoritmo['nome']} só ordena chaves inteiras)")

        print(f"\n--- {algoritmo['nome']}: ordenar por qual campo? ---")
        for chave_menu, campo in campos.items():
            print(f"{chave_menu} - {campo['nome']}")
        escolha_campo = input("Escolha uma opção (Enter para voltar): ").strip()
        if escolha_campo == "":
            continue
        if escolha_campo not in campos:
            print("Opção inválida!\n")
            continue

        ordenar_catalogo(algoritmo, campos[escolha_campo], filmes)


TAMANHO_PADRAO_COMPARATIVO = 1000


def ler_tamanho_amostra(total):
    while True:
        entrada = input(f"Quantos filmes usar? (1 a {total}, Enter = "
                        f"{TAMANHO_PADRAO_COMPARATIVO}): ").strip()
        if entrada == "":
            return min(TAMANHO_PADRAO_COMPARATIVO, total)
        if entrada.isdigit() and 1 <= int(entrada) <= total:
            return int(entrada)
        print("Valor inválido.\n")


def comparar_ordenacoes(filmes):
    campo = CAMPOS["1"]  # código: numérico, então todos os algoritmos se aplicam
    chave = campo["chave"]

    print("\n--- Comparativo de desempenho dos algoritmos de ordenação ---")
    print("(os algoritmos O(n^2) ficam lentos com o catálogo inteiro)")
    n = ler_tamanho_amostra(len(filmes))

    amostra = filmes[:n]
    crescente, _, _ = heap_sort(amostra, chave=chave)
    cenarios = {
        "Ordem original do CSV": amostra,
        "Já ordenado": crescente,
        "Ordem inversa": crescente[::-1],
    }

    for nome_cenario, entrada in cenarios.items():
        print(f"\n>> Cenário: {nome_cenario} | {n} filmes | chave: {campo['nome']}")
        cabecalho = f"{'Algoritmo':<18}{'Comparações':>14}{'Movimentações':>16}{'Tempo (ms)':>14}"
        print(cabecalho)
        print("-" * len(cabecalho))
        for algoritmo in ALGORITMOS_ORDENACAO.values():
            inicio = time.perf_counter()
            _, comparacoes, movimentacoes = algoritmo["funcao"](entrada, chave=chave)
            fim = time.perf_counter()
            print(f"{algoritmo['nome']:<18}{comparacoes:>14}{movimentacoes:>16}"
                  f"{(fim - inicio) * 1000:>14.4f}")
    print()


TIPOS_DE_ARVORE = {
    "1": {"nome": "Binária (sem balanceamento)", "classe": ArvoreBusca},
    "2": {"nome": "AVL", "classe": ArvoreAVL},
    "3": {"nome": "Rubro-Negra", "classe": ArvoreRubroNegra},
}


def construir_arvore(classe, filmes, chave):
    arvore = classe(chave=chave)
    inicio = time.perf_counter()
    for filme in filmes:
        arvore.inserir(filme)
    fim = time.perf_counter()
    return arvore, (fim - inicio) * 1000


def comparar_arvores(filmes):
    campo = CAMPOS["1"]  # código: chave única, cada filme vira um nó
    chave = campo["chave"]

    print("\n--- Comparativo entre árvores (inserção por código) ---")
    print("(a árvore binária sem balanceamento fica lenta com entrada já ordenada)")
    n = ler_tamanho_amostra(len(filmes))

    amostra = filmes[:n]
    crescente, _, _ = heap_sort(amostra, chave=chave)
    cenarios = {
        "Ordem original do CSV": amostra,
        "Já ordenado": crescente,
        "Ordem inversa": crescente[::-1],
    }

    print(f"\nAltura mínima possível: {math.ceil(math.log2(n + 1))} | "
          f"limite AVL: {1.44 * math.log2(n + 2):.1f} | "
          f"limite Rubro-Negra: {2 * math.log2(n + 1):.1f}")

    for nome_cenario, entrada in cenarios.items():
        print(f"\n>> Cenário: {nome_cenario} | {n} filmes | chave: {campo['nome']}")
        cabecalho = (f"{'Árvore':<29}{'Altura':>8}{'Comp. inserção':>16}{'Rotações':>10}"
                     f"{'Recolorações':>14}{'Busca média':>13}{'Tempo (ms)':>12}")
        print(cabecalho)
        print("-" * len(cabecalho))
        for tipo in TIPOS_DE_ARVORE.values():
            arvore, tempo_ms = construir_arvore(tipo["classe"], entrada, chave)
            # média de comparações de uma busca bem-sucedida por cada filme
            total_busca = sum(arvore.buscar(chave(f))[1] for f in entrada)
            rotacoes = getattr(arvore, "rotacoes", "-")
            recoloracoes = getattr(arvore, "recoloracoes", "-")
            print(f"{tipo['nome']:<29}{arvore.altura():>8}{arvore.comparacoes_insercao:>16}"
                  f"{rotacoes:>10}{recoloracoes:>14}{total_busca / n:>13.2f}{tempo_ms:>12.2f}")
    print()


LIMITE_VISUALIZACAO = 31  # mais que isso não cabe direito no terminal


def rotulo_do_no(arvore):
    def rotulo(no):
        filme = no.filmes[0]
        texto = f"{filme.codigo} {filme.titulo[:22]}"
        if isinstance(arvore, ArvoreAVL):
            return f"{texto} (FB={arvore.fator_balanceamento(no):+d})"
        if isinstance(arvore, ArvoreRubroNegra):
            return f"{texto} [{'V' if no.cor == VERMELHO else 'P'}]"
        return texto
    return rotulo


def ler_inteiro(mensagem, minimo, maximo, padrao):
    while True:
        entrada = input(f"{mensagem} ({minimo} a {maximo}, Enter = {padrao}): ").strip()
        if entrada == "":
            return padrao
        if entrada.isdigit() and minimo <= int(entrada) <= maximo:
            return int(entrada)
        print("Valor inválido.\n")


def mostrar_arvore(arvore):
    for linha in desenhar_arvore(arvore, rotulo_do_no(arvore)):
        print("  " + linha)
    extras = ""
    if hasattr(arvore, "rotacoes"):
        extras += f" | Rotações: {arvore.rotacoes}"
    if hasattr(arvore, "recoloracoes"):
        extras += f" | Recolorações: {arvore.recoloracoes}"
    print(f"Altura: {arvore.altura()} | Comparações na inserção: "
          f"{arvore.comparacoes_insercao}{extras}\n")


def visualizar_arvore(filmes):
    chave = CAMPOS["1"]["chave"]
    while True:
        print("\n--- Visualizar árvore: qual tipo? ---")
        for chave_menu, tipo in TIPOS_DE_ARVORE.items():
            print(f"{chave_menu} - {tipo['nome']}")
        print("0 - Voltar ao menu principal")

        escolha = input("Escolha uma opção: ").strip()
        if escolha == "0":
            return
        if escolha not in TIPOS_DE_ARVORE:
            print("Opção inválida!\n")
            continue
        tipo = TIPOS_DE_ARVORE[escolha]

        n = ler_inteiro("Quantos filmes inserir?", 1, LIMITE_VISUALIZACAO, 15)
        ordenar = input("Inserir já ordenado por código? (s/N): ").strip().lower() == "s"
        passo_a_passo = input("Mostrar passo a passo? (s/N): ").strip().lower() == "s"

        entrada = filmes[:n]
        if ordenar:
            entrada, _, _ = heap_sort(entrada, chave=chave)

        print(f"\n--- Árvore {tipo['nome']} | {n} filmes | chave: código ---")
        print("(deitada: a raiz fica à esquerda, a subárvore direita aparece em cima)")
        if tipo["classe"] is ArvoreAVL:
            print("FB = altura(direita) - altura(esquerda)")
        elif tipo["classe"] is ArvoreRubroNegra:
            print("[V] = vermelho | [P] = preto")

        arvore = tipo["classe"](chave=chave)
        for i, filme in enumerate(entrada, 1):
            arvore.inserir(filme)
            if passo_a_passo and i < len(entrada):
                print(f"\n> Inseriu {filme.codigo} ({i}/{len(entrada)}):")
                mostrar_arvore(arvore)
                input("Enter para inserir o próximo...")
        print(f"\n> Árvore final ({len(entrada)} filmes):")
        mostrar_arvore(arvore)


def menu_principal():
    filmes = carregar_filmes()
    estruturas = montar_estruturas(filmes)

    while True:
        print("=================================================")
        print("  CATÁLOGO DE FILMES - BUSCA, ORDENAÇÃO E ÁRVORES ")
        print("=================================================")
        for chave_menu, nome in METODOS.items():
            print(f"{chave_menu} - {nome}")
        print("8 - Listar catálogo")
        print("9 - Comparar desempenho dos métodos de busca")
        print("10 - Ordenar catálogo")
        print("11 - Comparar desempenho dos algoritmos de ordenação")
        print("12 - Comparar árvores (binária x AVL x rubro-negra)")
        print("13 - Visualizar árvore")
        print("0 - Sair")

        escolha = input("Escolha uma opção: ").strip()

        if escolha == "0":
            print("Encerrando...")
            break
        elif escolha == "8":
            listar_catalogo(filmes)
        elif escolha == "9":
            comparar_metodos(filmes, estruturas)
        elif escolha == "10":
            menu_ordenacao(filmes)
        elif escolha == "11":
            comparar_ordenacoes(filmes)
        elif escolha == "12":
            comparar_arvores(filmes)
        elif escolha == "13":
            visualizar_arvore(filmes)
        elif escolha in METODOS:
            menu_campo(escolha, METODOS[escolha], filmes, estruturas)
        else:
            print("Opção inválida!\n")


if __name__ == "__main__":
    menu_principal()
