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
as the overlap of the top-k selected bands across runs. We disentangle
prior-based gate initialisation from prior-based regularisation and examine
their distinct effects on learned spectral selections. Initialising at a
step-function prior over 281 near-infrared bands, from our own earlier work,
leaves the prior's saturated level operationally inert: the gradient there is
of order 10^-6 and the penalty cannot move it. That geometry creates the
possibility of an artefact but does not produce one; three conditions together
do, and we separate them: an oversized level set, ties that persist through
training, and a deterministic rule that resolves them. The near-infrared prior meets all three; an overlap of 0.9418, at that
codebase's convention of q = 28, falls to 0.7005 +- 0.0068 under random tie
resolution, against an exact expectation of 0.7012 for drawing 28 of 34
plateau bands twice. A continuous Raman prior
meets none. Outside the saturated plateau, the gates retained data-associated
structure, including positive alignment with a separate statistical reference
across the 223 floor-level bands. A displacement-based control in that earlier
study depends on neither the top-k selection nor the tie-breaking and is
immune to this artefact; excluding the plateau bands lowers it by 0.018
(Pearson) or 0.051 (Spearman) at the largest sample size, and what survives
still responds to n. For identical stored gates, at the revision data's own
convention of q = 29, the overlap ranged from 0.7443-0.7659 under one sorting
implementation to 0.9452-0.9867 under another, and reached 1.0000 with
index-based tie-breaking; when the selection boundary intersects a tied group,
the overlap reflects the complete selection procedure rather than an
identifiable property of the gates. We report twenty pre-registered
hypotheses, eight of which our criteria did not support; the tie-breaking
analysis was a post hoc diagnostic, reported separately from those verdicts.
