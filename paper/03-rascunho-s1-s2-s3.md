# Rascunho — Seções 1, 2 e 3

Data: 2026-10-25
Registro: **C**, conforme `00-estrutura.md`, seção "Registro editorial"
Sequência: condição de validade → mecanismo de falha → demonstração
experimental → controle não afetado → limites → recomendações

Exigências do autor atendidas aqui: as **duas convenções de decil** declaradas
na §2 (exigência 2 do registro), e a **alcançabilidade de parâmetros**
distinguida da **capacidade da classe de hipóteses** na §1.

A §1 não carrega números, por desenho.

---

## 1. Introduction

Spectral models that expose a per-band gate are attractive because the gate
invites a reading: the bands it raises are the bands the model found
informative. The same reading has been questioned where learned weights are
offered as explanations elsewhere — attention weights that do not track other
measures of importance, and whose very different configurations give the same
prediction [1] — and saliency maps that survive randomising the model and the
labels, which is to say that they are independent of both [2]. The mechanism
examined here was introduced for near-infrared regression at small sample
sizes [3] and carried to a second modality, with a literature-derived prior,
in [4]. When a prior derived from the literature is used to guide that
gate [4], the reading acquires a second claim — that the guidance makes the
selection reproducible, so that independent runs identify the same chemistry.
The usual evidence for this claim is the overlap of the top-k gated bands
across runs that differ only in their random seed, reported as a Jaccard
index [5].

**That overlap has to be read against chance, and the need to do so is not
new.** The feature-selection literature has corrected set overlap for chance
for nearly two decades: the consistency index of Kuncheva [6] subtracts the
hypergeometric expectation of the intersection of two random subsets of equal
size, and Nogueira et al. place that correction [7], and others, on a stated
set of properties. What this paper adds is narrower and specific to the way a
quantised prior is written down. When the prior assigns one value to a block of
bands, the gate inherits ties inside that block, and the top-k cut then falls
inside a tied set whose members a sorting rule — not the data — orders. Under
that condition the relevant chance level is not the expectation of the
intersection but the exact expectation of the Jaccard index over the tied
block, and the figure the overlap takes depends on the tie-breaking rule. The
conditions are geometric, they are checkable before any model is trained, and
the way of encoding a prior that we used in our own earlier work [4] violates
them. How often other encodings do is not something we measured, and we do not
assert it.

### 1.1 What the interpretive claim would have to assert

It helps to state the two claims in the terms a learning problem provides,
because they are not the same kind of claim and only one of them has an
established estimand.

The predictive claim is standard. A hypothesis class, a loss, and a
distribution over spectra and reference values define a risk; the empirical
risk on held-out data estimates it; and uniform convergence over the class
bounds the gap between the two as a function of sample size and the class's
capacity. The quantity being estimated exists independently of the estimator,
and the guarantee is about approaching it.

The interpretive claim has no such structure. To say that a procedure
*identifies* informative bands presupposes a target set of bands — a true
support — and asserts that the procedure estimates it. Agreement between two
runs then measures the variance of that estimator and says nothing about its
bias: two runs can agree perfectly and both be wrong, and they will do so
whenever the agreement is produced by something the two runs share that is not
the data. A prior shared by both runs is exactly such a thing.

We do not claim that seed overlap has no population limit. Under assumptions
about algorithmic stability, the data distribution and asymptotic behaviour, a
selection overlap may well converge to a well-defined population quantity, and
nothing here rules that out. The narrower point is the one the argument needs:
**even where the overlap converges, its limit is a property of the procedure's
agreement with itself, and convergence to it does not establish that the
selection recovers a true support.** Held-out risk differs not in having a
limit but in what the limit is — a property of the data distribution, against
which the estimate can be wrong in a way that more data corrects. Reproducibility is therefore necessary for recovery of a support and
nowhere near sufficient, and the gap between the two is where a prior can do
its work undetected.

We do not argue that the interpretive claim is unavailable. We argue that the
measure in common use does not test it, and we give the conditions under which
it would.

### 1.2 Restricted reachability is not restricted capacity

Part of our account turns on gate parameters that gradient descent cannot
move, and it is worth separating that from a claim we are not making.

