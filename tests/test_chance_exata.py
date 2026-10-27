"""The chance level for a tied block, and what the program used to call exact.

Calibrated by measured quantities, not arbitrary scales: the fixture reproduces
the real plateau geometry (L=34) and both decile conventions (q=28, 29), and the
asserted values are those recomputed from the archived gates. The earlier
failure in this program came from a fixture perturbed at sd=1e-2 when the data
sat at 1.5e-4 -- 70x off -- which made a real finding look refuted.

WHAT THESE TESTS ARE, AND WHAT THEY ARE NOT
-------------------------------------------
Recorded at the author's request, 2026-10-26, because the count is quoted often
enough that it could be mistaken for scientific validation. The suite holds two
kinds of test and neither establishes a scientific result.

TEXTUAL CONSISTENCY. Most of what follows checks that a claim retired in a
finding has not returned in the manuscript, that a number in the text matches
the number in the finding that declares it, and that a caveat required by a
review is still present. These catch propagation failures -- a correction
applied in one section and not in the three that repeat it, which has happened
repeatedly in this programme -- and nothing else. They would pass on a
manuscript whose every number was wrong, provided the wrong numbers agreed with
each other.

COMPUTATIONAL INTEGRITY. A smaller set checks properties of files, of
calculations and of the procedures implemented: that the exact hypergeometric
expectation matches an independent Monte Carlo route, that a convexity
inequality is strict, that a verifier refuses a subset of the required
partitions, that a figure's axis limits come from the data rather than from a
literal. These check that code does what it says.

NEITHER CATEGORY establishes scientific validity, soundness of the experimental
design, or correctness of a statistical interpretation. Every such judgement in
this programme came from reading, from a pre-registered criterion, or from
external review -- four of this session's corrections came from the last of
those, and no test in this file would have caught any of them.
"""
from __future__ import annotations

import importlib.util
from math import comb
from pathlib import Path

import numpy as np
import pytest

RAIZ = Path(__file__).resolve().parents[1]


def _mod():
    cam = RAIZ / "scripts" / "check_gates_r2.py"
    esp = importlib.util.spec_from_file_location("cgr2", cam)
    m = importlib.util.module_from_spec(esp)
    esp.loader.exec_module(m)
    return m


@pytest.mark.parametrize("q,esperado", [(28, 0.701177), (29, 0.744473)])
def test_esperanca_exata(q, esperado):
    assert _mod().jaccard_esperado_exato(q, 34) == pytest.approx(esperado,
                                                                abs=1e-6)


@pytest.mark.parametrize("q", [28, 29])
def test_aproximacao_e_limite_inferior_estrito(q):
    """q/(2L-q) is J(E[k]), and J is strictly convex, so Jensen is strict."""
    L = 34
    exato = _mod().jaccard_esperado_exato(q, L)
    aprox = q / (2 * L - q)
    assert aprox < exato
    # the ratio IS J evaluated at the hypergeometric mean overlap
    Ek = q * q / L
    assert Ek / (2 * q - Ek) == pytest.approx(aprox, abs=1e-12)


@pytest.mark.parametrize("q", [28, 29])
def test_exata_bate_com_monte_carlo(q):
    """Independent route to the same number: draw the subsets."""
    L, rng = 34, np.random.default_rng(0)
    v = [len(a & b) / len(a | b)
         for a, b in ((set(rng.choice(L, q, replace=False).tolist()),
                       set(rng.choice(L, q, replace=False).tolist()))
                      for _ in range(40000))]
    assert np.mean(v) == pytest.approx(_mod().jaccard_esperado_exato(q, L),
                                       abs=3e-4)


def test_hipergeometrica_soma_um():
    q, L = 29, 34
    tot = comb(L, q)
    s = sum(comb(q, k) * comb(L - q, q - k) / tot
            for k in range(max(0, 2 * q - L), q + 1))
    assert s == pytest.approx(1.0, abs=1e-12)


def test_o_script_nao_chama_a_aproximacao_de_acaso():
    """Guarded on the script, not on the notes: a dated note may quote a
    retired claim in order to retract it, and a live assertion may not.
    test_analise_condicional owns the same guard for the 10/10 count."""
    fonte = (RAIZ / "scripts" / "check_gates_r2.py").read_text()
    assert "chance 0.7436 against 0.7000" not in fonte
    assert "E[J] exact" in fonte and "q/(2L-q)" in fonte


def test_correcoes_datadas_presentes():
    """Each retracted claim keeps its original text plus a dated note."""
    f004 = (RAIZ / "findings"
            / "F004-estabilidade-interpretativa-e-funcao-dos-dados.md").read_text()
    # original text preserved
    assert "coincidem até" in f004
    # and corrected
    assert "Correção de 2026-10-24 — dois erros meus nesta nota" in f004
    assert "livre de empate a partir de n = 200" in f004
    f002 = (RAIZ / "findings"
            / "F002-o-que-as-metricas-interpretativas-medem.md").read_text()
    assert "0,701177" in f002 and "Jensen" in f002


def test_rascunho_nao_afirma_ausencia_total_de_empate():
    """The draft said the unanchored arm has no ties and the two rules agree
    to the last digit. True from n = 200, false below it. Corrected
    2026-10-24; the absolute phrasing must not come back."""
    t = (RAIZ / "paper" / "01-rascunho-resumo-e-s4.md").read_text()
    assert "where no ties occur" not in t
    assert "From n = 200 upward it carries no ties at all" in t
    assert "two orders of magnitude below" in t


def test_rascunho_usa_a_esperanca_exata():
    t = (RAIZ / "paper" / "01-rascunho-resumo-e-s4.md").read_text()
    assert "0.7012" in t and "0.7445" in t
    assert "strictly\nconvex" in t or "strictly convex" in t
    assert "0.7442" in t          # the measured q=29 collapse, no longer pending
    assert "PENDENTE" not in t


def test_cruzamento_acusa_convencao_divergente(tmp_path):
    """The guard that would have caught the mirrored error: in F004 I flagged
    ADR-0001's Jaccard range as divergent when the range was correct and my
    script had truncated q to 28 while the record declares 29. The script now
    reads the record's own q and must say CONVENTION, not DIVERGENCE."""
    import itertools
    import subprocess
    import sys

    p, L, rng = 281, 34, np.random.default_rng(0)
    prior = np.concatenate([np.full(223, 0.1), np.full(7, 0.6),
                            np.full(17, 0.8), np.full(L, 1.0)])
    plato = np.flatnonzero(prior >= 1.0 - 1e-9)
    g = np.repeat(np.clip(prior * 0.98, 1e-6, 1 - 1e-6)[None, :], 10, axis=0)
    g = np.clip(g + rng.normal(0, 1.5e-4, g.shape), 0.0, 1.0)
    g[:, plato] = 1.0 - 1e-6                       # bit-identical, as measured
    np.savez(tmp_path / "gates_n30.npz", gates_lit=g, prior=prior,
             wavelengths=np.linspace(1100.0, 2300.0, p))

    def jm(q):
        tops = [set(np.argsort(x)[::-1][:q].tolist()) for x in g]
        return float(np.mean([len(a & b) / len(a | b)
                              for a, b in itertools.combinations(tops, 2)]))

    (tmp_path / "gate_metrics.csv").write_text(
        "n_actual,p,q,jaccard_lit\n" f"30,{p},29,{jm(29):.6f}\n")

    def correr(*extra):
        return subprocess.run(
            [sys.executable, str(RAIZ / "scripts" / "check_gates_r2.py"),
             "--dir", str(tmp_path), *extra],
            capture_output=True, text=True, check=True).stdout

    def marcas(saida: str) -> list[str]:
        """The flags on the data lines only -- the legend names them too."""
        return [ln.split()[-1] for ln in saida.splitlines()
                if "jaccard_lit" in ln and "stored " in ln and "here " in ln]

    assert marcas(correr()) == ["ok"]
    # pinned to the other convention: flagged as incomparable, not as a
    # disagreement about the measurement
    assert marcas(correr("--q", "28")) == ["CONVENTION"]


