# Rascunho — Seção 5

Data: 2026-10-28
Registro: **C**, conforme `00-estrutura.md`

**Origem desta seção.** O conteúdo abaixo era a §4.3 do rascunho do dia 24 e foi
promovido a seção independente por decisão do autor em 2026-10-28. A razão é
científica: a §4 responde o que o Jaccard mede quando a seleção atravessa um
nível de empate; esta responde como a sobreposição se comporta quando aumenta o
tamanho amostral. São perguntas diferentes. As consequências do desempate para
a reprodutibilidade **ficaram na §4**, onde pertencem, para que esta seção não
seja repetição daquela.

O texto é o mesmo, com o título e a numeração ajustados. Nenhum número mudou.

---

## 5. Results — the response to sample size

The two conditions of the revision data separate on a property that requires no
knowledge of the mechanism — and, it turns out, one of them separates
identically under every selection procedure while the other has no single
answer to give.

**Without anchoring, the overlap rises with sample size, and the rise does not
depend on the tie rule.** It reaches 0.5658 at n = 1158 from roughly a tenth at
n = 30, and the rank correlation with n is **+0.9286 under index-order
tie-breaking, under the sort's own tie order, and under randomisation alike**.
The three procedures agree because, from n = 200 upward, no tie group sits on
the selection boundary at rank q, and a rule can only reorder values that are
exactly equal.

**Under prior-initialisation there is no association to report.** The series is
constant at 1.0000 under index-order tie-breaking and constant at 0.7442 under
randomisation; a rank correlation is undefined on a constant, which is a result
and not a missing value. The series varies only under the sort's own tie order,
and there what varies is the tie order: −0.3214 in the environment of the
published analysis and +0.5714 in a second environment, on the same stored
gates. The historical −0.3214 is retained as that environment's figure and is
not a property of the gates.

**The move from −0.3214 to +0.5714 is not a change in the relation between
spectral stability and sample size.** No such relation changed; the data are
the same bytes. What the two coefficients show is that a correlation computed
from an implicit deterministic selection is a function of the implementation
that resolved the ties. Reading the sign flip as evidence about stability and
sample size would repeat, one level up, the error the section is about.

Both associations are **exploratory**. The seven sizes are nested subsamples of
one collection of 725 fruits and the ten runs within a size share that size's
training data, so these are not seven independent draws from a population of
datasets; the p-values that accompanied these coefficients in earlier drafts
(0.0025 and 0.4821) assumed a replication unit the design does not supply, and
we report the coefficients descriptively and drop the p-values rather than
re-deriving a justification we do not have.

We draw the narrow conclusion: the two conditions do not measure the same
quantity. We do not claim that a legitimate stability measure must depend on n
— a measure may be flat because selection has already stabilised, because the
signal is too weak for more data to resolve, or because the procedure is
insensitive to the data by construction. Insensitivity to a large change in n
is a reason to look for the cause, and here the cause is measured.

The unanchored arm is not wholly tie-free, and the distinction matters for how
the comparison should be read. The criterion is not whether ties exist but
whether one sits **on the boundary** at rank q: ties strictly inside the
selected set leave the set unchanged, and only a group spanning the boundary
lets the rule decide which of its members are taken. From n = 200 upward no
group spans it — at n = 700 two tied values sit inside the selected set and
change nothing — and every procedure agrees to every digit. Below that, some
seeds end training with two or three distinct values across the 34 bands of the
plateau region, and the deterministic rule gains up to 0.028 over the randomised
one (n = 100: 0.1663 against 0.1393; both decile conventions agree on this).
That residual is two orders of magnitude below the 0.22 the anchored arm loses,
and the selected set there is not plateau-bound (0.000 to 0.276 of it falls
inside the plateau, against 1.000 when the prior initialises the gate). The
unanchored condition therefore measures band selection, with a small tie
artefact at the smallest sample sizes; the anchored condition, in NIR, does
not measure it at all.
