# Declarações e matéria de submissão

Data: 2026-10-26

Este arquivo reúne a matéria de submissão que o manuscrito ainda não tem, com a
**procedência de cada exigência declarada**. Duas categorias, nunca misturadas:

- **Confirmado** — texto lido na fonte oficial, com a data que a própria fonte
  mostra.
- **Não verificado** — exigência plausível, de guia genérico ou de instrução
  histórica, que **não** foi lida no Guide for Authors vigente da revista.

A segunda categoria não entra no manuscrito até ser lida. Uma regra aplicada por
analogia com outra revista da mesma editora é uma suposição, e já temos o hábito
de conferir suposições nesta pesquisa.

---

## 1. Declaração de IA generativa — CONFIRMADO

Fonte: Elsevier, *Generative AI policies for journals*, política de periódicos
da editora, com **"Policy updated June 2026"** na própria página. É política de
periódicos, não formatação específica da revista, e vale salvo declaração em
contrário no guia do Chemolab.

O que a política estabelece, em resumo e com o que importa aqui citado:

- **Cabeçalho exigido, literal:** *"Declaration of generative AI and
  AI-assisted technologies in the manuscript preparation process"*.
- **Posição:** declaração separada, no manuscrito, na submissão; ela
  **aparece no artigo publicado**.
- **Forma recomendada:** *"During the preparation of this work, the author(s)
  used [NAME OF TOOL / SERVICE] in order to [REASON]"*, mais a extensão da
  supervisão dos autores.
- **Não exige declaração:** *"Basic checks of grammar, spelling and punctuation
  do not need a declaration statement."*
- **IA como autor:** proibido. *"Authors should not list AI tools as an author
  or co-author, nor cite AI tools as an author."*
- **IA no método de pesquisa** (distinta da preparação do texto): descrita de
  modo reprodutível na seção de métodos — *"The use of the tools must be
  described in a reproducible manner in the Methods section"* — com nome,
  versão e desenvolvedor quando aplicável.
- **Figuras:** ilustração explicativa permitida com divulgação na legenda;
  **visualização de dados** só se derivada dos dados por método reprodutível
  descrito nos métodos; imagens de dados primários não podem ser criadas ou
  alteradas por IA; resumo gráfico não pode usar ferramenta genérica de imagem.

As cinco figuras deste manuscrito são geradas por `scripts/10_figuras.py` a
partir dos dados, versionado no repositório — são visualizações de dados por
método reprodutível descrito, que é o caso que a política permite. Nenhuma foi
produzida por ferramenta de imagem.

**Isso documenta a origem das figuras e não demonstra a conformidade dos
arquivos submetidos.** São afirmações diferentes, e só a segunda é o que chega
ao leitor do artigo. `scripts/12_verifica_figuras.py` confere a segunda em três
etapas separadas — entradas alcançáveis, execução completa, e conteúdo do PDF
regerado contra o comitado, comparado por rasterização porque o matplotlib
grava uma data de criação e a igualdade de bytes falha em figuras idênticas.
Uma figura cujas entradas não existem é relatada como **não verificável**,
nunca como verificada e nunca como errada.

A primeira execução dessa verificação encontrou uma divergência real no painel
(b) da Figura 3, registrada em `findings/F008`. Ela não é obsolescência do
arquivo: é dependência do algoritmo de ordenação. Enquanto o F008 não for
decidido, nenhuma das cinco figuras deve ser descrita como verificada.

### 1.1 Texto proposto para o manuscrito

> **Declaration of generative AI and AI-assisted technologies in the manuscript
> preparation process**
>
> During the preparation of this work the author used Claude (Anthropic)
> [and NAME EVERY OTHER TOOL USED] in order to draft and revise manuscript
> text, to assist in the critical review of the analysis, and to write and
> verify the analysis and figure-generation code. This assistance does not
> constitute independent scientific validation of the analyses, results or
> conclusions, for which the author remains solely responsible. The author
> reviewed and edited all output, corrected substantive errors in it, and takes
> full responsibility for the content of the publication. The analysis code is
> versioned in the repository cited in the data availability statement, so each
> reported quantity can be recomputed independently of how the code was
> written.

Quatro observações sobre esse texto, para o autor decidir e não para ser aceito
como está:

1. **Ele declara o escopo inteiro.** A política dispensa declaração para
   verificação básica de gramática e ortografia, e o auxílio aqui foi além
   disso: redação de seções, revisão científica e desenvolvimento de código. A
   declaração reflete isso. Encolhê-la para "assistência de redação" seria
   impreciso.
