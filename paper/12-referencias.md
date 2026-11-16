# Referências — estado, auditoria e entradas prontas

Data: 2026-10-29, com as decisões do autor de 2026-11-09
Status: **COMPLETO** — esta linha é lida por `scripts/17_citacoes.py`.

## Decisões do autor de 2026-11-09, e o que elas fecham

Quatro decisões. Três fecham sem bibliografia nenhuma e **estão aplicadas**; a
quarta identifica o fundador e deixa só os metadados em aberto.

**1. Bandas NIR — REVERTIDA em 2026-11-09, no mesmo dia.** A decisão era
condicional e a condição é falsa. O autor escreveu: *"Se foram definidos pelos
autores, descrevê-los como uma escolha metodológica."* Não foram. A §4.4 de
`[2]`, publicada, diz textualmente: *"For NIR, the prior is a fixed step
function over three **literature-derived** spectral regions relevant to dry
matter content — 680–700 nm (chlorophyll), 900–1000 nm (second C–H overtone),
and 1100–1200 nm (first C–H overtone) **[5]**"*, e essa `[5]` é o Saranwong de
2004, que aqui é a `[7]`.

Então o ramo aplicado era o errado, por falta da fonte, que existia. A §2.2 e
a legenda da Figura 1 voltaram a atribuir as janelas à literatura, agora com
referência. **O que permanece da decisão:** os três *níveis* são nossos e o
texto diz isso, e a frase de que nada no artigo depende de as janelas serem as
certas ficou — ela não era parte da retirada, era ganho, e vale igual com
fonte. A frase que generalizava para *"the ordinary way to encode published
band assignments"* **não** voltou: aquela era atribuição sem fonte sobre a
prática alheia, e continua fora.

**1b. O que a decisão original dizia, para registro.** *"Não apresentar os intervalos 680–700, 900–1000
e 1100–1200 nm como universalmente estabelecidos sem fonte específica. Se foram
definidos pelos autores, descrevê-los como uma escolha metodológica
fundamentada na análise espectral, sem atribuir validação externa
inexistente."* A §2.2 passou a dizer que as três janelas e os três níveis são
escolha dos autores e não especificação tirada de fonte, e acrescenta que nada
no artigo depende de serem as janelas certas — o que vale é o prior ter um
conjunto de nível maior que o conjunto selecionado. A legenda da Figura 1
idem. A frase que generalizava para *"the ordinary way to encode published band
assignments"* perdeu a atribuição. **Esta linha deixa de precisar de fonte.**

**2. Razão `q/(2L−q)`, §2.5 — rota B aplicada.** *"Enfraquecendo a afirmação
para aquilo que foi efetivamente demonstrado, sem inventar uma referência."* A
§2.5 e a §4.2.1 deixaram de afirmar o que terceiros fazem. A atribuição passou
a ser nossa, com o `F004` atrás: *"that is what we had done ourselves, treating
it as the exact value, until the correction recorded here"* e *"which we had
used ourselves as if it were exact"*. O título da §2.5 mudou de *"how it is
usually computed"* para *"how we had computed it"*, e a palavra `familiar` saiu
da §4.2.1 — era a última atribuição sem fonte. O artigo deixa de dizer que a
literatura erra e passa a dizer que nós erramos e corrigimos.

**3. `pgsg_1` R2 — aplicada.** *"Não citar resultados não publicados como
evidência independente. Se forem necessários à narrativa, identificá-los
explicitamente como observações preliminares dos autores, sem tratá-los como
publicação."* A §2.4, onde os dados da revisão entram, passou a declarar o que
eles são: material não publicado dos próprios autores, rodado sob o protocolo
publicado, de um manuscrito que não foi aceito e não será ressubmetido, usado
como observação preliminar e não como evidência publicada ou independente. O
resumo **não** foi tocado: a expressão `from our own earlier work` já tinha
saído dele na compressão, e o que resta é `at the revision convention of
q = 29`, que não afirma publicação.

**4. Fundador — identificado pelo autor, metadados em aberto.**

O autor declarou em 2026-11-09, com base no README do repositório público
`pgsg_0_corrigendum`, que o artigo fundador é:

> *"Prior-guided spectral gating for interpretable deep learning in
> near-infrared spectroscopy"*, Chemometrics and Intelligent Laboratory
> Systems, volume **277** (2026), artigo **105833**.

