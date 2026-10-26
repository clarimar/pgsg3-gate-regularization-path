# Rascunho — Seções 6, 7 e 8

Data: 2026-10-25
Registro: **C**, conforme `00-estrutura.md`
Resumo fixado: **C3, 242 palavras**, caso particular no resumo e generalização
na §2.2 e na Discussão

Todos os números conferidos contra `F001`, `F002`, `F003`, `F005` e `F006`
antes da redação. Divergências de convenção: nenhuma — estas seções não usam
métrica de decil em NIR, exceto onde explicitamente citada com o seu q.

**Uma partida do plano, declarada.** A §6 estava planejada como *um* parágrafo.
Escrevi dois: o segundo isola a não-uniformidade entre partições, que o plano
exigia explícita e que não cabe no primeiro sem enterrá-la. Se preferir um só,
o segundo entra como última frase do primeiro e perde ênfase.

---

## 6. Results — the prior controls

None of the metrics we tested separates the prior's chemical content from the
mere fact of anchoring. The pre-registered hypothesis that anchoring alone
buys little was not supported in any partition, in either arm: anchoring on a
prior whose content has been destroyed raises agreement with the external
reference from +0.031…+0.070 at λ = 0 to +0.087…+0.464 at λ = 1, so the
anchoring term and the content term have to be reported as separate
contributions rather than as one effect. Reproducibility behaves the same way
and survives its criterion by the wrong route. No control arm beats the
literature prior on seed-to-seed overlap — all ten control differences are
negative or null — but the `shuffled` arm, whose prior correlates *negatively*
with the data-derived reference in four of five partitions, still reaches an
overlap of 0.957 to 0.975 against the literature prior's 0.9763 to 1.0000.
Stability across seeds is therefore attainable with a prior anticorrelated
with the reference, which is enough to show that stability does not validate
the interpretation it is usually offered to support. Table 1 gives the
verdicts for all five control hypotheses.

These overlaps are not the quantity Section 4 found uninterpretable, and the
difference must be stated or this section would appear to contradict that one.
All runs reported here use θ₀ = 0, so no gate parameter is saturated, the count
of inert bands is zero in every cell, and the analysis script verifies the
absence of exact ties among the sorted values before reporting any overlap.
These figures are therefore genuine agreements among distinguishable values, at
q = 29. The 0.9418 of Section 4 comes from a different configuration — the
prior in the initialisation, at q = 28 — and the two must not be compared
directly. What makes the controls damaging to the interpretation here is not
that the numbers are artefacts; it is that a prior anticorrelated with the
reference earns a genuine one.

The pattern is not uniform across partitions, and any claim about it has to
say so. On the raw agreement metric the literature prior beats the relocated
`blocks` control in **4 of the 15** near-infrared partitions — one of the first
five, none of the second five, and three of the last five. We report the
aggregate and the per-block counts together because the aggregate alone would
support either a positive or a negative reading depending on which five
partitions a reader had seen.

---

## 7. Results — the Raman control

This section is where the explanation offered in Sections 3 and 4 is put at
risk. If the behaviour we describe followed from the architecture, the gate, or
the objective, it would appear again on a second modality. If it follows from
the prior's quantisation, it should disappear when the prior's functional form
changes and nothing else does. The code, the gate, the penalty and the training
procedure are identical between the two arms; only the prior differs.

### 7.1 The two conditions are absent

The Raman prior is a sum of Gaussians rather than a set of constants per
region. Over 1870 Raman shifts it takes 545 distinct values and attains its
maximum at a single band, with 1326 bands resting on its lower clip.

**The selected set is not confined to a tied block.** The fraction of the top
decile falling inside the 1326-band floor is 0.000 in all three partitions, and
the fraction inside the one-band maximum is 0.005 — one band of 187. The
corresponding fraction in near-infrared is 1.000 in 15 of 15 cells. The first
condition of Section 4 is not met.

