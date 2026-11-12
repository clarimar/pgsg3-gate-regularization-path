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
import re

RAIZ = Path(__file__).resolve().parents[1]

LIMITE_RESUMO = 250  # Chemolab, guide for authors: "does not exceed 250 words"



_TEX_GERADO: dict[str, str] = {}


def _tex_gerado(bib: bool = False) -> str:
    """Builds the .tex from the manuscript and returns it.

    Never reads paper/MANUSCRITO.tex from disk. That file is GENERATED and,
    since 2026-11-09, not tracked, so on any tree where someone built it
    earlier it can be stale -- and a test that reads it is asserting on an
    artefact nobody rebuilt. That is the defect this programme has now hit six
    times. On 2026-11-12 it hit the author's own machine: three tests failed
    there against a .tex built before the AI declaration existed, while the
    same three passed in the container that had just rebuilt it. A test that
    passes or fails according to what happens to be on disk measures the disk.
    """
    chave = "bib" if bib else "lista"
    if chave not in _TEX_GERADO:
        import subprocess
        import sys
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            saida = Path(d) / "M.tex"
            cmd = [sys.executable, str(RAIZ / "scripts" / "19_tex.py"),
                   "--src", str(RAIZ / "paper" / "MANUSCRITO.md"),
                   "--out", str(saida)]
            if bib:
                cmd.append("--bib")
            r = subprocess.run(cmd, capture_output=True, text=True, cwd=RAIZ)
            assert r.returncode == 0, (
                "19_tex.py falhou ao gerar o .tex para o teste:\n"
                + r.stdout + r.stderr)
            _TEX_GERADO[chave] = saida.read_text()
    return _TEX_GERADO[chave]


def _num_ref(trecho: str) -> str:
    """O número da referência cuja entrada contém `trecho`.

    Os testes citavam números literais e quebraram em toda renumeração --
    três vezes, e a numeração é por ordem de primeira aparição, de modo que
    inserir uma citação cedo desloca tudo. O número passa a ser lido da
    lista, e o que o teste fixa é a entrada, que é o que importa.
    """
    import re as _re
    texto = (RAIZ / "paper" / "12-referencias.md").read_text()
    m = _re.search(r"^## References[ \t]*$", texto, _re.M)
    corpo = texto[m.end():]
    f = _re.search(r"^## ", corpo, _re.M)
    if f:
        corpo = corpo[:f.start()]
    achados = [n for n, e in _re.findall(r"^\[(\d+)\]\s+(.+)$", corpo, _re.M)
               if trecho in e]
    assert len(achados) == 1, f"{trecho!r}: {len(achados)} entradas"
    return achados[0]


def _resumo_prosa(nome: str = "02-resumo-C.md") -> str:
    """The abstract alone, with its commented decision history stripped.

    Added 2026-10-28. The history above the '---' separator now QUOTES English
    fragments of the abstract, including one the author decided to REMOVE. An
    assertion run over the whole file could therefore be satisfied by the note
    that records the removal, which is the opposite of a guard. Every claim
    about the abstract is checked against the prose that will be submitted.
    """
    import re
    bruto = (RAIZ / "paper" / nome).read_text()
    partes = bruto.split("\n---\n", 1)
    assert len(partes) == 2, f"{nome} lost its '---' separator"
    return re.sub(r"\s+", " ", partes[1]).strip()


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


@pytest.mark.semantico
def test_etapa_b_item6_consistencia_tabela1_e_achados():
    """Author's closing criterion 4: Table 1 and F001-F007 must stay
    consistent with the new analyses. Findings and ADRs are never edited in
    place; corrections go in dated notes that preserve the original text."""
    import re
    est = re.sub(r"\s+", " ", (RAIZ / "paper" / "00-estrutura.md").read_text())
    # Tabela 1 e o texto da estrutura passam a citar o procedimento
    assert "**1,0000** por índice" in est
    assert "pela ordem do sort em numpy 2.4.6" in est
    assert "F004, F008" in est
    assert "+0,9286 nos três procedimentos**" in est
    assert "sem associação a reportar" in est
    assert "A decisão 6 não muda, mas o número passa a ser citado com o " \
           "procedimento" in est
    # F004 ganha nota datada, com o texto original preservado
    f004 = re.sub(r"\s+", " ", (RAIZ / "findings"
                  / "F004-estabilidade-interpretativa-e-funcao-dos-dados.md"
                  ).read_text())
    assert "Nota de 2026-10-27" in f004
    assert "O texto acima fica como está" in f004
    assert "**Nenhum veredito muda.**" in f004
    assert "idêntico nos três procedimentos" in f004
    assert "pressupõem sete observações independentes" in f004
    assert "ficam aqui no registro original" in f004
    # a ADR idem
    adr = re.sub(r"\s+", " ", (RAIZ / "docs" / "adr"
                 / "ADR-0001-escopo-e-datasets.md").read_text())
    assert "Nota de 2026-10-27" in adr
    assert "A decisão não muda" in adr
    assert "A citação acima fica como está" in adr
    # 9.3 compara por procedimento e sem valor-p
    s9 = re.sub(r"\s+", " ", (RAIZ / "paper"
                / "05-rascunho-s9-s10-s11.md").read_text())
    assert "has no comparable figure to offer" in s9
    assert "We give these rank correlations without p-values" in s9
    assert "the other has no response to report that is a property of the " \
           "gates" in s9


@pytest.mark.semantico
def test_etapa_b_431_reprodutibilidade_para_o_leitor():
    """Author's item 5: incorporate the non-portability into the discussion.
    It concerns the published record, so it must be stated as what a reader
    can and cannot reproduce, with the three consequences drawn."""
    import re
    t = re.sub(r"\s+", " ",
               (RAIZ / "paper" / "01-rascunho-resumo-e-s4.md").read_text())
    assert "4.3 What a reader of the earlier work can and cannot reproduce" in t
    # promovida a secao propria em 2026-10-28: a 4.3.1 deixou de existir
    assert "4.3.1" not in t
    assert "may not obtain the published figure" in t
    assert "Nothing need have gone wrong" in t
    assert "The rule is part of the estimator, not an implementation detail" in t
    assert "need not be evidence of error in either" in t
    # ... sob a condicao logica que o autor exigiu em 2026-10-27, sem a qual
    # a frase vira desculpa geral para irreprodutibilidade
    assert "or the point becomes a general excuse" in t
    assert "It does not hold when both claim the same procedure" in t
    assert "still demands investigation" in t
    assert "and, if those agree, to keep looking" in t
    # e nenhuma extrapolacao para a literatura
    assert "We make no claim about how widely this affects" in t
    assert "We have measured one prior, in one architecture, in two " \
           "environments" in t


@pytest.mark.semantico
def test_etapa_b_reporta_por_procedimento_e_nao_substitui():
    """Stage B, author 2026-10-27: the contribution is the comparison between
    procedures, not the replacement of the historical value by J = 1 or by
    J = 0.744. Every affected number must name its procedure, the historical
    row must survive with its environment stated, and the conclusion must be
    that the Jaccard is a property of the whole selection procedure rather
    than that the stability is simply artificial."""
    import re
    t = re.sub(r"\s+", " ",
               (RAIZ / "paper" / "01-rascunho-resumo-e-s4.md").read_text())
    # as quatro linhas, cada uma com o seu procedimento
    assert "ties broken by band index" in t and "1.0000** at every size" in t
    assert "numpy 2.4.6 / Python 3.14.6 | 0.9452 to 0.9867" in t
    assert "numpy 2.5.3 / Python 3.13.16 | 0.7443 to 0.7659" in t
    assert "ties resolved at random, 200 draws | 0.7442 at every size" in t
    # o historico e preservado, nao substituido
    assert "preserved here as the reproduction of a specific procedure" in t
    assert "not as a result another reader will obtain" in t
    # a causa nao e atribuida a versao
    assert "We do not claim the library version as the cause" in t
    # a formulacao do autor, mais precisa que "estabilidade artificial"
    assert ("the Jaccard is a property of the complete selection procedure, "
            "tie rule included") in t
    assert "not an identifiable property of the gates" in t
    assert "stronger and more precise statement than calling the stability "\
           "artificial" in t
    # e o limite de escopo: a metrica nao e invalida em toda aplicacao
    assert "It is also a bounded one" in t
    assert "does not make the top-q overlap an invalid measure in general" in t
    assert "the figure is a measurement of the gates" in t
    assert "the deterministic value taken on its own does not identify " \
           "spectral stability" in t
    # a mudanca de coeficiente nao e mudanca na relacao -- texto que foi
    # para a secao 5 na promocao de 2026-10-28
    s5 = re.sub(r"\s+", " ", (RAIZ / "paper" / "08-rascunho-s5.md").read_text())
    assert "is not a change in the relation between spectral stability and " \
           "sample size" in s5
    assert "No such relation changed; the data are the same bytes" in s5
    assert "would repeat, one level up, the error the section is about" in s5
    # 4.2: a leitura "similaridade fora do plato" era especifica do build
    assert "we drew that conclusion in an earlier draft" in t
    assert "A quantity that moves from near-unity to chance while the data "\
           "are held fixed is not measuring the data" in t


@pytest.mark.semantico
def test_etapa_b_43_sem_valor_p_sem_unidade_justificada():
    """Author 2026-10-27: do not keep a coefficient and p-value from an
    implementation whose rule was unspecified, and do not treat nested
    subsamples as independent draws. The association stays exploratory.

    Promoted to a section of its own on 2026-10-28, so this reads Section 5's
    file; the tie-breaking consequences stayed in Section 4."""
    import re
    t = re.sub(r"\s+", " ",
               (RAIZ / "paper" / "08-rascunho-s5.md").read_text())
    assert "## 5. Results — the response to sample size" in t
    # a associacao que sobrevive e identica entre procedimentos
    assert ("+0.9286 under index-order tie-breaking, under the sort's own tie "
            "order, and under randomisation alike") in t
    # e a que nao sobrevive nao tem associacao a reportar
    assert "there is no association to report" in t
    assert "a rank correlation is undefined on a constant" in t
    assert "which is a result and not a missing value" in t
    # o historico -0.3214 fica identificado, nao apagado
    assert "−0.3214 in the environment of the published analysis" in t
    assert "is retained as that environment's figure" in t
    # os valores-p caem, com o motivo
    assert "Both associations are **exploratory**" in t
    assert "assumed a replication unit the design does not supply" in t
    assert "drop the p-values rather than re-deriving a justification" in t


@pytest.mark.semantico
def test_etapa_b_secao6_invariancia_aritmetica():
    """Author's item 3: check the sensitivity of 0.9763-1.0000 BEFORE touching
    the interpretation. The check is the tie on the boundary, which makes the
    invariance arithmetic rather than a judgement."""
    import re
    t = re.sub(r"\s+", " ",
               (RAIZ / "paper" / "04-rascunho-s6-s7-s8.md").read_text())
    assert "so we checked it rather than inferred it" in t
    assert "No tie group sits on the selection boundary at rank q" in t
    assert "the same figure to every digit" in t
    assert "all give 0.9867" in t
    assert "invariance is arithmetic rather than a judgement" in t
    assert "need no qualification by sort kind" in t
    # verificavel, nao afirmado: o veredicto de uma linha e a condicao
    # suficiente sem ser mais forte do que o necessario (autor, 2026-10-28)
    assert "ends with a single verdict line" in t
    assert "or which was not measured at all" in t
    assert "absence of ties across the whole spectrum is not required" in t
    assert "the rule reordering equal values alone" in t


@pytest.mark.semantico
def test_secao12_conclusoes_responde_as_tres_perguntas():
    """Created by the integral audit of 2026-10-28: the paper had no
    conclusions section. It must answer what was demonstrated, what was
    observed, and what was not established -- and must integrate the
    pre-stage-B contribution so the paper does not read as a study about
    sorting algorithms."""
    import re
    t = re.sub(r"\s+", " ",
               (RAIZ / "paper" / "09-rascunho-s12.md").read_text())
    assert "## 12. Conclusions" in t
    # os dois papeis do prior, a contribuicao anterior a Etapa B
    assert "separating the roles of prior-based initialisation and " \
           "regularisation" in t
    # o mecanismo demonstrado
    assert "the selected subset depends on the tie-breaking rule" in t
    assert ("Jaccard overlap is a property of the complete selection "
            "procedure") in t
    # o observado, com os gates identicos
    assert "identical stored gates produced substantially different overlap" in t
    # o que NAO foi estabelecido
    assert "do not establish how frequently the mechanism occurs" in t
    assert "How common they are elsewhere is a question we leave open" in t
    # e a exigencia metodologica que resulta
    assert "identify the selection procedure and verify whether ties " \
           "intersect the" in t
    assert "neither requires retraining" in t


@pytest.mark.semantico
def test_referencia_e_separate_em_todo_o_manuscrito():
    """Author 2026-10-28, after the integral reading: "external reference"
    invites the reader to take it as statistically independent, when it is a
    second estimate built on the same training partition. The terminology is
    uniform -- "separate statistical reference" -- and the dependence is
    explained in Sections 8.3 and 12 rather than repeated at each mention.

    Three concepts the paper must not conflate: operational separation (gate
    and reference are different estimators), statistical dependence (both use
    the same training partition), and independent validation (not
    demonstrated here). The results support the first two only."""
    import re
    fontes = ["02-resumo-C.md", "03-rascunho-s1-s2-s3.md",
              "04-rascunho-s6-s7-s8.md", "05-rascunho-s9-s10-s11.md",
              "06-legendas-figuras.md", "08-rascunho-s5.md",
              "09-rascunho-s12.md", "01-rascunho-resumo-e-s4.md"]
    for nome in fontes:
        bruto = (RAIZ / "paper" / nome).read_text()
        # a nota de rascunho da secao 12 registra a troca e cita o termo
        # antigo; so o texto ingles do manuscrito e verificado
        if nome == "09-rascunho-s12.md":
            bruto = bruto.split("## 12. Conclusions", 1)[1]
        assert "external reference" not in bruto, nome
        assert "external, data-derived" not in bruto, nome
    # e o termo escolhido esta onde as quatro ocorrencias estavam
    i = re.sub(r"\s+", " ",
               (RAIZ / "paper" / "03-rascunho-s1-s2-s3.md").read_text())
    assert "a separate, data-derived statistical reference" in i
    s6 = re.sub(r"\s+", " ",
                (RAIZ / "paper" / "04-rascunho-s6-s7-s8.md").read_text())
    assert "agreement with the separate statistical reference" in s6
    assert "with the separate statistical reference across the bands" in s6
    assert "between the gate and the separate statistical reference" in s6
    leg = re.sub(r"\s+", " ",
                 (RAIZ / "paper" / "06-legendas-figuras.md").read_text())
    assert "the gate and the separate statistical" in leg
    # a dependencia continua explicada onde deve, sem repeticao
    assert "a second statistical estimate from the same data" in s6
    assert "not an independent determination" in s6


@pytest.mark.semantico
def test_secao12_nao_le_como_o_modelo_nao_aprende():
    """The author's own caveat of 2026-10-28: the sentence limiting the
    interpretation of stable selections must be confronted with the controls
    in F001-F003. It holds for the SELECTION under prior-initialisation; it
    does not hold as a claim about the gate, which F003 and Section 8.2 show
    aligns with a data-derived reference at the prior's floor. Without the
    floor clause the conclusion reads as 'the model does not learn'."""
    import re
    t = re.sub(r"\s+", " ",
               (RAIZ / "paper" / "09-rascunho-s12.md").read_text())
    assert "It does not limit the interpretation of the gate as a whole" in t
    # harmonizado com o resumo em 2026-10-28: "external" sugeria
    # independencia estatistica que a referencia nao tem
    assert "aligns positively with a separate statistical reference" in t
    assert "an external, data-derived reference" not in t
    assert "separate from the gate's own training but not independent of " \
           "the data" in t
    assert "the same under a prior whose content has been destroyed" in t
    assert "the top-decile metric never reads" in t
    # e a imprecisao de "strongly constrained" foi corrigida, nao embutida
    assert "not merely strong but inert in practice" in t
    assert "gradient of order 10⁻⁶" in t
    # mas sem afirmar imobilidade matematica: o autor recusou "do not move"
    # em 2026-10-28, e o F007 mediu max|d| entre 1,2e-6 e 6,7e-6 no plato
    assert "and\ndo not move" not in (RAIZ / "paper"
                                      / "09-rascunho-s12.md").read_text()
    # "far from constant" saiu por exigencia do autor em 2026-10-28: com
    # deslocamentos de 1e-6 ela sugeria variacao expressiva
    assert "far from constant" not in t
    assert "exhibit small but nonzero changes" in t
    assert "maximum displacements between 1.2 × 10⁻⁶ and 6.7 × 10⁻⁶" in t
    assert "operational rather than mathematical immobility" in t
    # e a referencia externa nao e verdade quimica
    assert "a second statistical estimate built on the same training" in t
    assert "not a demonstration that the gate recovers chemically true " \
           "bands" in t
    # as duas alteracoes ao texto do autor estao declaradas
    assert "A cláusula do piso foi acrescentada" in t
    assert '"Strongly constrained" foi precisado' in t
    assert "declaradas aqui e não embutidas em silêncio" in t


@pytest.mark.semantico
def test_secao10_separa_achado_de_limitacao_de_reprodutibilidade():
    """Author 2026-10-28: the result is that selection can depend on the tie
    rule; the LIMITATION is that the historical overlaps are not reproducible
    without specifying the procedure. Two different statements."""
    import re
    t = re.sub(r"\s+", " ",
               (RAIZ / "paper" / "05-rascunho-s9-s10-s11.md").read_text())
    assert "conditional on the selection procedure used to resolve tied" in t
    assert "reproducing the gate values alone does not guarantee" in t
    assert "should not be generalised to experiments in which the selection " \
           "boundary contains no ties" in t
    assert "not a further finding" in t
    # a falsa simetria da resposta a n saiu
    assert "Unanchored overlap grows with n here and anchored overlap does " \
           "not" not in t
    assert "for which a rank correlation with n is undefined" in t
    assert "cannot be interpreted as evidence of a sample-size response" in t
    # e a hierarquia dos diagnosticos esta declarada na 9.4
    assert "ordered by cost, which is not the same as being ordered by what" in t
    assert "It does not substitute for the boundary inspection" in t
    assert "settles the matter in one line and no retraining" in t


@pytest.mark.estrutural
def test_15_exige_doze_secoes():
    """The consolidator must now expect twelve, so a lost Section 12 is a gap
    and not a silently shorter paper."""
    src = (RAIZ / "scripts" / "15_consolidar_manuscrito.py").read_text()
    assert "SECOES_ESPERADAS = 12" in src
    assert '"09-rascunho-s12.md", ["12. Conclusions"]' in src
    assert "had no conclusion at all" in src


@pytest.mark.semantico
def test_resumo_na_ordem_logica_do_autor():
    """Author 2026-10-28: the abstract must carry BOTH contributions, in a
    stated logical order, and the two abstract additions must not be bought
    by dropping a standing requirement. Rewritten rather than appended."""
    import re
    t = _resumo_prosa("02-resumo-C.md")
    # 2. metodo: os dois papeis do prior, com a formulacao do autor
    assert ("We disentangle prior-based gate initialisation from prior-based "
            "regularisation") in t
    assert "their distinct effects on learned spectral selections" in t
    # 3. resultado: inercia operacional localizada
    assert "leaves the prior's saturated level operationally inert" in t
    # 4. contraponto: aprendizagem fora do plato, com "separate" e nao
    # "external" -- a referencia e outro estimador sobre os mesmos dados
    assert "Outside the saturated plateau, the gates retained data-associated" in t
    assert "a separate statistical reference across the 223 floor-level bands" in t
    assert "external statistical reference" not in t
    # 5. o resultado metodologico, e 6. o limite de interpretacao
    assert "the overlap reflects the complete selection procedure" in t
    # e o estatuto post hoc declarado tambem no resumo
    assert "the tie-breaking analysis was a post hoc diagnostic" in t


@pytest.mark.semantico
def test_pre_registro_declara_o_post_hoc_antes_dos_resultados():
    """Author's Table 1 condition, 2026-10-28: the tie-breaking analysis is a
    post hoc discovery and must be identified as such BEFORE the results, not
    only in the conclusion, so a reader knows which claims were committed in
    advance."""
    import re
    t = re.sub(r"\s+", " ",
               (RAIZ / "paper" / "03-rascunho-s1-s2-s3.md").read_text())
    assert ("The tie-breaking analysis was not part of the original "
            "pre-registered hypothesis set") in t
    assert "post hoc diagnostic investigation" in t
    assert ("reported separately from the pre-registered hypothesis verdicts "
            "in Table 1") in t
    assert "follows from the selection procedure itself" in t
    assert "specific to the experimental settings examined here" in t
    # e esta nos metodos, antes dos resultados, com o motivo
    assert "We state this before the results rather than in the discussion" in t
    assert "which claims were committed in advance" in t


@pytest.mark.estrutural
def test_15_recusa_resumo_partido_em_vez_de_truncar():
    """On 2026-10-28 the abstract was rewritten with a line beginning '--',
    which the prose filter read as a list bullet; the paragraph split and the
    longest block was a 228-word fragment missing its first two sentences.
    The generator reported 228 words and shipped it. A heuristic that
    silently ships a shortened abstract is worse than one that stops."""
    src = (RAIZ / "scripts" / "15_consolidar_manuscrito.py").read_text()
    # "--" mid-prose is not a list marker; a hyphen plus a space is
    assert 're.match(r"^[-*] ", s)' in src
    assert '"--" mid-prose is not one' in src
    # e mais de um bloco grande para em vez de escolher o maior
    assert "prose blocks" in src and "of 40+ words" in src
    assert "Taking the longest would " in src
    assert "report its word count as the" in src


