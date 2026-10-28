# Matriz de rastreabilidade

Gerado por `scripts/16_matriz_rastreabilidade.py`. Não editar: a categoria de cada
teste é declarada no próprio teste, por marcador `pytest`.

242 testes em 10 arquivos.

## semantico (20)

| teste | decisão protegida | arquivos |
| --- | --- | --- |
| `test_etapa_b_item6_consistencia_tabela1_e_achados` | Author's closing criterion 4: Table 1 and F001-F007 must stay | `00-estrutura.md`, `05-rascunho-s9-s10-s11.md`, `ADR-0001-escopo-e-datasets.md` |
| `test_etapa_b_431_reprodutibilidade_para_o_leitor` | Author's item 5: incorporate the non-portability into the discussion. | `01-rascunho-resumo-e-s4.md` |
| `test_etapa_b_reporta_por_procedimento_e_nao_substitui` | Stage B, author 2026-10-27: the contribution is the comparison between | `01-rascunho-resumo-e-s4.md`, `08-rascunho-s5.md` |
| `test_etapa_b_43_sem_valor_p_sem_unidade_justificada` | Author 2026-10-27: do not keep a coefficient and p-value from an | `08-rascunho-s5.md` |
| `test_etapa_b_secao6_invariancia_aritmetica` | Author's item 3: check the sensitivity of 0.9763-1.0000 BEFORE touching | `04-rascunho-s6-s7-s8.md` |
| `test_secao12_conclusoes_responde_as_tres_perguntas` | Created by the integral audit of 2026-10-28: the paper had no | `09-rascunho-s12.md` |
| `test_secao12_nao_le_como_o_modelo_nao_aprende` | The author's own caveat of 2026-10-28: the sentence limiting the | `09-rascunho-s12.md` |
| `test_secao10_separa_achado_de_limitacao_de_reprodutibilidade` | Author 2026-10-28: the result is that selection can depend on the tie | `05-rascunho-s9-s10-s11.md` |
| `test_resumo_na_ordem_logica_do_autor` | Author 2026-10-28: the abstract must carry BOTH contributions, in a | `02-resumo-C.md` |
| `test_pre_registro_declara_o_post_hoc_antes_dos_resultados` | Author's Table 1 condition, 2026-10-28: the tie-breaking analysis is a | `03-rascunho-s1-s2-s3.md` |
| `test_resumo_representa_o_artigo_depois_da_etapa_b` | First integral-audit finding, 2026-10-28: the abstract approved on | `02-resumo-C.md` |
| `test_tabela1_h0_sem_contagem_por_construcao` | H0's criterion is existential and defines no per-partition tally, so | `00-estrutura.md`, `F001-caminho-de-regularizacao.md` |
| `test_tres_niveis_de_evidencia_separados` | Author 2026-10-28: the manuscript must distinguish the demonstrated | `01-rascunho-resumo-e-s4.md`, `03-rascunho-s1-s2-s3.md` |
| `test_etapa_b_legenda_fig3_declara_regra_e_ambiente` | Author's item 4: the caption must declare rule, environment and origin, | `06-legendas-figuras.md` |
| `test_rascunho_nao_afirma_ausencia_total_de_empate` | The draft said the unanchored arm has no ties and the two rules agree | `08-rascunho-s5.md` |
| `test_resumo_C_carrega_as_quatro_exigencias` | The four binding requirements the author attached to approving | `02-resumo-C.md` |
| `test_estrutura_concilia_com_o_ADR_0003` | Item 2 of 'O que falta antes da prosa' said the editor route was | `00-estrutura.md` |
| `test_prior_nao_e_descrito_como_min_max` | The literature prior is not min-max normalised: make_literature_prior | `03-rascunho-s1-s2-s3.md`, `F002-o-que-as-metricas-interpretativas-medem.md`, `paper/03-rascunho-s1-s2-s3.md` |
| `test_f008_separa_o_medido_do_inferido` | The finding must keep three things apart: what was measured here, what | `F008-a-sobreposicao-deterministica-depende-do-sort.md` |
| `test_07_separa_exigencia_confirmada_de_nao_verificada` | The submission matter must keep the two categories apart: what was read | `07-declaracoes-submissao.md` |

