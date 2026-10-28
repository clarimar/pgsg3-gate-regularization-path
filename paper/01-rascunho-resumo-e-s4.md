# Rascunho — resumo e Seção 4

Data: 2026-10-24
Status: **primeiro rascunho, para revisão de voz e de conformidade com ADR-0003**

Escrito em inglês, registro Chemolab. Duas peças só: o resumo, onde vive o
enquadramento, e a §4, que é o resultado central e a única seção em que a
ressalva 3 do `ADR-0003` tem efeito sobre cada frase.

Um número está marcado como pendente. Não escrevo valor que não medi.

---

## Abstract

> Prior-guided spectral attention is commonly assessed for interpretive
> stability by the overlap of the top-k selected bands across independent
> runs. We show that this overlap can be determined by the geometry of the
> prior rather than by learned band relevance, and we separate two effects
> that are easily conflated. A literature prior encoded as a step function
> over 281 near-infrared bands places 34 bands at its maximum, more than the
> top-decile size q, so the selected set is drawn entirely from that plateau —
> in 15 of 15 cells of a pre-registered sweep. This alone bounds what the
> metric can register, without making its value artificial: with the prior
> kept out of the initialisation the plateau carries distinct values and the
> overlap is a genuine agreement among them. When the prior also initialises
> the gate, the plateau saturates (s(1−s) ≈ 10⁻⁶), its gate values become
> numerically identical, and the selection is settled by the tie-breaking
> rule, so the reported overlap instead tracks how similar the gates are in
> the bands the metric never selects: an overlap of 0.9418 falls to 0.7005 ±
> 0.0068 when ties are resolved at random rather than left to the sort,
> indistinguishable from the chance value of 0.7012 for drawing 28 of 34 bands
> twice. The same holds across seven training sizes from n = 30 to 1158. A
> displacement-based control reported in that earlier study uses gate values
> rather than their order, is unaffected by this property, and is what
> supports its interpretive claim. Overlap without anchoring grows with sample
> size (Spearman +0.93, p = 0.003); overlap under prior-initialisation does
> not (−0.32, p = 0.48), indicating that the two conditions do not measure the
> same quantity. A Raman arm with a continuous prior (545 distinct values,
> plateau of one band) shows neither property in 3 of 3 partitions, locating
> the cause in the prior's quantisation rather than in the architecture. Where
> the gate does align with a data-derived reference, the alignment is
> independent of which prior was used and concentrates in the bands the prior
> demotes. We state the conditions under which top-k overlap is informative
> and report all twenty pre-registered hypotheses with their verdicts.

**~300 palavras.** Longo para Chemolab; se precisar cortar, a frase sobre C1
não ser suficiente é a que eu manteria e a do controle de deslocamento a
segunda. Cortaria antes a enumeração de valores do prior. Pontos que a estrutura exigia e que estão lá: a frase sobre
o gate alinhar-se com os dados (penúltima) desfaz a leitura absoluta do título;
o controle Raman aparece como localização de causa, não como adorno; e as vinte
hipóteses estão anunciadas no resumo, não escondidas no suplementar.

**[corrigido]** A frase sobre o controle de deslocamento entrou no resumo, não
só na §4. Sem ela, o resumo deixa o leitor concluir que a alegação do artigo
anterior caiu, o que não é o caso — ela repousa naquele controle, que está de pé.

**Decisão sua:** "0.9418" no resumo identifica a célula publicada para quem
conhece o artigo anterior. Isso é transparência (ressalva 1) e não é verbo de
correção (ressalva 3). Se preferir, troco por "an overlap of 0.94" e o número
exato fica só na §4. Eu manteria o exato — é o que torna a afirmação
verificável.

---

## 4. What the top-decile overlap measures

### 4.1 The prior's geometry

The near-infrared literature prior is a step function with four distinct values
over the 281 retained bands: 0.1 on 223 bands, 0.6 on 7, 0.8 on 17, and 1.0 on
34. The elevated regions correspond to published assignments — the chlorophyll
band near 690 nm, the second C–H overtone near 950 nm, and the first overtone
near 1150 nm — and the remaining bands carry a floor.

Top-k overlap is evaluated on the top decile. Two conventions for q coexist in
this program's codebase and give different values at p = 281:
`ceil(0.10 p) = 29` and floor division `p // 10 = 28`. We state which applies
to each dataset throughout and never combine them, because the reference levels
differ.

