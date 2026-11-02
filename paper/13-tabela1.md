# Tabela 1 em inglês — proposta de tradução

Data: 2026-10-29
Status: **PROPOSTA, NÃO APROVADA** — esta linha é lida pelo teste.

## Por que este arquivo existe

A Tabela 1 é a única tabela do manuscrito, carrega as vinte hipóteses
pré-registradas com seus vereditos, é citada cinco vezes no corpo — e está
**inteiramente em português**. Cabeçalhos (`enunciado`, `veredito pelo
critério`, `o que o resultado sustenta`) e as vinte linhas. Medido em
2026-10-29: 67 ocorrências de marcadores portugueses na tabela, contra 6 no
resto do manuscrito, e essas 6 são uma nota de pendência que saiu do texto no
mesmo dia.

O guia exige inglês americano ou britânico, não uma combinação; uma tabela
inteira em terceira língua não é combinação de variantes, é texto ilegível
para o leitor da revista.

## O que esta tradução preserva, e onde eu paro

Cada verdito desta tabela é uma formulação sua, e quatro delas são correções
que você impôs contra leituras minhas. Traduzir é reenunciá-las em outra
língua, e é por isso que **nada aqui foi aplicado ao manuscrito**: a tabela em
português continua em `00-estrutura.md` e continua sendo a que o consolidador
emite. Se você aprovar, a mudança é de uma linha na ORDEM do consolidador, e o
original fica onde está — `00-estrutura.md` é documento de apparatus e é
português por desenho.

As quatro formulações vinculantes, marcadas abaixo com **[V]**: a de H0 (sem
contagem por construção), a de H5c (passou trivialmente), a de H10b (leitura
estreita) e a de H11a (o critério cobria menos do que supus).

**Um ponto que eu não resolvo sozinho.** Em H11a, *"o critério cobria menos do
que supus"* está na primeira pessoa do singular, e o resto da tabela e do
artigo fala em `we`. Não sei se o sujeito é você ou eu, e a escolha muda o que
a linha afirma. Traduzi como `than was assumed`, que é neutro e não atribui;
se o sujeito é a autoria, `than we assumed` é o certo. Decisão sua.

---

## Table 1

| | statement | verdict by the criterion | what the result supports |
| --- | --- | --- | --- |
| H0 | there is a λ with both decoupling and stability | supported | **no tally, by construction:** the criterion is existential — "there exists a range of λ" with ρ < 0.95, R² within 1 SD of the best and Jaccard ≥ 0.90 (`docs/protocolo_hipoteses.md`) — and it defines no per-partition tally. Adding *k/n* here would impose a unit the pre-registration does not have |
| H5a | the interior maximum transfers | not supported, 2/5 | the curve saturates instead of peaking |
| H5b | the anchored gate beats the prior alone | supported, 5/5 | — |
| H5c | the position of λ\* is stable | supported, 5/5 **(formal)** | **passed trivially and does not count as confirmation:** the neighbourhood of λ = 1 was defined as {0.7, 1, 10}, and λ = 10 is at once a grid neighbour and the boundary, so the test does not distinguish stable at 1 from pressed against the ceiling. A drafting failure in the criterion (F001) |
| H6 | the penalty improves R² | supported, 4/5 | an effect of regularisation, not of content |
| H7-blocks | the prior's content matters | not supported, 1/5 | refutation clause triggered |
| H7-shuffled | the same, against the shuffled prior | supported, 4/5 | contiguity matters |
| H8 | anchoring alone buys little | not supported, 0/5 | anchoring buys a great deal |
| H9-blocks | reproducibility does not depend on content | not supported, 3/5 | no control beats the literature prior |
| H9-shuffled | the same | supported, 5/5 | stability with ρ(prior, reference) negative |
| H10a | there is within-plateau ordering | not supported, 3/5 | the sign is inconsistent |
| H10b | the literature prior orders better than blocks | supported, 5/5 | **a narrow reading:** blocks is negative, not the literature prior positive |
| H11a | the residual decile leaves the plateau | supported, 5/5 | **the criterion covered less than was assumed:** the decile went to the floor |
| H11b | the residual distinguishes the arms | supported, 4/5 | `shuffled` beats the literature prior in 3 of 4 |
| H12a | the decile is not trapped in a tie (Raman) | supported, 3/3 | the defect is absent with a continuous prior |
| H12b | no collapse under tie-breaking (Raman) | supported, 3/3 | the same |
| H12c | the literature prior beats blocks (Raman) | supported, 2/3 | a significant reversal in partition 2 |
| H13a | the partial is positive | supported, 5/5 | and it is the same in all three arms |
| H13b | the literature prior beats blocks on the partial | not supported, 0/5 | **a badly designed criterion:** it conditions on the variable that distinguishes the arms |
| H13c | the floor finding recurs | supported, 5/5 | **primary criterion met in five held-out partitions.** Not an independent replication: partitions 10–14 share about 80% of their fruits with 5–9 (F003, correction of 2026-10-25) |

---

## As quatro escolhas de tradução que mudam o peso da frase

Não são sinônimos, e é onde a tradução pode trair o original:

| original | traduzido | o que eu considerei |
| --- | --- | --- |
| **[V]** `não define tally por partição` | `defines no per-partition tally` | `tally` já está em inglês no original; mantive a palavra em vez de trocar por `count`, porque é o termo que você usou e que o teste de H0 guarda |
| **[V]** `encostado no teto` | `pressed against the ceiling` | literal. `at the grid boundary` seria mais técnico e perderia a imagem, que é o que torna a falha de redação óbvia |
| **[V]** `leitura estreita` | `a narrow reading` | não `a narrow interpretation`: `reading` é o termo que o artigo usa em toda parte para a leitura que um resultado autoriza |
| `efeito de regularizador, não de conteúdo` | `an effect of regularisation, not of content` | `regularizador` é o agente; `of regularisation` é o processo. Em inglês `an effect of the regulariser` soaria como efeito do objeto, não do mecanismo |

E duas decisões de forma: `suportada` → `supported` e `não suportada` → `not
supported`, mantendo as frações como estão; `idem` → `the same`, duas vezes,
porque `idem` em tabela inglesa de revista é arcaísmo.