**Procedência desta linha, para não confundir dois graus de verificação:** isto
é **declaração do autor**, que é o autor do artigo e do repositório. Não é
leitura minha na fonte. Eu tentei ler esse repositório cinco vezes e o GitHub
recusou por limite de requisições em todas; a busca na web não traz nenhum
registro publicado do volume 277, artigo 105833. O que eu li na fonte, no
repositório `pgsg2-nir-raman-gating`, foi só a citação do artigo de
**modalidades**.

O que a identificação fecha e o que não fecha:

| campo | estado |
| --- | --- |
| título, periódico, volume, ano, número do artigo | declarados pelo autor |
| **DOI** | **aberto** — o próprio autor registra que não está confirmado |
| **lista definitiva de autores** | **aberta** — idem |

**E a identificação resolve o problema dos dois preprints sem escolha por
conveniência.** O título declarado pelo autor é o mesmo do preprint
`SSRN 6845520`, *"Prior-Guided Spectral Gating for Interpretable Deep Learning
in Near-Infrared Spectroscopy"*; o outro preprint, `SSRN 7070485`, tem título
diferente — *"…with End-to-End Optimization for NIR Spectroscopy: Scalable
Architecture for Interpretable Regression in Small-Sample Regimes"* — e esse é
o que o `README:30` chama de "Escala e amostras pequenas", rejeitado, e cujos
dados de sete tamanhos a decisão 3 acima declara como observações
preliminares. A correspondência é **por título**, não por data. Mesmo assim, o
preprint não é a referência: a referência é o artigo publicado, e os campos
que faltam são do artigo publicado.

**O corrigendum é entrada separada**, por decisão do autor: *"o artigo
publicado é a referência principal para a formulação fundadora, enquanto o
corrigendum deve ser citado separadamente quando o manuscrito discutir os erros
identificados e suas correções."* O autor registra que o README do corrigendum
documenta uma auditoria de reprodutibilidade — coluna de alvo mal identificada
no conjunto Tecator, diferenças entre execuções, inconsistências na reprodução
das correlações entre gates e priors — e que isso reforça não usar resultados
originais corrigidos como evidência independente. **Nada disso eu li; é
declaração do autor**, e não escrevi nenhum campo bibliográfico do corrigendum,
que também está em aberto.

### O corrigendum não foi respondido — 2026-11-09, segunda informação do autor

O autor informou que **o editor não respondeu a carta sobre o corrigendum**, e
que o fundador continua publicado sem as correções. Isso tem duas
consequências, e a primeira desfaz uma decisão dele de hoje mesmo.

**1. O corrigendum deixa de ser entrada bibliográfica.** Carta não respondida
não é publicação nem aceite: não tem periódico, volume, ano nem DOI, e não
existe forma de citá-la numeradamente. A decisão de *"citar o corrigendum
separadamente"* não é executável como referência. Se o manuscrito precisar
mencioná-lo, a forma é no corpo do texto — *"a correction has been submitted"*
— e não uma entrada na lista. **Isso reduz o bloqueio do `--strict` a um
registro só: DOI e autores do artigo publicado.**

**2. O artigo cita, como origem da formulação, um trabalho publicado cujos
erros os autores conhecem e que o registro não corrigiu.** Isso não é questão
bibliográfica, é de integridade, e é do autor. O que eu posso fazer é medir a
exposição **deste** artigo, e ela é menor do que parece.

Os três achados que o autor atribui ao README do corrigendum, confrontados com
o que este manuscrito usa:

| achado do corrigendum | este artigo depende? | medido |
| --- | --- | --- |
| coluna de alvo mal identificada no conjunto **Tecator** | **não** | `Tecator` não aparece em nenhum rascunho, achado ou documento deste repositório. Os dados aqui são manga (NIR) e `bioprocess_substrates` (Raman) |
| diferenças entre execuções de redes neurais | **não para número publicado** | a única figura publicada que este artigo reproduz é `0,9418 → 0,7005 ± 0,0068`, e o `F004:97` a atribui ao **artigo aceito** — modalidades — não ao fundador |
| inconsistências na reprodução das correlações gate–prior | **não** | as correlações deste artigo, ρ(gate, prior) de 0,9987 a 0,9999, são medição própria, registrada no `F001`, da varredura de λ deste repositório. Não são reprodução de valor do fundador |

E o que sobra atribuído ao fundador, depois das decisões de hoje, é **menos do
que ontem**: a construção do prior passou a ser declarada escolha metodológica
dos autores (decisão 1), então restam a **formulação** — citada na §1 como a
prática que o artigo examina — e o **protocolo**, incluindo a convenção
`q = 28`.