### 4.2 Three conditions, and what each one costs

A plateau larger than q does not by itself make a stability figure artificial.
The effect reported here requires three conditions, and they are separable. We
state them in order of what they cost the metric, and our data exhibit the
three combinations that occur.

**(C1) The plateau exceeds q.** Let L be the number of bands the prior places at
its maximum and suppose the trained gate is larger on all of them than on any
band outside. Then the top-q set is a subset of the plateau whenever L ≥ q, and
the metric never examines a band outside the prior's top level, whatever the
model has learned. Here L = 34 against q = 28 or 29.

C1 alone makes the metric **blind**, not artificial. With the prior moved out of
the initialisation (θ₀ = 0), the gate on the plateau is continuous, no two
values coincide, and the top-q set is chosen by magnitude: the overlap is then a
genuine agreement about which of the 34 bands rank highest. We observe exactly
this in a pre-registered sweep of three prior arms over five grouped
partitions — the decile lies inside the plateau in 15 of 15 cells, and no cell
contains an exact tie among trained gate values.

**(C2) The ties persist after training.** When the prior also initialises the
gate logits, θ₀ = logit(s), the gradient reaching θ scales with
σ′(θ) = s(1 − s), so bands with s = 1.0 begin where that factor is of order
10⁻⁶ and do not move within the budget. In the archived gate of the earlier
study the 34 plateau bands then hold one value to the last bit (0.99999380;
spread 0.0 × 10⁰; mean s(1 − s) = 6.2 × 10⁻⁶), and every band outside lies
strictly below.

**(C3) The tie is resolved by the sort.** With C1 and C2, the choice of q bands
from L is not made by magnitude, and the reported figure depends on the rule
that breaks the tie.

Under a rule that resolves ties at random, the selected set is uniform over the
C(L, q) subsets of the plateau. For two independent runs, |A ∩ B| is
hypergeometric and the expected overlap is

&nbsp;&nbsp;&nbsp;&nbsp;E[J] = Σₖ [ C(q,k) C(L−q, q−k) / C(L,q) ] · k / (2q − k),

which is **0.7012** for L = 34, q = 28 and **0.7445** for L = 34, q = 29. The
familiar approximation q/(2L − q) gives 0.7000 and 0.7436, within 0.0012 of the
exact values.

Under the deterministic rule actually used, `numpy.argsort` is not a stable
sort, so the order within a tied block follows the partition, which is a
function of the whole array — including the values the metric does not select.
The figure is therefore neither 1 (which an index-ordered rule would give) nor
the chance level. Holding the plateau as trained and perturbing only the
remaining bands, the overlap falls from 1.0000 at zero perturbation to 0.9678
at sd = 10⁻⁴ and 0.7500 at sd = 10⁻²; the value obtained on these data
corresponds to sd ≈ 1.5 × 10⁻⁴, consistent with the pairwise gate correlation
of 0.9995 recorded alongside it.

It is tempting to conclude that the figure therefore measures off-plateau
similarity, and we drew that conclusion in an earlier draft. It does not hold
across implementations. The partition path of an introsort is not specified by
the language, and on the same stored gates, with the same q and the same
formula, two builds of the same library return different figures: 0.9452 to
0.9867 under one and 0.7443 to 0.7659 — the chance level — under another
(Section 4.2.1). The off-plateau values are identical in both. So what the
deterministic figure reflects is the tie order a particular build produces,
which off-plateau similarity influences without determining. A quantity that
moves from near-unity to chance while the data are held fixed is not measuring
the data.

### 4.2.1 The three combinations, measured

Resolving the ties at random on the archived gate — the same gates, the same q,
the same formula, only the tie rule changed — gives 0.7005 +- 0.0068 over 200
draws, against the exact chance value of 0.7012 at that codebase's convention
(q = 28). The reported 0.9418 is reproduced by the deterministic rule **in the
environment in which it was obtained**, and that qualification is not a
formality: the next paragraph is the reason for it.