**There is no tie-breaking collapse.** The trained gates carry 5, 4 and 8
exactly tied values among 1870 bands. The overlap with ties left to the sort is
0.9596, 0.9589 and 0.9303; resolving those ties at random returns the same
three values, to a difference of 0.0000 in all three partitions. The
near-infrared arm of the earlier study drops by 0.2413 under the same
operation, and the seven training sizes of its revision data drop by the same
order. The second and third conditions are not met either.

Both of the properties documented in Sections 4 and 5 are therefore absent
under the same architecture and the same code, with only the functional form of
the prior exchanged. This is what the quantisation account predicts, and it is
the strongest control this work has: the behaviour is a property of how the
prior was written down, not of the method.

### 7.2 Anchoring buys reproducibility here, and the figure means it

With the defect absent, the same comparison becomes informative. Without
anchoring the Raman overlap is 0.56 to 0.58; with anchoring it rises to 0.93 to
0.98. There is no tied block to inflate it and no sort order inside the
selected set, so this increase is a measurement of what anchoring does to
selection stability rather than an artefact of the metric. The contrast with
near-infrared is the point of reporting both: the same nominal gain means
different things in the two arms, and only the geometry of the prior tells them
apart.

### 7.3 The strongest supporting fact is not in any verdict

One quantity in this arm requires no model at all. Correlating the prior's own
shape with the data-derived reference, before any training:

| arm | partition 0 | partition 1 | partition 2 |
| --- | --- | --- | --- |
| literature | **+0.2390** | **+0.1660** | **+0.1600** |
| `blocks` (relocated) | +0.0064 | −0.0435 | +0.0533 |
| `shuffled` | −0.0045 | −0.0141 | +0.0190 |

The published Raman prior is positioned where the data-derived reference puts
weight, and relocating or shuffling it drives that correlation to zero. This is
the opposite of what the near-infrared controls show, it is obtained without
fitting the gated model, and it is the clearest evidence in this paper that a
literature prior can carry information about the signal. It appears in no
pre-registered verdict, because we did not think to pre-register it.

### 7.4 The between-arm comparison, with its reversal

The pre-registered comparison asked whether the literature prior beats the
relocated control on agreement with the reference, with a criterion of two of
three partitions:

| partition | literature | `blocks` | delta | p |
| --- | --- | --- | --- | --- |
| 0 | +0.1964 | +0.0899 | **+0.1065** | 0.0020 |
| 1 | +0.1855 | +0.0855 | **+0.1000** | 0.0020 |
| 2 | +0.1584 | +0.1660 | **−0.0075** | 0.0098 |

The criterion is met at 2 of 3, but partition 2 is a *significant* reversal,
not a near-miss, and reporting the verdict without it would misdescribe the
result. The two supporting margins are about thirteen times larger than the
contrary one. The statement the data support is therefore: **the literature
prior wins clearly in two of three partitions, and in the third it ties, with
the relocated control marginally ahead.** It is not "the literature prior wins
in Raman" without qualification, and we do not write it that way anywhere in
this paper.

**Figure 4.** The continuous Raman prior with the position of the top decile
marked, and the overlap with ties left to the sort against the overlap with
ties resolved at random, for the three partitions. The two series coincide.

---

## 8. Results — where the alignment is

The gate does follow the data. This section reports where it can be seen to,
and the place is not the one the top-decile metric reads.

### 8.1 Alignment at the prior's floor, and what the plateau does not show

Within each level of the step-function prior, we correlate the gate's values
with the external reference across the bands at that level. This asks whether
the gate orders bands that the prior treats as equivalent, which is the only
place the gate can contribute information the prior did not already supply.
The two levels large enough for the analysis to interpret are the floor, with
223 bands, and the plateau, with 34; the remaining level of 7 bands is below
the threshold and is measured but never interpreted.

