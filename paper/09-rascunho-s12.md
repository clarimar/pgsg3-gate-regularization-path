# Rascunho — Seção 12 (Conclusões)

Data: 2026-10-28
Registro: **C**, conforme `00-estrutura.md`

**Origem.** A auditoria integral de 2026-10-28 encontrou que o manuscrito não
tinha seção de conclusões: o plano previa onze seções e nenhuma delas era uma,
e o artigo terminava em Trabalho futuro. O autor autorizou criar a §12,
preservando a numeração de 1 a 11.

**O texto abaixo é o do autor**, com duas alterações que a ressalva dele mesmo
exigiu, declaradas aqui e não embutidas em silêncio:

1. **A cláusula do piso foi acrescentada.** O autor pediu que "limiting the
   interpretation of stable spectral selections as evidence of learning from
   the data" fosse confrontada com os controles de F001–F003. Ela é defensável
   para a **seleção** de decil sob inicialização pelo prior: F001 mede ρ(gate,
   prior) entre 0,9987 e 0,9999 ao longo de quatro ordens de grandeza de λ, com
   34 parâmetros inertes. Ela **não** é defensável como afirmação sobre o gate
   aprender: F003 mede alinhamento positivo com a referência externa no piso do
   prior, 223 bandas, 5/5 com p = 0,0020, e a §8.2 mostra que esse alinhamento
   é o mesmo nos três braços — isto é, vem dos dados. Sem a cláusula do piso, a
   conclusão seria lida como "o modelo não aprende", que é exatamente a leitura
   que a §1.3 foi escrita para impedir.
2. **"Strongly constrained" foi precisado, e depois o meu próprio reforço foi
   corrigido.** Sob inicialização pelo prior a restrição não é uniforme nem
   meramente forte: está concentrada no nível saturado, e fora dele os
   parâmetros se movem. Mas a minha primeira redação dizia que os parâmetros
   do platô **"do not move"**, e o autor recusou em 2026-10-28: isso afirmaria
   imobilidade matemática. O F007 mediu `max |d|` no platô entre 1,2×10⁻⁶ e
   6,7×10⁻⁶ — pequeno e **não nulo**. A §12 passou a dizer inércia operacional
   e local, com os dois números, em vez de constância.
3. **"External" foi harmonizado com o resumo.** A auditoria de 2026-10-28
   apontou que a §12 dizia *external, data-derived reference* enquanto o
   resumo já usava *separate statistical reference*. Não é contradição
   matemática — a referência é externa ao treino do gate — mas "external"
   sugere independência estatística que não existe, e as duas partes do
   artigo não deviam escolher termos diferentes para a mesma coisa. A §12
   passou a dizer *separate*, e a frase seguinte explicita as duas metades:
   separada do treino do gate, **não** independente dos dados.
4. **A natureza da referência foi preservada.** O alinhamento no piso
   é evidência de estrutura aprendida associada aos dados; não demonstra
   recuperação de bandas quimicamente verdadeiras, porque a referência é um
   segundo estimador estatístico sobre os mesmos dados de treino (§8.3). Numa
   conclusão, a ressalva tem de estar ao lado da afirmação.

---

## 12. Conclusions

This study examined how prior-guided spectral gating can produce apparent
feature-selection stability that is not necessarily attributable to
data-driven spectral discrimination. By separating the roles of prior-based
initialisation and regularisation, we identified conditions under which the
prior's influence is not merely strong but inert in practice: where the prior
saturates the gate, the affected parameters receive gradient of order 10⁻⁶,
the penalty weight ceases to move them over four orders of magnitude, and the
bands held there are the ones the prior declares most important. The plateau
parameters exhibit small but nonzero changes, with maximum displacements
between 1.2 × 10⁻⁶ and 6.7 × 10⁻⁶ across the examined training sizes,
indicating operational rather than mathematical immobility. This limits the interpretation of a stable top-q selection as
evidence of data-driven selection. It does not limit the interpretation of the
gate as a whole: outside the saturated level the gate aligns positively with
a separate statistical reference in every partition measured, that alignment
is the same under a prior whose content has been destroyed, and it occurs at
the level of the prior that carries most of the spectrum and that the
top-decile metric never reads. That reference is separate from the gate's own
training but not independent of the data: it is a second statistical estimate
built on the same training partition, so the alignment is evidence of learned
structure associated with the data and not a demonstration that the gate
recovers chemically true bands.

A second finding concerns the measurement of selection stability itself. When
the top-q boundary intersects a group of exactly tied gate values, the
selected subset depends on the tie-breaking rule. Consequently, Jaccard
overlap is a property of the complete selection procedure, rather than an
independently identifiable property of the gate values. In the examined
near-infrared experiments, identical stored gates produced substantially
different overlap values under different sorting procedures and
implementations. Where no tied group crossed the selection boundary — every
control arm at θ₀ = 0, and the unanchored arm from n = 200 upward — the
selected subsets were invariant to tie-breaking, and we verified this rather
than assuming it.

These findings establish a computational mechanism and document its
experimental consequences under the investigated architecture, prior and
datasets. They do not establish how frequently the mechanism occurs in other
spectral-learning systems. The results therefore support a specific
methodological requirement: claims of spectral-selection stability should
identify the selection procedure and verify whether ties intersect the
selection boundary before overlap is interpreted as evidence of reproducible
feature selection. Both checks are arithmetic on quantities already stored,
and neither requires retraining.

Taken together, the two findings point at one thing rather than two. Apparent
stability of a spectral band selection can arise from the interaction between
the prior knowledge built into the model, the behaviour of the gates, and the
procedure that turns those gates into a discrete selection. This paper
demonstrates specific mechanisms of that interaction. How common they are
elsewhere is a question we leave open, and one that the checks above make
cheap to ask.
