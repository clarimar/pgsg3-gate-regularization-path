# Rascunho — Seções 9, 10 e 11

Data: 2026-10-25
Registro: **C**, conforme `00-estrutura.md`

A §9.3 é a subseção que a **exigência 3** do autor criou e que não existia no
plano v3. Ela contém **um número pendente**, marcado, e a razão está na §9.3
mesma: a imunidade do controle de deslocamento ao artefato de desempate é
demonstrável por argumento, mas a sua independência do platô é questão
empírica que ninguém no programa mediu. `scripts/09_controle_deslocamento.py`
a mede; até rodar, o texto declara o que sustenta e marca o resto.

Não escrevo valor que não medi.

---

## 9. Discussion

### 9.1 A fit–constraint trade-off that does not bind

The penalty weight λ is meant to trade fit against adherence to the prior, and
in the usual telling λ → ∞ is high bias while λ → 0 is high variance. Neither
end of that description survives measurement here, because the regularisation
path is **flat in risk**: held-out R² is equivalent across the whole range of
λ, in both modalities, and at all seven training sizes of the revision data.
Nothing is being traded. What varies along the path is the reproducibility of
the gate, and Sections 4 through 6 establish that the reproducibility in the
near-infrared arm is either uninterpretable or attainable with a prior
anticorrelated with the reference. The trade-off, stated honestly, is between
a stability that does not affect predictive risk and nothing at all.

This is not an argument against spectral priors. It is an argument against
reading a flat risk path as evidence that the prior costs nothing while the
interpretive metric improves, when the metric's improvement is the part that
does not survive scrutiny.

### 9.2 The objective resembles a PAC-Bayes bound and is not one

The trained objective is an empirical risk plus a Kullback–Leibler divergence
between the gate and a prior specified before seeing the data, which is the
shape of a PAC-Bayes bound. The resemblance is formal and we draw nothing from
it. Three things would have to change for the analogy to become an analysis:
the gate would have to be stochastic rather than a point estimate, so that
there is a posterior over hypotheses for the divergence to be taken between;
the divergence would have to be between distributions over hypotheses rather
than between a deterministic gate and a fixed vector; and inference would have
to sample from that posterior rather than evaluate a single gate.

We state this because the resemblance invites a generalisation claim that the
objective does not license, and because we made that error ourselves during
this work: we briefly treated an observed near-zero difference in held-out R²
as a prediction that a bound would contradict, when the objective being
optimised is not a bound and therefore predicts nothing of the kind. A
stochastic gate is listed in Section 11 as the change that would make the
analysis available.

### 9.3 Why the displacement control is immune, and what we have not measured

The earlier study anticipated the objection that a prior might buy
reproducibility by immobilising the gate rather than by guiding it, and
answered it with a displacement control: it measures d = g_final − g₀, the
change the gate undergoes during training, and reports the reproducibility of
that change across seeds, together with the observation that band-level
identification from |d| is weak. That control is what supports its interpretive
claim, and the defect documented in this paper does not reach it. The reason is
structural and worth setting out, because a reader who has followed Section 4
will reasonably ask.

The defect of Section 4 requires three things: a selected set of fixed size q,
a tied block larger than q from which that set is drawn, and a rule that
resolves the ties. The displacement correlation has none of them. It applies no
selection operator, so there is no q and no top-k cut; it is computed over all
281 bands rather than over a subset; and it therefore never consults an
ordering within a tied block, so no tie-breaking rule enters and `argsort`'s
instability cannot propagate into it. Each of the three conditions fails
separately, and any one failure is sufficient.

The statement we make is the author's:

> The displacement-based control is immune to the deterministic top-k
> tie-breaking artefact documented here, because it operates on gate
> displacements across all spectral bands without selecting a fixed-size
> subset. This does not imply immunity to prior-induced effects: under
> prior-based initialization, the saturated plateau contributes structurally
> identical, near-zero displacements across runs. The influence of these
> coordinates on displacement correlation must therefore be assessed
> separately.

### 9.3.1 The dependence, measured

Under the prior in the initialisation, θ₀ = logit(s), so g₀ = σ(logit(s)) = s
exactly, and d = g_final − s. Three facts about the plateau have to be kept
apart, because only the first is an exact equality and the paper has conflated
them before.

**Within each run, the gate values on the plateau are exactly equal to one
another.** Each seed holds one distinct value over the 34 bands, identical both
by value and by bit pattern in 10 of 10 runs in each of the seven training
sizes, and it is that equality *inside a run* that leaves the selected set to a
tie-breaking rule. This is the artefact of Section 4, and it is the only
property the artefact needs.