@pytest.mark.semantico
def test_resumo_representa_o_artigo_depois_da_etapa_b():
    """First integral-audit finding, 2026-10-28: the abstract approved on
    24/10 carried two p-values Section 5 disowns and reported -0.32 as a
    property of the gates. The author's decision was to REPLACE that sentence
    with the tie-breaking evidence, not to patch the coefficients, because
    correcting them would leave the false symmetry between the two arms."""
    import re
    r = _resumo_prosa("02-resumo-C.md")
    # a frase antiga saiu inteira, com os dois valores-p
    assert "Decile overlap grows with" not in r
    assert "p = 0.003" not in r and "p = 0.48" not in r
    # e no lugar entrou a evidencia central da Etapa B, com os mesmos gates
    assert "For identical stored gates" in r
    assert "0.7443-0.7659 under one sorting implementation" in r
    assert "0.9452-0.9867 under another" in r
    assert "1.0000 with index-based tie-breaking" in r
    assert ("the overlap reflects the complete selection procedure rather "
            "than an identifiable property of the gates") in r
    # as duas convencoes de decil ficam marcadas, para que q=28 e q=29 nao
    # sejam comparados diretamente (item 2 do autor)
    # Reworded by the author on 2026-10-29, at no cost in words, because the
    # guide requires "Abstracts must be able to stand alone": "that codebase"
    # had lost its antecedent when "from our own earlier work" came out of the
    # third sentence on 2026-10-28, and a demonstrative that points forward
    # does not hold in a text read on its own. Approved on the condition that
    # q = 28 stay explicit beside it, which the assertion enforces.
    assert "at the published convention of q = 28" in r
    assert "that codebase's convention" not in r
    # Reworded by the author on 2026-10-28, in the compression to the
    # journal's 250-word limit: "at the revision data's own convention of
    # q = 29" became "at the revision convention of q = 29", two words. The
    # requirement is unchanged -- q = 29 stays attributed to the revision and
    # separate from the q = 28 cell -- and the author chose this over cutting
    # the verb "examine", whose removal would have left "disentangle X from Y
    # and their effects" syntactically ambiguous. The guard follows the
    # author's wording; it does not keep a wording the author retired.
    assert "at the revision convention of q = 29" in r
    assert "at the revision data's own convention" not in r


@pytest.mark.semantico
def test_tabela1_h0_sem_contagem_por_construcao():
    """H0's criterion is existential and defines no per-partition tally, so
    the missing k/n is correct and the reason belongs in the cell. Adding 5/5
    would impose a unit the pre-registration does not have."""
    import re
    t = re.sub(r"\s+", " ", (RAIZ / "paper" / "00-estrutura.md").read_text())
    assert "sem contagem por construção" in t
    assert "o critério é existencial" in t
    assert "não define tally por partição" in t
    assert "imporia uma unidade que o pré-registro não tem" in t
    # e o 2/5 de H5a fica identificado como complemento, com a exaustividade
    f001 = re.sub(r"\s+", " ", (RAIZ / "findings"
                  / "F001-caminho-de-regularizacao.md").read_text())
    assert "o 2/5 de H5a" in f001
    assert "complemento aritmético do 3/5" in f001
    assert "exaustiva e mutuamente exclusiva" in f001
    assert "não um número que este achado" in f001


@pytest.mark.semantico
def test_tres_niveis_de_evidencia_separados():
    """Author 2026-10-28: the manuscript must distinguish the demonstrated
    computational mechanism, the observed experimental consequence, and the
    unestablished general prevalence -- with the contribution in the first two
    and the third offered as a question, never as a conclusion."""
    import re
    t = re.sub(r"\s+", " ",
               (RAIZ / "paper" / "01-rascunho-resumo-e-s4.md").read_text())
    assert "**The computational mechanism.**" in t
    assert "**The experimental consequence.**" in t
    assert "**The general prevalence.**" in t
    assert "**Demonstrated**, and not empirically" in t
    assert "**Observed**, in this dataset" in t
    assert "**Not established.**" in t
    assert "offered as a question rather than a finding" in t
    assert "The contribution of this paper is the first two rows" in t
    # e nenhuma afirmacao de prevalencia escapando logo depois do disclaimer
    assert "is not unusual, and the diagnosis is cheap" not in t
    assert "we are careful not to make one in the next breath either" in t
    assert "a question about the literature that we did not study" in t
    # a introducao nao afirma que a codificacao e amplamente reproduzida
    i = re.sub(r"\s+", " ",
               (RAIZ / "paper" / "03-rascunho-s1-s2-s3.md").read_text())
    assert "one widely reproduced way of encoding a prior" not in i
    assert "that we used in our own earlier work [4] violates them" in i
    assert "How often other encodings do is not something we measured" in i


@pytest.mark.estrutural
def test_16_reconcilia_a_unidade_de_contagem():
    """Author 2026-10-28: the report must declare its unit of count and not
    present a sum as if it matched the execution total. 242 functions against
    257 collected items left 15 unexplained; the 15 are parametrised cases,
    and the script computes them from the decorators rather than asserting
    them."""
    src = (RAIZ / "scripts" / "16_matriz_rastreabilidade.py").read_text()
    assert "UNIT OF COUNT: test FUNCTIONS defined at module level" in src
    assert "Not items collected by pytest, and" in src
    assert "def expansoes(" in src
    assert "items added by parametrised cases" in src
    assert "items this predicts pytest" in src
    # e a ressalva do modulo pulado por dependencia ausente
    assert "skipped for a missing" in src


@pytest.mark.estrutural
def test_16_chama_a_reconciliacao_de_estatica():
    """Author 2026-10-28: the AST count of parametrised cases is adequate for
    the static cases present, but must not be presented as a universal
    equivalent to pytest's collection. Dynamic parametrisation, parametrised
    fixtures, hook-generated cases and unavailable modules all break the
    equivalence, so the label is 'static reconciliation' and pytest's own
    count is the authority."""
    src = (RAIZ / "scripts" / "16_matriz_rastreabilidade.py").read_text()
    assert "STATIC reconciliation" in src
    assert "read from the source, not from a" in src
    assert "It is a prediction and not an equivalent" in src
    assert "built at runtime, parametrised fixtures" in src
    assert "cases generated by hooks" in src
    assert "pytest's own count is" in src
    # e existe o modo que confronta a predicao com a coleta real
    assert '"--collect"' in src
    assert '"--collect-only"' in src
    assert "the static prediction matches exactly" in src
    assert "DIFFERS from the prediction by" in src


@pytest.mark.estrutural
def test_16_check_confronta_a_matriz_com_os_testes():
    """Author's condition 2: being generated does not make the stored matrix
    synchronised -- the tests can change and the file not be regenerated. The
    generator must offer a check mode that rebuilds in memory, compares, and
    exits non-zero on divergence."""
    src = (RAIZ / "scripts" / "16_matriz_rastreabilidade.py").read_text()
    assert '"--check"' in src
    assert "def montar_md(" in src
    assert "OUT OF SYNC with the tests" in src
    assert "raise SystemExit(1)" in src
    assert "Being generated does not make it synchronised" in src
    assert "difflib" in src
    # e a matriz versionada esta de fato em sincronia agora
    import subprocess
    import sys
    r = subprocess.run(
        [sys.executable, "scripts/16_matriz_rastreabilidade.py",
         "--check", "docs/matriz-rastreabilidade.md"],
        cwd=RAIZ, capture_output=True, text=True)
    assert r.returncode == 0, (
        "docs/matriz-rastreabilidade.md is out of sync with the tests; "
        "regenerate it with --md.\n" + r.stdout[-800:])


@pytest.mark.estrutural
def test_16_declara_a_categoria_e_nao_a_infere():
    """The matrix must take each test's category from a declared pytest
    marker, never from its name or its assertions: a matrix built by guessing
    misclassifies quietly, which is the failure mode it exists to prevent.
    Unmarked tests are listed as UNCLASSIFIED with their count."""
    src = (RAIZ / "scripts" / "16_matriz_rastreabilidade.py").read_text()
    assert 'CATEGORIAS = ("semantico", "estrutural", "numerico")' in src
    assert "Nothing" in src and "is inferred from a test's name" in src
    assert "UNCLASSIFIED" in src
    assert "category is declared, never inferred" in src
    assert "would misclassify quietly" in src
    # e diz o que uma barreira semantica NAO estabelece
    assert "can satisfy a substring search and still carry a wrong" in src
    assert "not a substitute for reading" in src
    # as tres categorias estao registradas, para que marca desconhecida seja
    # erro de digitacao e nao categoria inventada de passagem
    tom = (RAIZ / "pyproject.toml").read_text()
    assert "[tool.pytest.ini_options]" in tom
    for c in ("numerico:", "estrutural:", "semantico:"):
        assert c in tom
    assert "a new category invented in" in tom


@pytest.mark.estrutural
def test_15_consolida_sem_perder_nem_inventar():
    """The consolidated manuscript is a build step over the drafts. It must
    copy the English verbatim, report every block it drops, anchor Table 1 on
    its own header rather than on the first table that matches, flag the two
    abstracts, and emit the section gap instead of inventing a Section 5."""
    src = (RAIZ / "scripts" / "15_consolidar_manuscrito.py").read_text()
    # a Tabela 1 e ancorada no cabecalho dela, nao na primeira que casar
    assert "veredito pelo critério | o que o resultado " in src
    assert "can ship the wrong" in src
    # A mensagem da âncora foi reenquadrada em 2026-11-09, quando a
    # Tabela 1 passou a vir da fonte em inglês. As quebras de string
    # são juntadas antes de procurar a frase: um teste sobre o texto de
    # uma mensagem não deve falhar por onde o autor do script quebrou a
    # linha.
    import re as _re
    junto = _re.sub(r'"\s*\n\s*f?"', "", src)
    assert ("rather than letting it match whichever table comes first"
            in junto)
    # os dois resumos sao sinalizados, nao resolvidos por delecao
    assert "TWO ABSTRACTS EXIST" in src
    assert "the drafts are not the place to " in src
    # o vao de secao sai como vao, e a verificacao fica depois de fechado
    assert "GAP:" in src
    assert "with a number invented to" in src
    assert "settle, not this script" in src
    # e a secao 5, promovida em 2026-10-28, esta na ORDEM
    assert '"08-rascunho-s5.md", ["5. Results — the response to sample size"]' in src
    assert "THE SECTION 5 GAP, AND HOW IT WAS CLOSED" in src
    assert "the next renumbering will need" in src
    # o consolidado nomeia o conteudo de que foi construido, de forma
    # DETERMINISTICA: a versao anterior punha a revisao git e a contagem de
    # arquivos sujos no cabecalho, o que fez o arquivo gerado depender da
    # arvore de trabalho e quebrou a entrega de 2026-10-28
    assert "Source digest:" in src
    assert "whatever the git state" in src
    assert "hashlib.sha256()" in src
    assert "it identifies the content that was consolidated" in src
    assert "Built from:" not in src
    # a revisao git vai para o stdout, nao para o artefato
    assert '"rev-parse", "--short", "HEAD"' in src
    assert "without contaminating the artefact" in src
    # e um bloco esperado que falte interrompe, em vez de abrir um buraco
    assert "manuscript with a hole in it" in src
    # o arquivo gerado se declara gerado
    assert "Do not edit this" in src


@pytest.mark.estrutural
def test_14_veredicto_de_uma_linha_nao_pode_ser_truncado():
    """The author's partition run of 2026-10-27 was piped through `tail -20`
    and the rows that mattered were above the cut. A check whose conclusion
    can be cropped off is not a check, so the verdict goes last and names the
    directories at fault."""
    src = (RAIZ / "scripts" / "14_etapa_b_por_procedimento.py").read_text()
    assert "SECTION 6 VERDICT over" in src
    assert "TIE ON THE BOUNDARY in" in src
    assert "PROCEDURES DISAGREE in" in src
    assert "NOT MEASURED in" in src
    assert "these are not covered by the verdict" in src
    assert "=> rule-invariant" in src
    assert "=> NOT established; see the lines above" in src
    assert "cannot hide a non-zero bnd" in src


@pytest.mark.semantico
def test_etapa_b_legenda_fig3_declara_regra_e_ambiente():
    """Author's item 4: the caption must declare rule, environment and origin,
    and the panel is plotted as drawn rather than redrawn."""
    import re
    t = re.sub(r"\s+", " ",
               (RAIZ / "paper" / "06-legendas-figuras.md").read_text())
    assert "procedure- and environment-specific" in t
    assert "plotted as drawn" in t and "rather than redrawn" in t
    assert "numpy 2.4.6 and" in t and "Python 3.14.6" in t
    assert "verified pixel-for-pixel" in t
    assert "**not** reproducible elsewhere" in t
    # e os paineis (a) e (c) nao carregam a dependencia
    assert "Panels (a) and (c) carry no such" in t
    assert "applies no selection operator at all" in t
    # a frase antiga, que afirmava ausencia de associacao detectavel, saiu
    assert "no statistically detectable monotonic association" not in t


@pytest.mark.numerico
def test_14_mede_a_fronteira_e_nao_conta_empates():
    """The criterion for rule-dependence is a tie group spanning rank q, not
    the presence of ties: n = 700 has ties inside the selected set and every
    procedure still agrees to every digit."""
    src = (RAIZ / "scripts" / "14_etapa_b_por_procedimento.py").read_text()
    assert "def empate_na_fronteira" in src
    assert "ord_desc[q - 1] == ord_desc[q]" in src
    assert "Ties strictly inside the" in src
    assert "different statements" in src
    # toda associacao sai marcada como exploratoria, com o motivo
    assert "EXPLORATORY in every row" in src
    assert "are not independent draws" in src
    # e o que o script NAO resolve fica dito
    assert "Does not settle: identity of selected sets" in src


@pytest.mark.semantico
def test_rascunho_nao_afirma_ausencia_total_de_empate():
    """The draft said the unanchored arm has no ties and the two rules agree
    to the last digit. True from n = 200, false below it. Corrected
    2026-10-24; the absolute phrasing must not come back.

    Corrected again 2026-10-27 (stage B): "carries no ties at all" from
    n = 200 is itself false -- n = 700 has two tied values INSIDE the selected
    set. What makes a selection rule-dependent is a tie group spanning the
    boundary at rank q, not the presence of ties, and measurement shows no
    group spans it from n = 200 upward. The criterion replaced the count."""
    import re
    t = re.sub(r"\s+", " ",
               (RAIZ / "paper" / "08-rascunho-s5.md").read_text())
    assert "where no ties occur" not in t
    assert "From n = 200 upward it carries no ties at all" not in t
    assert "The criterion is not whether ties exist but whether one sits" in t
    assert "on the boundary** at rank q" in t
    assert "at n = 700 two tied values sit inside the selected set and change" in t
    assert "two orders of magnitude below" in t


@pytest.mark.numerico
def test_rascunho_usa_a_esperanca_exata():
    """The draft must report the EXACT hypergeometric expectation of the
    Jaccard index, not the approximation, and must say why the two differ.

    F002's correction of 2026-10-24: q/(2L-q) is J evaluated at the expected
    overlap, not the expectation of J, and J is strictly convex in k, so
    E[J] > J(E[k]) by Jensen. The exact values are 0.7012 at q = 28 and 0.7445
    at q = 29, against 0.7000 and 0.7436 from the ratio -- a difference smaller
    than the sampling spread, which is what makes it easy to get wrong without
    consequence and worth guarding.

    The fourth assertion holds the measurement that replaced a placeholder:
    0.7442 is the randomised-tie collapse at q = 29, measured, where the draft
    once carried the word PENDENTE. A draft that reports an exact value and a
    pending note for the same quantity is the state this test exists to keep
    from returning.

    Decision recorded on 2026-11-02: this test was the one classified row in
    the matrix with a source and no decision -- the mirror of the broken links
    repaired the same day, missing the first term instead of the middle one.
    """
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


@pytest.mark.semantico
def test_resumo_C_carrega_as_quatro_exigencias():
    """The four binding requirements the author attached to approving
    register C, 2026-10-24. Recorded in 00-estrutura.md, 'Registro
    editorial'; two of them correct C's own first draft."""
    t = _resumo_prosa("02-resumo-C.md")
    # 1. a plateau larger than q creates the possibility, not the defect
    assert "does not produce one" in t
    assert "only if" not in t          # the overstated phrasing, retired
    # 2. the null model named in the sentence, with its q
    assert "28 of 34 plateau bands twice" in t
    # 3. the displacement control, and why it is immune
    assert "neither the top-k selection nor the tie-breaking" in t
    # 4. the eight refutations declared, not buried
    assert "six of which our criteria did not support" in t
    # The rewrite of 2026-10-28 compressed the abstract to fit two new
    # contributions and dropped requirements 1 and 2 in the process. This
    # test caught it. The two assertions above are the guard; this comment
    # is the record of what they are for.


@pytest.mark.semantico
def test_estrutura_concilia_com_o_ADR_0003():
    """Item 2 of 'O que falta antes da prosa' said the editor route was
    blocking and recorded my recommendation to notify. ADR-0003 decided
    otherwise. Both documents are committed, so the contradiction needs a
    dated note and the original text kept."""
    t = (RAIZ / "paper" / "00-estrutura.md").read_text()
    assert "Isso precisa\n   estar resolvido" in t      # original preserved
    assert "não é mais bloqueante" in t                 # and reconciled
    assert "não se verificou" in t


@pytest.mark.semantico
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
    assert "resemblance is\nformal and we draw nothing from it" in t
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
    t = _resumo_prosa("02-resumo-C.md")
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


@pytest.mark.numerico
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



@pytest.mark.estrutural
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


@pytest.mark.estrutural
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


@pytest.mark.numerico
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


@pytest.mark.numerico
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


@pytest.mark.semantico
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


@pytest.mark.estrutural
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


@pytest.mark.semantico
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
    # e o que FOI lido no guia fica citado literalmente, com a data
    assert "CONFIRMADO em 2026-10-28" in t
    assert "does not exceed 250 words" in t
    assert "each a maximum of 85 characters, including spaces" in t
    assert "1 to 7 keywords" in t
    assert "Authors must declare the use of generative AI tools" in t
    # o resumo contra o limite: a conta, e quem tomou a decisao
    assert "excesso **54**" in t
    # Updated 2026-10-28. The earlier guard asserted the 253-word floor I had
    # reported. That floor was invalid -- the route to it removed four
    # fragments the suite requires of the abstract -- so the guard now holds
    # the correction in place instead of the error: the real floor, the
    # corrected inventory, and the three decisions that closed the gap.
    assert "Esse número era inválido" in t
    assert "são **21**, em quatro funções de teste" in t
    assert "**145 palavras literais**" in t
    assert "O piso real da compressão é 266 palavras" in t
    assert "As últimas 17 palavras saíram por três decisões do autor" in t
    assert "Recusado pelo autor" in t and "sem espaços em torno do ±" in t
    # e as figuras conferidas, nao supostas
    assert "pdffonts` reporta `emb=yes` em todas" in t
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


@pytest.mark.estrutural
def test_09_garante_dtype_antes_de_comparar_bits():
    """view(np.int64) presupposes the array really is float64, which the
    author asked to be guaranteed rather than assumed."""
    src = (RAIZ / "scripts" / "09_controle_deslocamento.py").read_text()
    assert "if g_.dtype != np.float64:" in src
    assert "would compare the wrong width" in src
    # and the resolution question is checked, not asserted
    assert "exactly representable in" in src


@pytest.mark.numerico
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


@pytest.mark.numerico
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


@pytest.mark.semantico
def test_resumo_cabe_no_limite_confirmado_do_chemolab():
    """The journal's limit, read at the source on 2026-10-28: "You are
    required to provide a concise and factual abstract which does not exceed
    250 words." Quoted verbatim in 07-declaracoes-submissao.md.

    Two things are checked, and the second matters as much as the first. The
    abstract must fit the limit; and the count declared in the file's own
    header must be the measured count, so that a later edit cannot leave a
    stale number standing next to a text that no longer has it. The unit is
    whitespace-separated tokens, which is what the Word counter approximates
    and which the file states.
    """
    import re
    prosa = _resumo_prosa()
    medido = len(prosa.split())
    assert medido <= LIMITE_RESUMO, f"abstract at {medido} words"
    bruto = (RAIZ / "paper" / "02-resumo-C.md").read_text()
    declarado = re.search(r"(\d+) palavras por espaço em branco", bruto)
    assert declarado, "the abstract file no longer declares its word count"
    assert int(declarado.group(1)) == medido, (
        f"header says {declarado.group(1)}, measured {medido}")
    # the removed framing sentence must not creep back in
    assert "Interpretive stability in prior-guided" not in prosa


@pytest.mark.semantico
def test_highlights_nao_convertem_resultado_fraco_em_ausencia():
    """The three corrections the author approved on 2026-10-28. A highlight is
    read on its own, with no sentence beside it to qualify it, so each of the
    three earlier wordings failed a test the manuscript itself applies:

    H4 claimed alignment at the floor "not at its plateau", which Figure 5's
    caption explicitly refuses -- a weaker result at the plateau is not
    evidence of absence there. H3 used "operationally inert", a term defined
    only inside the abstract by its gradient clause; alone in a bullet it
    invites the mathematical-immobility reading F007 refutes (max |d| between
    1.2e-6 and 6.7e-6, small and NONZERO). H2 said "different sort rules",
    conflating the sorting implementation with the tie rule, which F008 keeps
    apart.
    """
    import re
    bruto = (RAIZ / "paper" / "07-declaracoes-submissao.md").read_text()
    t = re.sub(r"\s+", " ", bruto)
    # The retired wordings are QUOTED in the note that records why they were
    # retired, so the check reads the TABLE ROWS and not the section: a guard
    # that a correction note can satisfy guards nothing. Same lesson as the
    # abstract header, found the same day.
    secao = bruto.split("### 2.1", 1)[1].split("\n### ", 1)[0]
    linhas = [l for l in secao.splitlines()
              if re.match(r"^\|\s*\d+\s*\|", l)]
    textos = [l.split("|")[2].strip() for l in linhas]
    declarados = [int(l.split("|")[1].strip()) for l in linhas]
    assert 3 <= len(textos) <= 5, f"{len(textos)} highlights, the guide says 3 to 5"
    for n, h in zip(declarados, textos):
        assert len(h) == n, (h, len(h), n)      # contagem declarada = medida
        assert len(h) <= 85, (h, len(h))        # limite do guia
    assert textos == [
        "Top-q overlap depends on the tie rule when the boundary cuts equal "
        "gate values",
        "The same stored gates gave overlaps of 0.744 to 1.000 across sorting "
        "procedures",
        "Prior-based initialisation makes the saturated level unresponsive to "
        "the penalty",
        "Gates align with a separate statistical reference at the prior's "
        "223-band floor",
        "Check boundary ties before reading overlap as reproducible band "
        "selection",
    ]
    # e as tres redacoes retiradas ficam registradas como retiradas
    assert "afirmava o que a legenda da Figura 5 **recusa explicitamente**" in t
    assert "pequeno e **não nulo**" in t
    assert "fundia implementação de ordenação e regra" in t
    # o limite do guia e a contagem declarada, nao suposta
    assert "o limite é 85" in t
    assert "medida e não estimada" in t


