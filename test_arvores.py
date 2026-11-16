import math
import random
import unittest

from filmes import Filme
from arvores import (
    ArvoreAVL,
    montar_arvore_avl,
    ArvoreRubroNegra,
    montar_arvore_rubro_negra,
    VERMELHO,
    PRETO,
    desenhar_arvore,
)
from buscas import ArvoreBusca
import main


def gerar_filmes(n, semente=42):
    aleatorio = random.Random(semente)
    codigos = aleatorio.sample(range(500000), n)  # códigos únicos
    return [
        Filme(codigo=codigo,
              titulo=f"Filme {i}",
              ano=aleatorio.randint(1916, 2017),
              genero="Drama")
        for i, codigo in enumerate(codigos)
    ]


def filmes_com_codigos(codigos):
    return [Filme(codigo=c, titulo=str(c), ano=2000, genero="X") for c in codigos]


def em_ordem(no, chave):
    if no is None:
        return []
    return em_ordem(no.esquerda, chave) + [chave(no.filmes[0])] + em_ordem(no.direita, chave)


def estrutura(no, chave):
    """(chave, esquerda, direita) -- facilita comparar com o desenho dos slides."""
    if no is None:
        return None
    return (chave(no.filmes[0]), estrutura(no.esquerda, chave), estrutura(no.direita, chave))


class TestArvoreAVL(unittest.TestCase):

    def verificar_avl(self, no):
        """Confere |FB| <= 1 e se a altura guardada em cada nó está certa.
        Devolve a altura real da subárvore."""
        if no is None:
            return 0
        h_esq = self.verificar_avl(no.esquerda)
        h_dir = self.verificar_avl(no.direita)
        self.assertLessEqual(abs(h_dir - h_esq), 1, "nó desbalanceado")
        self.assertEqual(no.altura, 1 + max(h_esq, h_dir), "altura guardada errada")
        return no.altura

    def verificar_arvore(self, arvore, filmes, chave):
        self.verificar_avl(arvore.raiz)
        chaves = em_ordem(arvore.raiz, chave)
        self.assertEqual(chaves, sorted(set(chave(f) for f in filmes)),
                         "percurso em ordem não está ordenado")

    # ------------- exemplos dos slides -------------

    def test_caso1_rotacao_simples_esquerda(self):
        # slides 16-17: 8 (4, 10 (9, 15)) e insere 12 -> FB(8)=2, FB(10)=1
        arvore = montar_arvore_avl(filmes_com_codigos([8, 4, 10, 9, 15, 12]))
        self.assertEqual(arvore.rotacoes, 1)
        self.assertEqual(
            estrutura(arvore.raiz, arvore.chave),
            (10, (8, (4, None, None), (9, None, None)), (15, (12, None, None), None)),
        )

    def test_caso2_rotacao_dupla_esquerda_direita(self):
        # slides 19-20: 8 (4 (2, 6), 10) e insere 5 -> FB(8)=-2, FB(4)=1
        arvore = montar_arvore_avl(filmes_com_codigos([8, 4, 10, 2, 6, 5]))
        self.assertEqual(arvore.rotacoes, 2)
        self.assertEqual(
            estrutura(arvore.raiz, arvore.chave),
            (6, (4, (2, None, None), (5, None, None)), (8, None, (10, None, None))),
        )

    def test_rotacao_simples_direita(self):
        arvore = montar_arvore_avl(filmes_com_codigos([3, 2, 1]))
        self.assertEqual(arvore.rotacoes, 1)
        self.assertEqual(estrutura(arvore.raiz, arvore.chave),
                         (2, (1, None, None), (3, None, None)))

    def test_rotacao_dupla_direita_esquerda(self):
        arvore = montar_arvore_avl(filmes_com_codigos([1, 3, 2]))
        self.assertEqual(arvore.rotacoes, 2)
        self.assertEqual(estrutura(arvore.raiz, arvore.chave),
                         (2, (1, None, None), (3, None, None)))

    # ------------- propriedades -------------

    def test_insercao_aleatoria_mantem_avl(self):
        filmes = gerar_filmes(1000)
        arvore = montar_arvore_avl(filmes)
        self.verificar_arvore(arvore, filmes, arvore.chave)

    def test_insercao_ordenada_e_inversa_nao_degenera(self):
        filmes = sorted(gerar_filmes(1000), key=lambda f: f.codigo)
        limite = 1.45 * math.log2(len(filmes) + 2)  # altura máxima de uma AVL
        for nome, entrada in (("ordenada", filmes), ("inversa", filmes[::-1])):
            with self.subTest(cenario=nome):
                arvore = montar_arvore_avl(entrada)
                self.verificar_arvore(arvore, entrada, arvore.chave)
                self.assertLessEqual(arvore.altura(), limite)
                self.assertGreater(arvore.rotacoes, 0)

    def test_rotacoes_por_insercao_no_maximo_duas(self):
        arvore = ArvoreAVL()
        for filme in gerar_filmes(500):
            antes = arvore.rotacoes
            arvore.inserir(filme)
            self.assertLessEqual(arvore.rotacoes - antes, 2)

    def test_conta_comparacoes_na_insercao(self):
        arvore = montar_arvore_avl(filmes_com_codigos([2, 1, 3]))
        # 2: 0 comparações | 1: 1 | 3: 1
        self.assertEqual(arvore.comparacoes_insercao, 2)

    def test_arvore_vazia(self):
        arvore = ArvoreAVL()
        self.assertEqual(arvore.altura(), 0)
        self.assertEqual(arvore.buscar(10), ([], 0))

    # ------------- busca (herdada de ArvoreBusca) -------------

    def test_busca_por_codigo(self):
        filmes = gerar_filmes(500)
        arvore = montar_arvore_avl(filmes)
        for filme in filmes:
            encontrados, comparacoes = arvore.buscar(filme.codigo)
            self.assertEqual(encontrados, [filme])
            self.assertLessEqual(comparacoes, arvore.altura())
        self.assertEqual(arvore.buscar(-1)[0], [])

    def test_chaves_repetidas_ficam_no_mesmo_no(self):
        filmes = gerar_filmes(300)
        arvore = montar_arvore_avl(filmes, chave=lambda f: f.ano)
        self.verificar_arvore(arvore, filmes, arvore.chave)
        for ano in {f.ano for f in filmes}:
            esperado = [f for f in filmes if f.ano == ano]
            encontrados, _ = arvore.buscar(ano)
            self.assertEqual(encontrados, esperado)  # mantém a ordem de inserção

    def test_busca_por_trecho(self):
        filmes = gerar_filmes(200)
        arvore = montar_arvore_avl(filmes, chave=lambda f: f.titulo.casefold())
        encontrados, _ = arvore.buscar_por_trecho("filme 1")
        esperado = sorted((f for f in filmes if "filme 1" in f.titulo.casefold()),
                          key=lambda f: f.titulo.casefold())
        self.assertEqual(encontrados, esperado)
        encontrados, _ = arvore.buscar_por_trecho("filme 1", limite=5)
        self.assertEqual(len(encontrados), 5)


