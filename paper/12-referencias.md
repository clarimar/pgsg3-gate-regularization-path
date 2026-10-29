# Referências — estado, auditoria e entradas prontas

Data: 2026-10-29
Status: **INCOMPLETO** — esta linha é lida por `scripts/17_citacoes.py`.

## O estado, medido

O manuscrito **não tem nenhuma citação e nenhuma lista de referências**. Medido
em 2026-10-29 por varredura dos rascunhos: nenhum marcador `[n]`, nenhuma
citação autor-ano, nenhum arquivo `.bib`, nenhum bloco `## References`. Não é
uma lista incompleta: é a ausência da seção.

Isso não aparecia como pendência porque a lista de montagem final dizia
"conferir referências (colchetes, LTWA)", o que pressupõe referências a
conferir. A pressuposição estava errada, e o registro corrige o enunciado em
vez de ajustar a conta.

O guia exige, literal: número entre colchetes no texto, numeradas por ordem de
aparição, periódicos abreviados pela LTWA.

## O que eu não faço aqui

**Nenhuma entrada é escrita de memória.** Uma referência inventada é pior do
que uma referência ausente: a ausência é visível e a invenção não. As entradas
abaixo têm a procedência de cada campo declarada, e o que falta está marcado
`[FALTA: ...]` em vez de preenchido por plausibilidade. Os campos marcados
dependem de arquivos que só os autores têm.

## Entradas prontas

Duas, com todos os campos lidos na fonte hoje.

- **[pronta-mango]** N. Anderson, K. Walsh, P. Subedi, J. Walsh, Mango DMC and
  spectra Anderson et al. 2020, Mendeley Data, V3, 2024.
  doi:10.17632/46htwnp833.3
  *Procedência:* contribuidores, título, publicador, versão, ano e DOI lidos no
  registro `data.mendeley.com/datasets/46htwnp833/3` em 2026-10-29. O registro
  **não** oferece citação pré-formatada; os campos vêm dos seus metadados, e a
  ordem dos nomes é a do registro. O registro descreve espectros de absorbância
  NIR de 309 a 1149 nm, o que confere com a grade medida em `findings/F009`.
  *A conferir:* se o artigo companheiro de Anderson et al. (2020) também deve
  ser citado, decisão que é dos autores e não deste arquivo.
- **[pronta-numpy]** C.R. Harris, K.J. Millman, S.J. van der Walt, R. Gommers,
  P. Virtanen, D. Cournapeau, et al., Array programming with NumPy, Nature 585
  (2020) 357–362. doi:10.1038/s41586-020-2649-2
  *Procedência:* a citação que o projeto pede, lida em `numpy.org/citing-numpy`
  em 2026-10-29, com a lista completa de 26 autores no BibTeX de lá. `Nature`
  já é a forma LTWA.

## O conjunto Raman, identificado em 2026-10-29

`bioprocess_substrates` e `RamanBench` não identificavam publicação alguma. A
busca fechou os dois, e a identificação do conjunto **é por concordância
aritmética e não por nome**, o que fica dito em vez de escondido.

- **[pronta-raman-origem]** C. Lange, M. Altmann, D. Stors, S. Seidel,
  K. Moynahan, L. Cai, S. Born, P. Neubauer, M.N. Cruz Bournazou, Deep
  learning for Raman spectroscopy: Benchmarking models for upstream
  bioprocess monitoring, Measurement 258 (2026) 118884.
  doi:10.1016/j.measurement.2025.118884
  *Procedência:* título, autores na ordem, periódico, volume 258 (Parte A),
  número de artigo e DOI lidos na página do artigo na ScienceDirect em
  2026-10-29. O artigo descreve *"a new reference dataset of 6960 annotated
  spectra"* e os oito substratos — glucose, glycerol, acetate, EnPump,
  nitrate, yeast extract, phosphate, sulfate.
- **[pronta-raman-deposito]** o depósito público do conjunto:
  `chlange/SubstrateMixRaman`, Hugging Face Datasets, licença CC BY 4.0.
  *Procedência:* ficha do conjunto lida em 2026-10-29: 6.960 linhas, 1.878
  colunas, oito alvos com glicose entre eles, e o ponteiro para o artigo
  acima como fonte do processo de criação.