A note on that chance value, since the two candidates differ by less than our
sampling spread and the choice is therefore easy to get wrong without
consequence. We report the exact hypergeometric expectation
E[J] = sum_k P(k) k/(2q-k), and not the ratio q/(2L-q) that the band-selection
literature uses. The ratio is J evaluated at the expected overlap q^2/L, and
since J(k) = k/(2q-k) is strictly convex in k, Jensen's inequality makes it a
strict lower bound: low by 0.0012 at q = 28 and 0.0009 at q = 29 for a plateau
of 34. The gap changes no verdict reported here, but it is systematic and in
the direction that overstates any excess above chance.

The same configuration holds across the seven training sizes of the revision
data, n = 30 to 1158: the plateau has one distinct value in all 70 runs, and
the decile lies entirely within it. The overlap, however, is not one number.
Because the selected set is decided by the tie rule, it has to be reported
against the rule that produced it, and against the environment where the rule
is not fully specified by the language:

| selection procedure | overlap, seven sizes |
| --- | --- |
| ties broken by band index (`kind="stable"` or `"mergesort"`) | **1.0000** at every size |
| sort's own tie order, numpy 2.4.6 / Python 3.14.6 | 0.9452 to 0.9867 |
| sort's own tie order, numpy 2.5.3 / Python 3.13.16 | 0.7443 to 0.7659 |
| ties resolved at random, 200 draws | 0.7442 at every size |
| exact expectation E[J] for two q-subsets of L | 0.7445 |

Each row is the same stored gates, the same q = 29, the same formula. The third
row is the chance level; the first is unity. Reporting any single one of them as
*the* overlap would be reporting the procedure as if it were the data, and the
2.4.6 row — the historical one, which the published figure and Figure 3 both
carry — is preserved here as the reproduction of a specific procedure in a
specific environment, not as a result another reader will obtain.

We do not claim the library version as the cause. Version, build, array layout
and the partition path all enter an introsort's tie order, and separating them
is not necessary for the conclusion and not attempted here. What the comparison
establishes is that **the Jaccard is a property of the complete selection
procedure, tie rule included, and not an identifiable property of the gates
whenever the selection cuts through a level of exact ties.** That is a stronger
and more precise statement than calling the stability artificial.

It is also a bounded one. It does not make the top-q overlap an invalid
measure in general: where the selection boundary carries no tie — which is the
case in every control arm of Section 6 and in the unanchored arm from n = 200
upward — every tie rule returns the same set and the figure is a measurement
of the gates. What the result says is narrower: in this configuration, with a
quantised prior whose plateau contains the whole decile, the deterministic
value taken on its own does not identify spectral stability. The condition is
checkable before the metric is used, and that is the practical content of the
finding.

The claim is checkable too: `scripts/13_dependencia_do_sort.py` prints the table above with the
environment, the input hashes, the aggregation convention and the selected
index sets.

Resolving the ties at random gives 0.7442 +- 0.0063 in all seven cells, against
an exact expectation of 0.7445 -- a deviation of 0.04 standard deviations. This
is the row that reproduces across environments, because its tie key is random
by construction rather than left to the sort.

That the randomised figure is identical to four decimals across seven training
sizes is not a coincidence of seeding. When the selected set lies entirely
inside a plateau of one distinct value, the statistic is a function of q and the
plateau size alone: **the gate values enter nowhere in it.** This is the sharpest
available statement of C1 with C2. The quantity is not merely driven down to
chance by randomising the ties; under the deterministic rule the gate's
contribution to the selected set is confined to the order the sort leaves, and
no part of it survives a tie rule that ignores that order.

The Raman arm fails C1: its prior is a sum of gaussians with 545 distinct
values and attains its maximum at a single band, so the decile is not
plateau-bound and C2 cannot arise. Section 7 reports it.

| | C1 plateau > q | C2 ties persist | C3 sort resolves | what the figure is |
| --- | --- | --- | --- | --- |
| this work, θ₀ = 0 | yes | no | — | genuine agreement, within one prior level |
| earlier study and its revision data, θ₀ = logit s | yes | yes | yes | the tie rule of the build that ran, from unity to chance |
| Raman, continuous prior | no | no | — | unconstrained by the prior's geometry |

Two distinct statements follow, and conflating them overstates the result. C1
alone bounds **what the metric can register**. C1 with C2 and C3 determines
**the value it returns** — and C3, we can now add, is not a property of the
analysis but of its implementation.

### 4.3 What a reader of the earlier work can and cannot reproduce