**Across runs, the common plateau value is not the same.** We measured this
separately, per training size and never pooled across them, and it differs in
every one: the amplitude of the common value over the ten seeds runs from
2.4 × 10⁻⁷ at n = 30 to 4.1 × 10⁻⁶ at n = 1158. It is larger at larger sample
sizes over these seven conditions, which we report as an exploratory
association and not as evidence that more data drives seeds apart; seven
conditions cannot support that. So the two properties come apart, and the
mechanism rests on the first: a tie inside a run does not require two runs to
tie with each other.

**The displacement on the plateau is numerically negligible but not zero.** The
largest |d| there is between 1.2 × 10⁻⁶ and 6.7 × 10⁻⁶ across the seven
training sizes, against 1.6 × 10⁻² to 5.3 × 10⁻² under θ₀ = 0. The gate did
move, by about a part in a million. Saying d = 0 would be convenient and
false.

**What follows for the correlation is a near-constant block.** Under
prior-initialisation every plateau displacement lies within 6.7 × 10⁻⁶ of zero,
and the seeds differ there by between 2.4 × 10⁻⁷ and 4.1 × 10⁻⁶ depending on
the training size. Twelve per cent of the spectrum therefore carries a
displacement that is the same between seeds to within a few parts in a million,
and that near-constancy contributes agreement to ρ(d) for a reason unrelated to
learning. The dependence requires neither an exact zero nor exact equality
across seeds, which is why the measured near-constancy suffices.

Two caveats on the resolution of these figures.

The first is where the resolution is read. A gate is σ(θ) < 1, so the plateau
sits just below one, inside the binade [0.5, 1), where single-precision values
are spaced 2⁻²⁴ ≈ 5.96 × 10⁻⁸ apart. The familiar 2⁻²³ applies immediately
*above* one: unity is a power of two and lies on the boundary between two
spacing regions. At the correct local spacing, the across-run amplitudes are 4,
6, 4, 6, 20, 34 and 68 steps across the seven sizes — integer multiples, which
is what makes the figures look quantised. The resolution is a property of the
region the values occupy and not a universal detection floor for this quantity.

The second is what that quantisation licenses. The stored values are exactly
representable in single precision, which is a fact about where they lie and
not about how they were produced: rounding, an explicit cast, or a
quantisation step before storage would leave the same trace. We therefore
report the representability as measured, offer single-precision arithmetic
somewhere upstream as the explanation we find likeliest, and do not claim the
provenance, which would require tracing the types used in training, export and
loading. We
assessed it separately, as the statement above requires, computing

    ρ_all = corr(d⁽ᵃ⁾, d⁽ᵇ⁾)        ρ_outside = corr(d⁽ᵃ⁾_¬P, d⁽ᵇ⁾_¬P)

where P is the 34-band plateau, under both Pearson and Spearman because the
published control's definition is not recorded in our materials.

| n | ρ_all (Pearson) | ρ_outside | ρ_all (Spearman) | ρ_outside |
| --- | --- | --- | --- | --- |
| 30 | 0.2492 | 0.1358 | 0.2073 | 0.0788 |
| 60 | 0.2357 | 0.0605 | 0.2056 | 0.0404 |
| 100 | 0.2572 | 0.1233 | 0.2141 | 0.0720 |
| 200 | 0.7945 | 0.5888 | 0.6541 | 0.5026 |
| 400 | 0.8164 | 0.7259 | 0.7537 | 0.6490 |
| 700 | 0.8562 | 0.7990 | 0.7811 | 0.6830 |
| 1158 | 0.9369 | 0.9185 | 0.8879 | 0.8369 |

Removing the plateau lowers the figure in all seven cells under both
definitions, so **the dependence is real and we do not claim the control is
unaffected**. It is specific to the initialisation rather than to dropping
bands: under θ₀ = 0, where no plateau is saturated, the same removal changes
the correlation by −0.024 to +0.003, a mean of −0.012, against a mean of
−0.114 in the anchored arm — about nine times smaller. The premise is
confirmed directly, the largest |d| on the plateau being between 1.2 × 10⁻⁶
and 6.7 × 10⁻⁶ under prior-initialisation against 1.6 × 10⁻² to 5.3 × 10⁻²
under θ₀ = 0.

### 9.3.2 Its magnitude, and what the response to n does and does not show

Two things follow, and they point in opposite directions.

The dependence is largest where the published control makes no claim. At
n ≤ 100 the correlation outside the plateau is 0.04 to 0.14 against a total of
0.21 to 0.26, so displacement reproducibility in that regime is mostly the
plateau. At the full training size it is small: 0.9369 against 0.9185 under
Pearson and 0.8879 against 0.8369 under Spearman, a contribution of order 0.02
to 0.05. **Both definitions give the same answer, so the unrecorded definition
of the published figure does not change this conclusion.**

