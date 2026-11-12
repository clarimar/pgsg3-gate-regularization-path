# Matriz de rastreabilidade

Gerado por `scripts/16_matriz_rastreabilidade.py`. Não editar: a categoria de cada
teste é declarada no próprio teste, por marcador `pytest`.

307 funções de teste em 10 arquivos. A unidade de contagem é a **função de teste** definida no
nível do módulo, lida da fonte por AST — não é item coletado pelo pytest nem teste executado. Casos
parametrizados somam +15 itens na coleta.

## semantico (58)

| teste | decisão protegida | arquivos |
| --- | --- | --- |
| `test_etapa_b_item6_consistencia_tabela1_e_achados` | Author's closing criterion 4: Table 1 and F001-F007 must stay | `00-estrutura.md`, `05-rascunho-s9-s10-s11.md`, `ADR-0001-escopo-e-datasets.md` |
| `test_etapa_b_431_reprodutibilidade_para_o_leitor` | Author's item 5: incorporate the non-portability into the discussion. | `01-rascunho-resumo-e-s4.md` |
| `test_etapa_b_reporta_por_procedimento_e_nao_substitui` | Stage B, author 2026-10-27: the contribution is the comparison between | `01-rascunho-resumo-e-s4.md`, `08-rascunho-s5.md` |
| `test_etapa_b_43_sem_valor_p_sem_unidade_justificada` | Author 2026-10-27: do not keep a coefficient and p-value from an | `08-rascunho-s5.md` |
| `test_etapa_b_secao6_invariancia_aritmetica` | Author's item 3: check the sensitivity of 0.9763-1.0000 BEFORE touching | `04-rascunho-s6-s7-s8.md` |
| `test_secao12_conclusoes_responde_as_tres_perguntas` | Created by the integral audit of 2026-10-28: the paper had no | `09-rascunho-s12.md` |
| `test_referencia_e_separate_em_todo_o_manuscrito` | Author 2026-10-28, after the integral reading: "external reference" | `01-rascunho-resumo-e-s4.md`, `02-resumo-C.md`, `03-rascunho-s1-s2-s3.md` |
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
| `test_prior_nao_e_descrito_como_min_max` | The literature prior is not min-max normalised: make_literature_prior | `03-rascunho-s1-s2-s3.md`, `F002-o-que-as-metricas-interpretativas-medem.md`, `scripts/05_diagnostico_jaccard.py` |
| `test_f008_separa_o_medido_do_inferido` | The finding must keep three things apart: what was measured here, what | `F008-a-sobreposicao-deterministica-depende-do-sort.md` |
| `test_07_separa_exigencia_confirmada_de_nao_verificada` | The submission matter must keep the two categories apart: what was read | `07-declaracoes-submissao.md` |
| `test_resumo_cabe_no_limite_confirmado_do_chemolab` | The journal's limit, read at the source on 2026-10-28: "You are | `02-resumo-C.md` |
| `test_highlights_nao_convertem_resultado_fraco_em_ausencia` | The three corrections the author approved on 2026-10-28. A highlight is | `07-declaracoes-submissao.md` |
| `test_highlights_e_keywords_nao_divergem_entre_as_duas_fontes` | The five highlights and the six keywords now live in three places: the | `07-declaracoes-submissao.md`, `10-highlights.md`, `11-palavras-chave.md` |
| `test_12_audita_os_pontos_que_exigem_citacao` | The reference audit of 2026-10-29. The manuscript has no citations at | `12-referencias.md`, `15_consolidar_manuscrito.py` |
| `test_texto_declara_a_grade_e_o_truncamento` | F009's two text corrections, 2026-10-29. Both state a measured fact and | `03-rascunho-s1-s2-s3.md`, `06-legendas-figuras.md` |
| `test_cada_figura_e_citada_e_as_legendas_estao_em_ingles` | Two defects found by the conformity scan of 2026-10-29, both fixed in | `01-rascunho-resumo-e-s4.md`, `06-legendas-figuras.md`, `15_consolidar_manuscrito.py` |
| `test_12_aplica_as_tres_decisoes_que_fecham_sem_bibliografia` | Three of the author's four decisions of 2026-11-09 close without a | `01-rascunho-resumo-e-s4.md`, `02-resumo-C.md`, `03-rascunho-s1-s2-s3.md` |
| `test_07_registra_a_conformidade_medida_sem_alterar_a_citacao_do_autor` | The language rule, measured: British throughout, one American form, and | `05-rascunho-s9-s10-s11.md`, `07-declaracoes-submissao.md` |
| `test_12_fecha_o_conjunto_raman_por_concordancia_declarada` | The Raman dataset, identified on 2026-10-29. "bioprocess_substrates" | `12-referencias.md` |
| `test_12_registra_o_dossie_e_os_tres_destinos` | The dossier the author asked for on 2026-10-29, and the complication it | `12-referencias.md` |
| `test_07_registra_as_quatro_decisoes_e_a_condicao_nao_satisfeita` | The author's four decisions of 2026-10-29. Three are applied and one is | `07-declaracoes-submissao.md` |
| `test_18_mede_o_idioma_do_artefato_por_secao` | The manuscript is English, and anything in the drafting language that | `05-rascunho-s9-s10-s11.md`, `correcao-em-provas.md` |
| `test_13_aplica_a_tabela1_em_ingles_e_concilia_com_o_original` | The Table 1 translation, approved and applied on 2026-11-09: translate | `00-estrutura.md`, `13-tabela1.md`, `15_consolidar_manuscrito.py` |
| `test_19_declara_o_que_falta_em_vez_de_disfarcar` | The reading copy must say what it is not. Three things are missing from | `19_tex.py`, `paper/12-referencias.md`, `scripts/15_consolidar_manuscrito.py` |
| `test_bib_so_tem_entrada_verificada_e_bibtex_nao_ve_o_resto` | paper/referencias.bib carries only what was read at a source, and the | `12-referencias.md`, `referencias.bib` |
| `test_14_corrige_a_alegacao_causal_e_descreve_o_cruzamento` | The two scientific corrections of the 2026-11-02 referee report, | `03-rascunho-s1-s2-s3.md`, `04-rascunho-s6-s7-s8.md`, `06-legendas-figuras.md` |
| `test_12_mede_a_exposicao_ao_fundador_nao_corrigido` | The editor did not answer the letter about the corrigendum, so the | `12-referencias.md`, `F001-caminho-de-regularizacao.md`, `F004-estabilidade-interpretativa-e-funcao-dos-dados.md` |
| `test_12_aplica_seis_das_sete_e_reenquadra_a_novidade` | Six of the seven proposed references, approved and applied on | `03-rascunho-s1-s2-s3.md`, `12-referencias.md`, `scripts/17_citacoes.py` |
| `test_parecer1110_declara_o_tratamento_numerico_de_logit_e_da_kl` | Itens 2.1 e 2.2, ambos de prioridade alta. | `03-rascunho-s1-s2-s3.md` |
| `test_parecer1110_c1_usa_a_desigualdade_estrita` | Item 2.6. O título do C1 e a tabela da §4.4 já diziam "plateau > q"; só | `01-rascunho-resumo-e-s4.md`, `03-rascunho-s1-s2-s3.md`, `04-rascunho-s6-s7-s8.md` |
| `test_parecer1110_retira_a_equivalencia_de_r2_fora_do_alcance` | Item 2.3. A §9.1 dizia que o R² é equivalente "in both modalities", | `05-rascunho-s9-s10-s11.md` |
| `test_parecer1110_rademacher_e_fechamento_da_71` | Itens 2.4 e 2.5. Os dois trechos eram de minha redação. | `04-rascunho-s6-s7-s8.md`, `05-rascunho-s9-s10-s11.md` |
| `test_parecer1110_o_registro_existe_e_declara_o_que_ficou_pendente` | O parecer de 2026-11-02 tem registro em `14-parecer-2026-11-02.md`; o | `17-parecer-2026-11-10.md` |
| `test_decisao1110_qualifica_a_31_sem_atribuir_ao_sigma_sozinho` | O autor exigiu a qualificação e deu a redação. O argumento original | `03-rascunho-s1-s2-s3.md` |
| `test_decisao1110_declara_a_forma_acoplada_sem_alegar_razao_no_passo` | A objeção do autor: com momentos adaptativos não se compara o termo de | `03-rascunho-s1-s2-s3.md`, `pgsg_v3.py` |
| `test_decisao1110_nenhum_r2_por_tamanho_de_treino_e_nenhuma_alegacao_dele` | Medido em 2026-11-10: NENHUM csv deste repositório tem R² indexado por | `05-rascunho-s9-s10-s11.md`, `gate_metrics.csv` |
| `test_decisao1110_a_lacuna_do_controle_de_otimizador_esta_declarada` | Medido: `ctl_adam`, `ctl_adamw` e `ctl_piloto` rodaram só com | `03-rascunho-s1-s2-s3.md`, `05-rascunho-s9-s10-s11.md`, `aggregate.csv` |
| `test_ajustes_finais_1110_tiram_as_tres_alegacoes_excessivas` | Os três ajustes do autor sobre o patch aprovado, mais a gêmea que ele | `01-rascunho-resumo-e-s4.md`, `02-resumo-C.md`, `03-rascunho-s1-s2-s3.md` |
| `test_auditoria_bib_1110_nenhuma_alegacao_de_custo_nulo_sobrou` | A ressalva do autor sobre *"the evidence for the cost being nil"*, e as | `03-rascunho-s1-s2-s3.md`, `05-rascunho-s9-s10-s11.md` |
| `test_auditoria_bib_1110_saranwong_corrigida_e_sem_prenome_inventado` | A auditoria de 2026-11-10 achou um erro real: a [13] trazia 253--261, | `12-referencias.md`, `referencias.bib` |
| `test_auditoria_bib_1110_segunda_passagem_kullback_e_as_iniciais` | Segunda passagem da auditoria, 2026-11-10. | `12-referencias.md`, `referencias.bib` |
| `test_auditoria_bib_1110_terceira_passagem_e_o_doi_que_nao_foi_escrito` | As duas últimas pendências da auditoria. | `12-referencias.md`, `referencias.bib` |
| `test_credit_vem_do_autor_e_a_taxonomia_nao_foi_reescrita` | CRediT, fornecido verbatim pelo autor em 2026-11-11. | `09-rascunho-s12.md`, `15_consolidar_manuscrito.py`, `18-declaracoes.md` |
| `test_declaracao_de_ia_continua_em_aberto_e_declarada_como_tal` | A *Declaration of generative AI and AI-assisted technologies in the | `18-declaracoes.md`, `MANUSCRITO.md` |
| `test_citacoes_narrativas_nomeiam_o_autor_onde_o_colchete_e_sujeito` | Pedido do autor em 2026-11-11: referir-se aos autores "quando for o | `03-rascunho-s1-s2-s3.md` |
| `test_mapa_de_numeros_para_chaves_e_bijetivo_e_por_titulo` | O mapa número -> chave, gravado em 2026-11-11. | `12-referencias.md`, `referencias.bib` |
| `test_declaracao_de_ia_segue_a_politica_lida_na_fonte` | Acrescentada em 2026-11-11, com a política da Elsevier LIDA na fonte | `18-declaracoes.md`, `18_conformidade.py`, `19_tex.py` |