Initialising the gate at the prior places some parameters in a region where the
gradient of the training objective with respect to them is numerically
negligible. Those parameters are then effectively frozen: the fitted model
occupies a proper subset of the parameter space, and the bands they control
contribute a value fixed by the prior rather than learned. This is a statement
about which hypotheses the optimiser can reach from a particular starting
point.

It is not a statement about the hypothesis class. The class is the same
parametric family either way, with the same capacity by any of the usual
measures; nothing about the initialisation removes a function from it or
changes what it could express. In particular, no hierarchy of nested classes is
induced, and the apparatus of structural risk minimisation does not apply. The
restriction lives in the optimisation, not in the class, and the distinction
matters because the two have different remedies: a capacity restriction would
be a modelling choice to defend, whereas a reachability restriction is an
artefact of initialisation and is removed by changing it, which is what we
recommend.

### 1.3 What this paper does and does not conclude

We separate three conditions that are easily conflated, show which of them a
step-function prior satisfies, demonstrate the consequence on an archived
result, and verify on a second modality with a continuous prior that the
consequence is not intrinsic to the architecture. We then report where the gate
does and does not follow the data.

That last point should be stated at the outset, so that the paper is not read
as a denial of it. **The gate is not inert.** On both modalities it aligns with
a separate, data-derived statistical reference, the alignment is positive in
every
partition we measured, and it survives conditioning on the prior. What we find
is that this alignment is independent of which prior was used, and that it is
present at the prior's lowest level, which carries 223 of the 281 bands and
which the top-decile metric never reads. We do not claim it is *absent* at the
prior's maximum: the measurements there are inconsistent in sign and we
describe them as such, without converting a weaker result into a demonstrated
difference between the two levels (Section 8.1). The gate learns from the data;
the top-decile overlap, in the configuration examined here, is not where that
learning can be seen. Section 8 reports it.

---

## 2. Data and methods

### 2.1 Datasets

**Near-infrared.** The mango dry-matter dataset, version 3, harvest 4 [8],
whose calibration across seasons, locations and cultivars is reported by
Anderson et al. [9], with p = 281 wavelengths spanning 309 to 1149 nm in steps
of 3 nm. Splits are grouped by fruit: the collection holds 725 fruits of which
723 were measured twice [4], so a random split over spectra would place two
measurements of one fruit on opposite sides of the partition and inflate
held-out performance. All partitions reported here are grouped.

**Fruit identity is inferred, not supplied, and we state what that does and
does not guarantee.** The published file carries no fruit identifier. The
grouping variable is constructed as runs of consecutive rows sharing every
metadata field and the dry-matter value, and whole groups are assigned to one
side of a split. We verified three properties over all fifteen split seeds used
in this work and the one default. The group-size distribution reproduces the
recorded structure exactly: 723 groups of two spectra and 2 of one, 725 groups
over 1448 rows. No metadata-and-dry-matter key spans more than one group. And
in every split, no such key appears on both sides.

The third property is strong evidence of per-fruit separation and not a proof
of it. Concluding that no physical fruit straddles a split requires the further
assumption that every measurement of one fruit carries an identical key, which
is the assumption the identification procedure rests on; the check is therefore
circular with respect to it, and the file holds no fruit identifier with which
to break the circle. This is a limitation of the source data rather than of the
splitting procedure, and we report the verified properties rather than the
conclusion they would support under the extra assumption.

**Raman.** The `bioprocess_substrates` collection [10,11], glucose as the
regression target, with p = 1870 Raman shifts; the collection is also one of
the sets gathered by a public Raman benchmark [12]. The source records 6960 spectra; 488 carry
no glucose value and are dropped at ingestion, leaving 6472 analysed. The
exclusion criterion is a missing (`NaN`) target and nothing else, and the count
is recorded by the loader rather than reconstructed afterwards. Splits are not
grouped: the ingestion exposes no batch identifier, so no grouping variable is
available, and this is a limitation rather than a choice (Section 10).

### 2.2 Priors

The near-infrared prior is assembled by assigning one constant value to each of
three literature-derived regions relevant to dry-matter content [13] — 0.6 to
680–700 nm (chlorophyll), 1.0 to 900–1000 nm (second C–H overtone), 0.8 to
1100–1200 nm (first C–H overtone), the last two being the overtone regions
catalogued by Workman and Weyer [14] — over a floor of 0.1 elsewhere, and is
then divided by its maximum. The three levels are ours; the three windows and
their assignments are not. Nothing in this paper rests on the windows being the
right ones: what follows depends only on the prior having a level set larger
than the selected set, which Section 4 makes precise. On the 281-wavelength
axis this gives four distinct values, 0.1 on 223 bands, 0.6 on 7, 0.8 on 17,
and 1.0 on the 34 bands falling inside the 900–1000 nm window, which is 12.1%
of the spectrum.