And the displacement correlation responds to the data in the way the decile
overlap does not. Its rank correlation with training size is +0.9643
(p = 0.0005) over all bands, and it remains +0.8929 (p = 0.0068) with the
plateau removed, against −0.3214 (p = 0.4821) for the decile overlap under the
same initialisation.

Two cautions on reading that, both of which we judge necessary. The rank
correlation establishes a strong monotonic association between displacement
reproducibility and training size across the seven conditions examined, and
nothing beyond it. It does not establish that what remains once the plateau is
removed is the learning of chemically relevant bands: that inference needs a
known support, and neither dataset here provides one (Sections 1.1 and 8.3).
And responding to sample size is a diagnostic of sensitivity to the data, not
a test of interpretive validity. What we may say is that the displacement
control is sensitive to the data where the decile overlap is not, which is
favourable evidence about the measure and not a validation of any
interpretation built on it.

The conclusion therefore has three parts and we state all three. The
displacement control is immune to the artefact this paper documents. It
carries a measurable dependence on the prior's plateau: excluding the plateau
bands lowers the correlation by 0.018 under Pearson and 0.051 under Spearman
at the largest sample size, and by considerably more in small samples. What
survives that exclusion remains associated with sample size. None of this
amounts to a demonstration that the gate recovers chemically relevant bands,
and we do not offer it as one.

**[PENDÊNCIA RESIDUAL, de exatidão e não de conclusão — registrar se o ρ(d)
do artigo aceito é Pearson ou Spearman. A medida de 2026-10-25 mostra que a
conclusão é a mesma nas duas definições, logo isto deixou de ser pré-requisito
para o enunciado; continua desejável para a §2 citar a definição correta.
Exige a seção do artigo que define o controle, ou o código que o calcula.
Medidas em `findings/F007`.]**

We raised this as a suspicion against that control and it ended as evidence
for it, and we report it in that order deliberately. The one time in this work
that we asserted something about the earlier paper without reading its own
control section, we were wrong in the direction of overstatement, and the
correction is on record.

### 9.4 Prescriptions

Five recommendations follow, in increasing order of what they cost.

1. **Check all three conditions together, not the geometry alone.** Compare
   the prior's largest level set against q; check whether exact ties among the
   gate values survive training; and check what rule resolves them. Each is one
   line. A level set larger than q makes the artefact *possible*, because the
   selection can then fall entirely inside one level — but it does not by
   itself mean the metric registers nothing the prior does not already make,
   since the gate may separate those bands by differences it genuinely learned.
   What the figure reports is a tie rule's output only when all three hold, and
   the three are what Section 4.2 separates.
2. **Report the overlap under randomised tie resolution alongside the
   conventional figure.** The difference between the two is the size of the
   artefact, it costs one line of code, and it requires no change to the
   training procedure.
3. **Report the exact chance expectation, not q/(2L − q).** The ratio is J
   evaluated at the expected overlap and understates the expectation, in the
   direction that overstates any excess above chance (Section 2.5).
4. **Where the gate's band ordering is to be interpreted, avoid an
   initialisation that leaves parameters saturated — or demonstrate that it
   does not.** This is a methodological preference conditional on the use, not
   a general prohibition: nothing here shows that initialising at a prior is
   wrong for every purpose. In the configuration we examined, θ₀ = 0 with the
   prior in the penalty preserves the constraint while leaving every parameter
   reachable, and removes the condition of Section 4 entirely (Section 3.2);
   held-out R² is equivalent between the two across the λ grid, both
   modalities and the seven training sizes we ran, which is the evidence for
   the cost being nil and is as general as those runs. Section 9.3 adds a
   second reason within the same scope: initialising at the prior also leaves
   a block of coordinates with near-zero displacement, which contaminates a
   displacement-based control that would otherwise be clean.
5. **Vary the training set size and check whether the overlap responds.**
   Insensitivity across a large change in n is a reason to look for a cause,
   not a finding in itself — see the limitation in Section 10.

Conditioning the metric on the prior is not a substitute for any of these, and
Section 10 records why.

---

## 10. Limitations

**The reference is operational, not chemical truth.** Every agreement figure in
this paper compares the gate against the vector of absolute coefficients of a
partial least squares model calibrated on the same training partition. It is a
second statistical estimate from the same data. No ground-truth band support
exists for either dataset, so nothing here measures recovery of chemical
relevance, only concordance between two estimators.

**No accuracy claim for Raman.** The Raman ingestion exposes no batch
identifier, so no grouping variable is available and the partitions are not
grouped. Held-out R² is therefore not reported for that modality, and the
Raman arm functions exclusively as a control on the geometry of the prior.