def test_resumo_C_carrega_as_quatro_exigencias():
    """The four binding requirements the author attached to approving
    register C, 2026-10-24. Recorded in 00-estrutura.md, 'Registro
    editorial'; two of them correct C's own first draft."""
    import re
    # the file is wrapped prose, so match on collapsed whitespace
    t = re.sub(r"\s+", " ", (RAIZ / "paper" / "02-resumo-C.md").read_text())
    # 1. a plateau larger than q creates the possibility, not the defect
    assert "does not produce one" in t
    assert "only if" not in t          # the overstated phrasing, retired
    # 2. the null model named in the sentence, with its q
    assert "28 of 34 plateau bands twice" in t
    # 3. the displacement control, and why it is immune
    assert "neither the top-k selection nor the tie-breaking" in t
    # 4. the eight refutations declared, not buried
    assert "eight of which our criteria did not support" in t


def test_estrutura_concilia_com_o_ADR_0003():
    """Item 2 of 'O que falta antes da prosa' said the editor route was
    blocking and recorded my recommendation to notify. ADR-0003 decided
    otherwise. Both documents are committed, so the contradiction needs a
    dated note and the original text kept."""
    t = (RAIZ / "paper" / "00-estrutura.md").read_text()
    assert "Isso precisa\n   estar resolvido" in t      # original preserved
    assert "não é mais bloqueante" in t                 # and reconciled
    assert "não se verificou" in t


def test_prior_nao_e_descrito_como_min_max():
    """The literature prior is not min-max normalised: make_literature_prior
    assigns a constant per reported region and divides by a maximum that is
    already 1.0, and the minimum is 0.1, not 0.0. Two committed sources said
    min-max, which was both wrong and narrower than the finding. Corrected
    2026-10-25; the characterisation must not come back as a live claim."""
    for rel in ("scripts/05_diagnostico_jaccard.py",
                "paper/03-rascunho-s1-s2-s3.md"):
        t = (RAIZ / rel).read_text()
        assert "min-max normalized" not in t, rel
        assert "min–max normalised" not in t, rel
    # the construction-based statement replaces it
    t = (RAIZ / "paper" / "03-rascunho-s1-s2-s3.md").read_text()
    assert "property of the\nconstruction, not of the normalisation" in t
    # and the finding records the widened scope
    f002 = (RAIZ / "findings"
            / "F002-o-que-as-metricas-interpretativas-medem.md").read_text()
    assert "maior\nconjunto de nível exceda" in f002
    assert "vale para qualquer prior\nnormalizado min–max" in f002   # original


def test_s6_distingue_jaccard_genuino_do_artefato():
    """Section 6 reports overlaps of 0.957-1.0000 from this work (theta0 = 0,
    no ties, q = 29) which are genuine, while Section 4 reports 0.9418 from
    the earlier configuration (prior-init, q = 28) which is not. Without the
    distinction stated, Section 6 reads as contradicting Section 4."""
    t = (RAIZ / "paper" / "04-rascunho-s6-s7-s8.md").read_text()
    assert "not the quantity Section 4 found uninterpretable" in t
    assert "q = 29" in t and "q = 28" in t
    assert "a prior anticorrelated with the\nreference earns a genuine one" in t


def test_s7_nao_afirma_raman_sem_qualificar():
    """H12c passed at 2/3 but partition 2 is a significant reversal. The
    unqualified form 'the literature prior wins in Raman' must not appear."""
    t = (RAIZ / "paper" / "04-rascunho-s6-s7-s8.md").read_text()
    assert "wins clearly in two of three partitions" in t
    assert "significant* reversal" in t or "significant_ reversal" in t
    # E, 2026-10-26: calling a detected difference a tie contradicts the test.
    # p = 0.0098 means the reversal was registered; "ties ... marginally
    # ahead" was the retired wording, and this guard used to require it.
    assert "marginally ahead" not in t
    assert "in the third it ties" not in t
    assert "the relocated control holds a small advantage that the test" in t
    assert "calling a detected difference a" in t
    assert "it is not a tie" in t


def test_s8_nega_recuperacao_de_relevancia_verdadeira():
    """Mandatory note required by the review: the floor finding is not
    evidence of recovering true chemical relevance, because the reference is
    an absolute PLS coefficient vector from the same training partition."""
    t = (RAIZ / "paper" / "04-rascunho-s6-s7-s8.md").read_text()
    assert "not evidence that the gate recovers true chemical relevance" in t
    assert "operational\nreference" in t
    assert "no\nground-truth support exists" in t


def test_s9_imunidade_do_controle_e_declarada_sem_exagero():
    """Requirement 3 of the register: Section 9 must show why the displacement
    control depends on neither the top-k selection nor the tie-breaking. The
    argument is sound, but 'unaffected' overstates it: under prior-init
    d = g_final - s is identically 0 on the plateau, so 34 of 281 bands agree
    trivially. That is NOT the artifact, and it is not nothing. The section
    must claim the immunity and mark the plateau question as unmeasured."""
    import re
    t = re.sub(r"\s+", " ",
               (RAIZ / "paper" / "05-rascunho-s9-s10-s11.md").read_text())
    assert "immune to the deterministic top-k" in t
    assert "Each of the three conditions fails separately" in t
    # B, 2026-10-26: the displacement on the plateau is numerically negligible
    # but NOT zero -- F007 records max |d| between 1.2e-6 and 6.7e-6. The exact
    # equality is between the GATE VALUES, which is a different fact. This
    # guard used to require the false statement.
    assert "d = 0 on those 34 bands" not in t
    assert "numerically negligible but not zero" in t
    assert "Saying d = 0 would be convenient and false" in t
    # 2026-10-26: three properties kept apart. Only (1) was measured, so the
    # exact-equality claim is scoped to within a run and (2) is given as a
    # bound derived from the measured maximum, not as an observed equality.
    assert "Within each run, the gate values on the plateau are exactly equal" in t
    # superseded 2026-10-26: P2 was measured, so the text no longer says the
    # within-run equality is the only one we measured, nor that nothing
    # answers the across-run question. It says P2 is non-zero.
    assert "the only property the artefact needs" in t
    assert "Across runs, the common plateau value is not the same" in t
    assert "near-constant block" in t
    # the dependence is measured, so it is asserted, not merely flagged
    assert "the dependence is real and we do not claim the control is" in t
    assert "about nine times smaller" in t
    # and the author's veto of the full-support claim is honoured
    assert "interpretive conclusion stands on it" not in t
    assert "published control's definition is not recorded in our materials" in t