2. **"Assist in the critical review" não é validação.** Revisão crítica feita
   com auxílio de IA e validação científica independente são coisas diferentes,
   e a frase seguinte diz isso explicitamente em vez de deixar o leitor
   inferir. A responsabilidade pelas análises, resultados e conclusões é do
   autor, e a declaração afirma isso em vez de sugerir uma corroboração que não
   houve.
3. **O colchete não é descuido: é o que eu não sei.** Houve mais de uma
   ferramenta de IA no processo, e eu só posso atestar a que escreveu os
   patches desta sessão. As outras têm de ser nomeadas por quem as usou, e a
   declaração está errada enquanto o colchete estiver lá.
4. **Versão da ferramenta — e o limite da minha própria evidência.** A política
   pede nome, versão e desenvolvedor *quando aplicável*, no contexto de método.
   O identificador configurado desta sessão é `claude-opus-5`, mas o modelo que
   atende uma requisição pode diferir do configurado e mudar ao longo de uma
   sessão longa, e esta foi longa. Uma referência à *família* do modelo também
   não está sustentada pelos registros que eu posso oferecer. O defensável é
   nomear fornecedor e ferramenta — Claude (Anthropic) — sem atribuir versão.

### 1.2 O que a declaração **não** cobre

O modelo PGSG não é IA generativa auxiliando a preparação do manuscrito: é o
objeto da pesquisa. Ele pertence aos métodos, onde já está. Declarar o PGSG
nesta seção confundiria o leitor sobre o que foi assistido e o que foi
estudado.

---

## 2. Lido no guia vigente — CONFIRMADO em 2026-10-28

Fonte: *Guide for authors*, Chemometrics and Intelligent Laboratory Systems,
ScienceDirect. Citado literalmente onde o guia é literal.

| exigência | o guia diz | estado do manuscrito |
| --- | --- | --- |
| **resumo** | *"You are required to provide a concise and factual abstract which does not exceed 250 words."* | **conforme desde 2026-10-28**: 249 palavras, uma de margem; era 304, e a compressão está na §2.3 |
| **highlights** | *"Highlights should consist of 3 to 5 bullet points, each a maximum of 85 characters, including spaces."*; *"Submit highlights as a separate editable file in the online submission system"*, *"with the word 'highlights' included in the file name"* | **no manuscrito desde 2026-10-29**, antes do resumo e fora da numeração; a fonte do arquivo separado é `paper/10-highlights.md`, cujo nome já carrega a palavra; **falta** a conversão para o formato editável do envio |
| **palavras-chave** | *"You are required to provide 1 to 7 keywords for indexing purposes."*; *"Keywords should be written in English."*; *"Please try to avoid keywords consisting of multiple words (using 'and' or 'of')."* | **no manuscrito desde 2026-10-29**, depois do resumo; as quatro regras conferidas uma a uma em `paper/11-palavras-chave.md`. O guia **não diz** onde elas entram: a posição é convenção adotada |
| **página de título** | *"Provide the given name(s) and family name(s) of each author"*; afiliação por letra superscrita minúscula; *"Ensure that you provide the full name and postal address of each affiliation, including the country name"*; *"The email address of the corresponding author must be included on the title page and will be published in the article"* | **ausente** — o manuscrito não tem página de título. Depende de fatos dos autores: nomes, afiliações com endereço postal e país, e o e-mail do autor correspondente |
| **agradecimentos** | *"Acknowledgements should be placed in a separate section which appears directly before the reference list."* | ausentes; se houver, a posição está fixada |
| **resumo, autossuficiência** | *"Abstracts must be able to stand alone, as abstracts are often presented separately from the article."* | **um ponto aberto**, na §2.4 |
| **disponibilidade de dados** | *"you are encouraged to state the availability of any data at submission"*; política de dados Opção C: depositar e citar, ou declarar por que não pode ser compartilhado | **ausente**; os fatos a conferir estão na §3 |
| **declaração de IA** | *"Authors must declare the use of generative AI tools in the manuscript preparation process upon submission of the paper."* | texto pronto na §1.1, pendente de nomear as outras ferramentas |
| **conflito de interesses** | *"The declarations tool should always be completed"*; quem não tem nada a declarar escolhe *"I have nothing to declare"*; enviado como `.doc`/`.docx`; assinaturas não exigidas | **ausente** |
| **CRediT** | o autor correspondente reconhece as contribuições dos coautores pelos papéis CRediT, 14 categorias | **ausente** |
| **numeração de seções** | *"Divide your manuscript into clearly defined and numbered sections"*, subseções 1.1, 1.1.1; *"Do not include the article abstract within section numbering"* | **conforme**: doze seções, decimal, resumo fora da numeração |
| **referências** | número entre colchetes no texto, numeradas por ordem de aparição, periódicos abreviados pela LTWA; no envio qualquer estilo consistente é aceito | a conferir na montagem final |
| **figuras** | vetor em EPS ou PDF, **fontes embutidas**; legenda em cada item; cada figura citada no texto | **conforme**: as cinco são PDF vetorial, `pdffonts` reporta `emb=yes` em todas, DejaVu subsetado |
| **tabelas** | texto editável, não imagem; sem réguas verticais nem sombreamento | a conferir na montagem final |
| **idioma** | *"We recommend that you write in American or British English but not a combination of both."* | **medido em 2026-10-29** por `scripts/18_conformidade.py`: inglês britânico em todo o manuscrito, com **uma** exceção — `initialization`, dentro da citação em bloco da §9.3 que o texto apresenta como declaração dos autores. Decisão do autor, na §2.5 |
| **formato do fonte** | `.doc`/`.docx` ou `.tex`; coluna única no Word; *"A PDF is not an acceptable source file."* | o manuscrito está em Markdown; a conversão é etapa de envio |
| limite global do artigo | nenhum declarado para artigos completos; comunicações curtas não passam de quatro páginas impressas | não aplicável |
| resumo gráfico | o guia não menciona | não aplicável |

