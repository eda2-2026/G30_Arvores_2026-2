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
        super().__init__(chave=chave)  # já cria raiz, chave e comparacoes_insercao
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


VERMELHO = "vermelho"
PRETO = "preto"


class NoRN:
    def __init__(self, filme, pai=None):
        self.filmes = [filme]
        self.esquerda = None
        self.direita = None
        self.pai = pai
        self.cor = VERMELHO  # todo nó novo entra vermelho (RB-insert, linha 23)


def _cor(no):
    # folha (None) faz o papel do sentinela nil[T], que é sempre preto
    return no.cor if no is not None else PRETO


class ArvoreRubroNegra(ArvoreBusca):
    """Árvore rubro-negra (Cormen et al., cap. 13).

    Propriedades:
      1. todo nó é vermelho ou preto;
      2. a raiz é preta;
      3. toda folha (nil) é preta;
      4. se um nó é vermelho, os dois filhos são pretos;
      5. todos os caminhos de um nó até as folhas têm o mesmo nº de nós pretos.

    No lugar do sentinela nil[T] usamos None, tratado como preto (_cor).
    Assim buscar() e buscar_por_trecho() herdados de ArvoreBusca funcionam
    sem mudança.
    """

    def __init__(self, chave=lambda f: f.codigo):
        super().__init__(chave=chave)  # já cria raiz, chave e comparacoes_insercao
        self.rotacoes = 0
        self.recoloracoes = 0

    # altura() é herdada de ArvoreBusca

    def _pintar(self, no, cor):
        if no.cor != cor:
            no.cor = cor
            self.recoloracoes += 1

    # ---------------- rotações ----------------

    def _left_rotate(self, x):
        y = x.direita
        x.direita = y.esquerda
        if y.esquerda is not None:
            y.esquerda.pai = x
        y.pai = x.pai
        if x.pai is None:
            self.raiz = y
        elif x is x.pai.esquerda:
            x.pai.esquerda = y
        else:
            x.pai.direita = y
        y.esquerda = x
        x.pai = y
        self.rotacoes += 1

    def _right_rotate(self, y):
        x = y.esquerda
        y.esquerda = x.direita
        if x.direita is not None:
            x.direita.pai = y
        x.pai = y.pai
        if y.pai is None:
            self.raiz = x
        elif y is y.pai.direita:
            y.pai.direita = x
        else:
            y.pai.esquerda = x
        x.direita = y
        y.pai = x
        self.rotacoes += 1

    # ---------------- inserção ----------------

    def inserir(self, filme):
        chave_filme = self.chave(filme)
        y = None
        x = self.raiz
        while x is not None:
            self.comparacoes_insercao += 1
            y = x
            chave_x = self.chave(x.filmes[0])
            if chave_filme < chave_x:
                x = x.esquerda
            elif chave_filme > chave_x:
                x = x.direita
            else:
                x.filmes.append(filme)  # chave repetida: nenhuma propriedade muda
                return

        z = NoRN(filme, pai=y)
        if y is None:
            self.raiz = z
        elif chave_filme < self.chave(y.filmes[0]):
            y.esquerda = z
        else:
            y.direita = z

        self._inserir_fixup(z)

    def _inserir_fixup(self, z):
        while _cor(z.pai) == VERMELHO:
            avo = z.pai.pai  # existe: pai vermelho não pode ser a raiz
            if z.pai is avo.esquerda:
                y = avo.direita  # tio
                if _cor(y) == VERMELHO:
                    # caso 1: tio vermelho -> recolore e sobe dois níveis
                    self._pintar(z.pai, PRETO)
                    self._pintar(y, PRETO)
                    self._pintar(avo, VERMELHO)
                    z = avo
                else:
                    if z is z.pai.direita:
                        # caso 2: tio preto e z filho direito -> vira caso 3
                        z = z.pai
                        self._left_rotate(z)
                    # caso 3: tio preto e z filho esquerdo
                    self._pintar(z.pai, PRETO)
                    self._pintar(z.pai.pai, VERMELHO)
                    self._right_rotate(z.pai.pai)
            else:
                y = avo.esquerda
                if _cor(y) == VERMELHO:
                    self._pintar(z.pai, PRETO)
                    self._pintar(y, PRETO)
                    self._pintar(avo, VERMELHO)
                    z = avo
                else:
                    if z is z.pai.esquerda:
                        z = z.pai
                        self._right_rotate(z)
                    self._pintar(z.pai, PRETO)
                    self._pintar(z.pai.pai, VERMELHO)
                    self._left_rotate(z.pai.pai)

        self._pintar(self.raiz, PRETO)


def montar_arvore_rubro_negra(filmes, chave=lambda f: f.codigo):
    arvore = ArvoreRubroNegra(chave=chave)
    for filme in filmes:
        arvore.inserir(filme)
    return arvore


def desenhar_arvore(arvore, rotulo):
    """Desenha a árvore "deitada": a raiz fica à esquerda, a subárvore
    direita aparece acima do nó e a esquerda abaixo.

    rotulo(no) -> texto mostrado para cada nó. Devolve a lista de linhas.
    """
    linhas = []
    conectores = {None: "", "dir": "┌── ", "esq": "└── "}

    def visitar(no, prefixo, lado):
        if no is None:
            return
        # a barra "│" liga o nó ao irmão que fica do outro lado dele;
        # os filhos da raiz começam na mesma coluna que ela
        acima = "" if lado is None else ("│   " if lado == "esq" else "    ")
        abaixo = "" if lado is None else ("│   " if lado == "dir" else "    ")
        visitar(no.direita, prefixo + acima, "dir")
        linhas.append(prefixo + conectores[lado] + rotulo(no))
        visitar(no.esquerda, prefixo + abaixo, "esq")

    visitar(arvore.raiz, "", None)
    return linhas