def test_s9_pac_bayes_nao_extrai_previsao():
    """The committed plan binds this: formal resemblance, no prediction. We
    made the opposite error once and the section records it."""
    t = (RAIZ / "paper" / "05-rascunho-s9-s10-s11.md").read_text()
    assert "resemblance is formal and we draw nothing from" in t
    assert "we made that error ourselves" in t
    assert "is not a bound and therefore predicts nothing" in t


def test_s10_mantem_a_regra_de_n_retirada():
    """F004's overgeneralisation was withdrawn as a rule. Section 10 must keep
    it withdrawn and state only the narrow claim."""
    t = (RAIZ / "paper" / "05-rascunho-s9-s10-s11.md").read_text()
    assert "not a\nrule" in t
    assert "do not claim that a legitimate stability measure must depend on n" in t
    assert "do not measure the same quantity" in t


def test_script_09_existe_e_declara_o_que_nao_e():
    """It must not be mistaken for a recomputation of the published 0.9462."""
    t = (RAIZ / "scripts" / "09_controle_deslocamento.py").read_text()
    assert "WHAT THIS IS NOT" in t
    assert "does not restate" in t
    assert "g_0 = sigma(logit(s)) = s" in t



def test_f007_registra_as_tres_conclusoes():
    """F007 must keep the dependence, its magnitude, and the n-response the
    measurement produced -- including that the question began as a suspicion
    against the earlier control and ended as evidence for it."""
    f = (RAIZ / "findings"
         / "F007-o-controle-de-deslocamento-e-o-plato.md").read_text()
    assert "7 de 7" in f
    assert "Nove vezes" in f
    assert "+0,8929" in f and "p = 0,0068" in f
    assert "terminou produzindo evidência a favor dele" in f
    # and the two things it must disclaim
    assert "Não é recomputação do 0,9462" in f
    assert "Nenhum resultado do fixture sintético" in f


def test_resumo_suspende_a_sustentacao_integral():
    """Editorial decision of 2026-10-25: the abstract asserts immunity to the
    tie-breaking artefact but not that the displacement control sustains the
    earlier interpretation in full."""
    import re
    t = re.sub(r"\s+", " ", (RAIZ / "paper" / "02-resumo-C.md").read_text())
    assert "is what supports its interpretive claim" not in t
    assert "is immune to this artefact" in t
    assert "lowers it by 0.018 (Pearson) or 0.051 (Spearman)" in t
    assert "at the largest sample size" in t
    assert "what survives still responds to n" in t


def test_f007_nao_confunde_sensibilidade_com_validade():
    """The author's precision of 2026-10-25: +0.8929 is a monotonic
    association across seven conditions, not evidence that the remaining
    stability is the learning of chemically relevant bands, and responding to
    n is a sensitivity diagnostic rather than a test of interpretive
    validity. The earlier 'passes / fails' wording was too strong."""
    import re

    def plano(caminho):
        """Collapse wrapping AND blockquote markers: a '> ' at the start of a
        continuation line otherwise survives into the middle of a phrase."""
        bruto = caminho.read_text()
        bruto = re.sub(r"^>\s?", "", bruto, flags=re.M)
        return re.sub(r"\s+", " ", bruto)

    f = plano(RAIZ / "findings"
              / "F007-o-controle-de-deslocamento-e-o-plato.md")
    assert "associação monotônica forte nas sete condições examinadas" in f
    assert "não teste de validade interpretativa" in f
    assert "Não é validação interpretativa" in f
    s9 = plano(RAIZ / "paper" / "05-rascunho-s9-s10-s11.md")
    assert "does and does not show" in s9
    assert "not a test of interpretive validity" in s9
    assert "sensitive to the data where the decile overlap is not" in s9
    assert "we do not offer it as one" in s9


def test_figuras_nao_tem_titulo():
    """Standing constraint of the programme: no titles on plots. The
    identification lives in the captions file."""
    src = (RAIZ / "scripts" / "10_figuras.py").read_text()
    for proibido in ("set_title(", "suptitle(", "plt.title("):
        assert proibido not in src, proibido


def test_figura3_respeita_as_duas_ressalvas():
    """Author's constraints of 2026-10-25: shared x but INDEPENDENT y, because
    a Jaccard index and a displacement correlation are different statistics;
    and no causal reading of the association with n."""
    import re
    src = (RAIZ / "scripts" / "10_figuras.py").read_text()
    # the y limits come from the data, never a hard-coded window
    assert "set_ylim(0, 0.7)" not in src and "set_ylim(0.9, 1.01)" not in src
    assert "limits from the data, never hard-coded" in src
    leg = re.sub(r"\s+", " ", re.sub(r"^>\s?", "", (
        RAIZ / "paper" / "06-legendas-figuras.md").read_text(), flags=re.M))
    assert "The vertical axes are independent and deliberately so" in leg
    assert "would suggest an equivalence between them that does not hold" in leg
    assert "not an identification of the mechanism behind the growth" in leg
    assert "is not offered as a general law of growth" in leg
    assert "Nothing in this figure is evidence of a causal relation" in leg


def test_figuras_4_e_5_escritas_contra_o_layout_real():
    """Written only after the inventory reported the real fields. Figure 4
    reads cells.json rather than recomputing, Figure 5 imports the finding's
    own functions, and the rebuilt Raman prior is verified against what the
    registered run recorded."""
    import re
    src = (RAIZ / "scripts" / "10_figuras.py").read_text()
    # figure 4 does not recompute what the run already recorded
    assert '"j_index"' in src and '"j_random_sd"' in src
    # and the rebuilt prior is checked against the run, not trusted
    assert "does not match the registered run" in src
    assert "(pgsg1_root, pgsg2_root)" in src      # the importer's real order
    # figure 5 borrows the finding's own code path
    assert "06_analise_plato.py" in src
    assert "h10_serie" in src and "m.ler(d)" in src
    assert "A figure that" in src
    leg = re.sub(r"\s+", " ", re.sub(r"^>\s?", "", (
        RAIZ / "paper" / "06-legendas-figuras.md").read_text(), flags=re.M))
    assert "[pendente]" not in leg
    assert "The two series in panel (b) coincide" in leg
    assert "q = p // 10 = 187" in leg
    assert "fixed by the pre-registration and not chosen from the data" in leg
    assert "not evidence that either recovers chemically relevant bands" in leg


def test_fig5_nao_interpreta_nivel_pequeno():
    """06_analise_plato reports a level below MIN_BANDAS_NIVEL and never
    interprets it; the figure must not plot it as if it were comparable."""
    src = (RAIZ / "scripts" / "10_figuras.py").read_text()
    assert "MIN_BANDAS_NIVEL" in src
    assert "reports such a level and never" in src


def test_figura2_marca_o_que_toma_de_emprestimo():
    """Two numbers in Figure 2 are not recomputed: the accepted study's 0.9418
    and its 0.7005 collapse. They must be marked as constants with a source."""
    src = (RAIZ / "scripts" / "10_figuras.py").read_text()
    assert "PUB_J_SORT = 0.9418" in src
    assert "PUB_J_RAND = 0.7005" in src
    assert "NAO sao recomputados aqui" in src