@pytest.mark.estrutural
def test_16_nao_emite_linha_semantica_sem_fonte():
    """A semantic row with no source is a broken traceability link.

    Found in the author's run of 2026-10-28, immediately after the abstract
    compression. The four abstract tests had been redirected from reading
    `paper/02-resumo-C.md` to a helper, `_resumo_prosa`, which reads the file
    for them. The matrix takes each test's sources from the string literals in
    the test body, so three semantic rows -- the four binding requirements of
    register C, the author's logical order, and the Stage B evidence -- were
    printed with no source at all. `--check` passed throughout: the stored
    matrix matched the generated one, and both had lost the same link.

    The repair was to have the callers name the file they guard, so the link
    comes from a literal the test really passes to the reader rather than from
    a comment. This test is the barrier: the matrix's purpose is
    decision -> source -> test, and a row missing the middle term is not a
    formatting defect.

    IT HAPPENED AGAIN, and this guard did not catch it. On 2026-11-02 the
    author's matrix showed two more rows with no source --
    test_17_resolve_marcadores_e_ordem_de_aparicao (numerico) and
    test_18_nao_chama_de_mistura_o_que_e_ingles_britanico (estrutural) --
    through exactly the same cause: a helper, _mod17 and _mod18, holding the
    path literal that the test body no longer had. The guard missed them
    because I had scoped it to semantic rows only, having repaired the
    symptom in the category where I found it. It now covers every declared
    category, and the two helpers name the file they load.

    AND IT CHECKED ONE TERM OF THREE. The matrix prints decision -> source ->
    test, and the same run showed test_rascunho_usa_a_esperanca_exata with a
    source and no decision -- the first term missing instead of the middle
    one, which this guard was not looking at either. It now requires both of
    the terms the matrix can see: a declared category must come with a
    docstring and with at least one file the test names. The third term, the
    test itself, is the row.
    """
    import ast
    import importlib.util
    cam = RAIZ / "scripts" / "16_matriz_rastreabilidade.py"
    esp = importlib.util.spec_from_file_location("m16", cam)
    m16 = importlib.util.module_from_spec(esp)
    esp.loader.exec_module(m16)
    CATEGORIAS = ("semantico", "estrutural", "numerico")
    sem_fonte, sem_decisao = [], []
    for f in sorted((RAIZ / "tests").glob("test_*.py")):
        texto = f.read_text()
        for no in ast.walk(ast.parse(texto)):
            if not (isinstance(no, ast.FunctionDef)
                    and no.name.startswith("test_")):
                continue
            marcas = [d.attr for d in no.decorator_list
                      if isinstance(d, ast.Attribute)]
            cat = [c for c in CATEGORIAS if c in marcas]
            if not cat:
                continue
            if not m16.fontes_citadas(no, texto):
                sem_fonte.append(f"{no.name} [{cat[0]}]")
            if not ast.get_docstring(no):
                sem_decisao.append(f"{no.name} [{cat[0]}]")
    assert not sem_fonte, f"classified tests with no source: {sem_fonte}"
    assert not sem_decisao, (
        f"classified tests with no decision: {sem_decisao}")


@pytest.mark.semantico
def test_highlights_e_keywords_nao_divergem_entre_as_duas_fontes():
    """The five highlights and the six keywords now live in three places: the
    approval record in `07-declaracoes-submissao.md`, the submission sources
    `10-highlights.md` and `11-palavras-chave.md`, and the consolidated
    manuscript built from the latter two. A correction applied in one and not
    in the others is the propagation failure this suite exists for, and it has
    happened in this programme repeatedly.

    The manuscript is generated, so it is not read here: `15` builds it from
    the sources, and `test_15_consolida_sem_perder_nem_inventar` guards that
    build. What is checked is that the two sources agree with the record.
    """
    import re
    reg = re.sub(r"\s+", " ",
                 (RAIZ / "paper" / "07-declaracoes-submissao.md").read_text())
    hi = (RAIZ / "paper" / "10-highlights.md").read_text()
    kw = (RAIZ / "paper" / "11-palavras-chave.md").read_text()

    bullets = [l[2:].strip() for l in
               hi.split("## Highlights", 1)[1].splitlines() if l.startswith("- ")]
    assert 3 <= len(bullets) <= 5, f"{len(bullets)} highlights, the guide says 3 to 5"
    for b in bullets:
        assert len(b) <= 85, (b, len(b))     # limite do guia
        assert b in reg, f"highlight not in the approval record: {b}"
    # o nome do arquivo carrega a palavra que o guia exige
    assert "highlights" in (RAIZ / "paper" / "10-highlights.md").name
    assert "separate editable file" in hi

    chaves = [k.strip() for k in
              kw.split("## Keywords", 1)[1].replace("\n", " ").split(";")
              if k.strip()]
    assert 1 <= len(chaves) <= 7, f"{len(chaves)} keywords, the guide says 1 to 7"
    for k in chaves:
        # "avoid keywords consisting of multiple words (using 'and' or 'of')"
        assert " and " not in f" {k.lower()} ", k
        assert " of " not in f" {k.lower()} ", k
        assert k.lower() in reg.lower(), f"keyword not in the approval record: {k}"


@pytest.mark.estrutural
def test_15_emite_a_materia_de_frente_fora_da_numeracao():
    """Front matter, added 2026-10-29 after the second reading of the guide.

    Highlights before the abstract, keywords after it, and neither inside the
    section numbering -- the guide requires that of the abstract ("Do not
    include the article abstract within section numbering") and the same holds
    for what sits beside it. The twelve-section expectation must therefore be
    unchanged by the addition, which is the point of asserting it here: a
    front-matter block that counted as a section would make the gap check pass
    on a manuscript with thirteen.
    """
    src = (RAIZ / "scripts" / "15_consolidar_manuscrito.py").read_text()
    assert '("10-highlights.md", ["Highlights"])' in src
    assert '("11-palavras-chave.md", ["Keywords"])' in src
    assert "SECOES_ESPERADAS = 12" in src
    # a ordem declarada: highlights, resumo, palavras-chave
    i_h = src.index('("10-highlights.md"')
    i_r = src.index('("02-resumo-C.md"')
    i_k = src.index('("11-palavras-chave.md"')
    assert i_h < i_r < i_k, "front matter out of order in ORDEM"
    # e a posicao das palavras-chave esta declarada como convencao, nao como
    # exigencia lida no guia
    assert "Adopted convention, not a requirement read." in src


def _mod17(nome: str = "17_citacoes.py"):
    import importlib.util
    cam = RAIZ / "scripts" / nome
    esp = importlib.util.spec_from_file_location("c17", cam)
    m = importlib.util.module_from_spec(esp)
    esp.loader.exec_module(m)
    return m


@pytest.mark.numerico
def test_17_resolve_marcadores_e_ordem_de_aparicao():
    """The three arithmetic checks the guide's reference rules reduce to:
    every marker resolves, every entry is cited, and the numbering follows
    first appearance. Exercised on synthetic text, so the test does not depend
    on the manuscript's current citation state -- which is none.

    The marker reader must also not mistake a markdown link for a citation.
    The drafts are full of `[text](url)`, and a scanner that counted those
    would report citations that do not exist.
    """
    m = _mod17("17_citacoes.py")
    assert m.marcadores("a [1] b [2,3] c [5-7] d") == [1, 2, 3, 5, 6, 7]
    assert m.marcadores("see [the guide](http://x) and [F008]") == []
    assert m.marcadores("ranges backwards [7-5] are not expanded") == []
    # order of appearance
    texto = "first [2] then [1]"
    ordem = []
    for n in m.marcadores(texto):
        if n not in ordem:
            ordem.append(n)
    assert ordem == [2, 1] and ordem != sorted(ordem)
    # the list reader
    lista = "## References\n\n[1] A, Nature 1 (2020) 1-2.\n[2] B, [FALTA: year]\n"
    assert m.entradas(lista) == [(1, "A, Nature 1 (2020) 1-2."),
                                (2, "B, [FALTA: year]")]
    assert m.entradas("no heading here\n[1] A\n") == []
    assert m.estado_declarado("Status: **INCOMPLETO** — lido\n") == "INCOMPLETO"
    assert m.estado_declarado("nothing") == "NAO DECLARADO"


@pytest.mark.estrutural
def test_17_varre_os_rascunhos_que_a_ordem_declara():
    """The scanner takes its file list from the consolidator's ORDEM, not from
    a glob of paper/. A draft wired into the manuscript and not into the
    scanner would have its citations unchecked, and the two lists would drift
    apart silently -- which is how the front matter of 2026-10-29 could have
    been missed."""
    m = _mod17()
    fontes = m.fontes_do_texto()
    for esperado in ("10-highlights.md", "02-resumo-C.md",
                     "11-palavras-chave.md", "09-rascunho-s12.md",
                     "06-legendas-figuras.md", "00-estrutura.md"):
        assert esperado in fontes, esperado
    for nome in fontes:
        assert (RAIZ / "paper" / nome).is_file(), nome


@pytest.mark.semantico
def test_12_audita_os_pontos_que_exigem_citacao():
    """The reference audit of 2026-10-29. The manuscript has no citations at
    all, so the deliverable is the list of places that require one, each with
    who can close it -- not a list of references written from memory, which
    would be worse than the absence because the absence is visible.

    Two claims in the audit are load-bearing and are guarded by name. The
    first is the sentence about what the band-selection literature uses, which
    asserts something about the literature with no source at all. The second
    is the README's own instruction to cite the modalities paper for the
    architecture, because the manuscript that would have introduced it was
    rejected.
    """
    import re
    t = re.sub(r"\s+", " ", (RAIZ / "paper" / "12-referencias.md").read_text())
    assert "INCOMPLETO" in t
    assert "não tem nenhuma citação e nenhuma lista de referências" in t
    # nenhuma entrada escrita de memória, e o que falta fica marcado
    assert "Nenhuma entrada é escrita de memória" in t
    assert "[FALTA:" in t
    # os dois pontos de auditoria que não podem desaparecer
    assert "the ratio q/(2L-q) that the band-selection literature uses" in t
    assert "afirmação sobre a literatura sem uma única fonte" in t
    assert "Citar o artigo de modalidades para a arquitetura" in t
    # as duas entradas prontas têm procedência declarada
    assert "doi:10.17632/46htwnp833.3" in t and "Mendeley Data, V3, 2024" in t
    assert "doi:10.1038/s41586-020-2649-2" in t
    assert "Nature 585 (2020) 357–362" in t
    # A lista entra no manuscrito SOMENTE enquanto o estado declarado for
    # COMPLETO. Ate 2026-11-09 o consolidador nem conhecia este arquivo, e o
    # teste exigia que nao o conhecesse; agora ele o le e emite a secao, com
    # a condicao explicita, porque uma lista parcial emitida em silencio e o
    # que este programa recusa.
    src = (RAIZ / "scripts" / "15_consolidar_manuscrito.py").read_text()
    assert 'REFERENCIAS = "12-referencias.md"' in src
    assert 'if estado == "COMPLETO":' in src
    assert "References: NOT emitted" in src


@pytest.mark.numerico
def test_f009_mede_a_grade_e_separa_o_que_nao_afeta():
    """F009, measured from the stored wavelength grid on 2026-10-29: the grid
    is 309-1149 nm at 3 nm, and the prior's third declared region, 1100-1200
    nm, is truncated at 1149 -- 17 bands where the full window would hold
    about 34. The finding must keep three things apart: the measurement, what
    it does not affect (every result, because the plateau is the 900-1000 nm
    level and is fully covered), and what it does affect (what the text
    declares). It must also not propose fixing the prior's construction, which
    encodes a literature region and not an instrument range.
    """
    import re
    f = re.sub(r"\s+", " ",
               (RAIZ / "findings" /
                "F009-a-grade-de-ondas-e-a-terceira-regiao-do-prior.md"
                ).read_text())
    assert "309,0 a 1149,0 nm, 281 bandas, passo de 3,00 nm" in f
    assert "truncada em 1149 nm" in f
    assert "Não afeta nenhum resultado" in f
    assert "não deve ser corrigido no código" in f
    # e a medida tem de bater com os dados versionados, não com o texto
    import numpy as np
    z = np.load(RAIZ / "data" / "processed" / "gates_r2" / "gates_n1158.npz")
    w, pr = z["wavelengths"], z["prior"]
    assert len(w) == 281
    assert float(w.min()) == 309.0 and float(w.max()) == 1149.0
    assert float(np.median(np.diff(w))) == 3.0
    niveis = {round(float(v), 1): int((pr == v).sum())
              for v in np.unique(pr)}
    assert niveis == {0.1: 223, 0.6: 7, 0.8: 17, 1.0: 34}
    # a terceira região declarada não cabe na grade
    assert int(((w >= 1100) & (w <= 1200)).sum()) == 17


@pytest.mark.semantico
def test_texto_declara_a_grade_e_o_truncamento():
    """F009's two text corrections, 2026-10-29. Both state a measured fact and
    retract nothing: Section 2.1 gives the wavelength grid, and the Figure 1
    caption says the third region is truncated by the instrument's range.

    Without the first the second has nothing to rest on; with both, a reader
    can check the figure's printed band counts, which is what made the
    discrepancy findable in the first place. The caption must also keep saying
    that the plateau is covered in full, because that is the level where the
    paper's geometric condition is measured.
    """
    import re
    s2 = re.sub(r"\s+", " ",
                (RAIZ / "paper" / "03-rascunho-s1-s2-s3.md").read_text())
    assert "281 wavelengths spanning 309 to 1149 nm in steps of 3 nm" in s2
    # The captions are blockquotes, so the "> " markers are stripped BEFORE
    # the whitespace is collapsed; otherwise a sentence that wraps across
    # lines reads as "... ends at > 1149 nm" and no contiguous fragment of it
    # can be matched. Found the hard way, more than once in this suite.
    bruto = (RAIZ / "paper" / "06-legendas-figuras.md").read_text()
    leg = re.sub(r"\s+", " ",
                 "\n".join(re.sub(r"^\s*>\s?", "", l)
                           for l in bruto.splitlines()))
    assert "truncated by the instrument's range, which ends at 1149 nm" in leg
    assert "17 of the bands a full 100 nm window would hold" in leg
    assert "plateau at 900–999 nm is covered in full" in leg


def _mod18(nome: str = "18_conformidade.py"):
    import importlib.util
    cam = RAIZ / "scripts" / nome
    esp = importlib.util.spec_from_file_location("c18", cam)
    m = importlib.util.module_from_spec(esp)
    esp.loader.exec_module(m)
    return m


@pytest.mark.estrutural
def test_18_nao_chama_de_mistura_o_que_e_ingles_britanico():
    """The guide: "write in American or British English but not a combination
    of both". A checker for that is only useful if it does not push a correct
    text into an incorrect one, so three classes are excluded by name:

      - British English uses BOTH "program" (computer code) and "programme"
        (a plan or project), and both "license" (verb) and "licence" (noun).
        The manuscript uses each correctly, in that sense.
      - "size", "sized", "oversized" are the same word in both variants and
        are not -ise/-ize verb forms. This checker reported "oversized" as an
        American outlier on its first run, in an abstract that is British
        throughout.
      - "precise", "noise", "wise", "promise" and their kin end in -ise
        without being British spellings.
    """
    m = _mod18("18_conformidade.py")
    pbr = next(p for n, p, _ in m.PARES if n.startswith("-ise"))
    pam = next(p for n, _, p in m.PARES if n.startswith("-ise"))
    assert m.ocorrencias(pam, "an oversized level set of size 34") == []
    assert m.ocorrencias(pbr, "a precise and concise noise, otherwise") == []
    assert m.ocorrencias(pbr, "this programme and that program") == []
    assert m.ocorrencias(pam, "the licence the objective does not license") == []
    # and it does catch a real mixed pair
    assert m.ocorrencias(pbr, "prior-based initialisation") == ["initialisation"]
    assert m.ocorrencias(pam, "prior-based initialization") == ["initialization"]


@pytest.mark.semantico
def test_cada_figura_e_citada_e_as_legendas_estao_em_ingles():
    """Two defects found by the conformity scan of 2026-10-29, both fixed in
    the same commit, both in what the guide requires of every submission.

    FIGURE 2 WAS CITED NOWHERE. The guide requires each figure to be cited in
    the text, and Figure 2 -- the overlap by tie rule against the exact
    hypergeometric line, one of the paper's central figures -- had no citation
    at all. It is now cited where the randomised-tie result is reported, which
    is what the figure plots.

    THE CAPTION HEADINGS WERE IN PORTUGUESE. The caption text was English and
    the headings read "Figura N", and the generator copied them into an
    otherwise English manuscript. The drafts and the generator now agree on
    "Figure N", so the artefact carries no Portuguese label.
    """
    import re
    leg = (RAIZ / "paper" / "06-legendas-figuras.md").read_text()
    for n in range(1, 6):
        assert f"## Figure {n}" in leg, n
        assert f"## Figura {n}" not in leg, n
    src = (RAIZ / "scripts" / "15_consolidar_manuscrito.py").read_text()
    assert 'if t.startswith("Figure")' in src
    assert 'startswith("Figura")' not in src
    # Figure 2 cited where 0.7005 is reported, in 4.2.1
    s4 = re.sub(r"\s+", " ",
                (RAIZ / "paper" / "01-rascunho-resumo-e-s4.md").read_text())
    assert "at that codebase's convention (q = 28; Figure 2)" in s4


@pytest.mark.semantico
def test_12_aplica_as_tres_decisoes_que_fecham_sem_bibliografia():
    """Three of the author's four decisions of 2026-11-09 close without a
    single reference, and all three are applied here.

    BANDS. The three near-infrared windows are the authors' choice and are
    no longer presented as taken from a source, in Section 2.2 and in Figure
    1's caption, and the sentence that generalised to "the ordinary way to
    encode published band assignments" lost its attribution. Nothing in the
    paper rests on the windows being right, which the text now says.

    THE RATIO. Route B: Section 2.5 and 4.2.1 stop asserting what others do
    with q/(2L-q) and say what F004 records -- that this work had done it
    itself, treating the ratio as exact. The heading changed with them, and
    the word "familiar" went, because it was the last unsourced claim about
    general practice.

    THE REVISION DATA. Section 2.4, where it enters, declares it: the
    authors' own unpublished material, run under the published protocol,
    from a manuscript not accepted and not to be resubmitted, used as a
    preliminary observation and not as published or independent evidence.

    The abstract is NOT touched, by the author's instruction. It never
    claimed publication: "from our own earlier work" had already gone in the
    compression, and what remains is "at the revision convention of q = 29".
    This test asserts that too, because an edit made for the right reason in
    the wrong file is still an edit he refused.
    """
    t = re.sub(r"\s+", " ", (RAIZ / "paper" / "12-referencias.md").read_text())
    for marca in ("Bandas NIR — REVERTIDA", "rota B aplicada",
                  "`pgsg_1` R2 — aplicada"):
        assert marca in t, marca

    s2 = re.sub(r"\s+", " ",
                (RAIZ / "paper" / "03-rascunho-s1-s2-s3.md").read_text())
    s4 = re.sub(r"\s+", " ",
                (RAIZ / "paper" / "01-rascunho-resumo-e-s4.md").read_text())
    leg = re.sub(r"\s+", " ",
                 (RAIZ / "paper" / "06-legendas-figuras.md").read_text())

    # 1. REVERTIDA em 2026-11-09, depois de ler os PDFs. A decisao do autor
    # era condicional -- "se foram definidos pelos autores" -- e a condicao e
    # falsa: a secao 4.4 de [2], publicada, chama as tres janelas de
    # literature-derived e cita a sua propria referencia [5], que e o
    # Saranwong de 2004. As janelas tem fonte, e a atribuicao volta com ela.
    # O que permanece da decisao: os tres NIVEIS sao nossos, e o artigo diz
    # que nada nele depende das janelas serem as certas.
    n_sar = _num_ref("Saranwong")
    assert ("three literature-derived regions relevant to dry-matter "
            f"content [{n_sar}]") in s2
    assert "The three levels are ours; the three windows and their" in s2
    assert "assignments are not." in s2
    assert "level set larger than the selected set" in s2
    assert "methodological choice of ours" not in s2
    assert "the ordinary way to encode published band assignments" not in s2
    assert "three regions the authors selected" not in leg
    t12 = re.sub(r"\s+", " ",
                 (RAIZ / "paper" / "12-referencias.md").read_text())
    assert "Saranwong" in t12 and "literature-derived" in t12

    # 2. rota B: a atribuicao e nossa nos dois lugares, e o titulo acompanha
    assert "how we had computed it" in s2
    assert "how it is usually computed" not in s2
    assert "is often quoted as q / (2L" not in s2
    assert ("that is what we had done ourselves, treating it as the exact "
            "value") in s2
    assert "which we had used ourselves as if it were exact" in s4
    assert "that the band-selection literature uses" not in s4
    assert "familiar approximation" not in s4

    # 3. os dados da revisao, declarados onde entram
    assert ("The stored metrics and gate vectors of that revision are the "
            "authors' own unpublished material") in s2
    assert "not accepted and will not be resubmitted" in s2
    assert "not offered as published or as independent evidence" in s2
    # e a 5 continua chamando as associacoes de exploratorias, que e o que a
    # frase da 2.4 afirma sobre ela
    s5 = re.sub(r"\s+", " ",
                (RAIZ / "paper" / "08-rascunho-s5.md").read_text())
    assert "Both associations are **exploratory**" in s5

    # e o resumo nao foi tocado
    resumo = (RAIZ / "paper" / "02-resumo-C.md").read_text()
    prosa = " ".join(resumo.split("\n---\n", 1)[1].split())
    assert "at the revision convention of q = 29" in prosa
    assert "our own earlier work" not in prosa
    assert len(prosa.split()) == 249, len(prosa.split())


@pytest.mark.semantico
def test_07_registra_a_conformidade_medida_sem_alterar_a_citacao_do_autor():
    """The language rule, measured: British throughout, one American form, and
    that form sits inside the blockquote Section 9.3 presents as the authors'
    own statement. The blockquote is this programme's device for marking text
    the assistant does not rewrite, so the outlier is reported and left, with
    both defensible outcomes named. The record must also keep the two pairs
    that are NOT mixing, so that a later pass does not 'fix' a correct text.
    """
    import re
    t = re.sub(r"\s+", " ",
               (RAIZ / "paper" / "07-declaracoes-submissao.md").read_text())
    assert "Conformidade medida, 2026-10-29" in t
    assert "não era citada em lugar nenhum do texto" in t
    assert "rascunho e gerador passaram a dizer `## Figure N`" in t
    assert "Não a alterei" in t and "não reescrevo" in t
    assert "Não contado como mistura" in t
    assert "`program` (código) contra `programme` (projeto)" in t
    # a forma americana continua lá, intacta, no bloco do autor
    bruto = (RAIZ / "paper" / "05-rascunho-s9-s10-s11.md").read_text()
    assert "prior-based initialization" in bruto