### 2.1 Highlights — aprovados em 2026-10-28

Os cinco, aprovados pelo autor, com as funções que ele atribuiu a cada um:
mecanismo do desempate, magnitude observada, inércia localizada,
aprendizagem fora do platô e recomendação metodológica. A contagem é de
caracteres com espaços, medida e não estimada; o limite é 85.

| chars | texto |
| --- | --- |
| 78 | Top-q overlap depends on the tie rule when the boundary cuts equal gate values |
| 79 | The same stored gates gave overlaps of 0.744 to 1.000 across sorting procedures |
| 80 | Prior-based initialisation makes the saturated level unresponsive to the penalty |
| 79 | Gates align with a separate statistical reference at the prior's 223-band floor |
| 73 | Check boundary ties before reading overlap as reproducible band selection |

**Três foram corrigidos em 2026-10-28, por conteúdo e não por estilo.** Um
highlight é lido sozinho, sem a frase que o define ao lado, e as três redações
anteriores não sobreviviam a essa leitura:

1. `Gates align with a separate reference at the prior's floor, not at its
   plateau` afirmava o que a legenda da Figura 5 **recusa explicitamente**: um
   resultado mais fraco no platô não é evidência de ausência lá, e a ausência
   de diferença demonstrada entre os níveis não demonstra que se comportem
   igual. A nova redação diz onde o alinhamento foi medido — as 223 bandas do
   piso — e não afirma nada sobre o platô.
2. `Prior-based initialisation leaves the saturated level operationally inert`
   usava um termo que só existe no resumo, onde a cláusula do gradiente o
   define. Isolado num bullet, `inert` convida à leitura de imobilidade
   matemática, que o F007 refuta: `max |d|` no platô fica entre 1,2×10⁻⁶ e
   6,7×10⁻⁶, pequeno e **não nulo**. A nova redação nomeia o que não responde
   e a que não responde: a penalidade.
3. `under different sort rules` fundia implementação de ordenação e regra
   explícita de desempate, que o F008 separa — 0,9452–0,9867 e 0,7443–0,7659
   são a mesma regra em duas construções do numpy, e 1,0000 é outra regra.
   `across sorting procedures` cobre as duas fontes de variação sem igualá-las.

### 2.2 Palavras-chave — aprovadas em 2026-10-28

Seis, dentro do limite de sete: band selection; interpretability; prior-guided
gating; near-infrared spectroscopy; Raman spectroscopy; reproducibility.

### 2.3 O resumo contra o limite — resolvido em 2026-10-28

304 palavras, limite 250, excesso **54**. O resumo está hoje em **249**.

