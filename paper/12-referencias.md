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

## Entradas que dependem dos autores

| chave | o que o repositório já diz | o que falta |
| --- | --- | --- |
| `[autores-modalidades]` | *Gate Topology and Reproducibility of Prior-Guided Spectral Gating Across Near-Infrared and Raman Spectroscopy*, aceito no Chemometrics and Intelligent Laboratory Systems (ADR-0002, ADR-0003, README) | `[FALTA: lista de autores, ano, volume, número de artigo, DOI]`. O ADR-0003 registra **C. J. Coelho e G. Coelho** como os autores que decidiram a comunicação ao editor, o que não é a mesma coisa que a lista de autores do artigo, e eu não a deduzo daí |
| `[autores-fundador]` | o artigo fundador do programa, "NIR interpretável", publicado no Chemolab, com corrigendum proposto ao editor (README) | `[FALTA: título, autores, ano, volume, DOI]` |
| `[autores-incerteza]` | *Prior Specification Bounds What Spectral Attention Can Learn*, em submissão (README, ADR-0002) | `[FALTA: forma de citação de trabalho não publicado]`, e a decisão de citá-lo ou não |
| `[autores-raman]` | `bioprocess_substrates`, obtido via RamanBench, de `pgsg_2` (README) | `[FALTA: referência do RamanBench e do conjunto, com DOI se houver]` |

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

## Como isto fecha

`scripts/17_citacoes.py` confere, e nenhuma dessas conferências é opinião:
que todo marcador `[n]` do texto resolve para uma entrada; que nenhuma entrada
fica sem ser citada; que a numeração segue a ordem de primeira aparição; e que
nenhuma entrada com `[FALTA:` entra numa lista declarada completa. Enquanto o
`Status` no alto deste arquivo for `INCOMPLETO`, o script o relata em vez de
aprovar, e a seção de referências não é emitida no manuscrito — uma lista
parcial emitida em silêncio é exatamente o que este programa recusa.