@pytest.mark.estrutural
def test_18_separa_prosa_autoral_de_citacao_literal():
    """The author's decision of 2026-10-29: a verbatim quotation is reproduced
    as it was written, so an outlier inside one is not a defect; British
    spelling is required of authorial prose only.

    Before this, the checker demanded one variant everywhere, which amounted
    to asking that a quotation be altered to satisfy a rule about writing --
    worse than the mixing the rule exists to prevent. The split is measured on
    blockquote markers, because that is how this manuscript marks quotation.

    Figure captions are blockquotes too, and they ARE authorial, so they are
    counted on the authorial side. A test that did not pin that down would let
    a caption's spelling go unchecked.
    """
    m = _mod18()
    autoral, citado = m.separa_citacoes(
        "authorial line\n> quoted line\n  > indented quote\nmore authorial\n")
    assert "authorial line" in autoral and "more authorial" in autoral
    assert "quoted line" in citado and "indented quote" in citado
    assert "quoted line" not in autoral
    src = (RAIZ / "scripts" / "18_conformidade.py").read_text()
    # as legendas voltam para o lado autoral
    assert 'autoral = autoral_corpo + "\\n" + legendas' in src
    # e so a prosa autoral gera defeito
    assert "form(s) in AUTHORIAL prose" in src


@pytest.mark.semantico
def test_12_fecha_o_conjunto_raman_por_concordancia_declarada():
    """The Raman dataset, identified on 2026-10-29. "bioprocess_substrates"
    and "RamanBench" named no publication; the search closed both. The
    identification of the local file with the public deposit rests on three
    exact agreements with what the manuscript already declares -- 6960
    spectra, 1870 shifts plus eight targets against 1878 columns, glucose
    among the targets -- and NOT on a name match, because the name
    "bioprocess_substrates" appears in none of the sources.

    The record must say that, and must leave the confirmation with the author,
    who ingested the file. A dataset identified by three matching numbers and
    presented as identified by name would be the kind of quiet overreach this
    audit exists to prevent.
    """
    import re
    t = re.sub(r"\s+", " ", (RAIZ / "paper" / "12-referencias.md").read_text())
    assert "doi:10.1016/j.measurement.2025.118884" in t
    assert "Measurement 258 (2026) 118884" in t
    assert "arXiv:2605.02003v1" in t
    assert "chlange/SubstrateMixRaman" in t and "CC BY 4.0" in t
    assert "é por concordância aritmética e não por nome" in t
    assert "não aparece** em nenhuma das fontes" in t
    assert "é o autor quem a confirma" in t


@pytest.mark.semantico
def test_12_registra_o_dossie_e_os_tres_destinos():
    """The dossier the author asked for on 2026-10-29, and the complication it
    exposes. "our own earlier work" and "the earlier study" may point at
    DIFFERENT papers, and one of them cannot be cited as published: F004
    records that the seven-size gate vectors come from the pgsg_1 R2 revision,
    whose manuscript was rejected and will not be resubmitted, while the same
    finding calls q = 28 "a definição do código publicado", and ADR-0003 ties
    the displacement control to the accepted modalities paper.

    Three destinations, not one. The file must hold the dossier with file and
    line for each claim, and must not resolve the attribution, which is the
    authors'.
    """
    import re
    t = re.sub(r"\s+", " ", (RAIZ / "paper" / "12-referencias.md").read_text())
    assert "Dossiê" in t
    assert "Gate Topology and Reproducibility of Prior-Guided Spectral Gating" in t
    assert "C. J. Coelho e G. Coelho" in t
    assert "prior-guided-spectral-gating" in t
    assert "manuscrito **rejeitado**, não será ressubmetido" in t
    assert "Três destinos, não um" in t
    assert "Nenhuma dessas três atribuições é minha para fechar" in t
    # a busca pela razao, e o que ela nao demonstra
    assert "Não encontrei nenhuma" in t
    assert "Não ter encontrado não demonstra que não exista" in t


@pytest.mark.semantico
def test_07_registra_as_quatro_decisoes_e_a_condicao_nao_satisfeita():
    """The author's four decisions of 2026-10-29. Three are applied and one is
    conditional, and the record must not present the conditional one as
    settled: route A for Section 2.5 holds only if the ratio derives from a
    published methodology, and the search did not find one. A table that
    listed it as "decided" would turn an open question into a closed one.
    """
    import re
    t = re.sub(r"\s+", " ",
               (RAIZ / "paper" / "07-declaracoes-submissao.md").read_text())
    assert "As quatro decisões de 2026-10-29" in t
    assert "desde que q = 28 continue explícito ao lado" in t
    assert "condicional, e a condição não foi satisfeita" in t
    assert "manter verbatim dentro da citação literal" in t
    assert "`.tex`, como formato principal" in t
    # e o motivo da mudanca no verificador fica dito
    assert "pedia que uma citação literal fosse alterada" in t


@pytest.mark.semantico
def test_18_mede_o_idioma_do_artefato_por_secao():
    """The manuscript is English, and anything in the drafting language that
    reaches it is a defect of the submitted file. Found on 2026-10-29 and
    measured by section, because where it sits decides what it is:

      Table 1 -- the paper's only table, the record of all twenty
      pre-registered hypotheses, cited five times in the body -- is entirely
      in Portuguese, headers and all twenty rows.

      A drafting pendency note sat inside Section 9.3, in Portuguese, in the
      English text that goes to the journal.

    The note was moved verbatim to paper/correcao-em-provas.md the same day,
    which is where the accepted paper's open details live. The table is
    proposed for translation and awaits the author, so this check still
    reports a defect and --strict still fails. That is the correct state: the
    manuscript is not conformant until the table is in English.
    """
    m = _mod18()
    # a lista de marcadores nao pode disparar em ingles
    import re
    for inocente in ("a gate", "the data", "no tie", "and the prior",
                     "de facto", "e.g. the floor"):
        assert not re.findall(m.MARCADORES_PT, inocente, re.I), inocente
    for culpado in ("não suportada", "veredito pelo critério", "o platô",
                    "partições retidas"):
        assert re.findall(m.MARCADORES_PT, culpado, re.I), culpado
    # a nota de pendencia saiu da secao inglesa e esta preservada
    s9 = (RAIZ / "paper" / "05-rascunho-s9-s10-s11.md").read_text()
    assert "PENDÊNCIA RESIDUAL" not in s9
    provas = (RAIZ / "paper" / "correcao-em-provas.md").read_text()
    assert "PENDÊNCIA RESIDUAL, de exatidão e não de conclusão" in provas
    assert "Movida para cá em 2026-10-29" in provas
    assert "Medidas em `findings/F007`.]**" in provas


@pytest.mark.semantico
def test_13_aplica_a_tabela1_em_ingles_e_concilia_com_o_original():
    """The Table 1 translation, approved and applied on 2026-11-09: translate
    it in full, preserving content, identifiers and classifications. Every
    verdict in that table is one of the author's formulations and four are
    corrections he imposed against readings of mine, so translating is
    restating them in another language and was his to approve.

    What the applied table must carry: the four binding formulations, in
    English and marked; the translation choices that change the weight of a
    sentence rather than its words; and H11a's subject, which the author
    settled by keeping the one the original explicitly identifies -- first
    person singular, "than I assumed". Not the subject-less "than was
    assumed", which erases it, and not "than we assumed", which infers it
    from the rest of the paper.

    The consolidator now emits the English table and RECONCILES it against
    the Portuguese original row by row, which is what makes "preserving
    identifiers and classifications" a check rather than a promise. This test
    exercises that reconciliation on a tampered copy, because the rule is
    worth nothing if it cannot refuse.
    """
    import re
    import shutil
    import subprocess
    import sys
    bruto = (RAIZ / "paper" / "13-tabela1.md").read_text()
    t = re.sub(r"\s+", " ", bruto)
    assert "APROVADA E APLICADA em 2026-11-09" in t
    # as quatro formulacoes vinculantes, em ingles
    assert "no tally, by construction" in t
    assert "defines no per-partition tally" in t
    assert "passed trivially and does not count as confirmation" in t
    assert "a narrow reading" in t
    # o sujeito de H11a: explicito, nem apagado nem inferido
    assert "the criterion covered less than I assumed" in t
    assert "the criterion covered less than was assumed:" not in t
    assert "than we assumed:" not in t
    # e as duas coisas que o autor precisa ver: e a unica primeira pessoa do
    # manuscrito, e a formulacao pre-registrada de H11a nao tem sujeito
    assert "única** forma de primeira pessoa" in t or \
           "única forma de primeira pessoa" in t
    assert "pre-registro-H10-H11.md:133" in t
    pre = (RAIZ / "docs" / "pre-registro-H10-H11.md").read_text()
    assert "A fração do decil de resíduo que cai" in pre
    assert "supus" not in pre
    # as vinte hipoteses, nenhuma perdida
    linhas = [l for l in bruto.split("## Table 1", 1)[1].splitlines()
              if l.startswith("| H")]
    assert len(linhas) == 20, len(linhas)
    # o consolidador le a tabela inglesa e declara de onde ela vem
    src = (RAIZ / "scripts" / "15_consolidar_manuscrito.py").read_text()
    assert 'TABELA1 = "13-tabela1.md"' in src
    assert 'ESTRUTURA = "00-estrutura.md"' in src
    assert "reconciled against" in src

    # e a conciliacao recusa uma tabela adulterada. Tres adulteracoes, uma
    # por regra, cada uma numa copia propria do repositorio de rascunhos.
    def _recusa(troca_de, troca_para, esperado, tmp):
        destino = tmp / "rascunhos"
        shutil.copytree(RAIZ / "paper", destino)
        alvo = destino / "13-tabela1.md"
        texto = alvo.read_text()
        assert texto.count(troca_de) == 1, troca_de
        alvo.write_text(texto.replace(troca_de, troca_para, 1))
        r = subprocess.run(
            [sys.executable, "scripts/15_consolidar_manuscrito.py",
             "--dir", str(destino), "--out", str(tmp / "saida")],
            cwd=RAIZ, capture_output=True, text=True)
        assert r.returncode != 0, "a adulteração passou: " + r.stdout[-400:]
        assert esperado in (r.stdout + r.stderr), r.stdout + r.stderr

    import tempfile
    with tempfile.TemporaryDirectory() as d1:
        _recusa("| H11a |", "| H11z |", "Identifiers", Path(d1))
    with tempfile.TemporaryDirectory() as d2:
        _recusa("| H11a | the residual decile leaves the plateau | "
                "supported, 5/5 |",
                "| H11a | the residual decile leaves the plateau | "
                "not supported, 5/5 |",
                "the verdict changed in translation", Path(d2))
    with tempfile.TemporaryDirectory() as d3:
        _recusa("| H11a | the residual decile leaves the plateau | "
                "supported, 5/5 |",
                "| H11a | the residual decile leaves the plateau | "
                "supported, 4/5 |",
                "the k/n ratio changed in translation", Path(d3))


@pytest.mark.estrutural
def test_codigo_de_saida_nao_contradiz_o_veredito_impresso():
    """Found in the author's run of 2026-11-02: 18_conformidade.py printed
    "DEFECT: 74 Portuguese marker(s)" and exited 0, because the exit code was
    gated on --strict. `echo $?` then reported "conformidade: 0" directly
    under the defect it had just printed.

    That is the same class of defect as the standard deviation this programme
    once printed as 0.0000 while computing a z from it: a display -- here the
    exit code, which is what automation reads -- hiding the quantity it
    reports on. A defect now fails with or without the flag, and --strict adds
    only the stricter condition: failing when a check could not be MADE, or
    when the reference list is merely incomplete, which is a state and not a
    defect.

    Exercised through the real entry points, because the bug was in main() and
    a test of the helpers would have passed throughout.
    """
    import subprocess
    import sys
    import tempfile
    # The defect is CONSTRUCTED. The first version of this test ran the
    # script on the real manuscript and asserted that a DEFECT was printed,
    # using the Portuguese Table 1 as its fixture; when the table was
    # translated on 2026-11-09 the defect went away and this test failed,
    # having been measuring the manuscript instead of the script. A test
    # about a verdict must be able to build the case it checks, which is why
    # 18_conformidade.py took a --src.
    with tempfile.TemporaryDirectory() as d:
        # Sem extensão de propósito: um literal em forma de arquivo
        # seria lido como fonte guardada e entraria na matriz de
        # rastreabilidade, que é o defeito que
        # test_16_nao_lista_como_fonte_o_que_nao_e_arquivo
        # existe para impedir -- e impediu, nesta mesma rodada.
        copia = Path(d) / "manuscrito_com_defeito"
        copia.write_text(
            (RAIZ / "paper" / "MANUSCRITO.md").read_text()
            + "\n## Seção de teste\n\nEsta seção está em português, com "
              "veredito, critério, hipótese e partição.\n")
        r = subprocess.run([sys.executable, "scripts/18_conformidade.py",
                            "--src", str(copia)],
                           cwd=RAIZ, capture_output=True, text=True)
        assert "DEFECT" in r.stdout, r.stdout[-600:]
        assert r.returncode == 1, (
            f"a printed DEFECT must not exit 0; got {r.returncode}")
        # e a mensagem nomeia o arquivo lido, nao o padrao
        assert "manuscrito_com_defeito:" in r.stdout
    # e o manuscrito de verdade esta limpo desde que a Tabela 1 foi traduzida
    rl = subprocess.run([sys.executable, "scripts/18_conformidade.py"],
                        cwd=RAIZ, capture_output=True, text=True)
    assert "DEFECT" not in rl.stdout, rl.stdout[-600:]
    assert rl.returncode == 0, rl.stdout[-600:]
    # and the two gates are documented as different, not as the same
    s18 = (RAIZ / "scripts" / "18_conformidade.py").read_text()
    assert "A DEFECT ALWAYS FAILS, with or without the flag" in s18
    assert "could not be made at all" in s18
    # The citation script. Its case is CONSTRUCTED too. The first version
    # asserted that the real run printed INCOMPLETO and exited 0 -- using the
    # state of the reference list as its fixture. When the list was completed
    # on 2026-11-09 that broke, having measured the paper and not the script.
    # Fifth occurrence of this class, and the reason --dir now exists.
    import shutil
    with tempfile.TemporaryDirectory() as d:
        copia = Path(d) / "rascunhos"
        shutil.copytree(RAIZ / "paper", copia)
        refs = copia / "12-referencias.md"
        # (a) incomplete is a STATE: no flag means 0, --strict means 1
        refs.write_text(refs.read_text().replace(
            "Status: **COMPLETO**", "Status: **INCOMPLETO**", 1))
        r17 = subprocess.run([sys.executable, "scripts/17_citacoes.py",
                              "--dir", str(copia)],
                             cwd=RAIZ, capture_output=True, text=True)
        assert "INCOMPLETO" in r17.stdout
        assert r17.returncode == 0
        r17s = subprocess.run([sys.executable, "scripts/17_citacoes.py",
                               "--strict", "--dir", str(copia)],
                              cwd=RAIZ, capture_output=True, text=True)
        assert r17s.returncode == 1
        # (b) a PROBLEM is a DEFECT: it fails with no flag at all
        n_wold = _num_ref("PLS-regression")
        refs.write_text(refs.read_text().replace(f"\n[{n_wold}] S. Wold",
                                                 "\n[99] S. Wold", 1))
        r17p = subprocess.run([sys.executable, "scripts/17_citacoes.py",
                               "--dir", str(copia)],
                              cwd=RAIZ, capture_output=True, text=True)
        assert "PROBLEM" in r17p.stdout, r17p.stdout[-400:]
        assert r17p.returncode == 1
    # e a lista real esta completa e consistente desde 2026-11-09
    rr = subprocess.run([sys.executable, "scripts/17_citacoes.py", "--strict"],
                        cwd=RAIZ, capture_output=True, text=True)
    assert "COMPLETO" in rr.stdout and "PROBLEM" not in rr.stdout
    assert rr.returncode == 0, rr.stdout[-400:]
    # but a PROBLEM there fails without the flag too
    s17 = (RAIZ / "scripts" / "17_citacoes.py").read_text()
    assert "if problemas:\n        return 1" in s17


def _tex_recem_construido(tmp):
    """Build the manuscript and its .tex into a directory of this test's own,
    and return the .tex text.

    Added 2026-11-02 after two tests failed in the author's run and passed in
    mine. They asserted on paper/MANUSCRITO.tex, which IS tracked in his
    repository and is NOT in mine: there the file exists and can be stale --
    pytest runs before the generator in any sensible command order -- and here
    it is absent, so the tests skipped or passed vacuously. The verification
    could not see the defect it was meant to catch.

    A test about what the converter produces must run the converter. This is
    the third time a test in this suite has been caught reading a generated
    file instead of generating it.
    """
    import subprocess
    import sys
    md = tmp / "manuscrito_temporario"
    tex = tmp / "tex_temporario"
    r = subprocess.run(
        [sys.executable, "scripts/15_consolidar_manuscrito.py",
         "--out", str(md)], cwd=RAIZ, capture_output=True, text=True)
    assert md.is_file(), r.stdout + r.stderr
    r = subprocess.run(
        [sys.executable, "scripts/19_tex.py", "--src", str(md),
         "--out", str(tex)], cwd=RAIZ, capture_output=True, text=True)
    assert tex.is_file(), r.stdout + r.stderr
    return tex.read_text()


def _mod19(nome: str = "19_tex.py"):
    import importlib.util
    cam = RAIZ / "scripts" / nome
    esp = importlib.util.spec_from_file_location("c19", cam)
    m = importlib.util.module_from_spec(esp)
    esp.loader.exec_module(m)
    return m


@pytest.mark.estrutural
def test_19_recusa_caractere_nao_mapeado_em_vez_de_emitir():
    """The LaTeX build maps every non-ASCII character explicitly and stops on
    one it does not know, in prose and inside a code span alike.

    The alternative is what a permissive converter does: pass the byte through
    and let pdfLaTeX fail at compile time, or worse, drop it. The manuscript
    carries Greek letters, superscripts, subscripts and five kinds of dash,
    and a converter that guesses at them produces a document that looks right
    and says something else -- 10^-6 and 10^6 differ by one character.

    Mapped runs of scripts become one group: "10⁻⁶" is $^{-6}$, not three.
    """
    m = _mod19("19_tex.py")
    assert m.inline("10⁻⁶") == "10$^{-6}$"
    assert m.inline("θ₀ = logit(s)") == "$\\theta$$_{0}$ = logit(s)".replace(
        "$$", "")
    assert m.inline("ρ and λ") == "$\\rho$ and $\\lambda$"
    for ruim in ("a ♣ b", "`a ♣ b`"):
        with pytest.raises(SystemExit) as e:
            m.inline(ruim, onde="test")
        assert "unmapped character" in str(e.value)
    # os especiais do LaTeX sao escapados antes de qualquer macro entrar
    assert m.inline("100% of a_b & c") == "100\\% of a\\_b \\& c"


@pytest.mark.estrutural
def test_19_pesa_colunas_pela_media_e_pela_palavra_mais_longa():
    """Column widths proportional to the LONGEST cell is the obvious rule and
    it is wrong. Table 1 has one cell of about four hundred characters: under
    that rule it took 83% of the line and the hypothesis labels were squeezed
    into a column one character wide, breaking "H7-shuffled" down the page.

    A column needs at least the width of its longest unbreakable word, and
    beyond that the mean cell is the honest measure of how much it carries.
    """
    import re
    m = _mod19("19_tex.py")
    linhas = ["| H7-shuffled | short | " + "x" * 400 + " |",
              "| --- | --- | --- |",
              "| H0 | tiny | " + "y" * 380 + " |"]
    tex = "\n".join(m.tabela(linhas, longa=False))
    # [pP]: desde 2026-11-10 as colunas de parágrafo saem como P{...}, o tipo
    # com \raggedright do preâmbulo. A fração é a mesma; o que mudou é que a
    # coluna deixou de ser justificada.
    fracoes = [float(x) for x in re.findall(r"[pP]\{([0-9.]+)\\linewidth\}", tex)]
    assert len(fracoes) == 3
    assert tex.count("P{") == 3, "as colunas de parágrafo devem sair sem justificação"
    assert fracoes[0] > 0.05, f"label column squeezed to {fracoes[0]}"
    assert fracoes[2] > fracoes[0]          # a coluna longa ainda e a maior
    assert sum(fracoes) < 0.95              # sobra para \tabcolsep
    assert "\\toprule" in tex and "\\midrule" in tex
    assert "|" not in tex.split("\\begin{tabular}", 1)[1].split("}", 1)[0]


@pytest.mark.semantico
def test_19_declara_o_que_falta_em_vez_de_disfarcar():
    """The reading copy must say what it is not. Three things are missing from
    a submission file and no converter can supply them: the title page, whose
    facts are the authors'; the reference list, which does not exist; and
    elsarticle.cls, which is not installed where this file is built, so a file
    written against it could not be compiled before delivery.

    Each is declared in the output -- the author block carries a visible
    placeholder, the reference section says the list does not exist yet and
    points at the audit, and the preamble says which class and why. A reader
    who finds no references must be able to tell a manuscript without them
    from a conversion that lost them.
    """
    m = _mod19("19_tex.py")
    assert "elsarticle" in m.PREAMBULO and "NOT THE SUBMISSION FILE" in m.PREAMBULO
    # Built here, from a manuscript consolidated here, so that the test does
    # not depend on a generated file in the repository being up to date --
    # which is how this very test failed in the clean clone.
    import subprocess
    import sys
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        md = Path(tmp) / "manuscrito_temporario"
        tex = Path(tmp) / "tex_temporario"
        r = subprocess.run(
            [sys.executable, "scripts/15_consolidar_manuscrito.py",
             "--out", str(md)], cwd=RAIZ, capture_output=True, text=True)
        assert md.is_file(), r.stdout + r.stderr
        r = subprocess.run(
            [sys.executable, "scripts/19_tex.py", "--src", str(md),
             "--out", str(tex)], cwd=RAIZ, capture_output=True, text=True)
        assert tex.is_file(), r.stdout + r.stderr
        t = tex.read_text()
    # A PÁGINA DE TÍTULO EXISTE desde 2026-11-10, fornecida pelo autor, e o
    # marcador que dizia que ela faltava tem de ter saído -- dizê-lo era
    # verdade e passaria a ser mentira. As duas pontas são conferidas: o
    # arquivo construído traz os autores e os ORCIDs, e a fonte do conversor
    # guarda o marcador para um manuscrito que ainda não os tenha.
    assert "Title page pending" not in t
    assert "Guilherme Coelho" in t and "Clarimar Jos" in t
    assert "0000-0003-3045-4057" in t and "0000-0002-5163-2986" in t
    assert "Corresponding author" in t
    s19_tp = (RAIZ / "scripts" / "19_tex.py").read_text()
    assert "Title page pending" in s19_tp
    # The reference list EXISTS from 2026-11-09, so the placeholder that said
    # it did not must be gone from the output -- saying so was right while it
    # was true and would be a lie now. The converter reads which of the two
    # is the case instead of being told, so both branches are checked: the
    # built file carries the entries, and the source still holds the honest
    # placeholder for a manuscript that has none.
    assert "no reference list yet" not in t
    assert "\\section*{References}" in t
    assert "Chemometrics and Intelligent Laboratory Systems 277 (2026) 105833" in t
    assert t.count("\\item ") >= 9
    s19 = (RAIZ / "scripts" / "19_tex.py").read_text()
    assert "The manuscript has no reference list yet." in s19
    assert "paper/12-referencias.md" in s19
    assert "\\begin{document}" in t and "\\end{document}" in t
    # e a Tabela 1 sai como esta, sem o conversor decidir a traducao
    assert "a converter is not the place" in t