**E aqui há uma ambiguidade que esta notícia torna mais urgente.** O `F004:12`
chama `q = 28` de *"a definição do código publicado"*, e a §2.4 do manuscrito
diz *"the published ablation of the earlier study"*. Mas o `F004:97` atribui a
célula de 0,9418 ao **artigo aceito**. Há dois trabalhos publicados ou aceitos
no programa, e *"o código publicado"* não distingue qual. Enquanto não
distinguir, não se sabe se a convenção `q = 28` que este artigo declara vem do
fundador — o artigo com erros não corrigidos — ou de modalidades. **É o
problema dos três destinos outra vez, e agora ele importa para mais do que uma
referência.**

### As saídas, e nenhuma é minha

**(a) Citar o fundador como publicado, com uma frase de divulgação.** Uma
sentença, na §2 ou na §10, dizendo que os autores identificaram erros naquele
artigo, que uma correção foi submetida ao editor e não está publicada, e o que
este artigo toma e não toma dele. É o padrão em integridade de publicação,
custa uma frase, e a medição acima é o que a sustenta: nenhum resultado afetado
entra aqui.

**(b) Citar o fundador como publicado, sem comentário.** A medição defende: o
artigo não reproduz nenhum resultado afetado. Mas deixa o leitor sem aviso, e
um referee que conheça o corrigendum pode ler mal.

**(c) Reduzir o que é atribuído ao fundador ao mínimo** — prioridade da
formulação — e atribuir o protocolo explicitamente a modalidades onde for de
modalidades. Exige resolver primeiro de qual trabalho publicado vem `q = 28`,
que é a ambiguidade acima.

A minha inclinação é **(a)**, e ela não depende de resolver (c): a frase pode
dizer o que se sabe e calar sobre o que não se sabe. Mas a atribuição de
`q = 28` precisa ser resolvida de todo modo, porque hoje a §2.4 afirma uma
origem que o repositório não distingue.

### Fechado em 2026-11-09, com os PDFs na mão

O autor entregou os PDFs dos dois publicados e do submetido, e tudo o que
estava em aberto por falta de fonte fechou:

| antes | agora |
| --- | --- |
| fundador: DOI e autores em aberto | **lidos na primeira página do PDF**: quatro autores, vol. 277 (2026), art. 105833, DOI |
| modalidades: *in press*, sem DOI | **publicado**: vol. 280 (2027), art. 105926, DOI. O meu registro anterior vinha da linha de citação do repositório, que estava desatualizada |
| bandas NIR: sem fonte | a §4.4 de `[2]` as chama de *literature-derived* e cita a sua `[5]`, o Saranwong de 2004 — que aqui é a `[7]` |
| `q = 28`: de qual trabalho publicado | **de `[2]`**: ele usa manga n = 1448 e Raman glicose n = 6472, os dados deste artigo, e reporta o 0,9418. O fundador usa Tecator e Gasoline, que não aparecem aqui |
| PLS: fonte canônica | a `[4]` de `[1]`, Wold, Sjöström e Eriksson 2001 — aqui a `[9]` |
| corrigendum | não é entrada: o editor não respondeu |

**Uma consequência que muda a §1.** O prior do fundador **não é de
literatura**: o resumo dele diz que os gates são inicializados a partir de
medidas de importância de variável — ANOVA F, VIP, Random Forest. Quem usa
prior de literatura é `[2]`. Por isso a §1 cita `[1]` como a origem do
mecanismo e `[2]` como a prática que este artigo examina, e não o contrário.

**E a exposição ao fundador não corrigido encolheu de novo.** O achado do
corrigendum sobre o Tecator é sobre um conjunto que o fundador usa e este
artigo não; a figura publicada que reproduzimos é de `[2]`. A saída (a) —
uma frase de divulgação — continua em aberto e é do autor.

## Proposta de 2026-11-09: sete referências que o próprio texto pede

Status desta seção: **APROVADA E APLICADA em 2026-11-09** — seis das sete.

O autor aprovou A–F e manteve a G fora *"até sua leitura e verificação"*. E
fixou a moldura, que é o conteúdo da mudança e não um efeito dela: na §2.5, a
correção por acaso tem antecedentes, a razão `q/(2L−q)` é aproximação e não a
esperança exata do Jaccard, e a contribuição deste trabalho é a esperança
exata sob empates no platô com a regra de desempate; na §1, a novidade entra
como contribuição específica sobre **empates e quantização**, e não como a
descoberta de que é preciso corrigir por acaso. O teste confere as duas
molduras, inclusive pela negativa: a frase que reivindicaria a descoberta não
pode aparecer.

