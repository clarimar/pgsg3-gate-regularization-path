# Pré-registro — H7, H8 e H9 (controles de prior)

Registrado em: **2026-10-18**
Status: **fechado antes de qualquer execução com prior permutado**

Complementa `docs/pre-registro-H5-H6.md`, que deixou este controle
explicitamente de fora. Nada aqui altera os critérios de H0, H5 ou H6, já
avaliados.

---

## A ambiguidade que este controle resolve

O resultado de H5b — o gate ancorado concorda com a referência de relevância
melhor do que o prior sozinho, em 5/5 partições — admite **duas** explicações,
e os dados até aqui não as separam:

**(a) Conteúdo.** O prior carrega informação química genuína, e ancorar o gate
nele o leva às bandas que de fato sustentam o sinal.

**(b) Ancoragem.** Qualquer restrição suave sobre o gate o regulariza na
direção do que os dados sustentam, e o conteúdo do prior é incidental.

Sob (b), o achado central do trabalho seria sobre regularização, não sobre
química, e o enquadramento do artigo muda. Um parecerista levantará isso.

## Braços de controle

Implementados em `permute_prior` (`scripts/02_lambda_sweep_controlled.py`),
testados em `tests/test_prior_arms.py`:

| braço | o que preserva | o que destrói |
| --- | --- | --- |
| `literature` | tudo (prior publicado) | --- |
| `blocks` | multiset de valores, número de blocos, comprimento e forma interna de cada bloco | apenas **onde** os blocos ficam |
| `shuffled` | multiset de valores | posição **e** contiguidade |

`blocks` é o controle informativo: isola conteúdo químico mantendo "ênfase
contígua em alguma região", que é a propriedade estrutural que poderia, por si
só, regularizar o gate. `shuffled` destrói as duas coisas ao mesmo tempo, de
modo que um colapso ali não distingue qual delas importou — é o controle mais
fraco, reportado ao lado.

A permutação é sorteada **uma vez por partição** (semente = semente da
partição) e compartilhada por todas as sementes de modelo. Com um prior
diferente por execução, o Jaccard entre sementes cairia por motivo trivial e
H9 ficaria sem sentido.

## Desenho

As mesmas cinco partições agrupadas por fruto (`--split-seed 0..4`), a mesma
grade de λ, 10 sementes, orçamento fixo de 500 épocas, Adam, `--init zero`.
Dois braços novos: `--prior blocks` e `--prior shuffled`. **A grade e o
protocolo estão fechados: não serão refinados depois de ver os resultados.**

O braço `literature` já está executado (`results/ctl_part0..4`) e é reusado
sem nova execução.

---

## H7 — o conteúdo do prior importa

**Enunciado.** Em λ fixo, o prior de literatura produz concordância com a
referência de relevância maior do que um prior com os mesmos valores em
posições aleatórias.

**Comparação primária, em λ = 1** — valor fixado agora, não escolhido por
braço depois de ver os dados; é o argmax canônico já reportado. Pareado por
semente dentro de cada partição, Wilcoxon bilateral.

- **H7-blocks** *suportada* se `agree(literature, λ=1) > agree(blocks, λ=1)`
  com p < 0,05 em ≥ 4 das 5 partições.
- **H7-shuffled** idem para `shuffled`.

**Comparação secundária**, mais generosa ao controle: cada braço no seu
próprio argmax. Se H7 se mantiver também assim, a afirmação é mais forte.
Reportada à parte, não entra no veredito.

**Refutação.** Se `blocks` igualar ou superar `literature` em ≥ 2 partições, o
ganho de concordância **não** depende de onde o prior aponta, e a explicação
(b) passa a ser a leitura correta. O artigo é reescrito em torno de
regularização, não de química.

## H8 — a ancoragem sozinha compra pouco

**Enunciado.** Nos braços de controle, ancorar não eleva a concordância acima
do gate sem ancoragem.

**Critério.** Dentro de cada braço de controle, `agree(λ=1) − agree(λ=0)`
pareado por semente. *Suportada* se a diferença **não** for significativamente
positiva (p ≥ 0,05, ou negativa) em ≥ 4 das 5 partições.

Se H8 falhar — isto é, se um prior embaralhado também elevar a concordância —
então ancoragem e conteúdo contribuem ambos, e as duas parcelas precisam ser
reportadas separadamente. Isso **não** refuta H7: as duas podem ser
suportadas, e nesse caso a leitura é que a ancoragem fornece um ganho de base
e a química fornece um ganho adicional.

## H9 — a reprodutibilidade não depende do conteúdo

**Enunciado.** Os braços de controle alcançam Jaccard entre sementes
comparável ao do prior de literatura.

**Critério.** Em λ = 1, `|Jaccard(controle) − Jaccard(literature)| < 0,05` em
≥ 4 das 5 partições, para cada braço.

**Por que importa.** O artigo aceito do programa atribui ao prior de
literatura o valor de **estabilidade interpretativa** (Jaccard 0,90--0,94
contra 0,58--0,65 sem prior). Se um prior embaralhado produzir a mesma
estabilidade, então estabilidade entre sementes **não valida** a
interpretação: um gate pode ser perfeitamente reprodutível e apontar para o
lugar errado. Isso qualifica — não contradiz — a conclusão daquele artigo, e
é a razão pela qual a concordância com uma referência externa é necessária
além do Jaccard.

Se H9 for suportada, é resultado próprio e deve ser reportado com destaque,
inclusive com nota aos autores do artigo aceito.

---

## O que este controle não testa

Não testa se o prior de literatura é **ótimo**, apenas se sua posição importa
frente a posições aleatórias. Um prior melhor pode existir; encontrá-lo não
faz parte deste pré-registro.

Não separa, dentro de `blocks`, o efeito da contiguidade do efeito da largura
dos blocos, que são preservados juntos por construção.

## Regra de execução

Os dois braços × cinco partições são rodados **uma vez** e reportados qualquer
que seja o resultado. Sem repetição com outra semente de permutação, sem
refinamento de grade, sem troca de métrica. Falha de execução é registrada no
commit e a rodada recomeça do zero, com este documento inalterado.