**Primeiro, a correção de um número meu.** Eu relatei que a compressão sem
remoção de conteúdo chegava a **253**, três acima. Esse número era inválido:
a rota que o produzia removia quatro fragmentos que o conjunto de testes
exige do resumo, todos da decisão editorial de 2026-10-25 — `is immune to
this artefact`, `lowers it by 0.018 (Pearson) or 0.051 (Spearman)`, `at the
largest sample size` e `what survives still responds to n`. Eu havia
inventariado 17 fragmentos obrigatórios; são **21**, em quatro funções de
teste, somando **145 palavras literais** das 250 do limite. O inventário
passou a ser extraído das próprias asserções por AST, e não de uma lista
reescrita à mão, porque uma lista reescrita foi exatamente o que falhou.

**O piso real da compressão é 266 palavras**, com os 21 fragmentos intactos e
toda a redação auxiliar comprimida: 38 palavras saíram de redação auxiliar
(abertura encurtada, procedência dita uma vez em vez de duas, `and we separate
them` dispensado pelos dois-pontos, quatro substituições por formas mais
curtas). Sobravam 16 acima do limite, e a redação auxiliar restante no texto
era de cerca de 20 palavras — das quais 14 eram a frase de contextualização.
Logo 250 **não era alcançável** com aquela frase mantida, e a decisão deixou
de ser qual sinônimo usar.

**As últimas 17 palavras saíram por três decisões do autor, de 2026-10-28:**

| palavras | decisão |
| --- | --- |
| 14 | a frase de contextualização sai: *"Interpretive stability in prior-guided spectral attention is usually reported as top-k overlap across runs."* O enquadramento passa a ser feito na §1, e o autor registrou que a versão sem ela é cientificamente mais importante do que ela |
| 1 | `281 near-infrared bands` → `281 bands`: a modalidade é nomeada na frase seguinte, `The near-infrared prior meets all three` |
| 2 | `at the revision data's own convention of q = 29` → `at the revision convention of q = 29`, preferida pelo autor a cortar o verbo `examine`, cujo corte deixaria `disentangle X from Y and their effects` sintaticamente ambíguo |

**Recusado pelo autor:** escrever `0.7005±0.0068` sem espaços em torno do ±
para o contador registrar um token em vez de três. Economizava as duas
palavras sozinha, e seria explorar uma particularidade do contador em vez de
melhorar o texto.

**O que a compressão não tocou**, e que a verificação automatizada demonstra a
cada execução: a enumeração das três condições; a distinção entre
possibilidade geométrica e ocorrência efetiva (`permits an artefact but does
not produce one`); o modelo nulo hipergeométrico nomeado com o seu q = 28; o
controle de deslocamento com as duas quedas medidas; as oito refutações
declaradas; a cláusula do gradiente, que é o que define `operationally inert`
dentro do resumo; as duas convenções de decil, separadas nos seus resultados.

A contagem é de tokens separados por espaço em branco, que é o que o contador
do Word aproxima. A margem é de **uma palavra**, e é margem medida, não
estimada.

### 2.4 Segunda leitura do guia, 2026-10-29 — e o que ela abriu

A primeira leitura respondeu ao limite do resumo, aos highlights e às
palavras-chave. A segunda foi atrás de onde cada coisa entra no manuscrito, e
trouxe três itens que a primeira não tinha.

**1. O resumo precisa ser autossuficiente, e no ponto em que a compressão
mexeu ele deixou de ser.** O guia: *"Abstracts must be able to stand alone, as
abstracts are often presented separately from the article."* O resumo diz
`an overlap of 0.9418, at that codebase's convention of q = 28` — e `that
codebase` não tem antecedente dentro do resumo desde que `from our own earlier
work` saiu da terceira frase, em 2026-10-28. A única menção ao trabalho
anterior vem depois, em `Our earlier displacement-based control`, e um
demonstrativo que aponta para frente não se sustenta num texto lido isolado.

A correção mais barata **não custa palavra nenhuma**: `at that codebase's
convention of q = 28` → `at the published convention of q = 28`. Duas palavras
por duas, 249 continuam 249, o demonstrativo desaparece, e fica em paralelo
com `at the revision convention of q = 29`, que a compressão já deixou
autossuficiente. **É decisão do autor**, porque é um fragmento exigido pelo
conjunto de testes, e o texto não foi alterado aqui.