def test_s8_nao_confunde_diferenca_de_significancia():
    """The floor clears the criterion against zero and the plateau does not.
    That is NOT the floor exceeding the plateau: a paired test over the ten
    partitions gives p = 0.3223. The original wording invited the stronger
    reading; corrected 2026-10-25."""
    import re
    t = re.sub(r"\s+", " ",
               (RAIZ / "paper" / "04-rascunho-s6-s7-s8.md").read_text())
    assert "two of five partitions negative" not in t   # retired count
    assert "negative in four of the ten, two in each group of five" in t
    assert "A difference in significance is not the significance of a difference" in t
    # the three limits the author required, 2026-10-25
    assert "the partitions are not independent replicates" in t
    assert "approximately 80% overlap between training sets" in t
    # the author's precision of 2026-10-25: dependence breaks the calibration;
    # it does NOT license asserting the direction of the distortion
    assert "cannot be interpreted under the usual independence assumption" in t
    assert "draw no population-level inference from them" in t
    assert "not descriptive statistics" in t
    assert "we therefore do not assert that the tests are anti-conservative" in t
    # and the pre-registered criterion carries its own bound
    assert "conditional on the observed partition" in t
    assert "failing to clear a criterion is not evidence of absence" in t
    assert "not a demonstration that they are the same" in t
    assert "the converse error is equally available" in t
    # and the comparative framing must be gone from headings and openings
    assert "The alignment is in the bands the prior demotes" not in t
    intro = (RAIZ / "paper" / "03-rascunho-s1-s2-s3.md").read_text()
    assert "rather than in the bands it\npromotes" not in intro
    assert "We do not claim it is *absent* at the" in intro
    # the descriptive wording the author asked for, not "replication"
    assert "descriptive pattern recurred in both groups of five partitions" in t


def test_f003_registra_o_plato_nas_dez():
    """New numbers must not appear first in a figure. The plateau level on
    partitions 10-14 was computed while drawing Figure 5 and is recorded."""
    import re
    f = re.sub(r"\s+", " ", (RAIZ / "findings"
                             / "F003-onde-esta-o-sinal.md").read_text())
    assert "o platô nas dez partições" in f
    assert "números novos não devem aparecer primeiro numa figura" in f
    assert "4 de 10 negativas" in f and "p = 0,1055" in f
    assert "p = 0,3223" in f
    # the three limits, and that no conclusion rests on the p-values
    assert "Três limites, e os três são meus para declarar" in f
    assert "NÃO são réplicas independentes" in f
    assert "80,05% dos seus frutos" in f
    assert "nenhuma conclusão repousa neles" in f
    assert "não é teste de equivalência" in f
    assert "padrão descritivo recorreu nos dois grupos de cinco" in f


def test_fig5_exige_as_dez_particoes():
    """A pattern search matching ten cells today is not a guarantee. The
    figure refuses a subset instead of drawing it."""
    src = (RAIZ / "scripts" / "10_figuras.py").read_text()
    assert "PARTICOES_FIG5 = tuple(range(5, 15))" in src
    assert "not complete on a subset" in src
    assert "MISSING" in src and "DUPLICATE" in src
    # and it refuses a lambda other than the pre-registered one
    assert "LAM_FIXO is" in src and "not 1.0" in src



def test_legenda4_declara_o_limite_de_rastreabilidade():
    """Equal level counts and plateau size do not prove vector identity. The
    caption must separate: reconstruction by the original procedure, agreement
    of the recorded properties, and the absence of element-by-element
    verification against the vector actually used."""
    import re
    leg = re.sub(r"\s+", " ", re.sub(r"^>\s?", "", (
        RAIZ / "paper" / "06-legendas-figuras.md").read_text(), flags=re.M))
    assert "reconstructed by the original procedure" in leg
    assert "agree with those the registered run recorded" in leg
    assert "Element-by-element identity" in leg
    assert "necessary and not sufficient" in leg


def test_legenda5_declara_a_dependencia_entre_particoes():
    import re
    leg = re.sub(r"\s+", " ", re.sub(r"^>\s?", "", (
        RAIZ / "paper" / "06-legendas-figuras.md").read_text(), flags=re.M))
    assert "not independent replicates" in leg
    assert "share about 80% of their fruits" in leg
    assert "no rank test over these ten points carries its nominal level" in leg
    assert "not evidence of absence there" in leg
    assert "not a demonstration that they behave alike" in leg



def test_metodos_delimita_as_duas_unidades_de_replicacao():
    """Section 2 must say what a seed test and a partition count can each
    support, because the paper uses both and they answer different questions."""
    import re
    t = re.sub(r"\s+", " ",
               (RAIZ / "paper" / "03-rascunho-s1-s2-s3.md").read_text())
    assert "What a seed test and a partition count can each support" in t
    assert "conditional on that partition's training data" in t
    assert "not independent replicates either" in t
    assert "no test over partitions as population inference" in t


def test_script_11_verifica_vazamento_de_fruto():
    """The fruit id is inferred from runs of consecutive identical metadata,
    not read from a column. If a fruit's replicates are not adjacent it maps
    to several groups and can straddle the split, which is leakage."""
    src = (RAIZ / "scripts" / "11_verifica_agrupamento.py").read_text()
    assert "INFERRED, not read" in src
    # the check asks the question on the key, not on the group id
    assert "in BOTH the training and the test side" in src
    assert "holds whatever the group ids are" in src
    # but it is NOT a proof of fruit-level separation: the extra hypothesis it
    # needs is the identification procedure's own, so the check is circular
    assert "circular with respect to it" in src
    assert "strong evidence and not a proof" in src
    assert "no fruit-ID\ncolumn with which to break the circle" in src
    # and State B is not automatically safe
    assert "This is NOT automatically" in src
    assert "an earlier version of this script said it was" in src
    # coverage: every split seed the programme uses, not only Figure 5's
    assert "SEEDS_USADAS = tuple(range(0, 15)) + (42,)" in src
    assert "the result was" in src and "It did not." in src
    # the configuration must come FROM the experiments, not be copied: the
    # same seed is not the same partition under a different season filter,
    # test fraction, row order or split implementation
    assert "SEASON = 4" not in src and "TEST_FRACTION = 0.2" not in src
    assert "def constantes_do_sweep" in src
    assert "Read by parsing, not by import" in src
    assert "a silent copy is how a verifier ends up" in src
    # and State C decides by dependence, not by section
    assert "Identify the dependence, not the heading." in src
    # and it must not request DM twice: FRUIT_META already ends with it
    assert 'usecols=list(FRUIT_META))' in src
    # achar_csv cannot be called without importing the sweep, and therefore
    # torch, so the verifier does the one lookup it needs itself
    assert "cannot be called without importing the module" in src
    # a dirty result must not exit zero
    assert "SystemExit(0 if ok3 else 2)" in src



def test_metodos_declara_inferencia_do_fruto():
    """The methods must say fruit identity is inferred, list the three
    verified properties, and stop short of the conclusion they would support
    only under the extra assumption."""
    import re
    t = re.sub(r"\s+", " ",
               (RAIZ / "paper" / "03-rascunho-s1-s2-s3.md").read_text())
    assert "Fruit identity is inferred, not supplied" in t
    assert "723 groups of two spectra and 2 of one" in t
    assert "strong evidence of per-fruit separation and not a proof of it" in t
    assert "circular with respect to it" in t
    assert "limitation of the source data rather than of the splitting" in t
    assert "all fifteen split seeds used" in t



def test_limitacoes_delimita_a_identidade_inferida():
    """The author's formulation: absence of leakage was verified against
    inferred fruit identities, not independent physical identifiers."""
    import re
    t = re.sub(r"\s+", " ",
               (RAIZ / "paper" / "05-rascunho-s9-s10-s11.md").read_text())
    assert "Fruit identity is inferred" in t
    assert "not against independent physical identifiers" in t
    assert "the check cannot be independent of it" in t
    assert "plausible without making it verified" in t