- **[pronta-ramanbench]** M. Koddenbrock, C. Lange, R. Legner, M. Jaeger,
  M. Kögler, M.N. Cruz Bournazou, P. Neubauer, F. Bießmann, E. Rodner,
  RamanBench: A Large-Scale Benchmark for Machine Learning on Raman
  Spectroscopy, arXiv:2605.02003v1 [cs.LG], 3 de maio de 2026.
  *Procedência:* título, autores e identificador lidos na versão HTML do
  arXiv em 2026-10-29. É a via de acesso que o README nomeia, não a fonte do
  conjunto.

**Por que a identificação é defensável, e o que ela não é.** Três coincidências
exatas com o que o manuscrito já declara, nenhuma aproximada:

| o manuscrito declara | a ficha do depósito | o artigo de origem |
| --- | --- | --- |
| *"The source records 6960 spectra"* | 6.960 linhas | *"6960 annotated spectra"* |
| `p = 1870` deslocamentos Raman | 1.878 colunas = 1870 + 8 alvos | oito substratos |
| glicose como alvo da regressão | glicose entre os oito | glicose entre os oito |

O nome `bioprocess_substrates` **não aparece** em nenhuma das fontes: é o nome
local do conjunto no `pgsg_2`. A identificação é pela coincidência dos três
números, e é o autor quem a confirma — foi ele quem ingeriu o arquivo. O que
decide é se a ingestão do `pgsg_2` veio desse depósito; os 488 espectros sem
glicose descartados na ingestão são um quarto número que o autor pode conferir
contra o arquivo que tem em mãos.

## Entradas que dependem dos autores

| chave | o que o repositório já diz | o que falta |
| --- | --- | --- |
| `[autores-modalidades]` | *Gate Topology and Reproducibility of Prior-Guided Spectral Gating Across Near-Infrared and Raman Spectroscopy*, aceito no Chemometrics and Intelligent Laboratory Systems (ADR-0002, ADR-0003, README) | `[FALTA: lista de autores, ano, volume, número de artigo, DOI]`. O ADR-0003 registra **C. J. Coelho e G. Coelho** como os autores que decidiram a comunicação ao editor, o que não é a mesma coisa que a lista de autores do artigo, e eu não a deduzo daí |
| `[autores-fundador]` | o artigo fundador do programa, "NIR interpretável", publicado no Chemolab, com corrigendum proposto ao editor (README) | `[FALTA: título, autores, ano, volume, DOI]`. "Fundador" e "NIR interpretável" são rótulos internos do README e não identificam uma publicação |
| `[autores-incerteza]` | *Prior Specification Bounds What Spectral Attention Can Learn*, em submissão (README, ADR-0002) | `[FALTA: forma de citação de trabalho não publicado]`, e a decisão de citá-lo ou não |
| ~~`[autores-raman]`~~ | **resolvido em 2026-10-29**, abaixo | — |

## Dossiê: tudo o que o repositório registra sobre os dois artigos do programa

Reunido em 2026-10-29, a pedido do autor, para que a identificação seja feita
sobre o que está escrito e não sobre memória. Cada linha tem arquivo e linha.

**Modalidades** — o único com título completo registrado:

| onde | o que diz |
| --- | --- |
| `ADR-0002:14` | *"Gate Topology and Reproducibility of Prior-Guided Spectral Gating Across Near-Infrared and Raman Spectroscopy"* (aceito, Chemolab) |
| `ADR-0003:10` | o mesmo título, *"(aceito, Chemometrics and Intelligent Laboratory Systems)"*; e **"Decisão dos autores: C. J. Coelho e G. Coelho"** |
| `ADR-0002:16-21` | o que ele estabeleceu: 1.448 espectros NIR da safra 4 vêm de 725 frutos, 723 medidos duas vezes; e ΔR² = −0,108 ± 0,031 em dez divisões agrupadas, com PLS calibrado na partição de treino (1 EP, H entre 46 e 73) |
| `README:31` | "Modalidades NIR→Raman (*Gate Topology and Reproducibility…*) — **aceito** no Chemolab" |
| `README:37-38` | *"Citar o artigo de modalidades para a arquitetura"*, porque o manuscrito que introduziria a `PGSGv2Model` foi rejeitado |
| `F001:74` | ΔR² = −0,108 ± 0,031 citado como "do artigo de modalidades" |

**Fundador** — nenhum título registrado em lugar nenhum:

| onde | o que diz |
| --- | --- |
| `README:29` | "Fundador, NIR interpretável — publicado no Chemolab; corrigendum proposto ao editor" |
| `PROVENANCE.md:4` | o modelo veio de `pgsg_1/pgsg_v2.py`, repositório **`prior-guided-spectral-gating`** |
| `PROVENANCE.md:8-9` | *"Gerou todos os resultados publicados de pgsg_0/pgsg_1 e todos os de pgsg_2"* |
| `F002:130` | `make_literature_prior` é de `pgsg_1`, e é função degrau |
| `F004:12` | `q = p // 10 = 28`, *"a definição do código publicado"* |

**E aqui está a complicação que a identificação tem de resolver primeiro.**
As expressões *"our own earlier work"* (resumo e §3, o prior e os dados da
revisão R2) e *"the earlier study"* (§4.4 e §9.3, o controle de deslocamento)
podem apontar para **artigos diferentes**, e um deles não é citável como
publicado:

- `F004:8` diz que os vetores de gate dos sete tamanhos vêm da **revisão R2 do
  `pgsg_1`**, e qualifica: *"manuscrito **rejeitado**, não será
  ressubmetido"*. O `README:30` chama esse trabalho de "Escala e amostras
  pequenas", rejeitado. A `00-estrutura:415` o descreve como *"resultado real
  do pgsg_1 R2 que a rejeição deixou sem casa"*.
- Mas o `F004:9` acrescenta que a R2 rodou *"sob o protocolo publicado"*, e o
  `F004:12` chama `q = 28` de *"a definição do código publicado"* — ou seja,
  existe um artigo publicado cujo protocolo e código a R2 seguiu, que é o
  fundador.
- O `ADR-0003` liga a célula de 0,9418 e o controle de deslocamento ao artigo
  de **modalidades**, aceito.

Então, pelo que está escrito: o controle de deslocamento e o 0,9418 citam
**modalidades**; o prior e o protocolo citam o **fundador**; e os dados de sete
tamanhos vêm de um manuscrito **rejeitado**, que não tem referência publicada e
precisa ser declarado como dados não publicados dos próprios autores, se é isso
que o autor decidir. Três destinos, não um. Nenhuma dessas três atribuições é
minha para fechar.

## Auditoria dos pontos que exigem citação

Cada linha é uma frase que hoje está no manuscrito e que afirma algo cuja
sustentação está fora deste artigo. A coluna final diz quem pode fechar.

| § | a frase, encurtada | o que ela precisa | quem fecha |
| --- | --- | --- | --- |
| 1 | *"When a prior derived from the literature is used to guide that gate"* | ao menos uma fonte da prática que o artigo examina | autores |
| 2.1 | *"The mango dry-matter dataset, version 3, harvest 4 (DOI 10.17632/46htwnp833.3)"* | `[pronta-mango]`, e o DOI sai do corpo do texto para a referência | pronto |
| 2.1 | o conjunto Raman | `[autores-raman]` | autores |
| 2.2 | a arquitetura `PGSGv2Model` | `[autores-modalidades]` — o README determina: *"Citar o artigo de modalidades para a arquitetura"*, porque o manuscrito que a introduziria foi rejeitado | autores |
| 2.1 | os 1.448 espectros de 725 frutos, 723 medidos duas vezes | `[autores-modalidades]`, que estabeleceu esse fato (ADR-0002) | autores |
| 2.3 | *"680-700 nm (chlorophyll), 900-1000 nm (second C-H overtone), 1100-1200 nm (first C-H overtone)"* | as atribuições de banda são da literatura e hoje não têm fonte; é o prior inteiro do artigo | autores |
| 2.5 | *"the ratio q/(2L-q) that the band-selection literature uses"* | **é uma afirmação sobre a literatura sem uma única fonte.** Ou se cita quem usa a razão, ou a frase precisa ser enfraquecida para o que foi verificado | autores |
| 2.2 | PLS, coeficientes absolutos como referência | fonte canônica do PLS | autores |
| 2.4, 4.2.1 | `numpy.argsort` não é estável; a ordem segue a partição | `[pronta-numpy]`, e a ordenação em si | pronto |
| 4.4, 9.3 | *"the earlier study"*, o controle de deslocamento | `[autores-modalidades]` | autores |
| 3, 4 | *"our own earlier work"*, o prior e os dados da revisão R2 | `[autores-fundador]` | autores |
| 4.2, 9 | o gradiente de ordem 10⁻⁶ e o mecanismo da saturação | `[autores-incerteza]`, se os autores decidirem citar trabalho em submissão | autores |
| 2.2 | o otimizador, se nomeado nos métodos | fonte do Adam | autores |