One consequence of Section 4.2.1 deserves to be stated plainly rather than
left for a reader to discover, because it concerns the published record and
not only this analysis.

A reader who obtains the archived gates, applies the same selection code with
the same q, and computes the same statistic may not obtain the published
figure. Nothing need have gone wrong: the figure depends on the tie order of
the sort, and that order is not specified by the language where the selected
values are exactly equal. We observed the two outcomes on identical inputs,
and a third rule — tie-breaking by band index — returns unity. The published
number is therefore reproducible in the sense that matters for scrutiny, with
the procedure and environment named, and not reproducible in the sense a
reader would ordinarily assume.

Three practical consequences follow, and they are the ones we would want
applied to our own work:

1. **A top-q overlap should be reported with its tie rule stated**, as a
   matter of course, in the same way a p-value is reported with its test. The
   rule is part of the estimator, not an implementation detail of it.
2. **Where the selection cuts through a level of exact ties, the figure should
   not be reported alone.** The randomised value and the exact expectation
   cost nothing to compute and bound what the deterministic one can mean.
3. **A disagreement between two computations of this statistic need not be
   evidence of error in either — under a condition that must be stated, or
   the point becomes a general excuse for irreproducibility.** It holds when
   the two implement *different* tie rules, or when the rule of the original
   was never specified closely enough to be implemented twice. It does not
   hold when both claim the same procedure on the same inputs under the same
   numerical conditions: there, a divergence still demands investigation, and
   nothing here licenses attributing it to the sort. So the order of enquiry
   is to compare the tie rule and the environment *first*, which is why we
   record the input hashes, q, the aggregation convention and the selected
   index sets and not only the result — and, if those agree, to keep looking.

We make no claim about how widely this affects the band-selection literature,
and we are careful not to make one in the next breath either: whether a
quantised prior with a top-decile cut and a deterministic sort is a common
combination is a question about the literature that we did not study. We have
measured one prior, in one architecture, in two environments. What we can say
is that the three conditions are stated explicitly enough to be checked, and
that checking them on one's own data costs one script and no retraining —
`scripts/13_dependencia_do_sort.py` and `scripts/14_etapa_b_por_procedimento.py`
need only the stored gates and the prior.

### 4.4 What the earlier study already established

The study from which these data come anticipated the possibility that a prior
which immobilises the gate would make reproducibility trivial, and tested it: it
measured the across-seed agreement of the learned displacement d = g_final − g₀
rather than of the final gate, obtaining ρ(d) = 0.9462 in NIR and 0.976 in
Raman, and reported that the agreement on *which* bands move most is
considerably weaker, with a top-decile overlap of 0.38 in NIR. That control uses
gate values over all 281 bands rather than ranks within a tied block, and is
therefore immune to the artefact described here: no selection operator, no
top-q cut, and no tie-breaking rule enters it. Immunity to that artefact is
not independence from the prior's plateau, and the two should not be read as
one. Under prior-initialisation the plateau's displacement is the same to
within about a millionth across seeds, so twelve per cent of the spectrum
contributes agreement to that correlation for a reason unrelated to learning.
Section 9.3 measures how much: excluding the plateau lowers the correlation by
0.018 under Pearson and 0.051 under Spearman at the largest training size, and
by considerably more in small samples.

Our result is accordingly narrow and additive. It concerns what the final-gate
top-decile overlap registers under a quantised prior — not the arithmetic of any
reported value, which we reproduce exactly, and not the conclusion that control
supports. Gate correlations and predictive R² are likewise unaffected, since
both use values rather than their order.

### 4.5 Scope

The two statements of Section 4.2 have different scopes. C1 — a plateau larger
than q — is a property of the prior and the decile size alone, and bounds what
any top-q overlap on that prior can register. C2 and C3 concern a particular
initialisation and a particular tie-breaking rule, and determine the value the
statistic returns. Neither is a claim about top-k overlap in general, and
neither is a claim about other forms of interpretive stability: a measure may
legitimately be insensitive to sample size, or legitimately high, for reasons
that have nothing to do with the three conditions here. The Raman arm used a
continuous prior, fails C1, and is treated in Section 7.

It is worth separating what this paper establishes at three different strengths,
because they are easy to read as one claim and only two of them are results.