O autor observou que nove referências é pouco. Medi antes de propor: varri o
manuscrito por frases que afirmam algo sobre uma prática ou uma literatura e
não carregam marcador. Dezessete apareceram, e a maioria é o artigo sendo
cuidadoso em **não** afirmar — *"we make no claim about how widely this
affects the band-selection literature"*. Mas a varredura não pega a lacuna
maior, que é de método e não de frase.

### A lacuna que importa: o nível de acaso já tem literatura

**O §4 deste artigo deriva a esperança exata da sobreposição entre duas
seleções top-q sob um modelo hipergeométrico. Kuncheva fez isso em 2007.**
Lido na fonte: o índice de consistência dela parte de que, para `A` fixo de
tamanho `k` em `n` variáveis, `|A ∩ B|` de um `B` aleatório é hipergeométrico,
com `E[r] = k²/n`, e corrige o índice por esse valor. Nogueira, Sechidis e
Brown generalizaram em 2018, no JMLR, com propriedades declaradas e intervalos
de confiança.

Isto **não** diminui a contribuição do artigo — a esperança exata do *Jaccard*,
e não da interseção, sob empate no platô, é outra conta, e a demonstração de
que a regra de desempate decide o resultado é nova. Mas um referee de
quimiometria que conheça a literatura de estabilidade de seleção vai notar a
ausência, e a leitura mais natural da ausência é desfavorável. Com as duas
citadas, a §2.5 fica mais forte, não mais fraca: a razão `q/(2L−q)` que nós
usávamos era uma aproximação **quando já existia correção exata publicada**.

### A segunda lacuna: a tese tem parentes diretos

O artigo argumenta que a estabilidade de um gate pode refletir o prior e não
os dados. O análogo exato existe e é muito citado: Adebayo e co-autores
mostraram, em 2018, que alguns mapas de saliência são **independentes do
modelo e do processo gerador dos dados**, e propuseram testes de aleatorização
para detectá-lo; Jain e Wallace mostraram, em 2019, que pesos de atenção não
correspondem a importância e que distribuições muito diferentes dão a mesma
predição. A frase *"stability does not validate the interpretation it is
usually offered to support"* é dessa família e hoje aparece sozinha.

### As sete, com onde entrariam

| # | onde | a frase que a pede | referência |
| --- | --- | --- | --- |
| A | §1 | *"reported as a Jaccard index and compared, when it is compared at all, against an intuition of what chance would give"* | Kuncheva 2007 |
| B | §2.5 e §4.2 | o nível de acaso exato, e a razão que usávamos antes | Kuncheva 2007, Nogueira 2018 |
| C | §1.1 e §9 | *"stability does not validate the interpretation it is usually offered to support"* | Adebayo 2018 |
| D | §1 | a leitura de que o gate alto é a banda informativa | Jain e Wallace 2019 |
| E | §2.2 | as atribuições de banda, segunda fonte além do Saranwong | Workman e Weyer 2012 |
| F | §2.1 | o conjunto manga: o artigo, além do depósito de dados | Anderson et al. 2020 |
| G | §2.2 | *"the one-standard-error rule"* | **não verificada** — a fonte canônica é um livro-texto e eu não a li; não proponho campo nenhum sem ler |

### Os registros, e como cada um foi obtido

- **Kuncheva 2007** — L. I. Kuncheva, *A stability index for feature
  selection*, Proceedings of the 25th IASTED International Multi-Conference:
  Artificial Intelligence and Applications, 2007, pp. 390–395. **Lido o PDF
  no sítio da autora**, incluindo a definição do índice e a esperança
  hipergeométrica; veículo e páginas confirmados numa segunda fonte
  independente.
- **Nogueira, Sechidis e Brown 2018** — *On the stability of feature selection
  algorithms*, Journal of Machine Learning Research 18 (174) (2018) 1–54.
  **Lido na página do JMLR.**
- **Adebayo, Gilmer, Muelly, Goodfellow, Hardt e Kim 2018** — *Sanity checks
  for saliency maps*, Advances in Neural Information Processing Systems 31,
  2018. **Lido na página da conferência**, com a lista de autores na ordem.
- **Jain e Wallace 2019** — *Attention is not explanation*, Proceedings of the
  2019 Conference of the NAACL: HLT, Volume 1, Association for Computational
  Linguistics, 2019, pp. 3543–3556, doi 10.18653/v1/N19-1357. **Lido na ACL
  Anthology.**