def estrutura_com_cor(no, chave):
    """(chave, 'V'/'P', esquerda, direita)."""
    if no is None:
        return None
    return (chave(no.filmes[0]), "V" if no.cor == VERMELHO else "P",
            estrutura_com_cor(no.esquerda, chave), estrutura_com_cor(no.direita, chave))


class TestArvoreRubroNegra(unittest.TestCase):

    def verificar_propriedades(self, arvore):
        raiz = arvore.raiz
        if raiz is None:
            return
        self.assertEqual(raiz.cor, PRETO, "propriedade 2: raiz tem que ser preta")
        self.assertIsNone(raiz.pai)

        def altura_negra(no):
            """Confere as propriedades 1, 4 e 5 e os ponteiros pai.
            Devolve o nº de nós pretos de no até as folhas (folha None conta 1,
            propriedade 3)."""
            if no is None:
                return 1
            self.assertIn(no.cor, (VERMELHO, PRETO), "propriedade 1")
            for filho in (no.esquerda, no.direita):
                if filho is not None:
                    self.assertIs(filho.pai, no, "ponteiro pai errado")
                    if no.cor == VERMELHO:
                        self.assertEqual(filho.cor, PRETO,
                                         "propriedade 4: nó vermelho com filho vermelho")
            esquerda = altura_negra(no.esquerda)
            direita = altura_negra(no.direita)
            self.assertEqual(esquerda, direita, "propriedade 5: altura negra diferente")
            return esquerda + (1 if no.cor == PRETO else 0)

        altura_negra(raiz)

    def verificar_arvore(self, arvore, filmes):
        self.verificar_propriedades(arvore)
        self.assertEqual(em_ordem(arvore.raiz, arvore.chave),
                         sorted(set(arvore.chave(f) for f in filmes)),
                         "percurso em ordem não está ordenado")
        n = len(set(arvore.chave(f) for f in filmes))
        self.assertLessEqual(arvore.altura(), 2 * math.log2(n + 1),
                             "altura passou de 2 log(n + 1)")

    # ------------- exemplo dos slides 19-22 -------------

    def test_exemplo_dos_slides(self):
        # essa ordem de inserção monta exatamente a árvore do slide 19
        arvore = montar_arvore_rubro_negra(filmes_com_codigos([11, 2, 14, 1, 7, 15, 5, 8]))
        chave = arvore.chave
        self.assertEqual(
            estrutura_com_cor(arvore.raiz, chave),
            (11, "P",
             (2, "V", (1, "P", None, None),
                      (7, "P", (5, "V", None, None), (8, "V", None, None))),
             (14, "P", None, (15, "V", None, None))),
        )

        # inserir 4 passa pelos casos 1 -> 2 -> 3 (slides 19, 20 e 21)
        rotacoes_antes = arvore.rotacoes
        arvore.inserir(filmes_com_codigos([4])[0])
        self.assertEqual(arvore.rotacoes - rotacoes_antes, 2)

        # árvore final do slide 22
        self.assertEqual(
            estrutura_com_cor(arvore.raiz, chave),
            (7, "P",
             (2, "V", (1, "P", None, None),
                      (5, "P", (4, "V", None, None), None)),
             (11, "V", (8, "P", None, None),
                       (14, "P", None, (15, "V", None, None)))),
        )
        self.verificar_propriedades(arvore)

    # ------------- casos de rotação isolados -------------

    def test_caso3_rotacao_direita(self):
        arvore = montar_arvore_rubro_negra(filmes_com_codigos([3, 2, 1]))
        self.assertEqual(arvore.rotacoes, 1)
        self.assertEqual(estrutura_com_cor(arvore.raiz, arvore.chave),
                         (2, "P", (1, "V", None, None), (3, "V", None, None)))

    def test_caso2_vira_caso3(self):
        arvore = montar_arvore_rubro_negra(filmes_com_codigos([3, 1, 2]))
        self.assertEqual(arvore.rotacoes, 2)
        self.assertEqual(estrutura_com_cor(arvore.raiz, arvore.chave),
                         (2, "P", (1, "V", None, None), (3, "V", None, None)))

    def test_casos_espelhados(self):
        for codigos in ([1, 2, 3], [1, 3, 2]):
            with self.subTest(ordem=codigos):
                arvore = montar_arvore_rubro_negra(filmes_com_codigos(codigos))
                self.assertEqual(estrutura_com_cor(arvore.raiz, arvore.chave),
                                 (2, "P", (1, "V", None, None), (3, "V", None, None)))

    def test_caso1_so_recolore(self):
        arvore = montar_arvore_rubro_negra(filmes_com_codigos([2, 1, 3]))
        recoloracoes_antes = arvore.recoloracoes
        arvore.inserir(filmes_com_codigos([4])[0])  # tio (1) vermelho
        self.assertEqual(arvore.rotacoes, 0)
        # 1 e 3 ficam pretos; 2 fica vermelho e volta a ser preto por ser a raiz
        self.assertEqual(arvore.recoloracoes - recoloracoes_antes, 4)
        self.assertEqual(estrutura_com_cor(arvore.raiz, arvore.chave),
                         (2, "P", (1, "P", None, None),
                          (3, "P", None, (4, "V", None, None))))

    # ------------- propriedades -------------

    def test_insercao_aleatoria_mantem_propriedades(self):
        filmes = gerar_filmes(1000)
        self.verificar_arvore(montar_arvore_rubro_negra(filmes), filmes)

    def test_propriedades_valem_apos_cada_insercao(self):
        arvore = ArvoreRubroNegra()
        for filme in gerar_filmes(200, semente=7):
            arvore.inserir(filme)
            self.verificar_propriedades(arvore)

    def test_insercao_ordenada_e_inversa_nao_degenera(self):
        filmes = sorted(gerar_filmes(1000), key=lambda f: f.codigo)
        for nome, entrada in (("ordenada", filmes), ("inversa", filmes[::-1])):
            with self.subTest(cenario=nome):
                arvore = montar_arvore_rubro_negra(entrada)
                self.verificar_arvore(arvore, entrada)
                self.assertGreater(arvore.rotacoes, 0)

    def test_rotacoes_por_insercao_no_maximo_duas(self):
        arvore = ArvoreRubroNegra()
        for filme in gerar_filmes(500):
            antes = arvore.rotacoes
            arvore.inserir(filme)
            self.assertLessEqual(arvore.rotacoes - antes, 2)

    def test_conta_comparacoes_na_insercao(self):
        arvore = montar_arvore_rubro_negra(filmes_com_codigos([2, 1, 3]))
        self.assertEqual(arvore.comparacoes_insercao, 2)

    def test_arvore_vazia(self):
        arvore = ArvoreRubroNegra()
        self.assertEqual(arvore.altura(), 0)
        self.assertEqual(arvore.buscar(10), ([], 0))

    # ------------- busca (herdada de ArvoreBusca) -------------

    def test_busca_por_codigo(self):
        filmes = gerar_filmes(500)
        arvore = montar_arvore_rubro_negra(filmes)
        for filme in filmes:
            encontrados, comparacoes = arvore.buscar(filme.codigo)
            self.assertEqual(encontrados, [filme])
            self.assertLessEqual(comparacoes, arvore.altura())
        self.assertEqual(arvore.buscar(-1)[0], [])

    def test_chaves_repetidas_ficam_no_mesmo_no(self):
        filmes = gerar_filmes(300)
        arvore = montar_arvore_rubro_negra(filmes, chave=lambda f: f.ano)
        self.verificar_arvore(arvore, filmes)
        for ano in {f.ano for f in filmes}:
            esperado = [f for f in filmes if f.ano == ano]
            self.assertEqual(arvore.buscar(ano)[0], esperado)

    def test_busca_por_trecho(self):
        filmes = gerar_filmes(200)
        arvore = montar_arvore_rubro_negra(filmes, chave=lambda f: f.titulo.casefold())
        esperado = sorted((f for f in filmes if "filme 1" in f.titulo.casefold()),
                          key=lambda f: f.titulo.casefold())
        self.assertEqual(arvore.buscar_por_trecho("filme 1")[0], esperado)