def test_fig1_posiciona_contagem_no_maior_trecho():
    """A level with disjoint runs has a mean wavelength that can fall in a
    gap: on the real axis the floor's mean lands near 690 nm, inside the
    680-700 window, and the count printed on top of that spike. Found only by
    reconstructing the real geometry (309-1149 nm); the earlier fixture, whose
    axis was 1100-2300, hid it."""
    src = (RAIZ / "scripts" / "10_figuras.py").read_text()
    assert "LONGEST CONTIGUOUS" in src
    assert "max(trechos, key=len)" in src
    assert "prior == v].mean()" not in src       # the retired placement
    # and the caption box is no longer in the bottom strip, which the floor's
    # own count occupies on the real axis
    assert "The bottom strip is NOT free" in src


def test_fig3_rotula_sem_colisao():
    """On a log axis 700 and 1158 sit close enough that the two tick labels
    merged into '7001158' in all three panels of the real figure."""
    src = (RAIZ / "scripts" / "10_figuras.py").read_text()
    assert 'rotation=45, ha="right")' in src
    assert 'merged into "7001158"' in src


def test_verificador_separa_dez_de_dezesseis():
    """The closing sentence said 'those ten splits' while the audit covers
    sixteen seeds; the ten are F003's subset and the sentence must say so."""
    src = (RAIZ / "scripts" / "11_verifica_agrupamento.py").read_text()
    assert "those ten splits share about 80%" not in src
    # the sentence spans several print() calls, so assert fragments that each
    # fit on one line: collapsing whitespace leaves the '") print("' between
    assert "seeds 5 to 14, a subset of the" in src
    assert "seeds audited here" in src
    assert "The ten partitions that" in src


def test_gitignore_reconhece_paper_figuras():
    """The five PDFs entered a68d2a2 because no rule covered paper/figuras/,
    not because the whitelist named it. The policy now names it."""
    t = (RAIZ / ".gitignore").read_text()
    assert "!paper/figuras/*.pdf" in t
    assert "Entraram em a68d2a2 por ausencia de" in t


def test_tabela1_bate_com_os_achados():
    """Audit of 2026-10-26: every verdict and count in Table 1 against the
    finding that declares it. This test re-runs the comparison, so a future
    edit to either side that breaks the correspondence fails here."""
    import re
    tab = (RAIZ / "paper" / "00-estrutura.md").read_text()
    i = tab.index("## Tabela 1")
    linhas = [l for l in tab[i:].splitlines() if l.startswith("| H")]
    assert len(linhas) == 20, f"Table 1 has {len(linhas)} hypotheses, not 20"

    # as the findings declare them: F001 (H0, H5*, H6), F002 (H7-H9),
    # F003 (H10-H11), F005 (H12), F006 (H13)
    esperado = {
        "H0": ("suportada", None), "H5a": ("nao suportada", "2/5"),
        "H5b": ("suportada", "5/5"), "H5c": ("suportada", "5/5"),
        "H6": ("suportada", "4/5"), "H7-blocks": ("nao suportada", "1/5"),
        "H7-shuffled": ("suportada", "4/5"), "H8": ("nao suportada", "0/5"),
        "H9-blocks": ("nao suportada", "3/5"),
        "H9-shuffled": ("suportada", "5/5"), "H10a": ("nao suportada", "3/5"),
        "H10b": ("suportada", "5/5"), "H11a": ("suportada", "5/5"),
        "H11b": ("suportada", "4/5"), "H12a": ("suportada", "3/3"),
        "H12b": ("suportada", "3/3"), "H12c": ("suportada", "2/3"),
        "H13a": ("suportada", "5/5"), "H13b": ("nao suportada", "0/5"),
        "H13c": ("suportada", "5/5"),
    }

    def norm(s):
        for a, b in (("ã", "a"), ("á", "a"), ("é", "e"), ("ç", "c"),
                     ("ó", "o"), ("ú", "u"), ("í", "i")):
            s = s.replace(a, b)
        return s.lower()

    vistos = set()
    for l in linhas:
        c = [x.strip() for x in l.strip("|").split("|")]
        h, ver, interp = c[0], norm(c[2]), c[3]
        assert h in esperado, f"unknown hypothesis {h}"
        vistos.add(h)
        v, cnt = esperado[h]
        assert v in ver, f"{h}: verdict {c[2]!r} does not say {v!r}"
        if cnt:
            assert cnt in ver, f"{h}: count {c[2]!r} does not contain {cnt!r}"
        else:
            assert not re.search(r"\d/\d", ver), \
                f"{h}: carries a count the source does not declare"
        # H5c and H13c must not go back to an empty or unscoped interpretation
        if h == "H5c":
            assert "nao conta como confirmac" in norm(interp), \
                "H5c: F001 records that the criterion passed trivially and " \
                "does not count as confirmation; the cell must say so"
        if h == "H13c":
            assert "replicacao independente" in norm(interp) \
                or "nao e replicacao" in norm(interp), \
                "H13c: the partitions share ~80% of their fruits, so the " \
                "cell must not claim replication"
    assert vistos == set(esperado), f"missing: {set(esperado) - vistos}"



def test_tabela1_separa_criterio_de_interpretacao():
    """The verdict column reports the pre-registered rule's outcome and the
    other what the result supports; they can disagree, and H5c is where they
    do. Without that said, 'suportada' next to 'does not count as
    confirmation' reads as a contradiction inside the table."""
    import re
    t = re.sub(r"\s+", " ", (RAIZ / "paper" / "00-estrutura.md").read_text())
    assert "respondem perguntas diferentes e podem discordar" in t
    assert "o que o resultado sustenta" in t
    assert "suportada, 5/5 **(formal)**" in t
    assert "não é contradição da tabela" in t


def test_estrutura_tem_o_plato_nas_dez():
    """The section 8 claims table still showed '2 de 5 negativos', the figure
    from before the F003 extension of 2026-10-25 measured the plateau across
    all ten partitions."""
    import re
    t = (RAIZ / "paper" / "00-estrutura.md").read_text()
    assert "sinal inconsistente, 2 de 5 negativos" not in t
    assert "4 de 10 médias de partição negativas" in re.sub(r"\s+", " ", t)



def test_s9_prescricoes_nao_generalizam_alem_dos_dados():
    """Review of 2026-10-26, problems A and D. Prescription 1 claimed a level
    set larger than q means the metric registers nothing new, which ignores
    that the gate may separate those bands by learned differences.
    Prescription 4 was a universal prohibition with an unscoped no-cost
    claim."""
    import re
    t = re.sub(r"\s+", " ",
               (RAIZ / "paper" / "05-rascunho-s9-s10-s11.md").read_text())
    assert "cannot register any distinction the prior does not already make" not in t
    assert "Check all three conditions together, not the geometry alone" in t
    assert "makes the artefact *possible*" in t
    assert "may separate those bands by differences it genuinely learned" in t
    # prescription 4 scoped to the use, with the no-cost claim tied to the runs
    assert "Do not put the prior in the initialisation" not in t
    assert "a methodological preference conditional on the use, not a general" in t
    assert "is as general as those runs" in t


