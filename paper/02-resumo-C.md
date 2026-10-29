# Resumo — versão C
# Aprovado em 2026-10-24. Revisado em 2026-10-25 por decisão editorial
# do autor: não declarar sustentação INTEGRAL da interpretação anterior
# pelo controle de deslocamento. Medido em F007 no mesmo dia: a
# dependência do platô existe e é de ordem 0,02-0,05 em n cheio, e o
# que sobra responde a n (+0,8929, p = 0,0068). O resumo reporta os
# dois lados e não afirma sustentação integral.
#
# Comprimido em 2026-10-28 de 304 para 249 palavras, pelo limite
# confirmado do Chemolab — "does not exceed 250 words", lido no guia
# vigente e citado literalmente na `07-declaracoes-submissao.md`. A
# aritmética da compressão, o inventário dos 21 fragmentos obrigatórios
# e o ledger das 55 palavras que saíram estão na §2.3 daquele arquivo,
# com a correção do piso que eu havia relatado errado (266, não 253).
#
# Três decisões do autor, de 2026-10-28, e nenhuma outra:
#   1. a frase de contextualização saiu (14 palavras); o enquadramento
#      passa a ser feito na §1;
#   2. `281 near-infrared bands` para `281 bands` (1), redundância: a
#      modalidade é nomeada na frase seguinte;
#   3. `at the revision data's own convention of q = 29` para `at the
#      revision convention of q = 29` (2), preferida a cortar o verbo
#      `examine`, cujo corte deixaria `disentangle X from Y and their
#      effects` sintaticamente ambíguo.
#
# Recusado pelo autor: escrever `0.7005±0.0068` sem espaços para o
# contador registrar um token em vez de três.
#
# Não tocado: a enumeração das três condições; `permits an artefact but
# does not produce one`; o modelo nulo nomeado com o seu q = 28; a
# cláusula do gradiente, que é o que define `operationally inert` dentro
# do resumo; os quatro números medidos.

249 palavras por espaço em branco. Limite confirmado: 250.
Registro e exigências em `00-estrutura.md`, seção "Registro editorial".

---


We disentangle prior-based gate initialisation from prior-based
regularisation and examine their distinct effects on learned spectral
selections. Initialising at a step-function prior over 281 bands leaves
the prior's saturated level operationally inert, with gradients of order
10^-6 that the penalty cannot move. That geometry permits an artefact but
does not produce one; three conditions together do: an oversized level
set, ties surviving training, and a deterministic tie rule. The
near-infrared prior meets all three, a continuous Raman prior none:
overlap of 0.9418, at that codebase's convention of q = 28, falls to
0.7005 +- 0.0068 under random tie-breaking, against the exact expectation,
0.7012, for drawing 28 of 34 plateau bands twice. Outside the saturated
plateau, the gates retained data-associated structure, aligning positively
with a separate statistical reference across the 223 floor-level bands.
Our earlier displacement-based control depends on neither the top-k
selection nor the tie-breaking and is immune to this artefact; excluding
the plateau bands lowers it by 0.018 (Pearson) or 0.051 (Spearman) at the
largest sample size, and what survives still responds to n. For identical
stored gates, at the revision convention of q = 29, overlap ranged from
0.7443-0.7659 under one sorting implementation to 0.9452-0.9867 under
another, and 1.0000 with index-based tie-breaking; when ties cross the
boundary, the overlap reflects the complete selection procedure rather
than an identifiable property of the gates. We pre-registered twenty
hypotheses, eight of which our criteria did not support; the tie-breaking
analysis was a post hoc diagnostic, reported separately from those
verdicts.
