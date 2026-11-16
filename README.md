# G30_Árvores_2026.2

Trabalho 3<br>
Conteúdo da Disciplina: árvores balanceadas (AVL e Rubro-Negra)<br>

## Alunos
|Matrícula | Aluno |
| -- | -- |
| 21/1063256  |  Victor Hugo Rodrigues Guimarães |
| 21/1063229  |  Pedro Henrique dos Santos Ferreira |

## Sobre
Continuação do [trabalho de ordenação](https://github.com/eda2-2026/G30_Ordenacao_2026.2): o mesmo catálogo de filmes (`movies.csv`, 4803 filmes) que pode ser buscado por código, título, ano ou gênero e ordenado pelos algoritmos vistos em aula.

Nesta etapa entram as **árvores binárias de busca balanceadas**. No trabalho anterior a "Busca em Árvore Binária" só ficava balanceada porque a gente **ordenava** os filmes antes e inseria sempre o elemento do meio. Agora a **AVL** e a **Rubro-Negra** recebem os filmes em qualquer ordem e se rebalanceiam sozinhas a cada inserção, com **rotações** (e, na Rubro-Negra, **recolorações**).

## Screenshots

## Video
(a gravar)

## Instalação
Linguagem: Python 3 (sem bibliotecas externas)<br>

## Uso
Execute o código da main.py

```
python main.py
```

## Referências
- Slides "Árvores AVL (Balanceadas)" — Profª. Roseli A. F. Romero (ICMC/USP).
- Slides "Árvore Rubro-Negra" — Siang Wun Song (IME/USP), baseados em T. Cormen, C. Leiserson, R. Rivest e C. Stein, *Introduction to Algorithms*, 2ª ed., cap. 13.