At the prior's floor — the level of 0.1, carrying 223 of the 281 bands — the
correlation is positive in every partition measured: +0.2982, +0.1679, +0.1457,
+0.3418 and +0.2147 across partitions 5 to 9, and +0.2705, +0.3168, +0.1491,
+0.2901 and +0.2063 across partitions 10 to 14. In each of the ten, the
pre-registered test over the ten random initialisations within that partition
reaches its smallest attainable two-sided value, p = 0.0020. The first group of
five was pre-registered as a secondary observation and the second as a primary
criterion, and the direction is the same in all ten.

At the prior's maximum — the 34-band plateau — the pattern is different. The
partition means there are negative in four of the ten, two in each group of
five, and range from −0.1495 to +0.3578 against the floor's +0.1457 to
+0.3418. The descriptive pattern recurred in both groups of five partitions:
two negative means in each, with group means of +0.1139 and +0.1145.

**What may and may not be concluded from this needs stating carefully, and
three separate limits apply.**

*First, the partitions are not independent replicates.* The ten partitions are
repeated splits of the same 725 fruits, with approximately 80% overlap between
training sets (78% to 82% over the 45 pairs). Consequently, the
partition-level Wilcoxon p-values cannot be interpreted under the usual
independence assumption. We report them descriptively — p = 0.0020 for the
floor against zero, p = 0.1055 for the plateau, and p = 0.3223 for the two
paired against each other — but draw no population-level inference from them.
They are the output of tests whose inferential interpretation is compromised
by the design, not descriptive statistics, and we identify them as such
wherever they appear. The dependence is positive, which suggests the nominal
levels are optimistic, but the magnitude and even the direction of the
distortion depend on the joint distribution of these statistics, which we have
not characterised; we therefore do not assert that the tests are
anti-conservative, only that they are not calibrated for this design.

The pre-registered criterion for this result is a different test, within each
partition and across the ten random initialisations. That criterion is also
bounded, and the bound belongs in the methods rather than in a footnote: the
ten initialisations share the same training data, so the test characterises
the variability of the optimisation procedure conditional on the observed
partition. It does not, on its own, support population-level inference about
spectral relevance.

*Second, failing to clear a criterion is not evidence of absence.* The
plateau's correlations do not establish a positive association there; they also
do not establish that the gate carries no ordering information at that level.
Four of ten partition means are negative and six are positive, which is a
pattern we describe and do not interpret as an absence.

*Third, we did not demonstrate a difference between the two levels, and that
is not a demonstration that they are the same.* A paired comparison over the
partitions does not reach significance, which is not an equivalence test and
licenses no claim that the levels behave alike. A difference in significance
is not the significance of a difference, and the converse error is equally
available.

What survives all three limits is the description: the floor's partition means
are positive in ten of ten, the plateau's are not, and the selection metric of
Section 4 reads only the plateau.

### 8.2 The alignment does not depend on which prior was used

The same within-level correlation, measured on the control arms, gives +0.12 to
+0.37 across all three. A prior whose content has been destroyed produces the
same alignment as the published one. Whatever the gate is recovering at the
prior's floor, it is recovering from the data, and the prior's identity does not
enter.

This is the result that constrains the interpretation most tightly, and it cuts
both ways. Against the reading we began with, it shows that the alignment is
not evidence for the literature prior in particular. In favour of the method,
it shows the gate is not inert and not merely reproducing its initialisation:
something data-dependent is happening, consistently, in the 223 bands at the
prior's floor. Whether the same is true at the plateau is not settled by these
measurements in either direction.

### 8.3 What this is not

**This is not evidence that the gate recovers true chemical relevance.** The
reference is the vector of absolute coefficients of a partial least squares
model calibrated on the same training partition. It is an operational
reference — a second statistical estimate from the same data, not an
independent determination of which wavelengths carry dry-matter information.
Agreement between the gate and that reference means the two methods weight
similar regions. It does not establish that either is right, and it cannot: no
ground-truth support exists for this dataset, which is the gap identified in
Section 1.1 and the first item of the future work in Section 11.

**Figure 5.** Within-level correlation between the gate and the external
reference, by prior level, with the spread across seeds. The floor level and
the plateau level are the two the text distinguishes.