It is worth being exact about where the plateau comes from, because the
generality of what follows depends on it. **The plateau is a property of the
construction, not of the normalisation.** Division by the maximum is in fact
the identity map here, since the largest assigned value is already 1; all it
would ever do is fix the top level. The block of 34 numerically equal entries
exists because a single constant was assigned to a region 100 nm wide. Any
prior written in the form *these regions matter this much* has level sets as
large as the regions it names, whatever fixes the regions. The condition examined in this paper is therefore not a quirk
of one normalisation scheme: it is violated whenever the largest named region
contains more bands than the selected set.

The Raman prior is a sum of Gaussians centred on reported glucose bands, with a
width of 15 cm⁻¹, peak-normalised and clipped below at 0.01. It takes 545
distinct values over 1870 shifts and attains its maximum at a single band. The
two priors encode comparable chemical knowledge and differ in quantisation, and
that difference is what makes the Raman arm a control rather than a replication.

### 2.3 Gate and objective

The gate is a per-band sigmoid, `g = σ(θ)`, multiplying the spectrum before a
light multilayer perceptron, trained end to end; the architecture is the one
specified in [4], unmodified. The prior `s` enters in two
places, and the two are **crossed** rather than being alternatives, so that
four configurations are trained and not two:

- the **initialisation**, `θ₀ = logit(s)` against `θ₀ = 0`;
- the **penalty**, a term `λ · KL(g ‖ s)` averaged over bands, with λ on a
  logarithmic grid anchored at λ = 0 — which reproduces the earlier model
  exactly — and refined between 0.1 and 1, where the transition occurs.

Each initialisation is therefore trained across the whole λ grid. Section 3
compares the four: λ is what the zero-initialised arm varies in order to
constrain the solution, and it is also what the prior-initialised arm varies in
order to show that the penalty cannot move a gate that starts saturated. The
two must not be confused, and the one we recommend is the penalty applied from
`θ₀ = 0`.

**Numerical form of the two roles.** `logit(1)` is not defined and the
near-infrared prior attains 1 on 34 bands, so the implementation clips the
prior to `[ε, 1 − ε]` with `ε = 10⁻⁶` before either role reads it. The logit is
evaluated in double precision and the gate logits are held in single precision,
which puts a band at the prior's maximum at `θ₀ = 13.8155` and therefore at
`g₀ = 1 − 9.5 × 10⁻⁷`: the gate starts just inside the open interval and not at
the boundary, and `σ′(θ₀) = 9.5 × 10⁻⁷`. That factor is the one Section 3.1
reports, and it is a property of the clip rather than of the optimiser. The
penalty is the per-band Bernoulli divergence

`KL(g ‖ s) = (1/p) Σᵢ [ gᵢ log(gᵢ/sᵢ) + (1 − gᵢ) log((1 − gᵢ)/(1 − sᵢ)) ]`,

with both arguments clipped by the same `ε`, reduced by the **mean** over the
`p` bands so that λ is comparable across dimensionalities, and added once per
gradient step to the mini-batch mean squared error. Early stopping is decided
on validation mean squared error alone, with the penalty term excluded, so that
λ does not change the meaning of the selected epoch. Optimisation is Adam at a
learning rate of 10⁻³ with weight decay of 10⁻⁴ applied to all parameters, the
gate logits included. The decay is coupled, in the sense that `torch.optim.Adam`
adds the L2 term to the gradient before the adaptive moments normalise it;
AdamW, which decouples it, is run as a control, and the form of the decay is
therefore a design variable and not an implementation detail. At a band on the
plateau the decay contributes a term of `λ_wd · θ₀ = 1.4 × 10⁻³` to the
gradient on θ, and that term does not carry the `σ′` factor that attenuates the
contribution arriving from the data. We state this of the gradient and not of
the update: under adaptive moments the ratio of two gradient contributions does
not carry over to the ratio of their effects on the step, so nothing here
licenses a quantitative claim about how much of the update each one supplies.