@pytest.mark.estrutural
def test_15_carrega_o_titulo_do_artigo():
    """The consolidated manuscript had no title: its only top-level heading
    was the generator's own "Manuscript, consolidated". The title was settled
    on 2026-10-24 and lived only in 00-estrutura.md, which is apparatus and
    does not go to the journal.

    It is now read from that record's own Título block, from the first bold
    line -- not from the heading, which carries a version marker: the first
    reader took "[v2]" for the title and reported it as one word long.
    """
    import importlib.util
    cam = RAIZ / "scripts" / "15_consolidar_manuscrito.py"
    esp = importlib.util.spec_from_file_location("c15", cam)
    m15 = importlib.util.module_from_spec(esp)
    esp.loader.exec_module(m15)
    est = (RAIZ / "paper" / "00-estrutura.md").read_text()
    t = m15.titulo_do_artigo(est)
    assert t == ("When Spectral Attention Stability Reflects the Prior "
                 "Rather Than the Data")
    assert "[v2]" not in t and len(t.split()) > 3
    with pytest.raises(SystemExit):
        m15.titulo_do_artigo("# sem bloco de título algum\n")
    # and the consolidator really emits it -- checked on a manuscript built
    # here, not on the committed artefact, which may predate any change
    import subprocess
    import sys
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        md = Path(tmp) / "manuscrito_temporario"
        r = subprocess.run(
            [sys.executable, "scripts/15_consolidar_manuscrito.py",
             "--out", str(md)], cwd=RAIZ, capture_output=True, text=True)
        assert md.is_file(), r.stdout + r.stderr
        gerado = md.read_text()
    assert "## Title" in gerado and t in gerado


@pytest.mark.estrutural
def test_16_nao_lista_como_fonte_o_que_nao_e_arquivo():
    """The author's matrix of 2026-11-02 listed M.md as a guarded source in two
    rows. It was the name of a temporary file those tests wrote in order to
    build what they check -- not a repository file, and not something any test
    guards. (Written here without quotation marks on purpose: the extractor
    reads string literals from the whole source segment, docstring included,
    and the first version of this test cited the very name it forbids.)

    The matrix exists to say which repository files a test protects, so every
    cited name must be a tracked file or a declared build artefact. That rule
    lives HERE and not in the generator. It lived there for an afternoon, and
    it made the matrix depend on which build artefacts happened to be present:
    paper/MANUSCRITO.tex exists after a build and not in a fresh clone, so the
    same tests produced two different matrices and `--check` failed in a
    pristine checkout -- the one place it most needs to hold. The generator
    now lists what the tests cite, and this test says what they may cite.

    The rule also catches a mistyped path in a test that claims to guard a
    file which is not there, which would otherwise read as coverage. And one
    file is listed once: the same script cited as "17_citacoes.py" and as
    "scripts/17_citacoes.py" appeared twice in one row.
    """
    import ast as _ast
    import importlib.util
    cam = RAIZ / "scripts" / "16_matriz_rastreabilidade.py"
    esp = importlib.util.spec_from_file_location("m16b", cam)
    m16 = importlib.util.module_from_spec(esp)
    esp.loader.exec_module(m16)

    ARTEFATOS = {"MANUSCRITO.md", "MANUSCRITO.tex",
                 "matriz-rastreabilidade.md"}
    import subprocess
    r = subprocess.run(["git", "ls-files"], cwd=RAIZ,
                       capture_output=True, text=True)
    if r.returncode == 0:
        # Tracked files UNION what is on disk: a patch that adds a new paper
        # file leaves it untracked until the author commits, and the first
        # version of this guard failed on the very file the patch that
        # introduced it had just created.
        rastreados = {x.rsplit("/", 1)[-1] for x in r.stdout.split() if x}
        rastreados |= set(m16._arquivos_do_repositorio())
        for f in sorted((RAIZ / "tests").glob("test_*.py")):
            texto = f.read_text()
            for no2 in _ast.walk(_ast.parse(texto)):
                if not (isinstance(no2, _ast.FunctionDef)
                        and no2.name.startswith("test_")):
                    continue
                marcas = [d.attr for d in no2.decorator_list
                          if isinstance(d, _ast.Attribute)]
                if not any(c in marcas for c in
                           ("semantico", "estrutural", "numerico")):
                    continue
                for nome in m16.fontes_citadas(no2, texto):
                    base = nome.rsplit("/", 1)[-1]
                    assert base in rastreados or base in ARTEFATOS, (
                        f"{no2.name} cites {nome}, which is neither a tracked "
                        f"file nor a declared build artefact")

    fonte = (
        'def test_x():\n'
        '    b = "17_citacoes.py"\n'
        '    c = "scripts/17_citacoes.py"\n'
        '    d = "paper/02-resumo-C.md"\n')
    no = _ast.parse(fonte).body[0]
    fontes = m16.fontes_citadas(no, fonte)
    assert fontes.count("17_citacoes.py") == 1
    assert "scripts/17_citacoes.py" not in fontes      # a grafia mais curta
    assert "paper/02-resumo-C.md" in fontes            # a unica que aparece
    # e a matriz publicada nao lista fonte que nao seja arquivo. Só a TERCEIRA
    # coluna e lida: a segunda e a decisao, e a decisao deste teste cita
    # aquele nome entre aspas para registrar o defeito -- uma asserção sobre a
    # linha inteira acusaria o proprio registro do conserto.
    publicada = (RAIZ / "docs" / "matriz-rastreabilidade.md").read_text()
    for linha in publicada.splitlines():
        campos = [c.strip() for c in linha.split("|")]
        if len(campos) < 5 or campos[1].startswith(("---", "teste")):
            continue
        for nome in re.findall(
                r"[-\w./]+\.(?:md|py|toml|csv|json|npz|tex|bib)", campos[3]):
            base = nome.rsplit("/", 1)[-1]
            assert (base in m16._arquivos_do_repositorio()
                    or base in ARTEFATOS), (nome, linha[:80])


@pytest.mark.estrutural
def test_raiz_do_repositorio_nao_acumula_arquivo_solto():
    """Two files named `source` and `test` were committed to the repository
    root on 2026-11-02, swept in by `git add -A`. They are not in any patch
    this programme produced -- they came from a stray shell redirection -- and
    they entered the record of a scientific repository without anyone looking
    at them.

    The root of this repository holds a declared set: the README, the package
    configuration, the ignore file, and eight directories. Anything else at the
    top level is an accident until someone says otherwise, and an accident in
    a record whose point is traceability is worth one assertion.

    Adding a root entry on purpose means adding it here, which is the same
    rule the test categories and the consolidator's ORDEM follow: the set is
    declared, never inferred.
    """
    import subprocess
    ESPERADO = {
        ".gitignore", "README.md", "pyproject.toml",
        "data", "docs", "findings", "paper", "results", "scripts", "src",
        "tests",
    }
    # The INDEX, not HEAD: a file staged for the next commit is already on its
    # way into the record, and this catches it one step earlier. A file that is
    # merely present and untracked is not the repository's problem.
    r = subprocess.run(["git", "ls-files"],
                       cwd=RAIZ, capture_output=True, text=True)
    if r.returncode != 0:            # not a checkout: nothing to assert
        pytest.skip("not a git checkout")
    presentes = {x.split("/", 1)[0] for x in r.stdout.split() if x}
    sobra = presentes - ESPERADO
    assert not sobra, (
        f"files tracked at the repository root that are not declared: "
        f"{sorted(sobra)}. If one belongs there, add it to ESPERADO; if it is "
        f"an accident, `git rm --cached` it.")


@pytest.mark.semantico
def test_bib_so_tem_entrada_verificada_e_bibtex_nao_ve_o_resto():
    """paper/referencias.bib carries only what was read at a source, and the
    four groups that remain open must be invisible to bibtex.

    THE PER-CENT SIGN DOES NOT COMMENT IN BIBTEX. The first version of this
    file "commented out" the four stubs with a leading %, which is a LaTeX
    comment and nothing at all to bibtex: it read all four and emitted a
    bibitem for each with empty fields -- precisely the accident the stubs
    exist to prevent, committed in the act of preventing it. What bibtex looks
    for is the at-sign, so the stubs carry none.

    The same applies to prose: an at-sign anywhere outside an entry starts one.
    Three in the header of that first version produced three error messages in
    the bibtex log.

    So the check is mechanical: every at-sign in the file begins a verified
    entry, no entry body carries a FALTA marker, and the five verified keys
    agree with the records audited in 12-referencias.md.
    """
    import re
    bib = (RAIZ / "paper" / "referencias.bib").read_text()

    # toda arroba do arquivo abre uma entrada, e nao ha nenhuma na prosa
    arrobas = [m.start() for m in re.finditer(r"@", bib)]
    entradas = [m.start() for m in re.finditer(r"^@\w+\{", bib, re.M)]
    assert arrobas == entradas, (
        "an at-sign outside an entry: bibtex reads it as the start of one")
    # O numero total nao e fixado: ele cresce a cada escopo aprovado, e ja
    # quebrou este teste tres vezes. O que se exige e que a lista do .bib e a
    # do manuscrito tenham o mesmo tamanho -- um registro vivo aqui que nao
    # esteja la, ou o contrario, e o defeito que importa.
    import re as _re
    refs = (RAIZ / "paper" / "12-referencias.md").read_text()
    m = _re.search(r"^## References[ \t]*$", refs, _re.M)
    corpo = refs[m.end():]
    f = _re.search(r"^## ", corpo, _re.M)
    na_lista = _re.findall(r"^\[(\d+)\]\s+\S", corpo[:f.start()] if f else corpo,
                           _re.M)
    assert len(entradas) == len(na_lista), (
        f"{len(entradas)} entries in the .bib, {len(na_lista)} in the list")

    # nenhum corpo vivo carrega campo de preenchimento
    for m in re.finditer(r"^@(\w+)\{([^,]+),", bib, re.M):
        i = bib.index("{", m.start())
        nivel = 0
        for j in range(i, len(bib)):
            nivel += (bib[j] == "{") - (bib[j] == "}")
            if nivel == 0:
                break
        assert "[FALTA" not in bib[i:j + 1], m.group(2)

    # O que continua em aberto esta presente e sem a arroba. Tres dos quatro
    # grupos deixaram de estar em aberto em 2026-11-09: modalidades e
    # fundador foram lidos nos PDFs, e as bandas NIR ganharam fonte pela
    # lista de referencias do primeiro. Sobra o trabalho em submissao, cuja
    # citacao e decisao dos autores e nao foi tomada.
    assert re.search(r"^% \w+\{incerteza,", bib, re.M)
    for chave in ("modalidades", "fundador", "bandas-nir"):
        assert not re.search(rf"^% \w+\{{{re.escape(chave)},", bib, re.M), chave

    # as quatro novas, com a procedencia declarada em cada uma
    for chave in ("coelho2026pgsg", "coelho2027gatetopology",
                  "saranwong2004mango", "wold2001pls"):
        assert re.search(rf"^@\w+\{{{chave},", bib, re.M), chave
    # As cinco que nasceram de listas de referencias. Ate 2026-11-10 bastava
    # que dissessem SECOND-HAND PROVENANCE. A auditoria daquele dia conferiu
    # uma a uma e achou a saranwong ERRADA -- 253--261 contra as 137--145 que
    # o artigo tem --, de modo que o marcador generico foi substituido pelo
    # registro do que foi lido. O invariante que sobrevive, e que importa, e
    # mais forte: cada uma continua nomeando a lista de onde veio, e cada uma
    # que ainda tenha campo por ler diz OUTSTANDING em vez de calar.
    nascidas_de_lista = {
        "saranwong2004mango": "coelho2027gatetopology",
        "wold2001pls": "coelho2026pgsg",
        "anderson2020mango": "coelho2027gatetopology",
        "workman2012nir": "coelho2027gatetopology",
        "mcallester1999pacbayes": "Guedj",
    }
    for chave, origem in nascidas_de_lista.items():
        i = bib.index(chave)
        j = bib.index("\n}", i)
        # o .bib quebra as notas em varias linhas, entao o espaco e
        # normalizado antes de procurar qualquer frase
        corpo_entrada = re.sub(r"\s+", " ", bib[i:j])
        assert "note" in corpo_entrada, chave
        assert origem in corpo_entrada, f"{chave}: nao nomeia mais a origem"
        assert ("READ AT THE PUBLISHER" in corpo_entrada
                or "CONFIRMED" in corpo_entrada), chave
    # a saranwong carrega o registro corrigido, nao o herdado
    i = bib.index("saranwong2004mango")
    j = bib.index("\n}", i)
    assert "137--145" in bib[i:j] and "253--261" in bib[i:j], (
        "a entrada tem de trazer as paginas certas E dizer quais eram as "
        "erradas: um erro corrigido em silencio volta")
    assert "10.1016/j.postharvbio.2003.08.007" in bib[i:j]
    # e o que continua por ler diz OUTSTANDING. A saranwong saiu desta lista
    # em 2026-11-10: o unico campo que lhe faltava era o prenome dos autores,
    # e como NENHUMA fonte alcancavel imprime um -- todas dao J. Sornsrivichai
    # --, os prenomes foram reduzidos as iniciais em vez de escolhidos entre
    # duas grafias nao lidas. Nao sobra campo por ler, entao nao ha o que
    # declarar em aberto.
    # Na segunda passagem de 2026-11-10 a wold2001pls tambem saiu desta lista:
    # um terceiro catalogo reconfirmou volume, fasciculo, paginas, ano e DOI, e
    # os prenomes foram reduzidos as iniciais pela mesma razao da saranwong --
    # nenhuma fonte alcancavel imprime um. Sobra a anderson2020mango, cujo DOI
    # continua sem leitura e por isso continua declarado em aberto.
    # Em 2026-11-11 a anderson2020mango tambem saiu desta lista: o DOI, sua
    # ultima lacuna, foi RESOLVIDO -- doi.org redireciona para o PII que o
    # deposito dos autores da para o artigo. Nenhuma entrada carrega
    # OUTSTANDING agora, e o invariante passa a ser o mais forte dos dois:
    # nao que o que falta seja declarado, mas que nada falte.
    i = bib.index("anderson2020mango")
    j = bib.index("\n}", i)
    an = re.sub(r"\s+", " ", bib[i:j])
    assert "OUTSTANDING" not in an
    assert "THE DOI WAS RESOLVED" in an
    assert "the DOI was not read and is not written here" not in an
    for chave in ("saranwong2004mango", "wold2001pls"):
        i = bib.index(chave)
        j = bib.index("\n}", i)
        assert "OUTSTANDING" not in bib[i:j], (
            f"{chave} voltou a ter campo por ler; se for o caso, declare-o")
        assert "GIVEN NAMES REDUCED TO INITIALS" in re.sub(
            r"\s+", " ", bib[i:j]), chave
    # e as quatro lidas na fonte dizem onde foram lidas
    for chave, onde in (("jain2019attention", "ACL Anthology"),
                        ("adebayo2018sanity", "conference page"),
                        ("kuncheva2007stability", "author's own site"),
                        ("nogueira2018stability", "JMLR page"),
                        ("jaccard1912flora", "Read the article PDF"),
                        ("bartlett2002rademacher", "JMLR site"),
                        ("wilcoxon1945ranking", "scipy.stats.wilcoxon")):
        i = bib.index(chave)
        j = bib.index("\n}", i)
        assert onde in bib[i:j], chave
    # a Kuncheva e a antecedente, e o bib diz em que difere
    i = bib.index("kuncheva2007stability")
    j = bib.index("\n}", i)
    assert "E[r] = k^2/n" in bib[i:j]
    assert "same in kind, and differs in its argument" in bib[i:j]
    # o artigo do conjunto manga e o deposito sao registros distintos
    assert "anderson2024mango" in bib and "anderson2020mango" in bib
    # espaco normalizado: a nota quebra em varias linhas no .bib
    assert "different record from anderson2024mango" in re.sub(r"\s+", " ", bib)
    assert "10.1016/j.chemolab.2026.105833" in bib
    assert "10.1016/j.chemolab.2026.105926" in bib
    # e o corrigendum nao e entrada, porque o editor nao respondeu
    assert "corrigendum to coelho2026pgsg is NOT a reference" in bib
    # a unica entrada incompleta diz que e, e diz qual campo falta
    i = bib.index("kullback1951information")
    j = bib.index("\n}", i)
    # normalizado: o campo note e reenquadrado e a frase atravessa linhas
    kl = re.sub(r"\s+", " ", bib[i:j])
    # Ate 2026-11-10 esta entrada era a unica deliberadamente incompleta: o
    # Project Euclid recusava a leitura por verificacao de navegador e a faixa
    # de paginas nao estava escrita, porque escreve-la de memoria e exatamente
    # o que este programa proibe. Naquele dia o autor correspondente leu 79--86
    # no sumario do volume no JSTOR e conferiu contra outros indices, e o campo
    # entrou POR ESSA LEITURA. O invariante que sobrevive e mais forte que o
    # anterior: ou o campo falta, ou a nota diz quem o leu e onde.
    assert "pages = {79--86}" in kl   # kl vem com o espaco normalizado
    assert "INCOMPLETE ON PURPOSE" not in kl
    assert "THE PAGE RANGE WAS NOT READ" not in kl
    assert "SUPPLIED BY" in kl and "JSTOR" in kl

    # e as cinco verificadas batem com o registro da auditoria
    ref = (RAIZ / "paper" / "12-referencias.md").read_text()
    for doi in ("10.17632/46htwnp833.3", "10.1038/s41586-020-2649-2",
                "10.1016/j.measurement.2025.118884"):
        assert doi in bib and doi in ref, doi
    assert "2605.02003" in bib and "2605.02003" in ref
    assert "SubstrateMixRaman" in bib and "SubstrateMixRaman" in ref


@pytest.mark.estrutural
def test_19_numera_pela_profundidade_e_recusa_desencontro():
    """The numbers LaTeX prints must be the numbers the manuscript wrote.

    The manuscript writes 4.2, 4.2.1 and 4.3 all with three hashes, and the
    converter mapped hashes to levels: 4.2.1 became a subsection, LaTeX
    renumbered it 4.3, and every number after it shifted by one in every
    section that has a third level. The cross-references in the text are words
    -- "Section 4.3" -- not \\ref, so nothing complained: the document compiled
    and pointed the reader at the wrong subsection. The referee of 2026-11-02
    found it as a missing 4.2.1.

    The level now comes from the depth of the heading's own number, and the
    build simulates the counters and refuses when they disagree with what is
    written. A conversion that renumbers a manuscript in silence is worse than
    one that fails.
    """
    m = _mod19("19_tex.py")
    bom = [("4. T", ["### 4.1 a", "### 4.2 b", "### 4.2.1 c", "### 4.3 d"]),
           ("9. U", ["### 9.1 a", "### 9.2 b", "### 9.2.1 c", "### 9.3 d"])]
    assert m.confere_numeracao(bom) == []
    ruim = [("4. T", ["### 4.1 a", "### 4.3 b"])]          # salta 4.2
    assert m.confere_numeracao(ruim)
    ruim2 = [("4. T", ["### 4.1 a", "### 4.1.2 c"])]       # 4.1.1 esperado
    assert m.confere_numeracao(ruim2)
    # e o documento real traz os tres niveis como subsubsection -- construido
    # aqui, nao lido do artefato versionado, que pode estar velho
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        t = _tex_recem_construido(Path(tmp))
    assert t.count("\\subsubsection{") == 3, t.count("\\subsubsection{")


@pytest.mark.estrutural
def test_19_nao_leva_a_regua_do_markdown_para_a_legenda():
    """Figure 5's caption ended with a dash in the 31-page PDF. It was the
    Markdown rule "---" that separates the caption blocks, joined into the
    caption text along with the prose. The referee of 2026-11-02 saw it as a
    residual character, which is what it was.

    The rule lives in "19_tex.py", which is where the repair is."""
    import re
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        texto = _tex_recem_construido(Path(tmp))
    legendas = re.findall(r"\\caption\{(.*?)\}\n\\end\{figure\}",
                          texto, re.S)
    assert len(legendas) == 5
    for i, c in enumerate(legendas, 1):
        assert not c.rstrip().endswith("---"), f"Figure {i}"


@pytest.mark.semantico
def test_14_corrige_a_alegacao_causal_e_descreve_o_cruzamento():
    """The two scientific corrections of the 2026-11-02 referee report,
    approved by the author on 2026-11-09 and applied. Neither touches a
    number; both reduce a statement to what the design supports.

    FIRST: the Raman arm was called a control that isolates the prior, while
    Section 2.1 lists the dataset, the modality, the number of bands and the
    target as differing too -- and Section 7 itself states the condition that
    violates, "and nothing else does". It is now a check in a second
    modality, in all three places that claimed otherwise: the opening of
    Section 7, the close of 7.1, and Figure 4's caption. The three were found
    by reading, not by searching for one phrase, so the test checks all
    three.

    SECOND: Section 2.3 described two alternative configurations and said no
    penalty is applied under prior initialisation, while Section 3.1 reports
    rho across four orders of magnitude of lambda under that very
    initialisation -- which requires the penalty to be present. The sweep
    script's own --init flag confirms a crossing. The author's condition on
    the rewrite, checked here: the text must name the two crossed factors and
    must not suggest that only two configurations were evaluated.

    The superseded wording stays QUOTED in the record, so that what changed
    is legible without the git history, and absent from the drafts. Both are
    asserted: a record that keeps the old phrase and a draft that also keeps
    it would pass a test that only looked for the new one.
    """
    import re
    t = re.sub(r"\s+", " ", (RAIZ / "paper" / "14-parecer-2026-11-02.md"
                             ).read_text())
    assert "APROVADAS E APLICADAS em 2026-11-09" in t
    # o que era meu, e esta corrigido
    assert "era pior do que o parecer viu" in t
    assert "profundidade do número" in t
    # a prova interna das duas correcoes, preservada no registro
    assert "only the prior differs" in t and "and nothing else does" in t
    assert "no penalty is applied" in t
    assert "across four orders of magnitude of λ" in t
    assert "--init {prior, zero}" in t

    # Os rascunhos sao lidos com o espaco em branco normalizado: o texto e
    # reenquadrado em 79 colunas, e uma frase aprovada nao deixa de valer
    # porque passou a quebrar em outro ponto. A primeira versao deste teste
    # contou uma ocorrencia de duas por exigir a quebra de linha.
    def _texto(nome: str) -> str:
        # O marcador de citacao das legendas e retirado antes de normalizar:
        # sem isso, uma frase que atravessa duas linhas do bloco vira
        # "... a check in a > second modality ..." e nao casa.
        bruto = (RAIZ / "paper" / nome).read_text()
        bruto = re.sub(r"(?m)^>\s?", "", bruto)
        return re.sub(r"\s+", " ", bruto)

    # 1. os tres lugares do controle Raman
    s7 = _texto("04-rascunho-s6-s7-s8.md")
    assert "only the prior differs" not in s7
    assert "strongest control" not in s7
    assert "as Section 2.1 states" in s7
    assert s7.count("a check in a second modality") == 2
    assert "not an experiment that isolates it" in s7
    leg = _texto("06-legendas-figuras.md")
    assert "makes this a control and not a replication" not in leg
    assert "a check in a second modality rather than a replication" in leg

    # 2. a §2.3, com as duas exigencias do autor
    s2 = _texto("03-rascunho-s1-s2-s3.md")
    assert "no penalty is applied" not in s2
    assert "four configurations are trained and not two" in s2
    for fator in ("the **initialisation**", "the **penalty**"):
        assert fator in s2
    assert "`θ₀ = logit(s)` against `θ₀ = 0`" in s2
    assert "anchored at λ = 0" in s2
    # e a secao 3 continua falando dos dois papeis, que e o que ela mede
    assert "two ways" in s2 and "the two roles of the prior" in s2