**Two pre-registered criteria measured something other than what they were
written to measure, and we kept both verdicts.** The first conditioned the
agreement metric on the prior in order to test the prior's content; because the
prior is the variable that distinguishes the arms, conditioning on it removes
the contrast and rewards a prior anticorrelated with the reference. The
criterion was badly designed, the verdict stands as recorded, and the reading
we had attached to it is withdrawn. The second tested whether a residual decile
leaves the plateau, which it does — but leaving the plateau was not the same as
being unconfined, and the decile went to the prior's floor. Both are reported
in Table 1 with the verdict and the later interpretation in separate columns.

**One joint reading was never specified.** Two hypotheses about within-level
ordering were pre-registered separately, and how to read them together was not.
We report them separately and do not combine them.

**The response to sample size is an observation about this experiment, not a
rule.** Unanchored overlap grows with n here and anchored overlap does not. We
do not claim that a legitimate stability measure must depend on n: a measure
may be flat because selection has already stabilised, because the signal is too
weak for more data to resolve, or because the procedure is insensitive to the
data by construction. What the data support is the narrower statement that the
two conditions do not measure the same quantity.

**Fruit identity is inferred, so the leakage check is bounded by that
inference.** Absence of leakage was verified against fruit identities inferred
from the available records, not against independent physical identifiers. The
published file carries no fruit column; the grouping is constructed from runs
of consecutive rows with identical metadata and dry-matter value, and the
verification asks whether any such key appears on both sides of a split. It
does not, in any of the splits we use. Concluding from this that no physical
fruit straddles a split requires assuming that every measurement of one fruit
carries an identical key — the assumption the construction itself rests on —
so the check cannot be independent of it. The observable structure is
consistent with the recorded 725 fruits, 723 of them measured twice, which
makes the inference plausible without making it verified. Section 2.1.

**The PAC-Bayes connection is a formal resemblance.** Section 9.2.

**Displacement reproducibility is not interpretable in small samples under
prior-initialisation.** Section 9.3 reports that at n ≤ 100 the displacement
correlation outside the prior's plateau is 0.04 to 0.14 against a total of
0.21 to 0.26, so most of what the measure registers there is the block of
coordinates held at zero displacement by the initialisation. At the full
training size the contribution falls to between 0.02 and 0.05. We report the
figure with its sample size for this reason, and the published control, which
is computed at full size, is not affected by the small-sample behaviour. The
definition of the correlation used in that published control is not recorded
in our materials. Both Pearson and Spearman give the same qualitative
conclusion here, so the omission does not affect what we claim -- but the
original definition is still required to reproduce the earlier figure exactly,
and we record it as an open methodological point rather than a resolved one.

**The programme carries two decile conventions.** The stored metrics of the
earlier revision and this work use `ceil(0.10 p)` = 29; the published ablation
uses `floor(p/10)` = 28. They give different figures and different chance
levels, they are declared per protocol in Section 2.4, and they are never
mixed. This is an inconsistency in the programme, not a divergence between
sources: the two numbers that appeared to disagree were each correct under
their own convention. No figure is rehabilitated by the clarification, because
a tied block larger than q makes the selection figure a tie-breaking artefact
at either q.

**Five mechanical explanations were proposed during this work and discarded.**
Each was advanced as the cause of an observation and then refuted by a further
measurement — in one case by a synthetic fixture that was itself miscalibrated,
which reversed a correct finding before the real re-run reinstated it. We
record this because a reader is entitled to know how much of the final account
was arrived at by elimination rather than by prediction.

---

## 11. Future work

**A known support.** Every agreement figure in this paper is concordance with
a proxy. Measuring recovery rather than concordance requires a design in which
the informative bands are known independently of the model: synthetic spectra
with a support fixed by construction are the cheapest such design, and
controlled mixtures, reference standards and experimental systems whose
composition is set by the experimenter are others. We name synthetic data
because it is what we would run first, not because it is the only route. This is the first item because it is the one that would
convert the interpretive claim from unfalsifiable to testable.

**Empirical Rademacher complexity by fitting random labels.** Section 1.2
argues that prior-initialisation restricts reachability and not capacity. That
argument is analytic. Fitting random labels under both initialisations would
quantify the restriction instead of arguing it, and would test whether the
frozen plateau has any effect on what the model can fit.

**A stochastic gate.** The change that would make a PAC-Bayes analysis
available rather than a formal resemblance (Section 9.2).

**Scale and small samples.** The prior does not improve accuracy at any of
seven training sizes from n = 30 to 1158. That is a real result from the
earlier revision data, it bears directly on when a prior is worth using, and it
has no published home.

**The number of latent components against within-plateau ordering.** Across the
five partitions where both were measured, the rank correlation between the
selected H and the within-plateau agreement is +0.6000, with n = 5 and
p = 0.2848. Five points cannot settle it. We name it, declare the number, and
state that we did not run it.