## estrutural (33)

| teste | decisão protegida | arquivos |
| --- | --- | --- |
| `test_15_exige_doze_secoes` | The consolidator must now expect twelve, so a lost Section 12 is a gap | `09-rascunho-s12.md`, `15_consolidar_manuscrito.py` |
| `test_15_recusa_resumo_partido_em_vez_de_truncar` | On 2026-10-28 the abstract was rewritten with a line beginning '--', | `15_consolidar_manuscrito.py` |
| `test_16_reconcilia_a_unidade_de_contagem` | Author 2026-10-28: the report must declare its unit of count and not | `16_matriz_rastreabilidade.py` |
| `test_16_chama_a_reconciliacao_de_estatica` | Author 2026-10-28: the AST count of parametrised cases is adequate for | `16_matriz_rastreabilidade.py` |
| `test_16_check_confronta_a_matriz_com_os_testes` | Author's condition 2: being generated does not make the stored matrix | `16_matriz_rastreabilidade.py`, `docs/matriz-rastreabilidade.md` |
| `test_16_declara_a_categoria_e_nao_a_infere` | The matrix must take each test's category from a declared pytest | `16_matriz_rastreabilidade.py`, `pyproject.toml` |
| `test_15_consolida_sem_perder_nem_inventar` | The consolidated manuscript is a build step over the drafts. It must | `08-rascunho-s5.md`, `15_consolidar_manuscrito.py` |
| `test_14_veredicto_de_uma_linha_nao_pode_ser_truncado` | The author's partition run of 2026-10-27 was piped through `tail -20` | `14_etapa_b_por_procedimento.py` |
| `test_07_culpa_a_raiz_certa_pelo_modulo_que_falta` | Author's run, 2026-10-27: the handler for the pgsg2 import block blamed | `07_raman_lambda1.py` |
| `test_13_nao_esconde_um_sd_nao_nulo_atras_do_arredondamento` | Author's Raman run, 2026-10-27: the table printed sd as 0.0000 in all | `13_dependencia_do_sort.py` |
| `test_12_nao_chama_verificada_uma_figura_sem_entradas` | Reproducibility of a procedure is not conformity of a submitted file. | `12_verifica_figuras.py`, `pyproject.toml` |
| `test_09_garante_dtype_antes_de_comparar_bits` | view(np.int64) presupposes the array really is float64, which the | `09_controle_deslocamento.py` |
| `test_16_nao_emite_linha_semantica_sem_fonte` | A semantic row with no source is a broken traceability link. | `16_matriz_rastreabilidade.py` |
| `test_15_emite_a_materia_de_frente_fora_da_numeracao` | Front matter, added 2026-10-29 after the second reading of the guide. | `02-resumo-C.md`, `10-highlights.md`, `11-palavras-chave.md` |
| `test_17_varre_os_rascunhos_que_a_ordem_declara` | The scanner takes its file list from the consolidator's ORDEM, not from | `00-estrutura.md`, `02-resumo-C.md`, `06-legendas-figuras.md` |
| `test_18_nao_chama_de_mistura_o_que_e_ingles_britanico` | The guide: "write in American or British English but not a combination | `18_conformidade.py` |
| `test_18_separa_prosa_autoral_de_citacao_literal` | The author's decision of 2026-10-29: a verbatim quotation is reproduced | `18_conformidade.py` |
| `test_codigo_de_saida_nao_contradiz_o_veredito_impresso` | Found in the author's run of 2026-11-02: 18_conformidade.py printed | `12-referencias.md`, `17_citacoes.py`, `18_conformidade.py` |
| `test_19_recusa_caractere_nao_mapeado_em_vez_de_emitir` | The LaTeX build maps every non-ASCII character explicitly and stops on | `19_tex.py` |
| `test_19_pesa_colunas_pela_media_e_pela_palavra_mais_longa` | Column widths proportional to the LONGEST cell is the obvious rule and | `19_tex.py` |
| `test_15_carrega_o_titulo_do_artigo` | The consolidated manuscript had no title: its only top-level heading | `00-estrutura.md`, `15_consolidar_manuscrito.py` |
| `test_16_nao_lista_como_fonte_o_que_nao_e_arquivo` | The author's matrix of 2026-11-02 listed M.md as a guarded source in two | `16_matriz_rastreabilidade.py`, `17_citacoes.py`, `MANUSCRITO.md` |
| `test_raiz_do_repositorio_nao_acumula_arquivo_solto` | Two files named `source` and `test` were committed to the repository | `README.md`, `pyproject.toml` |
| `test_19_numera_pela_profundidade_e_recusa_desencontro` | The numbers LaTeX prints must be the numbers the manuscript wrote. | `19_tex.py` |
| `test_19_nao_leva_a_regua_do_markdown_para_a_legenda` | Figure 5's caption ended with a dash in the 31-page PDF. It was the | `19_tex.py` |
| `test_artefato_versionado_nao_pode_ficar_desatualizado` | A generated file kept under version control can go stale, and a stale | `MANUSCRITO.md`, `MANUSCRITO.tex`, `scripts/15_consolidar_manuscrito.py` |
| `test_parecer1110_a_forma_da_kl_declarada_e_a_do_codigo` | A equação escrita na §2.3 tem de ser a que o código avalia. Este teste | `pgsg_v3.py` |
| `test_parecer1110_figuras_entram_na_escala_em_que_foram_desenhadas` | Apresentação. `width=\linewidth` em todas as cinco ampliava as três | `19_tex.py` |
| `test_parecer1110_figura3_nao_se_redesenha_em_outro_ambiente` | O painel (b) da Figura 3 é específico do ambiente POR CONSTRUÇÃO: o | `10_figuras.py` |
| `test_decisao1110_a_condicional_da_91_e_sustentada_pelos_dados` | O autor condicionou a §9.1: *"se houver configurações com perda | `agregado.csv` |
| `test_decisao1110_a_trava_cobre_a_figura_2_tambem` | O autor pediu a proteção para todas as figuras dependentes de | `10_figuras.py` |
| `test_bibliografia_sai_sem_justificacao_esticada` | Inspeção do PDF definitivo, 2026-11-10. | `19_tex.py` |
| `test_bib_modo_cite_nao_toca_o_preambulo_nem_publica_a_auditoria` | Pedido do autor em 2026-11-11: `\cite{}` contra o `.bib`, não `[6]` | `19_tex.py` |