- **Workman e Weyer 2012** — *Practical guide and spectral atlas for
  interpretive near-infrared spectroscopy*, 2ª ed., CRC Press. Procedência de
  segundo grau: é a `[2]` da lista de `[2]`.
- **Anderson, Walsh, Subedi e Hayes 2020** — *Achieving robustness across
  season, location and cultivar for a NIRS model for intact mango fruit dry
  matter content*, Postharvest Biology and Technology 168 (2020) 111202.
  Procedência de segundo grau: é a `[4]` da lista de `[2]`. Note que **não é**
  a mesma entrada que o depósito de dados, que já é a `[3]`.

### O que eu não proponho

Não proponho citar preprocessamento (SNV, linha de base, despiking): **este
artigo não declara pré-processamento nenhum**, e citar o que não se faz seria
pior do que não citar. Não proponho a fonte do Adam: o otimizador não é
nomeado na prosa do manuscrito. E não proponho encher a introdução com
panorama de quimiometria profunda — o artigo é estreito de propósito, e uma
introdução larga enfraqueceria o escopo que a §2.2 acabou de declarar.

### O que ainda bloqueia o `17_citacoes.py --strict`

Depois destas quatro decisões, sobrou isto:

| entrada | o que falta | quem fecha |
| --- | --- | --- |
| ~~fundador~~ | **fechado**: lido no PDF | resolvido |
| ~~corrigendum~~ | **não é mais entrada** — carta não respondida não é citável; se entrar, entra no corpo do texto | resolvido |
| modalidades | nada — sai como *in press*, sem DOI porque não existe | pronto |
| §1, *"a prior derived from the literature"* | passa a citar o fundador, que é publicação da própria prática | fecha com o fundador |

Ou seja: **nenhum**. O `17_citacoes.py --strict` sai 0 desde 2026-11-09.

Duas coisas, que não bloqueiam e ficam registradas: a `[7]` e a `[9]` foram
lidas em listas de referências e não nos artigos citados, e devem ser
conferidas antes da submissão; e o trabalho em submissão, *Prior
Specification Bounds What Spectral Attention Can Learn*, **não** é citado —
citar trabalho em submissão é decisão dos autores e não foi tomada, embora
ele trate do mesmo gate saturado das §§3 e 9.

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

## References

Numbered by order of first appearance in the manuscript, which
`scripts/17_citacoes.py` checks. Each entry's provenance is in the table
below the list.

[1] S. Jain, B.C. Wallace, Attention is not explanation, in: Proceedings of the 2019 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies, Volume 1 (Long and Short Papers), Association for Computational Linguistics, Minneapolis, 2019, pp. 3543–3556. https://doi.org/10.18653/v1/N19-1357

[2] J. Adebayo, J. Gilmer, M. Muelly, I. Goodfellow, M. Hardt, B. Kim, Sanity checks for saliency maps, in: Advances in Neural Information Processing Systems 31, 2018.

[3] G. Coelho, A. de Lima das Chagas, L.C. Carneiro, C.J. Coelho, Prior-guided spectral gating for interpretable deep learning in near-infrared spectroscopy, Chemometrics and Intelligent Laboratory Systems 277 (2026) 105833. https://doi.org/10.1016/j.chemolab.2026.105833

[4] G. Coelho, C.J. Coelho, Gate topology and reproducibility of Prior-Guided Spectral Gating across near-infrared and Raman spectroscopy, Chemometrics and Intelligent Laboratory Systems 280 (2027) 105926. https://doi.org/10.1016/j.chemolab.2026.105926

[5] P. Jaccard, The distribution of the flora in the alpine zone, New Phytologist 11 (2) (1912) 37–50. https://doi.org/10.1111/j.1469-8137.1912.tb05611.x

[6] L.I. Kuncheva, A stability index for feature selection, in: Proceedings of the 25th IASTED International Multi-Conference: Artificial Intelligence and Applications, 2007, pp. 390–395.

[7] S. Nogueira, K. Sechidis, G. Brown, On the stability of feature selection algorithms, Journal of Machine Learning Research 18 (174) (2018) 1–54.

[8] N. Anderson, K. Walsh, P. Subedi, J. Walsh, Mango DMC and spectra Anderson et al. 2020, Mendeley Data, version 3, 2024. https://doi.org/10.17632/46htwnp833.3