### 2.4 Selection metric, and the two decile conventions in use

Interpretive stability is reported as the mean pairwise Jaccard index of the
top-q gated bands across seeds. The definition of q is not uniform across the
codebases this paper draws on, and because the two definitions give different
numbers and different chance levels, **we declare both and never mix them**:

| source | definition of q | q at p = 281 | exact E[J] on a 34-band plateau |
| --- | --- | --- | --- |
| this work, and the stored metrics of the earlier revision | `ceil(0.10 p)` | 29 | 0.7445 |
| the published ablation of [4] | `floor(p / 10)` | 28 | 0.7012 |

The stored metrics and gate vectors of that revision are the authors' own
unpublished material: they ran under the published protocol, but the
manuscript they belonged to was not accepted and will not be resubmitted.
Every figure drawn from them is therefore a preliminary observation of ours
and is not offered as published or as independent evidence; Section 5, which
uses the seven training sizes throughout, states that its associations are
exploratory.

Every selection figure below carries the convention of the code that produced
it. Figures taken from the published ablation are reported at q = 28 and
compared against 0.7012; figures recomputed on the stored gate vectors of the
earlier revision are reported at q = 29 and compared against 0.7445.

### 2.5 The chance level, and a correction to how we had computed it

Correcting set overlap for chance is established practice in the
feature-selection literature. The consistency index of Kuncheva [6] takes two
subsets of equal size q drawn from L variables, notes that the intersection of
a fixed subset with a random one is hypergeometric with expectation q²/L, and
subtracts that expectation so that independent draws score near zero; Nogueira
et al. put that correction [7] and its alternatives on a stated set of
properties. The point of this section is not that a correction is needed — that
was settled — but that the quantity being corrected is the Jaccard index and
not the intersection, and that for a Jaccard index the two corrections differ.

A chance level for a Jaccard index over a tied block of L bands may be computed
as q / (2L − q), and that is what we had done ourselves, treating it as the
exact value, until the correction recorded here. That expression is not the
expected Jaccard index: it is the Jaccard index evaluated at the hypergeometric
mean of Kuncheva [6], which is not the same thing. If two sets of size q are
drawn uniformly and independently from L bands, their overlap k is
hypergeometric with mean q²/L, and

J(q²/L) = (q²/L) / (2q − q²/L) = q / (2L − q)

identically: the familiar ratio is J evaluated at the expected overlap. But
J(k) = k/(2q − k) has J″(k) = 4q/(2q − k)³ > 0 for k < 2q, so J is strictly
convex in k and Jensen's inequality gives E[J] > J(E[k]). The ratio is a strict
lower bound. We therefore report the exact expectation,

E[J] = Σₖ [C(q,k) · C(L−q, q−k) / C(L,q)] · k / (2q − k),

which exceeds the ratio by 0.0012 at q = 28 and by 0.0009 at q = 29 for L = 34.
In the vocabulary of Kuncheva [6] and Nogueira et al. [7], the correction being
made here is the same in kind and different in its argument: the expectation is
taken of J(k) rather than J taken of the expectation of k. The gap is smaller
than the sampling spread of the estimates reported below and changes none of
our verdicts, but it is systematic and in the direction that overstates any
excess above chance, so it should not be carried into a comparison that is
closer than ours.

### 2.6 External reference

To ask whether the gate follows the data, we need a reference that the gate did
not help produce. We use the absolute regression coefficients of a partial
least squares model fitted on the training partition only. The number of latent
components H is chosen by the one-standard-error rule [15] — the most
parsimonious model whose error is within one standard error of the minimum,
which keeps the reference from being tuned to the partition it will be
compared on — on a cross-validated
error curve computed within the training partition — grouped by fruit for the
near-infrared data, and over plain folds for Raman, where no grouping variable
exists — with the search capped at 120 components and further capped by the
fold sizes. The reference is recomputed per partition and never shared across
partitions, and the gate plays no part in producing it.

The selected H is 46 to 72 across the fifteen near-infrared partitions, and 5,
6 and 6 across the three Raman partitions. The contrast is worth noting before
any comparison between the modalities: a reference built from tens of
components and one built from five or six are not equally sharp localisations
of the signal, and Section 10 returns to what that limits.

