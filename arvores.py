from buscas import ArvoreBusca


class NoAVL:
    def __init__(self, filme):
        # mesmo esquema do NoArvore: filmes com a MESMA chave ficam no mesmo nó
        self.filmes = [filme]
        self.esquerda = None
        self.direita = None
        self.altura = 1  # folha tem altura 1; subárvore vazia (None) tem altura 0


def _altura(no):
    return no.altura if no is not None else 0


class ArvoreAVL(ArvoreBusca):
    """Árvore binária de busca balanceada (Adelson-Velsky e Landis, 1962).

    Fator de balanceamento: FB = altura(direita) - altura(esquerda).
    FB negativo => pesada à esquerda => rotações à direita.
    FB positivo => pesada à direita  => rotações à esquerda.

    buscar() e buscar_por_trecho() são herdados de ArvoreBusca, pois só
    usam esquerda/direita/filmes.
    """

    def __init__(self, chave=lambda f: f.codigo):
        super().__init__(chave=chave)
        self.comparacoes_insercao = 0
        self.rotacoes = 0

    def altura(self):
        return _altura(self.raiz)

    @staticmethod
    def fator_balanceamento(no):
        return _altura(no.direita) - _altura(no.esquerda)

    def _atualizar_altura(self, no):
        no.altura = 1 + max(_altura(no.esquerda), _altura(no.direita))

    # ---------------- rotações ----------------

    def _rot_dir(self, p):
        q = p.esquerda
        temp = q.direita
        q.direita = p
        p.esquerda = temp
        self._atualizar_altura(p)  # p agora está abaixo de q: atualiza primeiro
        self._atualizar_altura(q)
        self.rotacoes += 1
        return q  # nova raiz da subárvore

    def _rot_esq(self, p):
        q = p.direita
        temp = q.esquerda
        q.esquerda = p
        p.direita = temp
        self._atualizar_altura(p)
        self._atualizar_altura(q)
        self.rotacoes += 1
        return q

    def _rot_esq_dir(self, p):
        # caso 2 pesado à esquerda: filho esquerdo com FB de sinal trocado
        p.esquerda = self._rot_esq(p.esquerda)
        return self._rot_dir(p)

    def _rot_dir_esq(self, p):
        # caso 2 pesado à direita: filho direito com FB de sinal trocado
        p.direita = self._rot_dir(p.direita)
        return self._rot_esq(p)

    def _balancear(self, no):
        fb = self.fator_balanceamento(no)

        if fb < -1:
            if self.fator_balanceamento(no.esquerda) > 0:
                return self._rot_esq_dir(no)   # caso 2: rotação dupla
            return self._rot_dir(no)           # caso 1: rotação simples

        if fb > 1:
            if self.fator_balanceamento(no.direita) < 0:
                return self._rot_dir_esq(no)   # caso 2: rotação dupla
            return self._rot_esq(no)           # caso 1: rotação simples

        return no

    # ---------------- inserção ----------------

    def inserir(self, filme):
        self.raiz = self._inserir(self.raiz, filme, self.chave(filme))

    def _inserir(self, no, filme, chave_filme):
        if no is None:
            return NoAVL(filme)

        self.comparacoes_insercao += 1
        chave_no = self.chave(no.filmes[0])

        if chave_filme < chave_no:
            no.esquerda = self._inserir(no.esquerda, filme, chave_filme)
        elif chave_filme > chave_no:
            no.direita = self._inserir(no.direita, filme, chave_filme)
        else:
            no.filmes.append(filme)  # chave repetida: não cria nó, altura não muda
            return no

        self._atualizar_altura(no)
        return self._balancear(no)


def montar_arvore_avl(filmes, chave=lambda f: f.codigo):
    """Insere os filmes na ordem em que vierem -- não precisa ordenar antes."""
    arvore = ArvoreAVL(chave=chave)
    for filme in filmes:
        arvore.inserir(filme)
    return arvore