**2. A instrução de posição da declaração de IA é contraditória no próprio
guia.** Ele diz *"The statement will appear in the published work and should be
placed in a new section before the references list"* e também que a declaração
*"must be declared by adding a statement at the end of the manuscript when the
paper is first submitted"*. As duas não se reconciliam, e a escolha não é
registrada aqui como exigência lida. Na montagem, seção própria imediatamente
antes das referências satisfaz a primeira e fica no fim do corpo do texto, o
que é a leitura mais defensável da segunda — mas é escolha, não leitura.

**3. Conflito de interesses não é seção do manuscrito.** O guia:
*"The resulting Word document containing your declaration should be uploaded at
the 'attach/upload files' step"*. É um arquivo do sistema de envio, gerado pela
ferramenta de declarações, e não um parágrafo do texto. Disponibilidade de
dados, CRediT e financiamento não têm posição declarada no guia.

## 3. Ainda NÃO VERIFICADO, e o que falta não é o guia

O manuscrito **não tem nenhum destes itens hoje**. A coluna "estado atual" é
inventário, não julgamento de conformidade, porque a exigência não foi lida.

Três itens saíram desta tabela em 2026-10-28, por terem sido lidos no guia e
passado para a §2: o limite do resumo, os highlights e as palavras-chave. O
que sobra aqui não depende do guia, e sim de fatos dos autores.

| item | estado atual no manuscrito | o que falta saber |
| --- | --- | --- |
| declaração de disponibilidade de dados | ausente | forma exigida; o Mango DMC v3 é público e o repositório também |
| disponibilidade de código | ausente no manuscrito, presente de fato | se a revista exige declaração própria ou cobre no item anterior |
| declaração de IA generativa | ausente | nada: confirmada na seção 1 |
| CRediT, financiamento, conflito de interesses | ausentes | forma exigida |
| figuras, tabelas, suplementar | 5 figuras em PDF, 5 legendas, 1 tabela | formato, resolução, limite de quantidade |

**A instrução histórica de 50 a 250 palavras é de 1992 e não entra aqui.** Ela
fica registrada como a origem da escolha de 250 feita na redação, não como
regra vigente. Se o guia atual disser outro número, o resumo muda; se disser
250, a coincidência foi sorte e não validação.

**Resolvido em 2026-10-28:** o guia vigente diz 250, e a coincidência com a
instrução de 1992 foi sorte. O parágrafo acima fica como estava, porque é o
registro de uma suposição que foi conferida e não de uma regra que mudou.

**As duas contagens do resumo não são um menu.** 251 por espaço em branco e 246
por tokens alfanuméricos são duas medidas do mesmo texto, e escolher a menor
porque ela cabe seria decidir a regra depois de ver o resultado — o erro que
este programa recusa em toda parte. A ordem é: identificar a regra vigente;
então medir por ela. Se o limite confirmado for 250 e a revista não declarar
convenção de contagem, a recomendação é **reduzir com margem**, para algo em
torno de 240, preservando os resultados quantitativos essenciais: 0.9418,
0.7005 ± 0.0068, a condição do platô e a frase do controle de deslocamento.
251 não é uma infração demonstrada — é uma margem que não existe.

**O princípio valeu, e a recomendação de 240 não foi seguida.** A ordem foi
mantida: o limite foi identificado primeiro, no guia, e só então o texto foi
medido por ele. Os 240 com margem folgada não eram alcançáveis — o piso da
compressão com os 21 fragmentos obrigatórios intactos é 266 (§2.3) —, e o
autor decidiu em 2026-10-28 ficar em 249, com uma palavra de margem, em vez
de retirar um compromisso científico para comprar folga.

---

## 4. Um arquivo de declarações não é uma declaração pronta

Disponibilidade de dados, disponibilidade de código, financiamento, conflitos
de interesses e contribuições CRediT dependem de **fatos** que precisam ser
conferidos antes de qualquer afirmação definitiva, e não apenas da forma que a
revista exige.

Em particular, não se declara disponibilidade pública de dados ou de código sem
confirmar que os materiais estão efetivamente acessíveis **nas condições
descritas**. Para este trabalho isso significa, no mínimo: que o repositório
está acessível a quem não é o autor; que o Mango DMC v3 continua obtenível pela
via que o artigo citar; que os `gates_r2` versionados bastam para reproduzir o
que o artigo afirma a partir deles; e que o que **não** está no repositório —
`results/raman_h12`, `cells.json`, os diretórios de partição `p*`, as raízes
`pgsg_1` e `pgsg_2` — está nomeado como indisponível em vez de implicitamente
coberto por uma frase de disponibilidade. O `12_verifica_figuras.py` já lista
quais faltam.