## numerico (10)

| teste | decisão protegida | arquivos |
| --- | --- | --- |
| `test_14_mede_a_fronteira_e_nao_conta_empates` | The criterion for rule-dependence is a tie group spanning rank q, not | `14_etapa_b_por_procedimento.py` |
| `test_rascunho_usa_a_esperanca_exata` | The draft must report the EXACT hypergeometric expectation of the | `01-rascunho-resumo-e-s4.md` |
| `test_s9_reporta_p2_medido_e_nao_um_limite` | The bound was superseded by the measurement on 2026-10-26: P1 holds | `05-rascunho-s9-s10-s11.md` |
| `test_05_nao_afirma_que_o_padrao_desempata_por_indice` | Mandatory correction, author 2026-10-27 (F008): the script used to print | `05_diagnostico_jaccard.py`, `13_dependencia_do_sort.py` |
| `test_13_mede_a_dependencia_do_sort_sem_inferir_ambiente` | F008: every top-q selection uses a bare np.argsort, whose default is not | `13_dependencia_do_sort.py` |
| `test_09_usa_o_espacamento_dos_valores_observados` | The plateau sits in [0.5, 1), where float32 spacing is 2**-24. An | `09_controle_deslocamento.py` |
| `test_f007_corrige_o_espacamento_e_separa_proveniencia` | The two corrections the author required on 2026-10-26, recorded in the | `F007-o-controle-de-deslocamento-e-o-plato.md` |
| `test_17_resolve_marcadores_e_ordem_de_aparicao` | The three arithmetic checks the guide's reference rules reduce to: | `17_citacoes.py` |
| `test_f009_mede_a_grade_e_separa_o_que_nao_afeta` | F009, measured from the stored wavelength grid on 2026-10-29: the grid | `F009-a-grade-de-ondas-e-a-terceira-regiao-do-prior.md`, `gates_n1158.npz` |
| `test_15_concilia_a_contagem_declarada_com_a_tabela1` | The manuscript said eight of twenty pre-registered hypotheses were not | `00-estrutura.md`, `02-resumo-C.md`, `03-rascunho-s1-s2-s3.md` |

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