## A frase da §2.5 — a alternativa não precisa de fonte nenhuma

O ponto mais exposto da auditoria tem saída sem depender de bibliografia, e é
decisão do autor entre duas rotas. **Nada foi alterado no texto.**

São duas frases, e as duas afirmam prática alheia sem fonte:

| onde | como está |
| --- | --- |
| §2.5 (`03-rascunho`, l. 221) | *"A chance level for a Jaccard index over a tied block of L bands is often quoted as q / (2L − q)."* |
| §4.2.1 (`01-rascunho`, l. 159) | *"We report the exact hypergeometric expectation E[J] = sum_k P(k) k/(2q-k), and not the ratio q/(2L-q) that the band-selection literature uses."* |

**Rota A — citar quem usa a razão.** Mantém as frases como estão e depende de
pelo menos uma fonte que use `q/(2L−q)` como nível de acaso. Só os autores
podem fechar.

**Rota B — afirmar só o que este repositório demonstra.** O `F004` registra, em
correção de 2026-10-24, que *este programa* usou `q/(2L−q)` como se fosse o
valor exato — *"usam a aproximação `q/(2L−q)` como se fosse o valor exato"* —
e o `F002` traz a derivação e os exatos, 0,701177 e 0,744473. Então a afirmação
pode ser sobre nós, verificável nos próprios achados:

- §2.5: *"A chance level for a Jaccard index over a tied block of L bands may
  be computed as q / (2L − q). That expression is not the expected Jaccard
  index."* — tira a afirmação sobre a prática de terceiros e mantém a
  matemática, que é o que o parágrafo precisa.
- §4.2.1: *"We report the exact hypergeometric expectation
  E[J] = sum_k P(k) k/(2q-k), and not the ratio q/(2L-q), which we had used
  ourselves as if it were exact."* — a atribuição passa a ser a nós, com o
  F004 por trás.

A rota B é a única que fecha sem bibliografia, e enfraquece a frase: o artigo
deixa de dizer que a literatura erra e passa a dizer que nós erramos e
corrigimos. É menos ambicioso e é o que está demonstrado.

### A decisão condicional do autor, e o que a busca achou

O autor decidiu em 2026-10-29: **rota A se o procedimento deriva de uma
metodologia publicada; se for definição original do estudo, a atribuição deve
ser nossa.** Isso transforma a decisão numa questão de fato, e a busca de
2026-10-29 não achou o fato que a rota A exige.

Procurei por fonte que use `q/(2L−q)` como nível de acaso do índice de Jaccard
em seleção de bandas ou de atributos. **Não encontrei nenhuma.** O que a
literatura de estabilidade tem é outra coisa, e relevante: medidas de
estabilidade de seleção de atributos com correção para o acaso, de que o
exemplar mais citado é *On the Stability of Feature Selection Algorithms*
(Nogueira & Brown, JMLR 18, 2017) — **cujo conteúdo eu não li e não verifiquei
aqui**, de modo que ele entra como pista e não como entrada.

**Não ter encontrado não demonstra que não exista**, e isso vale dito: uma
busca que falha é evidência fraca de ausência. Mas pela regra do próprio autor
o ônus é da rota A, e hoje ele não está cumprido; o que *está* demonstrado, no
F004, é que este programa usou a razão como se fosse exata. Logo a rota B é a
que o critério dele seleciona, e a rota A fica disponível se o autor conhecer a
fonte que eu não achei.

Uma terceira possibilidade, que é dele e não minha: citar a literatura de
estabilidade pelo **problema** — a necessidade de corrigir medidas de
sobreposição para o acaso — sem atribuir a ela a razão `q/(2L−q)`. Isso
sustentaria a §2.5 com bibliografia verificada sem afirmar o que não se
verificou. Exige ler Nogueira & Brown antes de citar.

## Como isto fecha

`scripts/17_citacoes.py` confere, e nenhuma dessas conferências é opinião:
que todo marcador `[n]` do texto resolve para uma entrada; que nenhuma entrada
fica sem ser citada; que a numeração segue a ordem de primeira aparição; e que
nenhuma entrada com `[FALTA:` entra numa lista declarada completa. Enquanto o
`Status` no alto deste arquivo for `INCOMPLETO`, o script o relata em vez de
aprovar, e a seção de referências não é emitida no manuscrito — uma lista
parcial emitida em silêncio é exatamente o que este programa recusa.