## 5. Como fechar

O guia recusou leitura automatizada em 2026-10-26 e respondeu em 2026-10-28;
a §2 é a conferência item por item que ele permitiu fazer, com citação
literal. Nada entra como conforme por analogia, e o que a §2 marca como *a
conferir na montagem final* — referências, tabelas, idioma, conversão do
formato do fonte — continua não conferido.

Falta, e depende de fatos que só os autores têm: nomear as outras ferramentas
de IA na declaração da §1.1; a declaração de conflito de interesses pela
ferramenta da revista; as contribuições CRediT; e a declaração de
disponibilidade de dados nas condições que a §4 lista. Os highlights e as
palavras-chave estão aprovados e ainda não inseridos no manuscrito.

---

## 6. Conformidade medida, 2026-10-29

`scripts/18_conformidade.py` mede o que das exigências do guia é aritmética
sobre o texto, e nada do que ele mede é juízo sobre a escrita.

**Dois defeitos encontrados e corrigidos no mesmo dia.** A Figura 2 — a
sobreposição por regra de desempate contra a esperança hipergeométrica exata,
uma das figuras centrais — **não era citada em lugar nenhum do texto**, e o
guia exige que cada figura seja citada. Passou a ser citada onde o resultado
de desempate aleatório é reportado, que é o que ela mostra. E as legendas
tinham cabeçalho em português, `## Figura N`, copiado para um manuscrito em
inglês; rascunho e gerador passaram a dizer `## Figure N`.

**Um ponto aberto, de uma linha.** O manuscrito é britânico de ponta a ponta —
`initialisation` 25 vezes, `randomised`, `behaviour`, `modelling`, `analysed`,
`centred` — com uma única forma americana: `initialization`, em
`05-rascunho-s9-s10-s11.md:84`, dentro da citação em bloco que a §9.3
apresenta como *"The statement we make is the author's"*. Não a alterei: o
bloco é o dispositivo que este programa usa para marcar texto do autor que eu
não reescrevo. As duas saídas defensáveis são grafá-la `initialisation`, por
ser prosa dos próprios autores adotada no artigo, ou mantê-la e aceitar a
mistura que o guia desaconselha. É decisão do autor.

**Não contado como mistura:** `program` (código) contra `programme` (projeto),
e `license` (verbo) contra `licence` (substantivo). O inglês britânico usa as
duas formas de cada par, e o manuscrito usa cada uma corretamente; um
verificador que as apontasse empurraria um texto correto para o errado.

---

## 7. As quatro decisões de 2026-10-29

| item | decisão do autor | estado |
| --- | --- | --- |
| resumo | usar `at the published convention`, **desde que q = 28 continue explícito ao lado** | **aplicado**; 249 palavras, sem custo, e o guarda do teste exige o `q = 28` ao lado |
| §2.5 | rota A se o procedimento deriva de metodologia publicada; se for definição original do estudo, a atribuição deve ser nossa | **condicional, e a condição não foi satisfeita**: a busca de 2026-10-29 não achou fonte que use `q/(2L−q)` como nível de acaso. Registrado na §2.5 de `12-referencias.md`, com a ressalva de que não achar não demonstra não existir |
| `initialization` | manter verbatim dentro da citação literal; grafia britânica na redação autoral | **aplicado no verificador, não no texto**: `18_conformidade.py` passou a contar prosa autoral e citação literal **separadamente**, e o manuscrito não tem nenhuma forma fora da variante em prosa autoral |
| conversão | `.tex`, como formato principal | aceito; a montagem é o próximo incremento |

**O que a terceira decisão mudou no verificador, e por quê.** Antes ele exigia
uma única variante em todo o texto, e com isso pedia que uma citação literal
fosse alterada para satisfazer uma regra de redação — o que é pior do que a
mistura que a regra evita. Agora ele separa as duas populações pelos
marcadores de citação em bloco, relata as duas, e só conta defeito o que
estiver em prosa autoral. As legendas das figuras também são blocos citados em
Markdown, mas são texto autoral, e por isso voltam para o lado autoral antes
da contagem.

Com isso o manuscrito **não tem nenhum defeito no que esse verificador mede**:
uma variante em prosa autoral, as cinco figuras e a Tabela 1 citadas, legendas
contíguas. O `--strict` sai com 0.