@pytest.mark.estrutural
def test_artefato_versionado_nao_pode_ficar_desatualizado(tmp_path):
    """A generated file kept under version control can go stale, and a stale
    one is worse than an absent one: it reads as the manuscript.

    Measured on 2026-11-02: the committed "paper/MANUSCRITO.md" differed from
    a fresh build in 53 lines. It carried no title, no highlights, no
    keywords and the 304-word abstract -- every line the front matter added,
    missing. It went stale because generated files were deliberately kept out
    of the patches, after one of them made a patch inapplicable; nothing then
    noticed that the committed copy had stopped matching the drafts.

    So: an artefact this repository tracks must equal what the generator
    produces from the drafts as they stand, and the failure message names the
    command that repairs it. An artefact it does not track is outside the
    rule -- there is nothing to go stale -- and is declared in .gitignore so
    that a wildcard add does not put it back silently.

    WHAT THIS COMPARES is the file in the working tree, not the bytes at
    HEAD. Comparing HEAD would be the stricter reading of "committed", and it
    cannot pass: the repair regenerates the working tree, so the guard would
    stay red until the commit, and a patch whose own tests fail is not a
    patch. The defect this catches is drafts edited without rebuilding the
    artefact, which is what actually happened, and in that state the working
    tree and HEAD agree.
    """
    import subprocess
    import sys

    def rastreado(caminho: str) -> bool:
        r = subprocess.run(["git", "ls-files", "--error-unmatch", caminho],
                           cwd=RAIZ, capture_output=True, text=True)
        return r.returncode == 0

    r = subprocess.run(["git", "rev-parse", "--git-dir"], cwd=RAIZ,
                       capture_output=True, text=True)
    if r.returncode != 0:
        pytest.skip("not a git checkout: there is nothing tracked to compare")

    gi = (RAIZ / ".gitignore").read_text()

    # 1. the consolidated manuscript. The temporary file is given a name with
    # no extension on purpose: a file-shaped literal would be read as a
    # guarded source and listed in the traceability matrix, which is the
    # defect test_16_nao_lista_como_fonte_o_que_nao_e_arquivo exists to stop.
    if rastreado("paper/MANUSCRITO.md"):
        novo = tmp_path / "manuscrito_fresco"
        c = subprocess.run(
            [sys.executable, "scripts/15_consolidar_manuscrito.py",
             "--out", str(novo)], cwd=RAIZ, capture_output=True, text=True)
        assert novo.is_file(), c.stdout + c.stderr
        atual = (RAIZ / "paper" / "MANUSCRITO.md").read_text()
        assert atual == novo.read_text(), (
            "paper/MANUSCRITO.md is not what the drafts now produce. "
            "Repair: run scripts/15_consolidar_manuscrito.py and commit the "
            "result, or stop tracking the artefact with git rm --cached")
    else:
        assert "MANUSCRITO.md" in gi, (
            "paper/MANUSCRITO.md is untracked and .gitignore does not name "
            "it, so the next wildcard add tracks it again")

    # 2. the LaTeX reading copy. Pure output of the converter, rebuilt by
    # every adjustment to it, and its diff is read by nobody -- so the
    # repository holds the source and not this.
    assert not rastreado("paper/MANUSCRITO.tex"), (
        "paper/MANUSCRITO.tex is tracked. It is the converter's output and "
        "goes stale at every change to it: run git rm --cached "
        "paper/MANUSCRITO.tex")
    assert "MANUSCRITO.tex" in gi

    # 3. and a rule written twice is a rule that was edited once. The
    # results block for aggregate outputs appeared in duplicate.
    linhas = [x.strip() for x in gi.splitlines() if x.strip()
              and not x.strip().startswith("#")]
    assert len(linhas) == len(set(linhas)), (
        "duplicate pattern in .gitignore: " + ", ".join(
            sorted({x for x in linhas if linhas.count(x) > 1})))


@pytest.mark.numerico
def test_15_concilia_a_contagem_declarada_com_a_tabela1():
    """The manuscript said eight of twenty pre-registered hypotheses were not
    supported. The verdict column of Table 1 -- which the same sentence cites
    as the list of verdicts -- has six, and so do the pre-registrations. The
    number never matched: the commit that wrote "eight" already had six in
    the table.

    Resolved by the author on 2026-11-09, by the third route: the abstract
    says six, which is the literal count by the criterion and keeps it at 249
    words; and 2.6, which has no word limit and is where Table 1 is
    introduced, carries both counts -- the six the criterion did not support,
    and the two that met their criterion only formally (H5c) or on a narrow
    reading (H10b).

    So this is no longer a record of a discrepancy. It is the arithmetic: the
    number the text states is COUNTED from the table the consolidator emits,
    not written in here, so that editing one without the other fails.
    """
    import re

    def _vereditos(arquivo: str, cabecalho: str) -> list[tuple[str, str]]:
        texto = (RAIZ / "paper" / arquivo).read_text()
        assert cabecalho in texto, f"{arquivo}: Table 1's header moved"
        linhas = []
        for linha in texto[texto.index(cabecalho):].splitlines():
            if linha.startswith("|"):
                celulas = [c.strip() for c in
                           linha.strip().strip("|").split("|")]
                if not all(c.startswith("---") for c in celulas):
                    linhas.append(celulas)
            elif linhas:
                break
        return [(r[0], r[2]) for r in linhas[1:]]

    pt = _vereditos("00-estrutura.md",
                    "| | enunciado | veredito pelo critério | o que o "
                    "resultado sustenta |")
    en = _vereditos("13-tabela1.md",
                    "| | statement | verdict by the criterion | what the "
                    "result supports |")
    assert len(pt) == len(en) == 20

    nao_pt = [r for r, v in pt if v.lower().startswith("não suportada")]
    nao_en = [r for r, v in en if v.lower().startswith("not supported")]
    assert nao_pt == nao_en == ["H5a", "H7-blocks", "H8", "H9-blocks",
                                "H10a", "H13b"]
    assert len([v for _, v in pt if v.lower().startswith("suportada")]) == 14

    # as razoes k/n sao as mesmas nas duas linguas: traduzir nao mexe em
    # resultado, e uma divergencia aqui seria mais grave que a contagem
    for (rotulo, vpt), (_, ven) in zip(pt, en):
        assert (re.findall(r"\d+\s*/\s*\d+", vpt)
                == re.findall(r"\d+\s*/\s*\d+", ven)), rotulo

    # A ARITMETICA: o numero vem da contagem, nao esta escrito neste teste.
    NUMERAL = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five",
               6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten"}
    quantos = NUMERAL[len(nao_pt)]
    resumo = (RAIZ / "paper" / "02-resumo-C.md").read_text()
    assert f"{quantos} of which our criteria did not support" in resumo
    s2 = re.sub(r"\s+", " ",
                (RAIZ / "paper" / "03-rascunho-s1-s2-s3.md").read_text())
    assert f"{quantos.capitalize()} were not supported." in s2

    # e a 2.6 carrega a segunda contagem, com a tabela nomeada como o lugar
    # onde o veredito e a leitura aparecem juntos
    assert ("Two more met their criterion only formally or on a narrow "
            "reading, and Table 1 records both the verdict and that reading."
            ) in s2
    # As duas que a segunda contagem conta sao as que a tabela qualifica, e
    # a tabela e que diz quais: H5c pelo "(formal)" no veredito, H10b pela
    # leitura estreita na coluna de interpretacao. Nenhuma outra linha
    # carrega qualquer das duas marcas, e e isso que faz a contagem fechar
    # em duas em vez de ser um numero escrito aqui.
    tabela_en = (RAIZ / "paper" / "13-tabela1.md").read_text()
    fileiras = [[c.strip() for c in l.strip().strip("|").split("|")]
                for l in tabela_en.split("## Table 1", 1)[1].splitlines()
                if l.startswith("| H")]
    formais = [r[0] for r in fileiras if "(formal)" in r[2]]
    estreitas = [r[0] for r in fileiras if "narrow reading" in r[3]]
    assert formais == ["H5c"], formais
    assert estreitas == ["H10b"], estreitas
    assert len(formais) + len(estreitas) == 2

    # e o registro fica, com a medicao e a decisao
    nota = re.sub(r"\s+", " ",
                  (RAIZ / "paper" / "15-contagem-das-hipoteses.md").read_text())
    assert "RESOLVIDO em 2026-11-09" in nota
    for rotulo in nao_pt:
        assert rotulo in nota
    assert "H5c" in nota and "H10b" in nota
    assert "d407f3a" in nota


@pytest.mark.semantico
def test_12_mede_a_exposicao_ao_fundador_nao_corrigido():
    """The editor did not answer the letter about the corrigendum, so the
    founder stays published with the errors its authors have identified.
    Author's information of 2026-11-09. Two consequences, recorded.

    FIRST, it undoes a decision of his from the same day: the corrigendum
    cannot be a reference. An unanswered letter has no journal, volume, year
    or DOI, so "cite the corrigendum separately" is not executable as a
    numbered entry; if the manuscript mentions it, it does so in the text.
    That leaves ONE bibliographic record blocking --strict, not two.

    SECOND, the paper cites as the origin of its formulation a published work
    whose errors the record has not corrected. That is integrity, not
    bibliography, and it is the author's. What a test can hold is the
    MEASUREMENT of this paper's exposure, because that is what any of the
    three routes has to be decided against:

      - Tecator, where the mis-identified target column was found, appears
        nowhere in this repository. This paper's data are mango and
        bioprocess_substrates.
      - the one published figure this paper reproduces, 0.9418 falling to
        0.7005 +- 0.0068, is attributed by F004 to the ACCEPTED paper, not to
        the founder.
      - this paper's gate-prior correlations are its own measurement,
        recorded in F001 from this repository's lambda sweep, not a
        reproduction of a published value.

    And the ambiguity the news makes urgent: F004 calls q = 28 "the
    definition of the published code" while attributing 0.9418 to the
    accepted paper. Two published-or-accepted works exist in the programme
    and that phrase does not say which. The test holds the question open
    rather than letting a guess settle it.
    """
    import re
    t = re.sub(r"\s+", " ", (RAIZ / "paper" / "12-referencias.md").read_text())
    assert "O corrigendum não foi respondido" in t
    assert "deixa de ser entrada bibliográfica" in t
    assert "a correction has been submitted" in t
    assert "reduz o bloqueio do `--strict` a um registro só" in t
    for saida in ("**(a) Citar o fundador como publicado, com uma frase de "
                  "divulgação.**",
                  "**(b) Citar o fundador como publicado, sem comentário.**",
                  "**(c) Reduzir o que é atribuído ao fundador ao mínimo**"):
        assert saida in t, saida
    assert "nenhuma é minha" in t

    # a medicao, conferida contra o repositorio e nao contra o registro
    arquivos = (list((RAIZ / "paper").glob("*.md"))
                + list((RAIZ / "findings").glob("*.md"))
                + list((RAIZ / "docs").glob("*.md")))
    com_tecator = [f.name for f in arquivos
                   if "tecator" in f.read_text().lower()]
    assert com_tecator == ["12-referencias.md"], com_tecator
    f004 = (RAIZ / "findings"
            / "F004-estabilidade-interpretativa-e-funcao-dos-dados.md"
            ).read_text()
    assert "braço NIR do artigo aceito" in f004
    assert "J = 0,9418" in f004
    f001 = (RAIZ / "findings" / "F001-caminho-de-regularizacao.md").read_text()
    assert "ρ(gate, prior) vai de 0,9987 a 0,9999" in f001

    # e a ambiguidade de q = 28 fica registrada como aberta
    assert "o problema dos três destinos outra vez" in t
    assert "a definição do código publicado" in f004


@pytest.mark.semantico
def test_12_aplica_seis_das_sete_e_reenquadra_a_novidade():
    """Six of the seven proposed references, approved and applied on
    2026-11-09. G stayed out: the one-standard-error rule's canonical source
    is a textbook nobody here has read, and no field is written unread.

    The author attached a framing to the approval, and it is the point of
    the change rather than a side effect of it. Section 2.5 must say that
    correcting overlap for chance has antecedents, that q/(2L-q) is an
    approximation and not the exact Jaccard expectation, and that this
    paper's contribution is the exact expectation under plateau ties with
    the tie-breaking rule. Section 1 must present the novelty as a specific
    contribution about ties and quantisation, NOT as the discovery that
    chance correction is needed. Both are asserted here, including the
    negative: the sentence that would claim the discovery must not appear.

    Fifteen entries, fifteen cited, numbered by first appearance. Four of
    them -- [8], [12], [13], [15] -- were read in other papers' reference
    lists rather than in the articles, and the audit says so for each.
    """
    import re
    import subprocess
    import sys
    t = re.sub(r"\s+", " ", (RAIZ / "paper" / "12-referencias.md").read_text())
    s1 = re.sub(r"\s+", " ",
                (RAIZ / "paper" / "03-rascunho-s1-s2-s3.md").read_text())

    # a moldura da 2.5: antecedentes, aproximacao, e qual e a contribuicao
    assert ("Correcting set overlap for chance is established practice in the "
            "feature-selection literature.") in s1
    n_kun = _num_ref("Kuncheva")
    # Desde 2026-11-11 a citação é narrativa: o colchete deixou de ser o
    # complemento de "of" e o nome da autora ocupa o lugar. A atribuição é a
    # mesma e fica mais forte, porque o leitor vê de quem é o índice sem ter
    # de descer à lista.
    assert f"The consistency index of Kuncheva [{n_kun}]" in s1
    assert f"The consistency index of [{n_kun}]" not in s1
    assert "hypergeometric with expectation q²/L" in s1
    assert ("The point of this section is not that a correction is needed — "
            "that was settled —") in s1
    assert ("it is the Jaccard index evaluated at the hypergeometric mean "
            f"of Kuncheva [{n_kun}]") in s1

    # a moldura da 1: a novidade e empate e quantizacao, nao a correcao
    assert ("the need to do so is not new" in s1
            or "the need to do so is not\nnew" in s1)
    assert "has corrected set overlap for chance for nearly two decades" in s1
    assert ("What this paper adds is narrower and specific to the way a "
            "quantised prior is written down.") in s1
    assert "the gate inherits ties inside that block" in s1
    # e o que NAO pode aparecer: a descoberta da necessidade de corrigir
    for falso in ("we introduce a chance correction",
                  "no chance correction exists",
                  "the first to correct for chance"):
        assert falso.lower() not in s1.lower(), falso

    # as seis entraram, a G nao
    for autor in ("Jain", "Adebayo", "Kuncheva", "Nogueira", "Workman",
                  "Anderson"):
        assert autor in t, autor
    assert "one-standard-error" not in t.split("## References")[1][:4000]

    # todas citadas e numeradas por ordem de aparicao. O numero total nao e
    # fixado aqui: ele cresce a cada escopo que o autor aprova, e o que o
    # teste guarda e a consistencia, nao a contagem.
    r = subprocess.run([sys.executable, "scripts/17_citacoes.py", "--strict"],
                       cwd=RAIZ, capture_output=True, text=True)
    assert r.returncode == 0, r.stdout[-400:]
    assert "numbering in order of appearance, no missing field" in r.stdout

    # e a procedencia esta declarada entrada por entrada. Ate 2026-11-10 o
    # resumo dizia que cinco entradas vinham de listas de referencias; a
    # auditoria daquele dia conferiu as cinco uma a uma, corrigiu a saranwong
    # e passou a declarar, por entrada, o que foi lido e o que falta. O
    # invariante e que a secao exista e nomeie o que continua por ler.
    assert "Auditoria de 2026-11-10: o que mudou" in t
    # Ate 2026-11-11 esta secao listava o que faltava ler. A auditoria fechou
    # naquele dia e a lista desapareceu por estar vazia; o invariante que a
    # substitui e mais forte: o arquivo declara, explicitamente, que nao ha
    # campo pendente. Se algum voltar a faltar, isto falha.
    assert "não há campo pendente" in t
    # "Achieving robustness" e o ARTIGO do conjunto manga; o deposito de
    # dados e outra entrada e nao e de segundo grau.
    # Ate 2026-11-10 as cinco traziam o marcador generico **segundo grau**. A
    # auditoria daquele dia conferiu uma a uma e o marcador deu lugar ao
    # registro do que foi lido, onde, e do que falta -- o que e mais forte,
    # nao menos. O invariante que sobrevive: cada uma continua nomeando a
    # lista de onde nasceu, e nenhuma volta ao marcador generico sozinho.
    import re as _re2
    # t vem com o espaco normalizado, entao as ancoras de linha nao valem
    # nele: a tabela e lida do arquivo cru.
    # O arquivo tem DUAS tabelas com [n] na primeira coluna desde a auditoria
    # de 2026-11-10 -- a de procedencia e a do que continua por ler --, entao
    # guardam-se TODAS as linhas de cada numero e exige-se que ALGUMA declare
    # a leitura. Guardar so a ultima faria o teste ler a tabela errada.
    _cru = (RAIZ / "paper" / "12-referencias.md").read_text()
    linhas = {}
    for m in _re2.finditer(r"^\| \[(\d+)\] \| .*$", _cru, _re2.M):
        linhas.setdefault(m.group(1), []).append(m.group(0))
    for trecho in ("Achieving robustness", "Saranwong", "Workman",
                   "PLS-regression", "PAC-Bayesian model averaging"):
        n_ref = _num_ref(trecho)
        candidatas = linhas[n_ref]
        for linha in candidatas:
            assert linha.strip() != f"| [{n_ref}] | **segundo grau**", trecho
        assert any("lista de" in l or "lido" in l.lower()
                   or "confirmado" in l.lower() for l in candidatas), \
            f"{trecho}: nenhuma linha declara a leitura -> {candidatas}"


# ============================================================================
# Parecer de 2026-11-10. Seis itens científicos e a apresentação. Cada
# correção abaixo foi MEDIDA no código antes de ser escrita no texto: o
# tratamento de logit(1), a forma da penalidade e as duas forças sobre θ saem
# de `src/pgsg_3/m_model/pgsg_v3.py`, não de leitura do manuscrito.
# ============================================================================


@pytest.mark.semantico
def test_parecer1110_declara_o_tratamento_numerico_de_logit_e_da_kl():
    """Itens 2.1 e 2.2, ambos de prioridade alta.

    logit(1) não existe e o prior do NIR vale 1 em 34 bandas. O código resolve
    com `np.clip(s, 1e-6, 1 - 1e-6)`, em float64, e guarda θ em float32: isso
    põe a banda do platô em θ₀ = 13,8155 e em g₀ = 1 − 9,5e-7, de onde sai o
    σ′ ≈ 10⁻⁶ que a §3.1 relata. A §2.3 não declarava nada disso.

    A penalidade: a §2.3 dizia "summed over bands" e o código toma a MÉDIA
    (`termo.mean()`), com os dois argumentos sob o mesmo clip. A descrição
    estava errada, não apenas incompleta.
    """
    import re
    s2 = re.sub(r"\s+", " ", (RAIZ / "paper" / "03-rascunho-s1-s2-s3.md"
                              ).read_text())
    # o que o codigo faz, declarado no metodo
    assert "ε = 10⁻⁶" in s2
    assert "13.8155" in s2 and "1 − 9.5 × 10⁻⁷" in s2
    assert "double precision" in s2 and "single precision" in s2
    # a penalidade, com a reducao correta e explicita
    assert "averaged over bands" in s2
    assert "summed over bands" not in s2
    assert "reduced by the **mean** over the" in s2
    # o early stopping nao ve o termo KL
    assert "without the penalty term" in s2 or "with the penalty term excluded" in s2
    # a segunda forca sobre theta, que nao passa por sigma'
    assert "weight decay of 10⁻⁴" in s2
    assert "does not carry the `σ′` factor" in s2
    # e a §3.1 deixou de dizer que o gate comeca exatamente em 1
    assert "start at a gate value of 1 and stay there" not in s2
    assert "1 − 9.5 × 10⁻⁷ — the clip declared in Section 2.3" in s2


@pytest.mark.estrutural
def test_parecer1110_a_forma_da_kl_declarada_e_a_do_codigo():
    """A equação escrita na §2.3 tem de ser a que o código avalia. Este teste
    não lê o texto: avalia `kl_bernoulli_np` e a fórmula do manuscrito nos
    mesmos vetores e exige igualdade. Se alguém trocar soma por média em um
    dos dois lados, isto falha.
    """
    np = pytest.importorskip("numpy")
    import importlib.util
    caminho = RAIZ / "src" / "pgsg_3" / "m_model" / "pgsg_v3.py"
    fonte = caminho.read_text()
    # a funcao nao depende de torch nem de pgsg_1: e extraida e avaliada so.
    import re as _re
    m = _re.search(r"_EPS = ([0-9eE.\-]+)", fonte)
    eps = float(m.group(1))
    assert eps == 1e-6, "a §2.3 declara ε = 10⁻⁶"
    corpo = _re.search(r"def kl_bernoulli_np.*?\n\n", fonte, _re.S).group(0)
    ns = {"np": np, "_EPS": eps}
    exec("import numpy as np\n" + corpo, ns)
    rng = np.random.default_rng(7)
    for _ in range(5):
        p = 281
        g = rng.random(p)
        s = rng.random(p)
        s[:34] = 1.0                      # o platô, que é o caso que importa
        gc = np.clip(g, eps, 1 - eps)
        sc = np.clip(s, eps, 1 - eps)
        manuscrito = float(np.mean(gc * np.log(gc / sc)
                                   + (1 - gc) * np.log((1 - gc) / (1 - sc))))
        assert abs(ns["kl_bernoulli_np"](g, s) - manuscrito) < 1e-12