[9] N. Anderson, K. Walsh, P. Subedi, C.H. Hayes, Achieving robustness across season, location and cultivar for a NIRS model for intact mango fruit dry matter content, Postharvest Biology and Technology 168 (2020) 111202. https://doi.org/10.1016/j.postharvbio.2020.111202

[10] C. Lange, M. Altmann, D. Stors, S. Seidel, K. Moynahan, L. Cai, S. Born, P. Neubauer, M.N. Cruz Bournazou, Deep learning for Raman spectroscopy: benchmarking models for upstream bioprocess monitoring, Measurement 258 (2026) 118884.

[11] C. Lange, SubstrateMixRaman, Hugging Face Datasets, chlange/SubstrateMixRaman, 2025.

[12] M. Koddenbrock, C. Lange, R. Legner, M. Jaeger, M. Kögler, M.N. Cruz Bournazou, P. Neubauer, F. Bießmann, E. Rodner, RamanBench: a large-scale benchmark for machine learning on Raman spectroscopy, arXiv:2605.02003, 2026. To appear in NeurIPS 2026 (Track on Evaluations and Datasets).

[13] S. Saranwong, J. Sornsrivichai, S. Kawano, Prediction of ripe-stage eating quality of mango fruit from its harvest quality measured nondestructively by near infrared spectroscopy, Postharvest Biology and Technology 31 (2) (2004) 137–145. https://doi.org/10.1016/j.postharvbio.2003.08.007

[14] J. Workman Jr., L. Weyer, Practical Guide and Spectral Atlas for Interpretive Near-Infrared Spectroscopy, second ed., CRC Press, 2012. ISBN 978-1-4398-7525-4.

[15] T. Hastie, R. Tibshirani, J.H. Friedman, The Elements of Statistical Learning: Data Mining, Inference, and Prediction, second ed., Springer, 2009.

[16] C.R. Harris, K.J. Millman, S.J. van der Walt, et al., Array programming with NumPy, Nature 585 (2020) 357–362.

[17] F. Wilcoxon, Individual comparisons by ranking methods, Biometrics Bulletin 1 (1945) 80–83. https://doi.org/10.2307/3001968

[18] S. Wold, M. Sjöström, L. Eriksson, PLS-regression: a basic tool of chemometrics, Chemometrics and Intelligent Laboratory Systems 58 (2) (2001) 109–130. https://doi.org/10.1016/S0169-7439(01)00155-1

[19] S. Kullback, R.A. Leibler, On information and sufficiency, Annals of Mathematical Statistics 22 (1) (1951) 79–86. https://doi.org/10.1214/aoms/1177729694

[20] D.A. McAllester, PAC-Bayesian model averaging, in: Proceedings of the 12th Annual Conference on Computational Learning Theory, ACM, 1999, pp. 164–170. https://doi.org/10.1145/307400.307435

[21] P.L. Bartlett, S. Mendelson, Rademacher and Gaussian complexities: risk bounds and structural results, Journal of Machine Learning Research 3 (2002) 463–482.

### Procedência de cada entrada, que não é a mesma para todas