class TestArvoreBinariaSemBalanceamento(unittest.TestCase):

    def test_entrada_ordenada_degenera_sem_estourar_recursao(self):
        # inserção e altura iterativas: 3000 > limite de recursão do Python
        filmes = filmes_com_codigos(range(3000))
        arvore = ArvoreBusca()
        for filme in filmes:
            arvore.inserir(filme)
        self.assertEqual(arvore.altura(), 3000)  # virou uma "lista"
        self.assertEqual(arvore.comparacoes_insercao, 3000 * 2999 // 2)
        self.assertEqual(arvore.buscar(2999)[1], 3000)

    def test_altura_vazia_e_balanceada(self):
        arvore = ArvoreBusca()
        self.assertEqual(arvore.altura(), 0)
        for filme in filmes_com_codigos([4, 2, 6, 1, 3, 5, 7]):
            arvore.inserir(filme)
        self.assertEqual(arvore.altura(), 3)


class TestDesenharArvore(unittest.TestCase):

    def test_desenho_da_arvore_final_dos_slides(self):
        arvore = montar_arvore_rubro_negra(
            filmes_com_codigos([11, 2, 14, 1, 7, 15, 5, 8, 4]))
        rotulo = lambda no: f"{no.filmes[0].codigo}{'V' if no.cor == VERMELHO else 'P'}"
        self.assertEqual(desenhar_arvore(arvore, rotulo), [
            "        ┌── 15V",
            "    ┌── 14P",
            "┌── 11V",
            "│   └── 8P",
            "7P",
            "│   ┌── 5P",
            "│   │   └── 4V",
            "└── 2V",
            "    └── 1P",
        ])

    def test_arvore_vazia(self):
        self.assertEqual(desenhar_arvore(ArvoreAVL(), str), [])


class TestIntegracaoMain(unittest.TestCase):

    def test_todos_os_metodos_de_busca_encontram_o_mesmo(self):
        filmes = gerar_filmes(300)
        estruturas = main.montar_estruturas(filmes)
        casos = [("1", filmes[10].codigo), ("1", -1),
                 ("3", filmes[0].ano), ("2", "filme 2"), ("4", "drama")]
        for campo_id, valor in casos:
            campo = main.CAMPOS[campo_id]
            esperado = None
            for metodo_id in main.METODOS:
                with self.subTest(campo=campo["nome"], valor=valor, metodo=metodo_id):
                    encontrados, _ = main.executar_busca(metodo_id, campo, valor,
                                                         filmes, estruturas)
                    codigos = sorted(f.codigo for f in encontrados)
                    if campo["modo"] == "contem":
                        # busca por trecho para no limite: só confere quantidade
                        codigos = len(codigos)
                    if esperado is None:
                        esperado = codigos
                    self.assertEqual(codigos, esperado)


if __name__ == "__main__":
    unittest.main()
