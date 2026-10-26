# Legendas das figuras

Data: 2026-10-25
Gerador: `scripts/10_figuras.py`

Regra do programa: **nenhum gráfico carrega título.** Toda a identificação está
aqui. As figuras 1, 2 e 3 estão geradas; as 4 e 5 aguardam o layout real dos
arquivos de resultado, que não vou adivinhar.

---

## Figura 1

> **The near-infrared literature prior.** The prior assigns one constant value
> to each reported absorption region — 0.6 to 680–700 nm, 1.0 to 900–1000 nm,
> 0.8 to 1100–1200 nm — over a floor of 0.1 elsewhere, and is then divided by
> its maximum, which is already 1. The 281 wavelengths therefore take four
> distinct values, and the number of bands at each is printed above its step.
> The shaded block is the prior's maximum: 34 bands, larger than the
> top-decile size q at either convention in use (28 in the published ablation,
> 29 here). That inequality is the geometric condition examined in Section 4.
> The plateau is a property of this construction and not of the
> normalisation.

## Figura 2

> **Overlap of the top-decile gated bands across seeds, by how ties are
> resolved.** Filled markers are the seven training sizes of the earlier
> revision data, at that dataset's own convention q = 29; open markers at the
> right are the cell reported in the accepted study, at the convention of the
> code that produced it, q = 28. Circles give the overlap with ties left to
> `numpy.argsort`, squares the overlap with ties resolved at random over 200
> draws, with error bars at one standard deviation across draws. The dotted
> line is the exact hypergeometric expectation of the Jaccard index for two
> independent uniform draws of q bands from the 34-band plateau; it is not
> q/(2L − q), which is the same index evaluated at the expected overlap and a
> strict lower bound by convexity (Section 2.5). The randomised series lands
> on that expectation in every cell, because the selected set lies entirely
> inside a plateau of one distinct value and the gate values then enter the
> statistic nowhere.

## Figura 3

> **Response of two stability measures to the training set size.** Panel (a):
> top-decile overlap across seeds with the prior kept out of the
> initialisation. Panel (b): the same overlap with the prior in the
> initialisation. Panel (c): the reproducibility of the gate displacement
> d = g_final − g₀ across seeds, computed over all 281 bands and again with
> the prior's 34-band plateau excluded, with error bars at one standard
> deviation across seed pairs.
>
> The horizontal axis is shared so that the panels may be compared by slope.
> **The vertical axes are independent and deliberately so: a Jaccard index and
> a displacement correlation are different statistics, and a common vertical
> scale would suggest an equivalence between them that does not hold.** Panel
> (a) shows the growth observed over these seven sizes and is not offered as a
> general law of growth; panel (b) shows high overlap with no statistically
> detectable monotonic association with n; in panel (c) the vertical distance
> between the two series is the observed difference between the correlations,
> which is the plateau's contribution.
>
> **Seven sample sizes support a statement about sensitivity to the data, not
> an identification of the mechanism behind the growth.** Nothing in this
> figure is evidence of a causal relation, and the association in panels (a)
> and (c) is not evidence that the gate recovers chemically relevant bands
> (Sections 8.3 and 9.3.2).

## Figura 4

> **The Raman control.** Panel (a): the Raman prior, a sum of Gaussians over
> the 1870 Raman shifts, which takes 545 distinct values and attains its
> maximum at a single band, with 1326 bands resting on its lower clip. **This
> prior was reconstructed by the original procedure rather than read from an
> archived vector.** Its properties agree with those the registered run
> recorded — the same 545 distinct values and the same single-band maximum —
> and the figure is not drawn unless they do. Element-by-element identity with
> the vector actually used in that run was not verified, because the run
> archived the properties and not the vector; two different priors could share
> those properties, so the agreement is necessary and not sufficient. Panel
> (b): the overlap of the top-decile gated bands across seeds in the three
> partitions, with ties left to `numpy.argsort` and with ties resolved at
> random, error bars at one standard deviation across 200 draws.
>
> **The two series in panel (b) coincide**, to a difference of 0.0000 in every
> partition, because the trained gates carry only 5, 4 and 8 exactly tied
> values among 1870 bands and the selected set is not drawn from a tied block.
> The same operation lowers the near-infrared figure of the accepted study by
> 0.2413. The architecture, the gate, the objective and the training procedure
> are identical between the two modalities; only the functional form of the
> prior differs, which is what makes this a control and not a replication.
>
> The decile here follows the published definition q = p // 10 = 187, the
> convention of the code that produced the Raman run. It is not mixed with the
> q = 29 of Figures 2 and 3 (Section 2.4).

## Figura 5

> **Within-level agreement between the gate and the external reference, by
> partition.** For each prior level, the rank correlation between the gate and
> the absolute coefficients of the PLS model calibrated on that partition's
> training split, computed within the bands at that level, averaged over the
> ten seeds, with error bars at one standard deviation across seeds. Two
> levels are shown: the prior's floor, which carries 223 of the 281 bands, and
> its plateau, which carries 34. The prior's remaining level of 7 bands is
> below the threshold at which the analysis interprets a within-level
> correlation and is not plotted.
>
> All values are at λ = 1, fixed by the pre-registration and not chosen from
> the data, and are computed by the same functions that produced the result in
> the text rather than recomputed for the figure.
>
> The floor's partition means are positive in all ten; the plateau's are
> negative in four of the ten, two in each group of five. **The ten partitions
> are not independent replicates**: each is an 80/20 split of the same 725
> fruits under a different seed, and any two training sets share about 80% of
> their fruits, so the panel shows how the measurement behaves under
> re-splitting and no rank test over these ten points carries its nominal
> level (Section 8.1). The figure does not establish that the gate carries
> ordering information at the floor and not at the plateau: a weaker result at
> the plateau is not evidence of absence there, and the absence of a
> demonstrated difference between the levels is not a demonstration that they
> behave alike. **This is agreement between two estimators built from the same
> training data, not evidence that either recovers chemically relevant bands**
> (Section 8.3).