def test_s11_nao_reivindica_exclusividade_do_sintetico():
    """Problem G: controlled mixtures, reference standards and experimental
    systems with a known composition also measure recovery."""
    import re
    t = re.sub(r"\s+", " ",
               (RAIZ / "paper" / "05-rascunho-s9-s10-s11.md").read_text())
    assert "only design that measures recovery" not in t
    assert "controlled mixtures, reference standards" in t
    assert "not because it is the only route" in t



def test_s1_nao_nega_limite_populacional_a_sobreposicao():
    """Problem C of the 2026-10-26 review: saying seed overlap converges to no
    population quantity is stronger than needed and may be false under
    stability assumptions. The argument only needs that convergence does not
    establish recovery of a true support."""
    import re
    t = re.sub(r"\s+", " ",
               (RAIZ / "paper" / "03-rascunho-s1-s2-s3.md").read_text())
    assert "converges to no population quantity" not in t
    assert "We do not claim that seed overlap has no population limit" in t
    assert "does not establish that the selection recovers a true support" in t


def test_s4_declara_a_dependencia_do_plato_na_propria_secao():
    """Problem F: 'unaffected by the property described here' in 4.4 invites a
    wider reading than 9.3 supports, and the reader should not have to wait
    for the discussion."""
    import re
    t = re.sub(r"\s+", " ",
               (RAIZ / "paper" / "01-rascunho-resumo-e-s4.md").read_text())
    assert "unaffected by the property described here" not in t
    assert "Immunity to that artefact is not independence from the prior" in t
    assert "0.018 under Pearson and 0.051 under Spearman" in t


def test_correcao_em_provas_separa_imunidade_de_independencia():
    """Author's two precisions of 2026-10-26: the insertion may not call the
    displacement control 'unaffected', because immunity to the tie-breaking
    artefact is not independence from the plateau; and the Raman clause must
    not imply interpretive validity. The optional abstract clause is dropped."""
    import re
    t = re.sub(r"\s+", " ", re.sub(r"^>\s?", "",
               (RAIZ / "paper" / "correcao-em-provas.md").read_text(),
               flags=re.M))
    assert "their order, is unaffected." not in t
    assert "no tie-breaking rule enters it" in t
    assert "whether that correlation is also independent of the plateau is a" in t
    assert "the mechanism described here does not arise" in t
    assert "A oração no resumo foi retirada" in t
    assert "in NIR this overlap is evaluated within the prior" not in t



def test_f002_registra_a_ambiguidade_do_plato():
    """The sentence 'bit-identical in every seed' admits two readings and only
    one was measured: check_gates_r2 counts distinct values per row and never
    compares rows. The artefact needs only the within-run reading."""
    import re
    f = re.sub(r"\s+", " ", (RAIZ / "findings"
               / "F002-o-que-as-metricas-interpretativas-medem.md").read_text())
    assert "uma frase ambígua sobre o platô" in f
    assert "nunca compara linhas entre si" in f
    assert "O artefato precisa apenas da primeira leitura" in f
    assert "nenhum script do programa media a segunda" in f


def test_script_09_mede_as_tres_propriedades():
    """Within-run spread, across-run spread of the level, and max |d|. The
    second was measured by nothing in this programme until 2026-10-26."""
    src = (RAIZ / "scripts" / "09_controle_deslocamento.py").read_text()
    assert "P1 value-equal in" in src
    assert "P2 across-run amplitude of the common" in src
    assert "nothing in this programme measured it until now" in src



def test_09_nao_reduz_p2_a_media():
    """Author's requirement of 2026-10-26: P2 is the amplitude over the COMMON
    plateau value per run, computed only where P1 holds. A mean would hide
    within-run variation precisely when the quantity is meaningless, and a 0.0
    from subtraction is not by itself evidence of bit-identical storage."""
    src = (RAIZ / "scripts" / "09_controle_deslocamento.py").read_text()
    assert "g[plato].mean()" not in src          # the retired reduction
    assert "P2 NOT COMPUTED" in src
    assert "no single value to compare" in src
    assert "value equality on the stored doubles" in src
    assert "v.view(np.int64)" in src             # the bit-level comparison
    assert "a mean would hide within-run variation" in src


def test_s9_reporta_p2_medido_e_nao_um_limite():
    """The bound was superseded by the measurement on 2026-10-26: P1 holds
    10/10 by value and by bit in all seven sizes, and P2 is non-zero in all
    seven, from 2.4e-7 to 4.1e-6, measured per size and never pooled."""
    import re
    t = re.sub(r"\s+", " ",
               (RAIZ / "paper" / "05-rascunho-s9-s10-s11.md").read_text())
    assert "identical both by value and by bit pattern in 10 of 10 runs" in t
    assert "Across runs, the common plateau value is not the same" in t
    assert "per training size and never pooled across them" in t
    assert "2.4 × 10⁻⁷ at n = 30 to 4.1 × 10⁻⁶ at n = 1158" in t
    # the mechanism rests on P1 alone, and the text must say so
    assert "the only property the artefact needs" in t
    assert "a tie inside a run does not require two runs to tie with each" in t
    # P2 vs n is exploratory, not causal: seven conditions (2026-10-26)
    assert "exploratory association and not as evidence" in t
    assert "seven conditions cannot support that" in t
    # resolution read at the OBSERVED values, not at 1.0. The plateau sits in
    # [0.5, 1), where the single-precision spacing is 2**-24; 2**-23 applies
    # above 1.0. An earlier draft used 2**-23 and halved every step count.
    assert "binade [0.5, 1)" in t
    assert "2⁻²⁴ ≈ 5.96 × 10⁻⁸" in t
    assert "4, 6, 4, 6, 20, 34 and 68 steps" in t
    assert "not a universal detection floor" in t
    assert "2⁻²³" in t and "applies immediately" in t
    # representability is not provenance
    assert "a fact about where they lie and not about how they were produced" in t
    assert "do not claim the provenance" in t



def test_07_culpa_a_raiz_certa_pelo_modulo_que_falta():
    """Author's run, 2026-10-27: the handler for the pgsg2 import block blamed
    --pgsg2-root for a missing `pgsg_1`, because pgsg2.models.adapter imports
    pgsg_1 itself. It answered the failure by telling the author to pass the
    path already passed. Which root is at fault is decided by the missing
    module, not by which block raised."""
    src = (RAIZ / "scripts" / "07_raman_lambda1.py").read_text()
    assert "def falta_pgsg1(" in src
    assert 'if nome.split(".")[0] == "pgsg_1":' in src
    assert "not by\n        # which import block raised" in src
    # and both messages now report whether the directory holds the package,
    # so the author does not have to guess which path is wrong
    assert "has src/pgsg_1:" in src and "has pgsg2:" in src
    assert "exists: {pgsg1_root.is_dir()}" in src


