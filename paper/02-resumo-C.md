# Resumo — versão C, aprovada em 2026-10-24

242 palavras. Registro e exigências em `00-estrutura.md`, seção
"Registro editorial". Limite do Chemolab não confirmado.

---

Interpretive stability in prior-guided spectral attention is usually reported 
as the overlap of the top-k selected bands across independent runs. We give 
the conditions under which that overlap measures band selection, and show 
that a step-function prior over 281 near-infrared bands -- the one used in 
our own earlier work -- violates them. When a level set of the prior is 
larger than the selected set, the selection can fall entirely inside it, and 
the overlap then registers only the ordering the gate itself carries there. 
That geometry creates the possibility of an artefact but does not produce 
one; three conditions together do, and we separate them: an oversized level 
set, ties that persist through training, and a deterministic rule that 
resolves them. The near-infrared prior meets all three when it also 
initialises the gate, saturating the plateau until its values are numerically 
identical: an overlap of 0.9418 falls to 0.7005 +- 0.0068 under random tie 
resolution, against an exact expectation of 0.7012 for drawing 28 of 34 
plateau bands twice. A continuous Raman prior meets none. A 
displacement-based control in that earlier study uses gate values rather than 
their order, so it depends on neither the top-k selection nor the 
tie-breaking, and it is what supports its interpretive claim. Overlap grows 
with sample size without anchoring (+0.93, p = 0.003) and not under 
prior-initialisation (-0.32, p = 0.48). We report twenty pre-registered 
hypotheses, eight of which our criteria did not support.