@pytest.mark.semantico
def test_parecer1110_c1_usa_a_desigualdade_estrita():
    """Item 2.6. O título do C1 e a tabela da §4.4 já diziam "plateau > q"; só
    o corpo dizia "whenever L ≥ q". Com L = q o platô inteiro é selecionado e
    a fronteira cai fora dele, de modo que nenhum empate precisa ser desfeito
    — que é justamente a condição que o C1 existe para enunciar.
    """
    import re
    for nome in ("01-rascunho-resumo-e-s4.md", "03-rascunho-s1-s2-s3.md",
                 "04-rascunho-s6-s7-s8.md", "05-rascunho-s9-s10-s11.md"):
        t = (RAIZ / "paper" / nome).read_text()
        assert "L ≥ q" not in t, nome
        assert "L >= q" not in t, nome
    s4 = re.sub(r"\s+", " ", (RAIZ / "paper" / "01-rascunho-resumo-e-s4.md"
                              ).read_text())
    assert "subset of the plateau whenever L > q" in s4
    assert "The inequality is strict because at L = q" in s4


@pytest.mark.semantico
def test_parecer1110_retira_a_equivalencia_de_r2_fora_do_alcance():
    """Item 2.3. A §9.1 dizia que o R² é equivalente "in both modalities",
    enquanto a §10 — e o próprio `scripts/07_raman_lambda1.py`, que imprime
    "R2 is not reported for that reason" — dizem que o Raman não tem R² de
    teste. Não era exagero de linguagem: era uma afirmação sobre uma grandeza
    que o artigo não possui. E não há teste de equivalência com margem.
    """
    import re
    s9 = re.sub(r"\s+", " ", (RAIZ / "paper" / "05-rascunho-s9-s10-s11.md"
                              ).read_text())
    assert "held-out R² is equivalent across the whole range of λ, in both modalities" not in s9
    # SUPERSEDIDO no mesmo dia: a redação que eu havia escrito deu lugar à do
    # autor, verbatim, que evita também a alegação por tamanho de treino. O
    # conteúdo é asseverado em test_decisao1110_nenhum_r2_por_tamanho_de_treino.
    assert "does not constitute a formal equivalence test" in s9
    assert "predictive equivalence cannot be assessed from held-out R²" in s9
    # a §9.4 carregava a mesma alegacao e foi corrigida junto
    assert "equivalent between the two across the λ grid, both modalities" not in s9
    assert "the Raman arm reports no held-out R² at all" in s9
    # e a §10, que e a fonte da contradicao, continua dizendo o que dizia
    assert "Held-out R² is therefore not reported for that modality" in s9


@pytest.mark.semantico
def test_parecer1110_rademacher_e_fechamento_da_71():
    """Itens 2.4 e 2.5. Os dois trechos eram de minha redação.

    §11: ajustar rótulos aleatórios com um otimizador mede memorização e
    alcançabilidade; não estima a complexidade de Rademacher empírica, que é
    um supremo sobre uma classe. §7.1: o fechamento afirmava propriedade do
    prior contra propriedade do método, o que a comparação entre modalidades
    não isola — os braços também diferem em dados, dimensão e alvo.

    A frase "a check in a second modality" é a correção que o autor aprovou em
    2026-11-09 e permanece nos dois lugares: o parecer de 2026-11-10 pediu a
    retirada da cláusula causal, não dela.
    """
    import re
    s11 = re.sub(r"\s+", " ", (RAIZ / "paper" / "05-rascunho-s9-s10-s11.md"
                               ).read_text())
    assert "estimate the empirical Rademacher complexity of the two function classes" not in s11
    assert "not an estimate of the empirical Rademacher complexity" in s11
    assert "is the supremum of a signed average over a class" in s11
    assert "memorise an uninformative target" in s11

    s7 = re.sub(r"\s+", " ", (RAIZ / "paper" / "04-rascunho-s6-s7-s8.md"
                              ).read_text())
    assert "the behaviour is a property of how the prior was written down" not in s7
    assert ("the between-modality comparison does not isolate the effect of "
            "the prior's functional form") in s7
    assert s7.count("a check in a second modality") == 2


@pytest.mark.estrutural
def test_parecer1110_figuras_entram_na_escala_em_que_foram_desenhadas():
    """Apresentação. `width=\\linewidth` em todas as cinco ampliava as três
    estreitas em 1,43x a 1,93x: o mesmo rótulo de 7pt saía a 7pt numa figura e
    a 13pt noutra, e a menor delas foi a que o parecerista leu como ilegível.
    Agora cada figura entra no tamanho em que foi desenhada, e só é reduzida
    se transbordar.
    """
    t = (RAIZ / "scripts" / "19_tex.py").read_text()
    assert "\\\\figuranatural" in t or "figuranatural" in t
    assert "includegraphics[width=\\\\linewidth]{%s}" not in t
    assert "\\newsavebox{\\caixafigura}" in t
    # a reducao continua existindo para o caso de transbordo
    assert "\\ifdim\\wd\\caixafigura>\\linewidth" in t
    # e as colunas de paragrafo deixaram de ser justificadas
    assert "\\newcolumntype{P}[1]{>{\\raggedright\\arraybackslash}p{#1}}" in t
    assert "\\usepackage{array,booktabs,longtable}" in t


@pytest.mark.estrutural
def test_parecer1110_figura3_nao_se_redesenha_em_outro_ambiente():
    """O painel (b) da Figura 3 é específico do ambiente POR CONSTRUÇÃO: o
    decil cai dentro do platô empatado e quem decide o conjunto é a ordem de
    desempate do `numpy.argsort`. Em 2026-11-10 um redesenho num contêiner
    produziu 0,7443-0,7659 no lugar dos 0,9452-0,9867 publicados e teria
    sobrescrito a figura em silêncio — que é a classe de defeito deste
    programa: tratar artefato gerado como se fosse reprodução.

    A trava recusa a sobrescrita; a figura entregue continua sendo a medida.
    """
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "figs1110", RAIZ / "scripts" / "10_figuras.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    assert m.FIG3B_PUBLICADO == (0.9452, 0.9867)
    fonte = (RAIZ / "scripts" / "10_figuras.py").read_text()
    assert "permitir_redesenho" in fonte
    # desde a decisão do autor de 2026-11-10 a trava é um auxiliar partilhado
    # com a Figura 2; a mensagem e a condição vivem nele.
    assert "redrawing would replace the " in fonte
    assert "measurement rather than reproduce it" in fonte
    assert "fora and alvo.exists() and not permitir_redesenho" in fonte


@pytest.mark.semantico
def test_parecer1110_o_registro_existe_e_declara_o_que_ficou_pendente():
    """O parecer de 2026-11-02 tem registro em `14-parecer-2026-11-02.md`; o
    de 2026-11-10 tem o seu. O registro existe para que o que mudou seja
    legível sem o histórico do git, e para que o que NÃO foi aplicado não se
    perca: três pontos aguardam o autor.

    O quase-acidente da Figura 3 fica registrado com os dois números, porque
    um erro evitado que não é escrito volta a acontecer.
    """
    import re
    t = re.sub(r"\s+", " ", (RAIZ / "paper" / "17-parecer-2026-11-10.md"
                             ).read_text())
    assert "APROVADO PELO AUTOR EM 2026-11-10, COM TRÊS AJUSTES FINAIS" in t
    # a quarta rodada do mesmo dia: a ressalva do "cost being nil" e a
    # auditoria bibliografica, com o erro que ela achou
    assert "Quarta rodada, 2026-11-10" in t
    assert "253–261" in t and "31(2), 137–145" in t
    assert "A numeração das referências **não mudou**" in t
    # a quinta rodada: Kullback completa e os prenomes nao lidos removidos
    assert "Quinta rodada" in t
    assert "Sexta rodada" in t and "10.1145/307400.307435" in t
    assert "é precisamente por ser fácil que não foi escrito" in t
    assert "a auditoria bibliográfica fecha" in t
    assert "Um campo certo pelo motivo errado" in t
    assert "79–86" in t
    assert "Um prenome plausível é mais perigoso que uma inicial" in t
    import re as _re3
    assert "21 entradas, 21 citadas, em ordem de primeira aparição" in _re3.sub(r"\s+", " ", t)
    # os numeros medidos, nao recontados de memoria
    assert "13,815509796142578" in t and "9,536734 × 10⁻⁷" in t
    assert "weight_decay = 1e-4" in t and "1,4 × 10⁻³" in t
    # o quase-acidente, com as duas faixas
    assert "0,7443–0,7659" in t and "0,9452–0,9867" in t
    # e a base declarada da rodada
    assert "e98726474af6c59a864f8e9be0ff3d1f76993116" in t
    assert "## Pendente" in t and "Ajustes finais do autor, 2026-11-10" in t


# ============================================================================
# Decisões do autor de 2026-11-10, sobre o parecer do mesmo dia.
# ============================================================================


@pytest.mark.semantico
def test_decisao1110_qualifica_a_31_sem_atribuir_ao_sigma_sozinho():
    """O autor exigiu a qualificação e deu a redação. O argumento original
    atribuía a imobilidade do platô à saturação da sigmoide; o decaimento
    chega a θ sem o fator σ′, de modo que a persistência é propriedade do
    procedimento inteiro.

    A redação do autor entra verbatim. O que foi acrescentado é o limite da
    leitura: o que se observa persistir é o GATE, e gate imóvel não é prova de
    parâmetro imóvel — distinção que o próprio autor levantou.
    """
    import re
    s3 = re.sub(r"\s+", " ", (RAIZ / "paper" / "03-rascunho-s1-s2-s3.md"
                              ).read_text())
    # a redacao do autor, literal
    assert ("The prior-initialised plateau begins in a numerically saturated "
            "region of the sigmoid") in s3
    assert ("introducing an additional contribution to parameter updates that "
            "is not attenuated by the sigmoid derivative") in s3
    assert ("an empirical property of the complete optimisation procedure, "
            "rather than a consequence of sigmoid saturation alone") in s3
    # a alegacao anterior saiu
    assert "The parameters are free in the class and unreachable by the optimiser" not in s3
    # e a distincao gate/parametro ficou escrita
    assert "what we observe to persist is the gate" in s3
    assert "is not by itself evidence that its parameter cannot" in s3


@pytest.mark.semantico
def test_decisao1110_declara_a_forma_acoplada_sem_alegar_razao_no_passo():
    """A objeção do autor: com momentos adaptativos não se compara o termo de
    decaimento ao gradiente dos dados para concluir influência na atualização.
    Procedente — o "1450x" saiu, e a §2.3 passa a dizer de que fala.

    O teste também fixa a implementação exata, que foi a verificação
    obrigatória do item 5: `torch.optim.Adam`, L2 ACOPLADO.
    """
    import re
    s2 = re.sub(r"\s+", " ", (RAIZ / "paper" / "03-rascunho-s1-s2-s3.md"
                              ).read_text())
    assert "The decay is coupled, in the sense that `torch.optim.Adam` adds the L2 term to the gradient before the adaptive moments normalise it" in s2
    assert "design variable and not an implementation detail" in s2
    assert "We state this of the gradient and not of the update" in s2
    assert "does not carry over to the ratio of their effects on the step" in s2
    # e o codigo tem de continuar sendo o que o texto declara
    fonte = (RAIZ / "src" / "pgsg_3" / "m_model" / "pgsg_v3.py").read_text()
    assert 'cls = torch.optim.Adam if self.optimizer == "adam" else torch.optim.AdamW' in fonte
    assert 'optimizer: str = "adam"' in fonte


@pytest.mark.estrutural
def test_decisao1110_a_condicional_da_91_e_sustentada_pelos_dados():
    """O autor condicionou a §9.1: *"se houver configurações com perda
    relevante, essa primeira frase deverá ser restringida"*. Este teste não lê
    o texto — abre os agregados do NIR e exige que a condição valha.

    Critério: a amplitude de R² ao longo de λ não excede o espalhamento
    típico entre sementes, e o máximo NÃO está em λ = 0 (não há deterioração
    monotônica ao ligar a penalização).
    """
    import csv
    for nome in ("sweep_nir", "sweep_nir_init0"):
        caminho = RAIZ / "results" / nome / "agregado.csv"
        if not caminho.exists():
            pytest.skip(f"{nome} ausente neste ambiente")
        rs = list(csv.DictReader(caminho.open()))
        r2 = [float(r["r2_media"]) for r in rs]
        sd = [float(r["r2_sd"]) for r in rs]
        amplitude = max(r2) - min(r2)
        tipico = sum(sd) / len(sd)
        assert amplitude <= 2 * tipico, (
            f"{nome}: amplitude {amplitude:.4f} contra sd típico "
            f"{tipico:.4f} — a §9.1 teria de ser restringida")
        lam = [float(r["lam"]) for r in rs]
        assert lam[r2.index(max(r2))] != 0.0, (
            f"{nome}: o máximo de R² está em λ = 0, o que seria deterioração "
            "monotônica ao ligar a penalização")


@pytest.mark.semantico
def test_decisao1110_nenhum_r2_por_tamanho_de_treino_e_nenhuma_alegacao_dele():
    """Medido em 2026-11-10: NENHUM csv deste repositório tem R² indexado por
    tamanho de treino. Todo arquivo com `r2` é indexado por λ; as sete frações
    estão em `gate_metrics.csv`, que não tem coluna de R².

    Logo a alegação "equivalente nas sete frações" nunca teve dado por trás, e
    o texto não pode voltar a fazê-la. Este teste guarda as duas pontas: o
    dado e a afirmação.
    """
    import csv
    gm = RAIZ / "data" / "processed" / "gates_r2" / "gate_metrics.csv"
    if gm.exists():
        colunas = next(csv.reader(gm.open()))
        assert not [c for c in colunas if "r2" in c.lower()], \
            "gate_metrics.csv passou a ter R²; a §9.1 pode ser reexaminada"
    import re
    s9 = re.sub(r"\s+", " ", (RAIZ / "paper" / "05-rascunho-s9-s10-s11.md"
                              ).read_text())
    # a redacao do autor, verbatim
    assert ("Within the near-infrared experiments, the evaluated configurations "
            "showed no material deterioration in the reported predictive "
            "performance measures across the examined regularisation "
            "settings") in s9
    assert "This observation is descriptive and does not constitute a formal equivalence test" in s9
    assert "the available data do not support the required batch-aware evaluation" in s9
    # e nenhuma alegacao de R2 por tamanho de treino sobrou
    assert "No R² is reported by training size" in s9
    assert "across the λ grid and the seven training sizes" not in s9


@pytest.mark.semantico
def test_decisao1110_a_lacuna_do_controle_de_otimizador_esta_declarada():
    """Medido: `ctl_adam`, `ctl_adamw` e `ctl_piloto` rodaram só com
    `init=zero`, onde não se forma platô. Não há neste repositório nenhum dado
    sobre decaimento acoplado contra desacoplado SOB SATURAÇÃO — que é o braço
    em que o platô persiste.

    Isso torna a ablação a única fonte possível para explicação causal, e tem
    de estar declarado onde o leitor procura: limitação na §10, experimento na
    §11, e remissão na §3.1.
    """
    import csv
    for nome in ("ctl_adam", "ctl_adamw"):
        caminho = RAIZ / "results" / nome / "aggregate.csv"
        if not caminho.exists():
            continue
        inits = {r["init"] for r in csv.DictReader(caminho.open())}
        assert inits == {"zero"}, (
            f"{nome} passou a ter init={inits - {'zero'}}; a §10 e a §11 "
            "precisam ser reexaminadas")
    import re
    s = re.sub(r"\s+", " ", (RAIZ / "paper" / "05-rascunho-s9-s10-s11.md"
                             ).read_text())
    assert "The optimiser control does not cover the saturated arm" in s
    assert "was run from θ₀ = 0 only, where no plateau forms" in s
    assert "Weight decay on the gate logits, with the prior in the initialisation" in s
    s3 = re.sub(r"\s+", " ", (RAIZ / "paper" / "03-rascunho-s1-s2-s3.md"
                              ).read_text())
    assert "the ablation named in Section 11, which we did not run" in s3


@pytest.mark.estrutural
def test_decisao1110_a_trava_cobre_a_figura_2_tambem():
    """O autor pediu a proteção para todas as figuras dependentes de
    ordenação. Medido: a Figura 2 plota a mesma `jaccard_sort` do painel (b) da
    Figura 3 e calcula os mesmos 0,7443-0,7659 neste ambiente — corria risco
    idêntico e estava sem trava.

    As Figuras 1, 4 e 5 ficam fora por medição: a 5 lê células e reporta
    correlação de postos sobre valores de gate, sem seleção top-q.
    """
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "figs1110b", RAIZ / "scripts" / "10_figuras.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    assert m.JACCARD_SORT_PUBLICADO == (0.9452, 0.9867)
    assert m.FIG3B_PUBLICADO == m.JACCARD_SORT_PUBLICADO   # nome anterior vivo
    assert callable(m.exigir_faixa_publicada)

    # a trava recusa quando a faixa divirja E a figura exista
    import inspect
    from pathlib import Path as _P
    assinatura = inspect.signature(m.figura2).parameters
    assert "permitir_redesenho" in assinatura, \
        "figura2 sem a trava: plota jaccard_sort e corre o mesmo risco"
    fonte = (RAIZ / "scripts" / "10_figuras.py").read_text()
    assert fonte.count("exigir_faixa_publicada(") == 3   # def + figura2 + figura3
    assert "figura2(dados, out, q, a.permitir_redesenho_fig3)" in fonte


@pytest.mark.semantico
def test_ajustes_finais_1110_tiram_as_tres_alegacoes_excessivas():
    """Os três ajustes do autor sobre o patch aprovado, mais a gêmea que ele
    não nomeou.

    §3.1 se contradizia com a §2.3: dizia que o gradiente de QUALQUER perda
    carrega σ′, depois de o artigo passar a demonstrar que o termo L2 não
    carrega. §9.1 afirmava que nada está sendo trocado, o que a ausência de
    deterioração observada não demonstra — e repetia a alegação duas sentenças
    adiante, em forma mais forte. §11 sustentava acurácia nas sete frações num
    dado que este repositório não tem.
    """
    import re
    s3 = re.sub(r"\s+", " ", (RAIZ / "paper" / "03-rascunho-s1-s2-s3.md"
                              ).read_text())
    assert "The gradient of any loss with respect to θ carries a factor" not in s3
    assert "Gradients propagated through the sigmoid gate carry a factor σ′(θ) = g(1 − g)" in s3

    s9 = re.sub(r"\s+", " ", (RAIZ / "paper" / "05-rascunho-s9-s10-s11.md"
                              ).read_text())
    assert "Within that scope, nothing is being traded" not in s9
    assert ("Within the evaluated near-infrared configurations, changes in gate "
            "stability were not accompanied by a consistent deterioration in "
            "the reported predictive performance") in s9
    # a gemea, que repetia a alegacao em forma mais forte
    assert "a stability that does not affect predictive risk" not in s9
    assert "a stability whose predictive cost we did not detect in these configurations" in s9

    # §11: nenhuma alegacao de acuracia por fracao, aqui ou em qualquer rascunho
    assert "The prior does not improve accuracy at any of seven training sizes" not in s9
    assert "Whether the prior improves accuracy at small training sizes is a question this paper does not answer" in s9
    for nome in ("01-rascunho-resumo-e-s4.md", "03-rascunho-s1-s2-s3.md",
                 "04-rascunho-s6-s7-s8.md", "05-rascunho-s9-s10-s11.md",
                 "02-resumo-C.md", "08-rascunho-s5.md"):
        t = (RAIZ / "paper" / nome).read_text()
        assert "improve accuracy at" not in t, nome
        assert "improves accuracy at any" not in t, nome


@pytest.mark.semantico
def test_auditoria_bib_1110_nenhuma_alegacao_de_custo_nulo_sobrou():
    """A ressalva do autor sobre *"the evidence for the cost being nil"*, e as
    duas gêmeas que o mesmo excesso tinha em outros lugares.

    "Custo nulo" afirma ausência de custo, que os resultados não demonstram.
    O manuscrito inteiro passa a dizer o que foi observado — ausência de
    deterioração material nas configurações avaliadas — sem estabelecer
    equivalência. Este teste varre TODOS os rascunhos, porque a mesma frase
    reapareceu em três lugares diferentes ao longo da revisão.
    """
    import re
    import glob
    for caminho in sorted(glob.glob(str(RAIZ / "paper" / "0*.md"))):
        t = re.sub(r"\s+", " ", open(caminho).read())
        nome = caminho.rsplit("/", 1)[-1]
        for excesso in ("the cost being nil",
                        "costs nothing in predictive performance",
                        "Within that scope, nothing is being traded",
                        "a stability that does not affect predictive risk"):
            assert excesso not in t, f"{nome}: {excesso!r}"
    s9 = re.sub(r"\s+", " ", (RAIZ / "paper" / "05-rascunho-s9-s10-s11.md"
                              ).read_text())
    assert ("which supports the absence of a material predictive deterioration "
            "in the evaluated configurations, without establishing "
            "equivalence") in s9
    s3 = re.sub(r"\s+", " ", (RAIZ / "paper" / "03-rascunho-s1-s2-s3.md"
                              ).read_text())
    assert ("showed no material predictive deterioration in the configurations "
            "we evaluated") in s3
    assert "without establishing equivalence" in s3


@pytest.mark.semantico
def test_auditoria_bib_1110_saranwong_corrigida_e_sem_prenome_inventado():
    """A auditoria de 2026-11-10 achou um erro real: a [13] trazia 253--261,
    copiado da lista de referências de [4]. O artigo é 31(2), 137--145. Não é
    detalhe de estilo — é a citação que sustenta as três janelas NIR, e teria
    ido ao periódico apontando páginas que não existem nesse artigo.

    A faixa corrigida foi reconferida num segundo índice independente. Os
    prenomes foram reduzidos às iniciais porque nenhuma fonte alcançável
    imprime um: a escolha entre *Jingtair* e *Jinda* seria um campo escrito
    sem leitura, que é exatamente o que este programa proíbe.
    """
    bib = (RAIZ / "paper" / "referencias.bib").read_text()
    inicio = bib.index("@article{saranwong2004mango")
    entrada = bib[inicio:bib.index("\n}", inicio)]
    assert "pages   = {137--145}" in entrada
    assert "253--261" not in entrada.split("note")[0], \
        "a faixa errada voltou ao registro"
    assert "number  = {2}" in entrada
    assert "doi     = {10.1016/j.postharvbio.2003.08.007}" in entrada
    # nenhum prenome: so iniciais, que e o que as fontes imprimem
    assert "Sornsrivichai, J." in entrada
    for inventado in ("Jingtair,", "Jinda,", "Sirinnapa", "Sumio"):
        assert inventado not in entrada.split("note")[0], \
            f"{inventado}: prenome não lido voltou ao campo author"
    # e a lista numerada carrega a mesma faixa
    lista = (RAIZ / "paper" / "12-referencias.md").read_text()
    assert "31 (2) (2004) 137–145" in lista
    assert "(2004) 253–261" not in lista