def test_13_nao_esconde_um_sd_nao_nulo_atras_do_arredondamento():
    """Author's Raman run, 2026-10-27: the table printed sd as 0.0000 in all
    three partitions while returning z = -1.0 sd for two of them, which only a
    non-zero sd can produce. Exactly zero and merely small are different
    claims and must not render identically."""
    src = (RAIZ / "scripts" / "13_dependencia_do_sort.py").read_text()
    assert "{sd:>14.3e}" in src          # sd in full precision
    assert "{ji - jr:>13.3e}" in src     # and the difference beside it
    assert "a display hiding" in src
    assert "EXACTLY zero and merely small are different" in src
    # a spread at floating-point noise is no spread, with the threshold set
    # by np.spacing at the observed magnitude and not by a round number
    assert "8.0 * float(np.spacing(abs(media)))" in src
    assert "3.0 ulp of a double" in src
    assert "divides noise by noise" in src
    # the tolerance is operational, documented as such, not statistical
    assert "OPERATIONAL NUMERICAL TOLERANCE" in src
    assert "carries no significance" in src
    # metric invariance and set invariance are printed as separate claims
    assert "TWO CLAIMS, KEPT APART" in src
    assert "can return the same Jaccard" in src
    assert "does not persist" in src


def test_05_nao_afirma_que_o_padrao_desempata_por_indice():
    """Mandatory correction, author 2026-10-27 (F008): the script used to print
    that argsort breaks ties by band index. That is kind="stable"; the default
    is an introsort and is not stable. A claim the programme made about itself,
    and it was wrong."""
    src = (RAIZ / "scripts" / "05_diagnostico_jaccard.py").read_text()
    assert "argsort then breaks ties by band index" not in src
    assert "CORRECTED 2026-10-27" in src
    assert "is an introsort and is NOT stable" in src
    assert "partly a property" in src and "of the build" in src
    assert "13_dependencia_do_sort.py" in src
    # and the untied branch now says why it is also sort-independent
    assert "no\n        tie rule is involved" in src or (
        "and no" in src and "tie rule is involved" in src)


def test_13_mede_a_dependencia_do_sort_sem_inferir_ambiente():
    """F008: every top-q selection uses a bare np.argsort, whose default is not
    a stable sort, so the deterministic overlap measures the tie rule. The
    script must demonstrate the instability rather than quote the docs, print
    the numpy version, and compare against the randomised rule."""
    src = (RAIZ / "scripts" / "13_dependencia_do_sort.py").read_text()
    assert 'KINDS = ("quicksort", "heapsort", "mergesort", "stable")' in src
    assert 'np.argsort(t, kind="stable")' in src        # stability, measured
    assert "np.__version__" in src                      # environment, printed
    assert "esperanca_exata" in src                 # against E[J], not q/(2L-q)
    assert "jaccard_sorteado" in src                    # and the robust rule
    # the script must not call the Jaccard empty (author, 2026-10-27): it
    # measures agreement of the sets a stated procedure produces, and the
    # script quantifies how atypical that procedure is instead
    assert "as empty as a quantity can be" not in src
    assert "does not identify the spectral" in src
    assert "z = (J_kind - mean_random) / sd_random" in src
    assert "def z_na_populacao" in src
    # sd = 0 is the most robust case, not an infinity
    assert "would manufacture an" in src
    # the five provenance items the author required
    assert "def sha256" in src
    assert "Aggregation convention, stated rather than left to be inferred" in src
    assert "not be presumed a sufficient cause" in src
    # the Raman arm, from the recorded cells, without retraining
    assert "def raman_de_cells" in src
    assert "j_random_sd already\n    bounds what ANY tie rule can do" in src
    # the three procedures, not a new official one
    assert "Three procedures, and the manuscript needs all three" in src


def test_f008_separa_o_medido_do_inferido():
    """The finding must keep three things apart: what was measured here, what
    the manuscript reports from another environment, and the author's numpy
    version, which was NOT measured and must not be inferred from a Jaccard."""
    import re
    t = re.sub(r"\s+", " ", (RAIZ / "findings"
               / "F008-a-sobreposicao-deterministica-depende-do-sort.md"
               ).read_text())
    assert "numpy 2.5.3" in t                   # o ambiente desta medicao
    assert "0,9452 a 0,9867" in t               # o do autor, conforme o texto
    assert "não foi medida" in t and "inferi-la de um valor de Jaccard" in t
    # a Figura 3 nao esta obsoleta: a explicacao e o ambiente
    assert "não está obsoleta" in t
    # o que NAO e afetado, incluindo o motivo certo no Raman
    assert "Não afeta P1, P2 nem P3" in t
    assert "robusto **porque** não satisfaz C1" in t
    assert ("A quantidade em que o manuscrito se apoia reproduz entre "
            "ambientes") in t
    # as cinco afirmacoes do texto que precisam de decisao
    assert "precisam de decisão do autor" in t
    assert "argsort then breaks ties by band index" in t
    # --- extensao de 2026-10-27: o ambiente do autor, medido
    assert "numpy 2.4.6, Python 3.14.6" in t
    assert "dígito por dígito" in t
    # as tres correcoes minhas, preservando o texto original
    assert "O texto acima fica como escrito" in t
    assert "eu chamei o Jaccard de quantidade vazia, e ele não é" in t
    assert "+40,7 desvios" in t
    assert ("J = 1 é consequência da regra de desempate, não evidência "
            "adicional") in t
    # a causa nao e presumida pela versao
    assert "não demonstra que esta diferença específica" in t
    assert "SHA-256 dos sete" in t
    # o Raman: caminho sem retreino, e ainda nao medido
    assert "não exige retreino" in t
    # medido em 2026-10-27: a explicacao plausivel passou a resultado, e o
    # desvio e ruido de ponto flutuante -- 3,0 ulp -- e nao dispersao
    assert "ruído de ponto flutuante, não dispersão" in t
    assert "3,0 ulp" in t
    assert "nenhuma ordem de empate moveu o valor do Jaccard" in t
    # as duas afirmacoes ficam separadas: metrica sim, conjuntos nao
    assert "Duas afirmações, e só uma está demonstrada" in t
    assert "Igualdade de valor não é igualdade de conjunto" in t
    assert "o `07_raman_lambda1.py` não persiste" in t
    # e o limiar e tolerancia operacional, nao estatistica
    assert "tolerância numérica operacional" in t
    assert "não carrega nível de significância" in t
    # a raiz do pgsg_1, localizada e nao presumida
    assert "Dropbox/pgsg/pgsg_1" in t
    assert "cópias `vendor/` do pacote" in t
    # as cinco figuras reproduzem na maquina do autor: a divergencia do
    # painel (b) era entre ambientes, nao do arquivo comitado
    assert "5 of 5 figures regenerated and matched" in t
    assert "nunca divergiu na máquina que o produziu" in t
    assert "idêntica, pixel a pixel" in t
    assert "reproduzível no ambiente que a gerou" in t
    assert "não é portável" in t
    assert "Não há nada a substituir" in t
    # e o que a verificacao NAO estabelece
    assert "nem que outra pessoa as obtenha" in t
    assert "é um resultado a qualificar" in t
    assert "era ruído dividido por ruído" in t
    assert "treze ordens de grandeza acima" in t
    assert "a robustez é medida, e a falha de C1 é a explicação dela" in t
    # o defeito de exibicao que a propria saida revelou
    assert "só um desvio **não nulo** produz" in t
    # e a raiz culpada pelo modulo que falta
    assert "a raiz culpada é decidida pelo **módulo que falta**" in t
    assert "continuam **não verificadas**" in t
    assert "não existe** nessa" in t
    # figuras e as duas etapas
    assert "não é substituído" in t
    assert "**Não iniciada**" in t


