import math
import random
import unittest

from filmes import Filme
from arvores import ArvoreAVL, montar_arvore_avl


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


if __name__ == "__main__":
    unittest.main()