| n | como o registro foi obtido |
| --- | --- |
| [1] | **lido na ACL Anthology**: autores, veículo, páginas, DOI |
| [2] | **lido na página da conferência**: os seis autores na ordem, NeurIPS 2018 |
| [3] | **lido no PDF do artigo**, primeira página |
| [4] | **lido no PDF do artigo**, primeira página |
| [5] | **lido o PDF do artigo**: autor, periódico, vol. 11 nº 2, pp. 37–50, 1912; DOI do registro da Wiley |
| [6] | **lido o PDF no sítio da autora**; veículo e páginas confirmados numa segunda fonte |
| [7] | **lido na página do JMLR** |
| [8] | lido no depósito da Mendeley Data |
| [9] | **parcialmente confirmado em 2026-11-10**: periódico, vol. 168, nº de artigo 111202 e ano conferem com dois registros independentes dos próprios autores (repositório institucional e a publicação relacionada do depósito Mendeley). **A linha de autores foi lida** no repositório, que imprime *Nicholas Anderson, Kerry Walsh, Phul Subedi, CH Hayes*: as iniciais do meio que o registro de segundo grau trazia (T., B., P.) e o prenome *Chris* não aparecem em nenhuma fonte alcançável e foram removidos. **O DOI foi resolvido em 2026-11-11** (quarta passagem) |
| [10] | lido na fonte; conferido contra a lista de [4] |
| [11] | lido na fonte; conferido contra a lista de [4] |
| [12] | lido na fonte; conferido contra a lista de [4] |
| [13] | **LIDO NO EDITOR em 2026-11-10, e o registro de segundo grau ESTAVA ERRADO**: trazia 253–261 da lista de [4]; o artigo é 31(2), 137–145, DOI 10.1016/j.postharvbio.2003.08.007. **Reconferido no mesmo dia num segundo índice independente**, que traz vol. 31 e 137–145 e confirma a correção. Prenomes reduzidos às iniciais: nenhuma fonte alcançável imprime um |
| [14] | **lido no editor em 2026-11-10**: autores, edição, selo, ano e ISBN 978-1-4398-7525-4 conferem com o registro de segundo grau vindo da lista de [4] |
| [15] | **lido num registro bibliográfico**: autores, título e subtítulo, 2ª ed., Springer, 2009, ISBN 0387848576. A série não é impressa lá e por isso não entra |
| [16] | citação pedida pelo próprio projeto NumPy |
| [17] | **lido na documentação do `scipy.stats.wilcoxon`**, que é a função que o nosso código chama, e que também confirma ser o teste de postos sinalizados sobre diferenças pareadas |
| [18] | **confirmado em 2026-11-10** contra três catálogos independentes: vol. 58 nº 2, 2001, 109–130, e o DOI lido ali. Prenomes **reduzidos às iniciais** no mesmo dia: nenhuma fonte alcançável imprime um, todas dão `S. Wold, M. Sjöström, L. Eriksson`, e a entrada passa a carregar as iniciais lidas em vez dos prenomes de segundo grau (lista de [3]) |
| [19] | **completa em 2026-11-10**: título, autores, periódico, vol. 22 nº 1, ano e DOI vêm da URL canônica do Project Euclid; **o intervalo 79–86 foi lido pelo autor correspondente** no sumário do volume no JSTOR e conferido contra outros índices, e entrou por essa leitura. O Project Euclid recusara três leituras aqui por verificação de navegador, e nenhuma sessão que montou este arquivo teve navegador conectado. **Em momento algum a faixa foi escrita de memória** |
| [20] | **confirmado em 2026-11-10 contra DOIS índices independentes** que reproduzem o registro da ACM: autor e afiliação, veículo (COLT '99), ano, páginas 164–170 e DOI `10.1145/307400.307435` conferem nos dois com a entrada, que viera da lista do primer de Guedj. A página da própria ACM não é alcançável daqui, então os campos repousam nos índices e não no registro em si — nenhum deles veio de memória |
| [21] | **lido o PDF no JMLR**: cabeçalho com volume, páginas e ano |

### Auditoria de 2026-11-10: o que mudou

As cinco entradas de segundo grau foram conferidas uma a uma. **Uma estava
errada**: a `[13]`, de Saranwong, trazia o intervalo de páginas 253–261
copiado da lista de referências de [4]; o artigo é **31(2), 137–145**. Não é
detalhe de estilo — é a citação que sustenta as três janelas NIR, e teria ido
ao periódico apontando para páginas que não existem nesse artigo. As outras
quatro conferiram nos campos que foi possível ler, e três ganharam o DOI ou o
ISBN que faltava.

Nenhuma entrada carrega mais a marca `segundo grau` sozinha: cada uma diz
agora o que foi lido, onde, e o que continua por ler.

Desde 2026-11-11 **não há campo pendente**: a última lacuna era o DOI da `[9]`,
fechada na quarta passagem abaixo. Nenhum campo deste arquivo foi escrito de
memória — o que não foi lido não está no `.bib` nem na lista.

### Segunda passagem, 2026-11-10

A `[19]`, de Kullback e Leibler, **deixou de estar incompleta**: o autor
correspondente leu o intervalo **79–86** no sumário do volume no JSTOR e o
conferiu contra outros índices, e o campo entrou por essa leitura. O Project
Euclid havia recusado três tentativas aqui por verificação de navegador.

Três entradas perderam prenomes que ninguém tinha lido. A regra aplicada é a
mesma nas três: **onde nenhuma fonte alcançável imprime um prenome, a entrada
carrega a inicial que as fontes imprimem**, em vez do prenome herdado de uma
lista de referências. Vale para a `[13]` (Saranwong), a `[18]` (Wold) e a
`[9]` (Anderson), esta última com a linha de autores lida no repositório
institucional dos próprios autores.

Um prenome plausível é mais perigoso que uma inicial, porque passa por
verificado.

### Terceira passagem, 2026-11-10: as duas últimas pendências

A `[20]` fechou: um **segundo** índice independente reproduz o registro da ACM
inteiro — autor e afiliação, COLT '99, ano, 164–170 e o DOI — e confere com a
entrada. A página da própria ACM continua inalcançável daqui, o que está
escrito na nota: os campos repousam em dois índices que reproduzem o registro,
não no registro em si.

O **DOI da `[9]` não foi obtido**, após cinco tentativas por rotas distintas:
a página do editor e o ScienceDirect não são alcançáveis daqui, o x-mol e o
scilit responderam com verificação de navegador, o repositório institucional
não imprime DOI, e o depósito Mendeley dá o PII `S0925521420301629` mas só o
DOI do próprio conjunto de dados.

**O PII não foi convertido em DOI.** O padrão da Elsevier tornaria fácil
escrever `10.1016/j.postharvbio.2020.111202`, e é precisamente por ser fácil
que não foi escrito: seria um campo plausível e não lido, que é o que esta
auditoria existe para impedir. A entrada seguiu sem DOI, dizendo por quê.

### Quarta passagem, 2026-11-11: o DOI da [9], resolvido

O autor correspondente forneceu o DOI, e ele **foi resolvido** antes de
entrar: `doi.org`, o resolvedor do próprio registro, redireciona
`10.1016/j.postharvbio.2020.111202` para o PII **`S0925521420301629`** — o
mesmo PII que o depósito Mendeley dos autores dá para este artigo, lido ali em
2026-11-10.

A distinção importa e está escrita na nota. A cadeia é resolvedor + depósito,
não o padrão de nomes da Elsevier. O padrão teria produzido **a mesma
cadeia de caracteres** sem evidência nenhuma, e foi recusado por isso na
véspera; o que mudou não foi o valor do campo, foi existir prova de que ele
designa este artigo. Um campo certo pelo motivo errado continua sendo um campo
sem leitura.

A página do editor segue inalcançável daqui, o que também está na nota.

**Um defeito encontrado ao escrever o DOI.** A redução de prenomes de
2026-11-10 alcançara o `.bib` e **não** a lista numerada, que é o que o
manuscrito publica: a `[9]` ainda saía no PDF como `N.T. Anderson, K.B. Walsh,
P.P. Subedi`, com as três iniciais do meio que haviam sido removidas por nunca
terem sido lidas. O teste da véspera conferia só o `.bib` e por isso não viu.
Corrigido nos dois, e o teste passa a conferir a **lista impressa**: corrigir
um lado e não o outro é pior que não corrigir, porque faz este arquivo
descrever algo que o leitor não recebe. As `[13]` e `[18]` já estavam certas
na lista.

**Com isso a auditoria fecha**: nenhuma entrada tem campo por ler.
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

## Mapa de números para chaves BibTeX

Estabelecido em 2026-11-11, por **pareamento de títulos** entre a lista
numerada e o `paper/referencias.bib`, exigindo bijeção: 21 para 21, cada
título casando com exatamente uma chave e cada chave com exatamente um
número. Não foi inferido de nomes de chave — há dois Anderson, dois Lange e
dois Coelho no arquivo, e parear por nome de chave citaria o artigo errado.

O mapa existe para que o `19_tex.py --bib` emita `\cite{}` sem recalcular
nada no momento do build. Um pareamento por heurística a cada compilação
seria uma decisão silenciosa sobre qual obra está sendo citada.

| nº | chave BibTeX |
| --- | --- |
| [1] | `jain2019attention` |
| [2] | `adebayo2018sanity` |
| [3] | `coelho2026pgsg` |
| [4] | `coelho2027gatetopology` |
| [5] | `jaccard1912flora` |
| [6] | `kuncheva2007stability` |
| [7] | `nogueira2018stability` |
| [8] | `anderson2024mango` |
| [9] | `anderson2020mango` |
| [10] | `lange2026raman` |
| [11] | `lange2025substratemix` |
| [12] | `koddenbrock2026ramanbench` |
| [13] | `saranwong2004mango` |
| [14] | `workman2012nir` |
| [15] | `hastie2009elements` |
| [16] | `harris2020numpy` |
| [17] | `wilcoxon1945ranking` |
| [18] | `wold2001pls` |
| [19] | `kullback1951information` |
| [20] | `mcallester1999pacbayes` |
| [21] | `bartlett2002rademacher` |

A numeração continua sendo **por ordem de primeira aparição**, e o estilo
`unsrt` numera do mesmo jeito, de modo que os números gerados pelo BibTeX
têm de coincidir com os desta tabela. Essa coincidência é verificada, não
suposta.
