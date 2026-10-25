# Resumo — versão C
# Aprovado em 2026-10-24. Revisado em 2026-10-25 por decisão editorial
# do autor: não declarar sustentação INTEGRAL da interpretação anterior
# pelo controle de deslocamento. Medido em F007 no mesmo dia: a
# dependência do platô existe e é de ordem 0,02-0,05 em n cheio, e o
# que sobra responde a n (+0,8929, p = 0,0068). O resumo reporta os
# dois lados e não afirma sustentação integral.

250 palavras. Registro e exigências em `00-estrutura.md`, seção
"Registro editorial". Limite de trabalho: 250.

---


Interpretive stability in prior-guided spectral attention is usually reported
as the overlap of the top-k selected bands across runs. We give the conditions
under which that overlap measures band selection, and show that a step-
function prior over 281 near-infrared bands -- from our own earlier work --
violates them. When a level set of the prior is larger than the selected set,
the selection can fall entirely inside it, and the overlap registers only the
ordering the gate carries there. That geometry creates the possibility of an
artefact but does not produce one; three conditions together do, and we
separate them: an oversized level set, ties that persist through training, and
a deterministic rule that resolves them. The near-infrared prior meets all
three when it also initialises the gate, saturating the plateau until its
values are numerically identical: an overlap of 0.9418 falls to 0.7005 +-
0.0068 under random tie resolution, against an exact expectation of 0.7012 for
drawing 28 of 34 plateau bands twice. A continuous Raman prior meets none. A
displacement-based control in that earlier study depends on neither the top-k
selection nor the tie-breaking and is immune to this artefact; excluding the
plateau bands lowers it by 0.018 (Pearson) or 0.051 (Spearman) at the largest
sample size, and what survives still responds to n. Decile overlap grows with
n without anchoring (+0.93, p = 0.003) and not under prior- initialisation
(-0.32, p = 0.48). We report twenty pre-registered hypotheses, eight of which
our criteria did not support.