| | status |
| --- | --- |
| **The computational mechanism.** Where the selection boundary cuts through a level of exactly equal values, the top-q set is decided by the tie rule rather than by the values. | **Demonstrated**, and not empirically: it follows from what a sort does with equal keys. The boundary condition is checkable on any stored gate. |
| **The experimental consequence.** On the near-infrared gates examined here, procedures differing only in tie rule return overlaps from 0.7442 to 1.0000 on identical inputs, and the published figure is one of them. | **Observed**, in this dataset, this architecture, this prior, two environments. |
| **The general prevalence.** How large and how frequent this effect is across other architectures, priors and datasets. | **Not established.** We did not measure it, and nothing here should be read as having measured it. It is an implication worth investigating, offered as a question rather than a finding. |

The contribution of this paper is the first two rows. The third is stated so
that a reader does not take it from us, and the check that would begin to
answer it is in the repository and needs no retraining.

---

## Conformidade com o ADR-0003, frase por frase

Verificação explícita, porque a ressalva 3 é verificável e não declarativa.

| exigência | como o rascunho cumpre |
| --- | --- |
| relatar a propriedade e os números | §4.1 a §4.3 e §5, com todos os valores medidos |
| citar o artigo anterior como fonte | "the earlier study", "that codebase", "the revision data" |
| não afirmar que as conclusões estão corrigidas | nenhum verbo de correção aparece; §4.4 fala de *escopo*, não de estatuto |
| não afirmar que permanecem válidas | §4.4 diz o que **não** é afetado (R², ρ) e cala sobre o resto |
| deixar a medida falar | §4.2 termina em "reproduced exactly", sem conclusão editorial |
| **[novo]** não exagerar o alcance | §4.2 separa C1 (métrica cega) de C1+C2+C3 (valor artificial), com as três combinações medidas |
| **[novo]** não construir espantalho | §4.4 reporta o controle de deslocamento do artigo anterior e diz que ele **não** é afetado, antes de enunciar o que o nosso achado acrescenta |

**Onde eu quase escorreguei, e registro:** a primeira versão de §4.4 dizia
"these results do not invalidate the earlier study" — o que é afirmação sobre
estatuto, na direção oposta, e viola a mesma ressalva. Trocado por um enunciado
sobre o que a métrica registra. Negar a invalidação é tão editorial quanto
afirmá-la.

**Onde eu escorreguei de fato, e é pior:** a primeira versão deste rascunho não
mencionava que o artigo anterior **já havia testado** a leitura alternativa, com
o controle de deslocamento, e que **já reportava** o Jaccard de 0,38 em NIR.
Omitir isso seria construir espantalho, e um parecerista que leia os dois acha
na primeira passada. A §4.4 passou a abrir por aquele controle, antes de dizer o
que o nosso achado acrescenta — que é estreito: o que o número de decil final
registra, e não a conclusão que o controle sustenta.

---

## Mudanças desta versão

- **§4.2 reestruturada em três condições separáveis** (C1 platô > q, C2 empates
  persistentes, C3 resolução pelo sort), com as três combinações que os nossos
  dados exibem numa tabela. Atende à precisão do parecer: platô > q não torna a
  estabilidade artificial por si só.
- **Matemática explícita**, pedida no item 2 do parecer: a esperança exata de J
  sob desempate aleatório é hipergeométrica, dá 0,7012 em q = 28 e 0,7445 em
  q = 29, e a aproximação q/(2L − q) erra por 0,0012.
- **Dois enunciados em vez de um**: C1 limita o que a métrica registra; C1+C2+C3
  determina o valor. Conflatá-los exagera o resultado — e eu os conflatava.
- **Resumo** passou a citar o controle de deslocamento do artigo anterior.

## O que preciso de você

1. **Rodar `check_gates_r2.py`** sem `--q` para fechar o número pendente de
   §4.2.1. O alvo é E[J] = 0,7445; se vier longe disso, há coisa a entender
   antes de a frase ser escrita.
2. **O estágio editorial do artigo anterior** — publicado ou em provas. Não
   muda nada no rascunho acima; muda a terceira via registrada no `ADR-0003`.
3. **Voz e registro**: este é o tom que eu levaria às onze seções. Se estiver
   seco demais ou técnico demais para o Chemolab, melhor ajustar agora que
   depois de dez seções escritas.
4. **"0.9418" no resumo**: manter exato ou arredondar.