## estrutural (9)

| teste | decisão protegida | arquivos |
| --- | --- | --- |
| `test_15_exige_doze_secoes` | The consolidator must now expect twelve, so a lost Section 12 is a gap | `09-rascunho-s12.md`, `15_consolidar_manuscrito.py` |
| `test_15_recusa_resumo_partido_em_vez_de_truncar` | On 2026-10-28 the abstract was rewritten with a line beginning '--', | `15_consolidar_manuscrito.py` |
| `test_16_declara_a_categoria_e_nao_a_infere` | The matrix must take each test's category from a declared pytest | `16_matriz_rastreabilidade.py`, `pyproject.toml` |
| `test_15_consolida_sem_perder_nem_inventar` | The consolidated manuscript is a build step over the drafts. It must | `08-rascunho-s5.md`, `15_consolidar_manuscrito.py` |
| `test_14_veredicto_de_uma_linha_nao_pode_ser_truncado` | The author's partition run of 2026-10-27 was piped through `tail -20` | `14_etapa_b_por_procedimento.py` |
| `test_07_culpa_a_raiz_certa_pelo_modulo_que_falta` | Author's run, 2026-10-27: the handler for the pgsg2 import block blamed | `07_raman_lambda1.py` |
| `test_13_nao_esconde_um_sd_nao_nulo_atras_do_arredondamento` | Author's Raman run, 2026-10-27: the table printed sd as 0.0000 in all | `13_dependencia_do_sort.py` |
| `test_12_nao_chama_verificada_uma_figura_sem_entradas` | Reproducibility of a procedure is not conformity of a submitted file. | `12_verifica_figuras.py`, `pyproject.toml` |
| `test_09_garante_dtype_antes_de_comparar_bits` | view(np.int64) presupposes the array really is float64, which the | `09_controle_deslocamento.py` |

## numerico (7)

| teste | decisão protegida | arquivos |
| --- | --- | --- |
| `test_14_mede_a_fronteira_e_nao_conta_empates` | The criterion for rule-dependence is a tie group spanning rank q, not | `14_etapa_b_por_procedimento.py` |
| `test_rascunho_usa_a_esperanca_exata` |  | `01-rascunho-resumo-e-s4.md` |
| `test_s9_reporta_p2_medido_e_nao_um_limite` | The bound was superseded by the measurement on 2026-10-26: P1 holds | `05-rascunho-s9-s10-s11.md` |
| `test_05_nao_afirma_que_o_padrao_desempata_por_indice` | Mandatory correction, author 2026-10-27 (F008): the script used to print | `05_diagnostico_jaccard.py`, `13_dependencia_do_sort.py` |
| `test_13_mede_a_dependencia_do_sort_sem_inferir_ambiente` | F008: every top-q selection uses a bare np.argsort, whose default is not | `13_dependencia_do_sort.py` |
| `test_09_usa_o_espacamento_dos_valores_observados` | The plateau sits in [0.5, 1), where float32 spacing is 2**-24. An | `09_controle_deslocamento.py` |
| `test_f007_corrige_o_espacamento_e_separa_proveniencia` | The two corrections the author required on 2026-10-26, recorded in the | `F007-o-controle-de-deslocamento-e-o-plato.md` |

## UNCLASSIFIED (206)

Sem marcador. A categoria não é inferida.

- `test_analise_condicional.py` — 27
- `test_analise_controles.py` — 21
- `test_analise_plato.py` — 24
- `test_chance_exata.py` — 46
- `test_diagnostico_jaccard.py` — 23
- `test_grouped.py` — 10
- `test_pgsg_v3.py` — 19
- `test_prior_arms.py` — 10
- `test_raman_arm.py` — 22
- `test_smoke.py` — 4