### 2.7 Pre-registration

**What a seed test and a partition count can each support.** Two units of
replication appear below and they answer different questions. A test across the
ten random initialisations within one partition characterises the variability
of the optimisation procedure *conditional on that partition's training data*,
which all ten initialisations share; it does not by itself support
population-level inference about spectral relevance. A count across partitions
describes how a measurement behaves under re-splitting, and the partitions are
repeated 80/20 splits of the same 725 fruits with approximately 80% overlap
between training sets, so they are not independent replicates either. We report
seed tests as statements about run-to-run stability, partition counts as
descriptions, and no test over partitions as population inference.

Every hypothesis reported in this paper was written down, with its acceptance
criterion, and committed before the runs that evaluate it. Criteria were not
amended after the data were seen; where a criterion turned out to measure
something other than what it was written to measure, the original text is kept
and the misreading is reported alongside the verdict. Table 1 lists all twenty
hypotheses with their verdicts and, in a separate column, the interpretation we
reached afterwards. Six were not supported. Two more met their criterion only formally or on a narrow reading, and Table 1 records both the verdict and that reading.

**The tie-breaking analysis was not part of the original pre-registered
hypothesis set.** It was introduced as a post hoc diagnostic investigation
after the observed stability patterns raised questions about the
interpretation of top-q overlap. Accordingly, the results of this analysis are
reported separately from the pre-registered hypothesis verdicts in Table 1.
The computational dependence of top-q selection on boundary ties follows from
the selection procedure itself; its observed magnitude and consequences are
specific to the experimental settings examined here. We state this before the
results rather than in the discussion, because a reader is entitled to know
which claims were committed in advance and which were not before reading
either.

---

## 3. Results — the two roles of the prior

A prior can enter this model in two ways, and the distinction is usually
treated as an implementation detail. It is not: one of the two restricts which
gate configurations the optimiser can reach, and the other does not.

### 3.1 Initialising at the prior freezes the plateau

Under `θ₀ = logit(s)`, the 34 bands at the prior's maximum start at a gate
value of 1 − 9.5 × 10⁻⁷ — the clip declared in Section 2.3, not the boundary
itself — and stay there. Gradients propagated through the sigmoid gate carry a
factor σ′(θ) = g(1 − g), which at the plateau is of order 10⁻⁶, and
9.5 × 10⁻⁷ exactly at initialisation; the Fisher
information for those coordinates is 8.6 × 10⁻⁹ against 0.72 for the bands off
the plateau, a ratio of about eight orders of magnitude.

The prior-initialised plateau begins in a numerically saturated region of the
sigmoid, strongly attenuating gradients propagated through the gate. However,
the optimiser also applies weight decay to the gate logits, introducing an
additional contribution to parameter updates that is not attenuated by the
sigmoid derivative. The observed persistence of the plateau is therefore an
empirical property of the complete optimisation procedure, rather than a
consequence of sigmoid saturation alone. Section 1.2's distinction between what
is free in the class and what the optimiser reaches should be read in that
narrower sense: what we observe to persist is the gate, and a gate that does
not move is not by itself evidence that its parameter cannot. Separating the
two would take the ablation named in Section 11, which we did not run — the
optimiser control reported here was run from θ₀ = 0, where no plateau forms.

The consequence is visible in how little the penalty weight then matters. With
the prior in the initialisation, ρ(gate, prior) stays between 0.9987 and 0.9999
across four orders of magnitude of λ: the gate is pinned by where it started,
and the term that was supposed to control how strongly the prior acts is
inert.

### 3.2 Separating the two roles removes the restriction

Setting θ₀ = 0 and letting the prior act only through the penalty removes the
saturation entirely. The count of inert bands — bands whose gate cannot move —
is zero at every λ across seven grids, and zero across all 1500 runs of the
five partitions used for the controls. The prior still constrains the solution;
it no longer decides which solutions are available.

This is the first of our recommendations and the cheapest: the prior's
constraint and the prior's starting point are separable, and separating them
showed no material predictive deterioration in the configurations we evaluated
(Section 5), without establishing equivalence, while removing the condition
that the rest of this paper is about.

**Figure 1.** The near-infrared prior as a step function over the 281
wavelengths, with its four levels, the 34-band plateau at the maximum, and the
top-decile size q marked at both conventions, 28 and 29.