@pytest.mark.semantico
def test_auditoria_bib_1110_segunda_passagem_kullback_e_as_iniciais():
    """Segunda passagem da auditoria, 2026-11-10.

    A [19] deixou de estar incompleta: o autor correspondente leu 79--86 no
    sumário do volume no JSTOR, depois de o Project Euclid recusar três
    tentativas aqui por verificação de navegador. O campo entra por essa
    leitura e a nota diz de quem foi.

    E três entradas perderam prenomes que ninguém lera. A regra é a mesma nas
    três: onde nenhuma fonte alcançável imprime prenome, fica a inicial que as
    fontes imprimem. Um prenome plausível é mais perigoso que uma inicial,
    porque passa por verificado.
    """
    bib = (RAIZ / "paper" / "referencias.bib").read_text()

    i = bib.index("@article{kullback1951information")
    kl = bib[i:bib.index("\n}", i)]
    assert "pages   = {79--86}" in kl
    assert "SUPPLIED BY" in kl and "CORRESPONDING AUTHOR" in kl
    assert "JSTOR" in kl
    assert "INCOMPLETE ON PURPOSE" not in kl
    assert "written\n             on that reading and on no inference" in kl

    # as tres entradas sem prenome inventado
    import re
    for chave, proibidos in (
            ("saranwong2004mango", ("Jingtair", "Jinda", "Sirinnapa", "Sumio")),
            ("wold2001pls", ("Svante", "Michael", "Lennart")),
            ("anderson2020mango", ("Chris", "Nicholas T.", "Kerry B.",
                                   "Phul P."))):
        i = bib.index(chave)
        corpo = bib[i:bib.index("\n}", i)]
        autores = corpo[corpo.index("author"):corpo.index("title")]
        for nome in proibidos:
            assert nome not in autores, f"{chave}: {nome!r} voltou ao author"
    # o que FOI lido continua escrito
    i = bib.index("anderson2020mango")
    an = bib[i:bib.index("\n}", i)]
    assert "Anderson, Nicholas" in an and "Hayes, C. H." in an
    assert "AUTHOR LINE WAS READ" in an

    # A LISTA IMPRESSA, nao so o .bib. Em 2026-11-11 descobriu-se que a
    # reducao de prenomes da vespera tinha alcancado o .bib e NAO a lista
    # numerada, que e o que o manuscrito publica: a [9] ainda saía como
    # "N.T. Anderson, K.B. Walsh, P.P. Subedi" no PDF. Corrigir um e nao o
    # outro e pior que nao corrigir, porque o arquivo de auditoria passa a
    # descrever algo que o leitor nao recebe.
    lista = (RAIZ / "paper" / "12-referencias.md").read_text()
    import re as _re5
    m = _re5.search(r"^## References[ \t]*$", lista, _re5.M)
    corpo = lista[m.end():]
    f = _re5.search(r"^## ", corpo, _re5.M)
    entradas = {n_: e for n_, e in _re5.findall(r"^\[(\d+)\]\s+(.+)$",
                                                corpo[:f.start() if f else None],
                                                _re5.M)}
    autores9 = entradas[_num_ref("Achieving robustness")].split(", Achieving")[0]
    for proibido in ("N.T.", "K.B.", "P.P."):
        assert proibido not in autores9, (
            f"a lista impressa ainda traz {proibido}, que o .bib removeu por "
            "nunca ter sido lido")
    assert autores9 == "N. Anderson, K. Walsh, P. Subedi, C.H. Hayes"
    assert "10.1016/j.postharvbio.2020.111202" in entradas[
        _num_ref("Achieving robustness")]
    for trecho, esperado in (
            ("Saranwong", "S. Saranwong, J. Sornsrivichai, S. Kawano"),
            ("PLS-regression", "S. Wold, M. Sjöström, L. Eriksson")):
        assert entradas[_num_ref(trecho)].startswith(esperado), trecho

    assert "22 (1) (1951) 79–86" in lista
    assert "Segunda passagem, 2026-11-10" in lista
    assert "Um prenome plausível é mais perigoso que uma inicial" in lista


@pytest.mark.semantico
def test_auditoria_bib_1110_terceira_passagem_e_o_doi_que_nao_foi_escrito():
    """As duas últimas pendências da auditoria.

    A [20] fechou contra um SEGUNDO índice independente. O DOI da [9] não foi
    obtido em cinco rotas, e — isto é o ponto — NÃO foi construído a partir do
    PII, embora o padrão da Elsevier tornasse trivial escrever
    `10.1016/j.postharvbio.2020.111202`. Um campo plausível e não lido é
    exatamente o que esta auditoria existe para impedir, e a facilidade de
    produzi-lo é razão para desconfiar dele, não para escrevê-lo.

    Este teste guarda a ausência: se esse DOI aparecer algum dia, terá de vir
    com uma nota dizendo onde foi lido.
    """
    bib = (RAIZ / "paper" / "referencias.bib").read_text()
    i = bib.index("anderson2020mango")
    entrada = bib[i:bib.index("\n}", i)]
    import re as _re4
    nota = _re4.sub(r"\s+", " ", entrada[entrada.index("note"):])
    # O DOI entrou em 2026-11-11, e este teste cobra dele o que cobrava da
    # ausencia: a cadeia so vale acompanhada da prova de que designa ESTE
    # artigo. A prova e o resolvedor do registro redirecionando para o PII
    # que o deposito dos autores da para o artigo -- nao o padrao de nomes da
    # Elsevier, que produziria a mesma cadeia sem evidencia nenhuma e foi
    # recusado por isso na vespera. Um campo certo pelo motivo errado continua
    # sendo um campo sem leitura.
    if "10.1016/j.postharvbio.2020.111202" in entrada.split("note")[0]:
        assert "THE DOI WAS RESOLVED" in nota
        assert "doi.org" in nota and "S0925521420301629" in nota
        assert "not by the Elsevier naming pattern" in nota
    else:
        assert "10.1016/j.postharvbio.2020.111202" not in bib, (
            "a cadeia aparece em algum lugar sem estar no campo doi")

    i = bib.index("mcallester1999pacbayes")
    mc = __import__("re").sub(r"\s+", " ", bib[i:bib.index("\n}", i)])
    assert "CONFIRMED AGAIN" in mc and "SECOND, independent" in mc
    assert "10.1145/307400.307435" in mc
    assert "no field was taken from memory" in mc

    ref = (RAIZ / "paper" / "12-referencias.md").read_text()
    assert "Terceira passagem, 2026-11-10" in ref
    assert "O PII não foi convertido em DOI" in ref
    assert "S0925521420301629" in ref
    # a tabela de pendencias deixou de existir em 2026-11-11, quando o DOI da
    # [9] -- a ultima lacuna -- foi resolvido. O invariante que substitui a
    # contagem de linhas: o arquivo declara que nao ha campo por ler, e diz
    # pela quarta passagem como o ultimo foi fechado.
    assert "não há campo pendente" in ref
    assert "Quarta passagem, 2026-11-11" in ref
    assert "Um campo certo pelo motivo errado continua sendo um campo" in ref
    assert "nenhuma entrada tem campo por ler" in ref
    assert "alcançara o `.bib` e **não** a lista numerada" in ref


@pytest.mark.estrutural
def test_bibliografia_sai_sem_justificacao_esticada():
    """Inspeção do PDF definitivo, 2026-11-10.

    A lista de referências tinha o mesmo defeito que a Tabela 1 tivera: um DOI
    e um nome de periódico não hifenizam, de modo que a justificação estica o
    espaço entre palavras no lugar deles -- visivelmente nas entradas [18] e
    [20], cujas URLs são longas. Listas de referências são convencionalmente
    compostas sem justificação por essa razão exata.

    O grupo tem de FECHAR: um \\begingroup sem \\endgroup deixaria o resto do
    documento sem justificação, que é um defeito maior que o corrigido.
    """
    t = (RAIZ / "scripts" / "19_tex.py").read_text()
    assert "\\\\begingroup\\\\raggedright" in t
    assert "\\\\endgroup" in t
    corpo = _tex_gerado()
    assert corpo.count("\\begingroup\\raggedright") == corpo.count("\\endgroup"), \
        "um \\begingroup sem \\endgroup: o resto do documento perde a justificação"
    i = corpo.index("\\section*{References}")
    trecho = corpo[i:i + 400]
    assert "\\begingroup\\raggedright" in trecho


@pytest.mark.semantico
def test_credit_vem_do_autor_e_a_taxonomia_nao_foi_reescrita():
    """CRediT, fornecido verbatim pelo autor em 2026-11-11.

    Quem fez o quê não é inferível do repositório, então os papéis são dele e
    não foram compostos aqui. A única alteração ao texto recebido foi desfazer
    a hifenação de quebra de linha do copiar-colar (`edit-ing`,
    `Visual-ization`, `administra-tion`).

    O ponto delicado: `Conceptualization` e `Visualization` são nomes FIXOS da
    taxonomia CRediT. O verificador de conformidade os acusou como formas
    `-ize` contra a norma britânica do manuscrito, e respeitá-lo teria
    corrompido a taxonomia para satisfazer uma regra sobre prosa autoral. A
    seção foi declarada reproduzida, como References e Authors.
    """
    import re
    fonte = (RAIZ / "paper" / "18-declaracoes.md").read_text()
    assert "FORNECIDA PELO AUTOR em 2026-11-11" in fonte
    assert "não foram compostos por mim" in fonte

    decl = re.sub(r"\s+", " ", fonte[fonte.index("## CRediT"):])
    # os papeis, exatamente como vieram, com a hifenacao desfeita
    assert ("**Guilherme Coelho:** Investigation, Writing – review & editing."
            in decl)
    assert ("**Clarimar José Coelho:** Conceptualization, Methodology, "
            "Software, Formal analysis, Validation, Data curation, "
            "Visualization, Supervision, Project administration, Writing – "
            "original draft, Writing – review & editing.") in decl
    for partido in ("edit-ing", "Visual-ization", "administra-tion"):
        assert partido not in decl, partido

    # a taxonomia nao foi reescrita para -isation
    for britanico in ("Conceptualisation", "Visualisation"):
        assert britanico not in fonte, britanico
    conf = (RAIZ / "scripts" / "18_conformidade.py").read_text()
    assert "CRediT authorship contribution statement" in conf
    assert "would\n# corrupt the taxonomy" in conf

    # entra depois da §12 e fora da numeracao: nao e a secao 13
    cons = (RAIZ / "scripts" / "15_consolidar_manuscrito.py").read_text()
    i = cons.index('("09-rascunho-s12.md"')
    j = cons.index('("18-declaracoes.md"')
    assert j > i, "a declaração tem de vir depois da última seção numerada"
    assert "SECOES_ESPERADAS = 12" in cons

    # e chega ao manuscrito e ao .tex, com o & escapado
    md = (RAIZ / "paper" / "MANUSCRITO.md").read_text()
    assert "## CRediT authorship contribution statement" in md
    corpo = _tex_gerado()
    assert "\\section*{CRediT authorship contribution statement}" in corpo
    assert "review \\& editing" in corpo
    assert "review & editing" not in corpo, "& sem escape quebra o LaTeX"


@pytest.mark.semantico
def test_declaracao_de_ia_continua_em_aberto_e_declarada_como_tal():
    """A *Declaration of generative AI and AI-assisted technologies in the
    writing process* ainda não existe, e o arquivo de declarações diz isso em
    vez de ficar calado.

    Parte da prosa deste manuscrito foi redigida por mim, de modo que a
    declaração se aplica; o texto dela é do autor e não será escrito aqui. Se
    alguém a acrescentar, este teste cobra que o aviso de pendência saia
    junto — um manuscrito que declara e um arquivo que diz estar pendente é
    pior que qualquer um dos dois sozinho.
    """
    fonte = (RAIZ / "paper" / "18-declaracoes.md").read_text()
    md = (RAIZ / "paper" / "MANUSCRITO.md").read_text()
    assert "AI-assisted" in md, "a declaração saiu do manuscrito"
    # entrou em 2026-11-11, logo o aviso de pendencia tem de ter saido
    assert "Ainda não decidido" not in fonte, (
        "a declaração de IA entrou no manuscrito mas o arquivo de "
        "declarações ainda a chama de pendente")


@pytest.mark.semantico
def test_citacoes_narrativas_nomeiam_o_autor_onde_o_colchete_e_sujeito():
    """Pedido do autor em 2026-11-11: referir-se aos autores "quando for o
    caso". O caso não é todo marcador.

    A distinção aplicada: onde o colchete é SUJEITO da oração, ou complemento
    de "of"/"in" representando a obra, ele não é uma referência mas um nome
    disfarçado, e o leitor tem de descer à lista para saber de quem se fala.
    Onde é apoio parentético — `the one-standard-error rule [15]`, `a Jaccard
    index [5]` — o nome só atrapalharia.

    Os sobrenomes foram LIDOS da lista numerada, não recordados, e a forma
    segue o número de autores: Kuncheva (uma), Nogueira et al. (três),
    Anderson et al. (quatro), Workman and Weyer (dois).
    """
    import re
    s1 = re.sub(r"\s+", " ", (RAIZ / "paper" / "03-rascunho-s1-s2-s3.md"
                              ).read_text())
    kun, nog = _num_ref("A stability index"), _num_ref("On the stability of")
    and_, wor = _num_ref("Achieving robustness"), _num_ref("Practical Guide")

    # o colchete deixou de ser o complemento de "of"/"in"
    for antes in (f"index of [{kun}]", f"mean of [{kun}]",
                  f"reported in [{and_}]", f"catalogued in [{wor}]"):
        assert antes not in s1, antes
    for depois in (f"index of Kuncheva [{kun}]",
                   f"mean of Kuncheva [{kun}]",
                   f"reported by Anderson et al. [{and_}]",
                   f"catalogued by Workman and Weyer [{wor}]",
                   f"In the vocabulary of Kuncheva [{kun}] and Nogueira "
                   f"et al. [{nog}]"):
        assert depois in s1, depois

    # como SUJEITO, o verbo concorda com os autores e nao com o colchete
    assert f"Nogueira et al. place that correction [{nog}]" in s1
    assert f"Nogueira et al. put that correction [{nog}]" in s1
    for errado in (f"[{nog}] places", f"[{nog}] puts"):
        assert errado not in s1, f"{errado}: sujeito voltou a ser o colchete"

    # e o apoio parentetico NAO ganhou nome: nomear tudo seria tao errado
    # quanto nomear nada
    assert "one-standard-error rule [" in s1
    assert re.search(r"Jaccard index\s*\[\d+\]", s1)

    # nenhum marcador foi criado nem destruido: a numeracao e por ordem de
    # primeira aparicao, e acrescentar um deslocaria todos os seguintes
    # A sequencia abaixo e a do commit-base e994... verificada em 2026-11-11:
    # a citacao narrativa nao acrescentou, removeu nem reordenou nenhum
    # marcador. Isso importa porque a numeracao e por ordem de PRIMEIRA
    # aparicao, de modo que inserir um marcador cedo deslocaria todos os
    # seguintes e invalidaria a lista inteira.
    assert re.findall(r"\[(\d+)\]", s1) == [
        "1", "2", "3", "4", "4", "5", "6", "7", "4", "8", "9", "4", "12",
        "13", "14", "4", "4", "6", "7", "6", "6", "7", "15"]


@pytest.mark.estrutural
def test_bib_modo_cite_nao_toca_o_preambulo_nem_publica_a_auditoria():
    """Pedido do autor em 2026-11-11: `\\cite{}` contra o `.bib`, não `[6]`
    literal. O modo `--bib` do conversor, e os dois defeitos que ele revelou.

    PRIMEIRO: substituir `[n]` no documento inteiro destrói o preâmbulo. Ali
    `[1]` é contagem de argumentos de macro -- `\\newcolumntype{P}[1]{...}`,
    `\\providecommand{\\semfigura}[1]{...}` -- e virou `\\cite{...}` na primeira
    tentativa, com 46 erros de LaTeX. A substituição vale só depois do
    `\\begin{document}`.

    SEGUNDO: `unsrt` imprime o campo `note`, e as nossas notas são registros
    de proveniência. Citar contra o `.bib` de registro punha "Read the PDF on
    the author's own site, including Definition 1 and the hypergeometric
    expectation E[r] = k^2/n" DENTRO da lista de referências do artigo -- 240
    linhas de `.bbl` para 21 referências, e quatro erros, porque as notas
    carregam matemática crua. O `.bib` de submissão sai sem elas.
    """
    import re
    t = (RAIZ / "scripts" / "19_tex.py").read_text()
    assert "def bib_para_submissao" in t
    assert "def mapa_citacoes" in t
    assert '"--bib"' in t
    # a substituicao delimitada
    assert 'marca = "\\\\begin{document}"' in t
    assert "corte = corpo.index(marca) + len(marca)" in t
    assert "miolo, n_sub = re.subn" in t
    # as recusas: marcador sem chave, marcador sobrevivente, nota sobrevivente
    assert "Refusing to emit a document that cites nothing" in t
    assert "markers survived the" in t
    assert "Refusing to print the audit trail in the paper" in t
    # e o mapa e LIDO, nao recalculado
    assert "rather than recomputed" in t


@pytest.mark.semantico
def test_mapa_de_numeros_para_chaves_e_bijetivo_e_por_titulo():
    """O mapa número -> chave, gravado em 2026-11-11.

    Pareado por TÍTULO com bijeção exigida, não por nome de chave: o arquivo
    tem dois Anderson, dois Lange e dois Coelho, e parear por nome citaria o
    artigo errado. Este teste refaz o pareamento e exige o mesmo resultado,
    de modo que uma entrada nova ou renomeada não passa calada.
    """
    import re, unicodedata

    def norm(s: str) -> str:
        s = unicodedata.normalize("NFKD", s)
        s = "".join(c for c in s if not unicodedata.combining(c))
        return re.sub(r"\{|\}|\\[a-zA-Z]+|[^a-z0-9]", "", s.lower())

    bib = (RAIZ / "paper" / "referencias.bib").read_text()
    titulos = {}
    for m in re.finditer(r"^@\w+\{([^,]+),(.*?)\n\}", bib, re.M | re.S):
        tm = re.search(r"title\s*=\s*\{(.+?)\}\s*,\s*\n", m.group(2), re.S)
        if tm:
            titulos[m.group(1)] = norm(tm.group(1))

    ref = (RAIZ / "paper" / "12-referencias.md").read_text()
    m = re.search(r"^## Mapa de n.meros para chaves BibTeX[ \t]*$", ref, re.M)
    assert m, "o mapa desapareceu do arquivo de referências"
    corpo = ref[m.end():]
    f = re.search(r"^## ", corpo, re.M)
    mapa = dict(re.findall(r"^\|\s*\[(\d+)\]\s*\|\s*`([^`]+)`",
                           corpo[:f.start() if f else None], re.M))
    assert len(mapa) == 21
    assert len(set(mapa.values())) == 21, "duas linhas apontam a mesma chave"
    assert set(mapa.values()) == set(titulos), "o mapa e o .bib divergem"

    # cada numero casa, POR TITULO, com a chave que o mapa lhe da
    mt = re.search(r"^## References[ \t]*$", ref, re.M)
    lista = ref[mt.end():]
    fl = re.search(r"^## ", lista, re.M)
    entradas = dict(re.findall(r"^\[(\d+)\]\s+(.+)$",
                               lista[:fl.start() if fl else None], re.M))
    for num, chave in mapa.items():
        assert titulos[chave] in norm(entradas[num]), (
            f"[{num}] -> {chave}: o título do .bib não está na entrada da lista")


@pytest.mark.semantico
def test_declaracao_de_ia_segue_a_politica_lida_na_fonte():
    """Acrescentada em 2026-11-11, com a política da Elsevier LIDA na fonte
    naquela data e não de memória. Ela exige três coisas, e as três são
    asseveradas aqui.

    TÍTULO exato. COLOCAÇÃO imediatamente acima das referências, o que no
    conversor significa depois da Tabela 1 e antes de qualquer um dos dois
    caminhos de bibliografia -- vale no `--bib` e na lista digitada.
    CONTEÚDO nomeando a ferramenta, a finalidade e a extensão da supervisão.

    O texto é um rascunho meu submetido ao autor: uma declaração afirma
    conduta dele, não minha, e o arquivo-fonte diz quais orações são
    afirmações sobre os autores que só eles podem confirmar.
    """
    import re
    titulo = ("Declaration of Generative AI and AI-assisted technologies "
              "in the writing process")
    md = re.sub(r"\s+", " ", (RAIZ / "paper" / "MANUSCRITO.md").read_text())
    assert f"## {titulo}" in re.sub(r"\s+", " ",
                                    (RAIZ / "paper" / "MANUSCRITO.md"
                                     ).read_text())
    # os tres elementos de conteudo que a politica pede
    assert "used Claude (Anthropic)" in md                  # a ferramenta
    assert "to draft and revise prose in this manuscript" in md   # a finalidade
    assert "The authors reviewed and edited all of that output" in md  # supervisão
    assert "take full responsibility for the content of the publication" in md

    # colocacao: emitida DEPOIS da Tabela 1 e ANTES das referencias, nos dois modos
    conv = (RAIZ / "scripts" / "19_tex.py").read_text()
    i_tab = conv.index('corpo_para_tex(por_titulo["Table 1"]')
    i_dec = conv.index("decl_ia = (")
    i_bib = conv.index("    if a.bib:")
    assert i_tab < i_dec < i_bib, "a declaração saiu do lugar que a política exige"
    assert 'if por_titulo.get(decl_ia):' in conv, (
        "sem a guarda, um título sem corpo imprimiria uma declaração que os "
        "autores não fizeram")

    corpo = _tex_gerado()
    assert corpo.index("\\section*{" + titulo + "}") < \
        corpo.index("\\section*{References}")

    # e a secao e reproduzida: nomes de ferramenta nao sao grafia autoral
    conf = (RAIZ / "scripts" / "18_conformidade.py").read_text()
    assert titulo in conf

    # o arquivo-fonte declara o que e rascunho e o que ficou em aberto
    fonte = (RAIZ / "paper" / "18-declaracoes.md").read_text()
    assert "rascunho meu e precisa da sua decisão" in fonte
    assert "Isso deixa uma pergunta em aberto, e ela é sua" in fonte
    assert "imediatamente acima das referências" in fonte