def test_12_nao_chama_verificada_uma_figura_sem_entradas():
    """Reproducibility of a procedure is not conformity of a submitted file.
    A figure whose inputs are absent is NOT VERIFIABLE, never verified and
    never wrong, and the script must not write into paper/figuras."""
    src = (RAIZ / "scripts" / "12_verifica_figuras.py").read_text()
    assert "NOT VERIFIABLE" in src
    assert "is NOT shown to be wrong" in src
    assert "`paper/figuras` is never written to by this script" in src
    # byte comparison is wrong for matplotlib PDFs, and the reason is stated
    assert "matplotlib stamps a creation date" in src
    # a mismatch is reported, not diagnosed
    assert "does not diagnose" in src
    assert "renderer" in src
    # bugs found by the author's run of 2026-10-27:
    # (a) pdftoppm needs its output directory to exist
    assert 'destino.mkdir(parents=True, exist_ok=True)' in src
    # (b) a failed regeneration must stop the script, not be compared anyway
    assert "is worse than no " in src
    assert r"because\n  it looks like one" in src
    # (c) a missing renderer is a verdict per figure, not a traceback
    assert "class SemRasterizador" in src
    assert "except SemRasterizador as e:" in src
    # (d) --pgsg2-root is the src dir, as 10_figuras.py's own error says
    assert "pgsg2-nir-raman-gating/src" in src
    assert "CONTAINS the `pgsg2` package" in src
    # (e) a provenance field must not degrade to "?": pypdfium2 5.x has no
    # __version__, so the version comes from the distribution metadata
    assert 'version("pypdfium2")' in src
    assert "a provenance field reporting that it does not" in src
    # (f) and the rasteriser is a declared optional extra, so the next person
    # is not left to discover the requirement from a NOT VERIFIABLE line
    assert "pip install -e '.[verify]'" in src
    tom = (RAIZ / "pyproject.toml").read_text()
    assert "[project.optional-dependencies]" in tom
    assert 'verify = ["pypdfium2"]' in tom
    assert "cannot be declared here" in tom


def test_07_separa_exigencia_confirmada_de_nao_verificada():
    """The submission matter must keep the two categories apart: what was read
    at the official source with its own date, and what is plausible but
    unverified for THIS journal. A rule applied by analogy with another
    Elsevier title is an assumption, and this programme checks assumptions."""
    import re
    t = re.sub(r"\s+", " ",
               (RAIZ / "paper" / "07-declaracoes-submissao.md").read_text())
    # a declaracao de IA: cabecalho literal e data da propria fonte
    assert ("Declaration of generative AI and AI-assisted technologies in the "
            "manuscript preparation process") in t
    assert "Policy updated June 2026" in t
    assert "Basic checks of grammar, spelling and punctuation" in t
    assert "reproducible manner in the Methods section" in t
    # o que NAO foi verificado fica rotulado, e o inventario nao e veredito
    assert "NÃO VERIFICADO" in t
    assert "inventário, não julgamento de conformidade" in t
    assert "Nada entra como conforme por analogia" in t
    # a instrucao de 1992 nao e tratada como regra vigente
    assert "é de 1992 e não entra aqui" in t
    # o PGSG nao e IA generativa auxiliando a redacao
    assert "é o objeto da pesquisa" in t
    # a versao do modelo nao e afirmada como identificador unico, nem por
    # familia: nem uma coisa nem outra esta sustentada pelos registros
    assert "pode diferir do configurado" in t
    assert "também não está sustentada pelos registros" in t
    assert "nomear fornecedor e ferramenta" in t
    # revisao assistida nao e validacao independente
    assert ("constitute independent scientific validation of the "
            "analyses") in t
    assert "Assist in the critical review" in t and "não é validação" in t
    # mais de uma ferramenta participou, e o que falta esta marcado como falta
    assert "NAME EVERY OTHER TOOL USED" in t
    assert "a declaração está errada enquanto o colchete estiver lá" in t
    # reprodutibilidade de procedimento nao e conformidade do arquivo
    assert ("documenta a origem das figuras e não demonstra a conformidade "
            "dos arquivos submetidos") in t
    assert "nenhuma das cinco figuras deve ser descrita como verificada" in t
    # as duas contagens do resumo nao sao um menu
    assert "não são um menu" in t
    assert "decidir a regra depois de ver o resultado" in t
    assert "reduzir com margem" in t
    # disponibilidade so se declara depois de conferir os fatos
    assert "nas condições\ndescritas" in (RAIZ / "paper"
           / "07-declaracoes-submissao.md").read_text()
    assert "está nomeado como indisponível" in t


def test_09_garante_dtype_antes_de_comparar_bits():
    """view(np.int64) presupposes the array really is float64, which the
    author asked to be guaranteed rather than assumed."""
    src = (RAIZ / "scripts" / "09_controle_deslocamento.py").read_text()
    assert "if g_.dtype != np.float64:" in src
    assert "would compare the wrong width" in src
    # and the resolution question is checked, not asserted
    assert "exactly representable in" in src


def test_09_usa_o_espacamento_dos_valores_observados():
    """The plateau sits in [0.5, 1), where float32 spacing is 2**-24. An
    earlier version used 2**-23 -- the spacing ABOVE 1.0, since 1.0 is a power
    of two on a boundary -- and reported half the number of steps. The script
    must read the spacing at the observed values, and must not present exact
    representability as proof of single-precision provenance."""
    src = (RAIZ / "scripts" / "09_controle_deslocamento.py").read_text()
    assert "2.0) ** -23" not in src and "2.0)**-23" not in src
    assert "the binade [0.5, 1.0), where the single-precision spacing is" in src
    assert "The spacing 2**-23 applies ABOVE 1.0" in src
    assert "does NOT show they were computed in single precision" in src
    assert "Confirming" in src and "provenance needs the dtypes" in src
    # spacing is local, so it is read at BOTH ends of the observed range and
    # the step count is withheld when the values straddle a binade boundary.
    # Found by a fixture whose plateau crossed 1.0: the old code read the
    # spacing at the max and applied it to the whole range.
    assert "Spacing is a LOCAL property" in src
    assert "np.spacing(np.float32(lo))" in src
    assert "np.spacing(np.float32(hi))" in src
    assert "straddle a binade boundary" in src
    assert "step count withheld: no single resolution" in src
    # an amplitude in steps is not a count of representable values, and the
    # two part company exactly where the refusal applies (author, 2026-10-26)
    assert "the NUMBER of" in src and "representable values between two floats" in src
    assert "equals A/ulp only" in src
    assert "nor a count of the" in src


def test_f007_corrige_o_espacamento_e_separa_proveniencia():
    """The two corrections the author required on 2026-10-26, recorded in the
    finding with the original error named rather than quietly replaced."""
    import re
    t = re.sub(r"\s+", " ", (RAIZ / "findings"
               / "F007-o-controle-de-deslocamento-e-o-plato.md").read_text())
    # erro 1: o espacamento
    assert "2⁻²⁴ = 5,960464×10⁻⁸" in t
    assert "4, 6, 4, 6, 20, 34 e 68" in t
    assert "o dobro do que eu havia reportado" in t
    assert "não** é piso universal de detecção" in t
    # erro 2: representabilidade nao e proveniencia
    assert "representabilidade não é proveniência" in t
    assert "pertencem à grade do `float32`" in t
    assert "proveniência confirmada" in t
    # P2 vs n exploratoria, P2 vs max|d| nao e evidencia independente
    assert "associação exploratória**" in t
    assert "não uso a correlação entre P2 e max |d| como evidência" in t
    assert "compartilham dependência matemática" in t
