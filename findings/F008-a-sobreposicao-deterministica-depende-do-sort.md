# F008 — A sobreposição determinística depende do algoritmo de ordenação

Data: 2026-10-26
Autor do registro: assistente, sob revisão do autor
Estado: **medido num ambiente, pendente de medição no ambiente do autor**

## O que me levou até aqui

Eu não estava procurando isto. O autor pediu (ponto 3 de 2026-10-26) que
reprodutibilidade de procedimento não fosse confundida com conformidade
editorial: o fato de `scripts/10_figuras.py` ser versionado documenta a origem
das figuras, mas não demonstra que elas ainda se reproduzem. Escrevi
`scripts/12_verifica_figuras.py` para conferir isso e ele falhou — em três
figuras, por tamanho de página. Tamanho de página seria recorte do
`bbox_inches`, coisa de versão de biblioteca. Mas o texto extraído dos PDFs
mostrou outra coisa:

| | painel (b) da Figura 3, rótulos do eixo y |
| --- | --- |
| PDF comitado | 0,94  0,96  0,98  1,00 |
| PDF regerado aqui | 0,73  0,74  0,75  0,76  0,77  0,78 |

Mesmo arquivo de dados, versionado no repositório. Mesmo script, versionado.
Valores diferentes.

## O mecanismo, medido

Toda seleção top-q do programa está escrita assim, em nove lugares:

```python
np.argsort(g)[::-1][:q]
```

sem `kind=`. O padrão do numpy é `'quicksort'`, que é um introsort e **não é
estável**: a ordem entre valores exatamente iguais é definida pela
implementação e depende do arranjo do vetor inteiro, não só dos valores
empatados.

No platô, cada banda selecionada está empatada com todas as outras — é a
propriedade P1 do F007, igualdade exata dentro de cada execução, 70 de 70.
Logo o **conjunto** selecionado é decidido inteiramente pela regra de
desempate, e a sobreposição entre duas sementes mede essa regra, não os gates.

Medido em `data/processed/gates_r2`, q = ceil(0,10·281) = 29, platô L = 34,
dez sementes por tamanho:

| tamanho n | `stable` / `mergesort` | `quicksort` / `heapsort` / padrão | sorteado | E[J] em L |
| --- | --- | --- | --- | --- |
| 30 | 1,0000 | 0,7496 | 0,7442 | 0,7445 |
| 60 | 1,0000 | 0,7506 | 0,7442 | 0,7445 |
| 100 | 1,0000 | 0,7533 | 0,7442 | 0,7445 |
| 200 | 1,0000 | 0,7443 | 0,7442 | 0,7445 |
| 400 | 1,0000 | 0,7659 | 0,7442 | 0,7445 |
| 700 | 1,0000 | 0,7512 | 0,7442 | 0,7445 |
| 1158 | 1,0000 | 0,7550 | 0,7442 | 0,7445 |

Ambiente desta medição: numpy 2.5.3, Python 3.13, Linux (contêiner).
`scripts/13_dependencia_do_sort.py` reproduz a tabela e imprime a versão.

Com `kind="stable"`, em `gates_n100`, as dez sementes selecionam **o mesmo**
conjunto — os índices 202 a 230, que são os 29 últimos do platô 197–230, porque
`argsort` ascendente deixa empates em ordem de índice e o `[::-1]` a inverte.
Um conjunto distinto entre dez sementes, J = 1,0000 exatamente. Com o padrão:
**dez** conjuntos distintos, interseção par a par de 24 a 27 de 29.

## Três ambientes, três valores da mesma estatística

| | sobreposição determinística, sete tamanhos |
| --- | --- |
| aqui, `kind="stable"` | 1,0000 em todos |
| aqui, `kind` padrão (numpy 2.5.3) | 0,7443 a 0,7659 |
| ambiente do autor, conforme §4.2.1 e a Figura 3 comitada | 0,9452 a 0,9867 |

O manuscrito relata o terceiro. Ele não coincide com nenhum dos dois primeiros,
e é consistente com o PDF comitado — isto é, a Figura 3 **não está obsoleta**;
ela foi desenhada num ambiente cujo introsort deixa o bloco empatado quase, mas
não exatamente, em ordem de índice.

**Isto é uma medição de um ambiente, não do ambiente do autor.** A versão de
numpy da máquina do autor não foi medida, e inferi-la de um valor de Jaccard
seria exatamente o tipo de inferência que esta pesquisa não aceita. O
`13_dependencia_do_sort.py` resolve isso numa execução.

## O que isto afeta, e o que não afeta

**Não afeta o argumento central — reforça-o.** Uma quantidade que vai de 0,744
a 1,000 nos mesmos dados conforme o algoritmo de ordenação que rodou é tão
vazia quanto uma quantidade pode ser. A §4 já diz que, sob a regra
determinística, "the gate's contribution to the selected set is confined to the
order the sort leaves". O que esta medição acrescenta é que *the order the sort
leaves* não é uma coisa determinada: é uma escolha de implementação.

**Não afeta o número de que o manuscrito depende.** A regra sorteada dá 0,7442
aqui e 0,7442 ± 0,0063 na máquina do autor, contra E[J] = 0,7445 nos dois. A
quantidade em que o manuscrito se apoia reproduz entre ambientes; a que ele
critica não reproduz. A assimetria é favorável e vale ser dita.

**Não afeta P1, P2 nem P3.** Nenhuma delas passa por ordenação.

**Não afeta o braço Raman, e pelo motivo certo.** Lá os gates treinados têm 5,
4 e 8 valores exatamente empatados entre 1870 bandas, e o decil não é
confinado a empate: a §7 mostra fração 0,000 no piso e 0,005 no máximo. Com o
conjunto selecionado praticamente livre de empates, a regra de desempate quase
não tem sobre o que operar, e 0,9596 / 0,9589 / 0,9303 não é um valor dominado
por empate. O braço Raman é robusto **porque** não satisfaz C1 — o que é a tese
do artigo, aparecendo de novo onde não foi procurada.

**Afeta estas afirmações do texto, que precisam de decisão do autor:**

1. §4.2.1, "the overlap ranges from 0.9452 to 0.9867 at that dataset's own
   convention (q = 29)" — medição de um ambiente.
2. §4.3, "it stays between 0.9452 and 0.9867 and shows no relation to sample
   size (−0.3214, p = 0.4821)" — a conclusão sobrevive em qualquer dos três
   ambientes (constante em 1,0000; ou oscilando sem tendência em torno do
   acaso), mas o coeficiente relatado é do ambiente do autor.
3. §4.2, "The reported 0.9418 is reproduced exactly by the deterministic rule" —
   é reprodução *naquele ambiente*. Afirmação mais fraca e ainda útil.
4. §6, "the literature prior's 0.9763 to 1.0000" — mesmo braço, θ₀ = logit s,
   mesma exposição; precisa ser conferido.
5. `scripts/05_diagnostico_jaccard.py`, linha 220, imprime "argsort then breaks
   ties by band index". Isso é verdade de `kind="stable"`, não do padrão. É uma
   afirmação do programa sobre si mesmo, e está errada no ambiente medido aqui.

## O que eu recomendo, para o autor decidir

**Declarar `kind` explicitamente em todos os nove pontos de seleção.** Não para
corrigir um erro de cálculo — não há erro de cálculo — mas porque uma regra de
desempate que o artigo *analisa* não pode ficar implícita na implementação. Com
`kind="stable"` o valor passa a ser 1,0000 em todos os sete, que é o enunciado
mais limpo possível de C1+C2+C3: sob desempate por índice, a sobreposição é
identicamente um e não contém informação alguma sobre os gates. O número do
artigo deixa de ser 0,9452–0,9867 e passa a ser exatamente 1, com o valor
anterior registrado como o que uma ordenação não estável produz.

A alternativa é manter o padrão e relatar versão e plataforma junto de cada
valor determinístico. É defensável e pior: amarra um resultado do artigo a um
detalhe de build.

**Nos dois casos, a §4 ganha uma frase**, porque isto é um achado e não um
ajuste: a sobreposição determinística é função da regra de desempate, e nos
mesmos dados ela vale 1,000 sob ordenação estável e cai ao acaso sob ordenação
não estável. Isso é mais forte do que qualquer coisa que o texto afirma hoje.

## Procedência

- Medido aqui: a tabela de sete tamanhos por quatro `kind`, os conjuntos
  selecionados em `gates_n100`, a não estabilidade do padrão do numpy, o texto
  extraído dos cinco PDFs comitados.
- Lido do manuscrito e do PDF comitado: 0,9452–0,9867 e os rótulos 0,94–1,00.
- **Não medido:** a versão de numpy do autor, e portanto a causa exata do
  terceiro valor. Pendente de `13_dependencia_do_sort.py` na máquina dele.

---

## Extensão de 2026-10-27 — o ambiente do autor, a quantificação, e três correções minhas

O texto acima fica como escrito. Três coisas nele precisam de correção, e as
correções vão aqui em vez de substituí-lo.

### O ambiente do autor, medido e não inferido

Execução do `13_dependencia_do_sort.py` na máquina do autor, 2026-10-27:
**numpy 2.4.6, Python 3.14.6, Linux-7.0.0-38-generic, glibc 2.43.**

| regra | sete tamanhos |
| --- | --- |
| `quicksort` = `heapsort` = padrão | **0,9452 a 0,9867** |
| `mergesort` = `stable` | 1,0000 |
| sorteada | 0,7442, contra E[J] = 0,7445 |

Os valores do padrão coincidem com os do manuscrito **nos sete tamanhos, dígito
por dígito**: 0,9600, 0,9556, 0,9689, 0,9867, 0,9763, 0,9452, 0,9496 — e a §4.2.1
relata a faixa 0,9452–0,9867. O terceiro valor da tabela acima deixa de ser "o
ambiente do autor conforme o texto" e passa a ser medido. A Figura 3 comitada
está explicada.

E a regra sorteada dá 0,7442 nos dois ambientes, contra E[J] = 0,7445 nos dois.

### Correção 1 — eu chamei o Jaccard de quantidade vazia, e ele não é

Escrevi acima que uma quantidade que varia com o algoritmo de ordenação "é tão
vazia quanto uma quantidade pode ser". O autor corrigiu, e está certo: o Jaccard
continua medindo a concordância dos conjuntos que um procedimento específico
produz. O defeito é mais estreito e pior de explicar — essa concordância **não
identifica a estabilidade espectral** que a métrica foi oferecida para avaliar,
porque todo elemento concordante vem de um único bloco empatado e a regra de
desempate, não o gate, decide quais deles entram.

### Correção 2 — e dá para quantificar, em vez de qualificar

A regra sorteada amostra ordens de empate uniformemente. Então a média e o
desvio dela descrevem a **população de respostas disponível a qualquer regra de
desempate**, e cada `kind` pode ser localizado nessa população:

    z = (J_kind − média_sorteada) / desvio_sorteado

Medido, com desvio sorteado 0,0063 nos sete tamanhos:

| regra | onde a resposta cai |
| --- | --- |
| `stable` / `mergesort` | **+40,7 desvios** em todos os sete |
| `quicksort` / `heapsort`, numpy 2.5.3 | +0,0 a +3,4 desvios |
| `quicksort` / `heapsort`, numpy 2.4.6 (autor) | ≈ +32 a +38 desvios |

Isto é o enunciado que o manuscrito pode fazer sem chamar nada de vazio: **sob
desempate por índice a resposta fica a quarenta desvios da ordem de empate
típica.** Não é uma quantidade sem conteúdo; é uma quantidade cujo conteúdo é a
regra de desempate.

O `13` também conta os conjuntos distintos entre as dez sementes: `stable` dá
**1** conjunto nos sete tamanhos, `quicksort` dá 10 em seis deles e 9 em
n = 1158 — duas sementes coincidiram por acaso. E todos os conjuntos
selecionados, sob as quatro regras, ficam **inteiramente dentro do platô**.

### Correção 3 — `kind="stable"` não elimina o artefato, e eu recomendei como se eliminasse

Eu recomendei declarar `kind="stable"` nos nove pontos e passar a relatar
1,0000. O autor recusou a segunda metade, e o motivo é mais forte do que a
recomendação: como a ordem das bandas é fixa, a ordenação estável seleciona
sistematicamente os mesmos índices empatados, e **J = 1 é consequência da regra
de desempate, não evidência adicional de bandas estáveis**. Trocar um artefato
implícito por um artefato explícito não é progresso; o progresso é mostrar que a
métrica é sensível à regra.

Os três procedimentos, como o autor os definiu:

| procedimento | finalidade |
| --- | --- |
| ordenação estável explícita | demonstrar a estabilidade artificial máxima que uma regra determinística produz |
| desempate aleatório com sementes controladas | estimar a concordância sem privilegiar posições fixas no platô |
| ordenação original, sem `kind` | reproduzir historicamente os resultados anteriores, **identificando o ambiente** |

Os valores históricos não são substituídos por 1,0000. São preservados com a
origem declarada.

## A causa não está demonstrada só pela versão

A instabilidade da ordenação explica por que **não há garantia** de preservação
da ordem dos empates. Ela não demonstra que esta diferença específica entre dois
ambientes foi causada exclusivamente pela versão do numpy. O `13` passou a
imprimir o que falta para decidir isso em outro lugar:

| item exigido | onde está agora |
| --- | --- |
| identidade dos arrays de entrada | SHA-256 dos sete `.npz`, impresso |
| q e índices efetivamente selecionados | q e L por arquivo; contagem de conjuntos distintos; `--indices` imprime os conjuntos |
| convenção de agregação do Jaccard | declarada: média simples sobre os C(10,2) = 45 pares, nenhuma semente de referência |
| implementação exata da ordenação | as quatro `kind` lado a lado, e a não estabilidade do padrão medida no próprio script |
| versões | numpy, scipy, python, plataforma e executável |

Com os dois ambientes imprimindo o mesmo bloco, a comparação é arquivo por
arquivo e conjunto por conjunto, sem presumir causa.

## O braço Raman: o caminho existe e não exige retreino

O autor exigiu quantificar, não argumentar a partir do número de empates. Os
vetores de gate do Raman não são persistidos pelo `07_raman_lambda1.py`, então as
quatro `kind` não se aplicam ali diretamente. **Não precisam.** A regra sorteada
amostra ordens de empate uniformemente, logo `j_random_sd` já limita o que
qualquer regra pode fazer, e `j_index` se localiza nesse desvio — e as três
quantidades já estão gravadas em `cells.json`.

O `13` passou a ler esse arquivo e a imprimir, por partição, `j_index`,
`j_random`, o desvio, `max_empates`, a fração no platô e onde a regra de índice
cai. Desvio zero significa que **nenhuma ordem de empate muda o valor**, que é a
afirmação de que o controle Raman precisa.

### Medido na execução do autor, 2026-10-27

| partição | j_index | j_random | desvio | j_i − j_r | empates máx. |
| --- | --- | --- | --- | --- | --- |
| 0 | 0,9596 | 0,9596 | 0 exato | 0 exato | 5 |
| 1 | 0,9589 | 0,9589 | 3,339×10⁻¹⁶ | −3,331×10⁻¹⁶ | 4 |
| 2 | 0,9303 | 0,9303 | 3,339×10⁻¹⁶ | −3,331×10⁻¹⁶ | 8 |

**O desvio é ruído de ponto flutuante, não dispersão.** 3,339×10⁻¹⁶ sobre um
Jaccard de 0,959 são **3,0 ulp** de um `float64` nessa magnitude
(`np.spacing(0.9589)` = 1,110×10⁻¹⁶), e a diferença `j_i − j_r` são os mesmos
3,0 ulp. Isso é resíduo de somatório sobre 200 sorteios que devolveram **o mesmo
valor**, não variação entre ordens de empate.

Então o resultado é mais forte do que "cai dentro da dispersão": **nenhuma ordem
de empate moveu o valor do Jaccard** além da resolução do cálculo, nos 200
sorteios examinados. Contra +32 a +41 desvios no braço NIR, onde o desvio é
0,0063 — treze ordens de grandeza acima.

### Duas afirmações, e só uma está demonstrada

O autor separou as duas em 2026-10-27, e eu as havia escrito como se fossem a
mesma:

| afirmação | estado |
| --- | --- |
| **invariância da métrica** — nenhuma ordem de empate moveu o Jaccard além da resolução do cálculo | **demonstrada**, nos sorteios examinados |
| **invariância dos conjuntos selecionados** — nenhuma regra de desempate altera quais bandas entram | **não demonstrada** |

Duas seleções diferentes podem devolver o mesmo Jaccard. Igualdade de valor não
é igualdade de conjunto, e eu escrevi "nenhuma ordem de empate muda a seleção"
a partir de uma medição que só sustenta a primeira linha. Fechar a segunda
exige comparar os conjuntos de índices diretamente, o que exige os vetores de
gate do Raman — que o `07_raman_lambda1.py` não persiste. Não está disponível a
partir das células gravadas, e não é afirmado.

O braço NIR tem as duas, porque os gates estão armazenados: a tabela de
conjuntos distintos mostra `stable` com um conjunto e o padrão com vários.

E o limiar de oito ulp é **tolerância numérica operacional**, documentada como
tal: é onde vive o resíduo de somatório em precisão dupla sobre algumas centenas
de termos. Não é limiar estatístico, não carrega nível de significância, e "sem
dispersão" é afirmação sobre a resolução deste cálculo — não demonstração de que
a quantidade não possa variar.

E o `−1,0 desvio` que as partições 1 e 2 exibiam era ruído dividido por ruído:
com `j_i − j_r` igual a `−sd`, o quociente é −1,0 para qualquer par assim, o que
explica por que duas partições deram exatamente o mesmo número. O `13` passou a
chamar isso de **sem dispersão**, com o limiar dado por `8 · np.spacing(|média|)`
— a precisão do próprio valor — e não por um número redondo escolhido para
caber. Um desvio real continua produzindo z: conferido com fixture a +6,0
desvios.

A inversão de ordem que o autor apontou — eu havia escrito que o braço é
"robusto porque falha C1" antes de medir — fica registrada acima e corrigida
aqui: a robustez é medida, e a falha de C1 é a explicação dela, não a evidência
dela.

**Um defeito de exibição, encontrado por esta mesma saída.** A tabela imprimia o
desvio com quatro casas, mostrando `0,0000` nas três partições, enquanto
calculava `−1,0 desvio` em duas — o que só um desvio **não nulo** produz. Zero
exato e pequeno demais para quatro casas são afirmações diferentes e estavam
renderizando igual. O `13` passou a imprimir desvio e diferença em precisão
plena, e o teste de zero exato passou de 5×10⁻⁵ para precisão de máquina.

## Figuras

A Figura 3 não é considerada validada enquanto o painel (b) divergir. A
diferença entre eixos em torno de 0,95 e em torno de 0,75 é substantiva e não é
renderização nem `bbox_inches`. O PDF comitado **não é substituído**: preserva-se
o artefato histórico, identifica-se a origem, e a versão revisada sai de uma
implementação explicitamente especificada.

## Duas etapas, e esta é a A

**Etapa A — diagnóstico e rastreabilidade.** Executar os scripts, registrar
ambiente, entradas, resultados por regra e as divergências das figuras,
preservando os artefatos históricos. É o que este documento faz.

**Etapa B — revisão científica.** Atualizar números, figuras e discussão a
partir do diagnóstico completo, deixando explícito a qual procedimento pertence
cada resultado. **Não iniciada**, e não deve ser antes da execução do `13` com o
`cells.json` do Raman.

P1, P2 e P3 não são reabertas: o que se descobriu é dependência da métrica em
relação à implementação, não falha da caracterização do platô.


## Um erro de diagnóstico no `07`, encontrado pela mesma execução

O `10_figuras.py` recusou-se a rodar com:

```
could not import the pgsg_2 Raman modules (No module named 'pgsg_1').
--pgsg2-root must be the directory that CONTAINS the `pgsg2` package ...
given: /home/clarimar/pgsg/pgsg2-nir-raman-gating/src
```

O módulo que falta é `pgsg_1`, e a mensagem culpa `--pgsg2-root` e manda passar
o caminho que já havia sido passado. A causa: `pgsg2.models.adapter` importa
`pgsg_1` por dentro, e o `except` do bloco de imports do pgsg2 atribuía
**qualquer** `ModuleNotFoundError` à raiz do pgsg2.

Corrigido: a raiz culpada é decidida pelo **módulo que falta**, via `e.name`, e
não pelo bloco que levantou. As duas mensagens passaram a reportar se o
diretório existe e se contém o pacote, para que o caminho errado se identifique
sozinho:

```
could not import pgsg_1 (No module named 'pgsg_1').
--pgsg1-root must be the pgsg_1 repository root: the directory that holds
`src/pgsg_1` and `pgsg_v2.py`. Both it and its `src` go on sys.path.
given: /home/clarimar/pgsg/pgsg_1
  exists: False;  has src/pgsg_1: False;  has pgsg_1: False
```

Reproduzido com um `pgsg2` sintético que importa `pgsg_1` por dentro, que é a
condição exata da falha.

**Consequência para a Etapa A:** as Figuras 1 e 4 continuam **não verificadas**,
porque a regeneração nunca completou. Não é divergência — é ausência de medição,
e o `12` para em vez de comparar saída parcial.

E a execução de 2026-10-27 mostrou que `~/pgsg/pgsg_1` **não existe** nessa
máquina: `ls` falhou nos dois caminhos. Localizado por busca, sem caminho
presumido:

```
/home/clarimar/Dropbox/pgsg/pgsg_1
/home/clarimar/Dropbox/pgsg/pgsg_1/src/pgsg_1
/home/clarimar/Dropbox/pgsg/pgsg_2/vendor/pgsg_1
/home/clarimar/pgsg/pgsg2-nir-raman-gating/vendor/pgsg_1
```

A raiz a usar é `/home/clarimar/Dropbox/pgsg/pgsg_1`, porque é a que **contém**
`src/pgsg_1`; as duas últimas são cópias `vendor/` do pacote, não raízes de
repositório. O `--pgsg1-root` é a raiz, não o `src`: o `importar` põe as duas no
`sys.path`.

---

## As figuras reproduzem, e isso fecha a Etapa A delas

Execução do `12_verifica_figuras.py` na máquina do autor, 2026-10-27, com
`--pgsg1-root ~/Dropbox/pgsg/pgsg_1`:

```
2. Execution        exit status 0
3. Content, regenerated against committed
  OK   fig1_prior_degrau.pdf             IDENTICAL   max|diff| 0
  OK   fig2_colapso_por_desempate.pdf    IDENTICAL   max|diff| 0
  OK   fig3_resposta_ao_tamanho.pdf      IDENTICAL   max|diff| 0
  OK   fig4_controle_raman.pdf           IDENTICAL   max|diff| 0
  OK   fig5_alinhamento_intra_nivel.pdf  IDENTICAL   max|diff| 0
  5 of 5 figures regenerated and matched.
```

**Zero pixels de diferença nas cinco**, a 150 dpi, com todas as entradas
presentes. E isso muda a leitura do painel (b) da Figura 3.

### O painel (b) nunca divergiu na máquina que o produziu

Eu encontrei 0,73–0,78 onde o PDF comitado mostrava 0,94–1,00 e chamei de
divergência. Era divergência **entre ambientes**, não divergência do arquivo:

| | painel (b) |
| --- | --- |
| PDF comitado | 0,9452–0,9867 |
| regeneração na máquina do autor, numpy 2.4.6 | **idêntica, pixel a pixel** |
| regeneração no contêiner, numpy 2.5.3 | 0,7443–0,7659 |

A Figura 3 é **reproduzível no ambiente que a gerou** e **não é portável** —
exatamente pelo mesmo mecanismo que torna os números da §4.2.1 não portáveis, e
pelo mesmo motivo. O arquivo comitado está correto para o procedimento e o
ambiente declarados. Não há nada a substituir.

O que a verificação estabelece, e só isso: as cinco figuras saem do código e dos
dados versionados, nas versões de biblioteca daquela máquina. Não estabelece que
sejam as figuras certas para publicar, nem que outra pessoa as obtenha — e a
Figura 3 painel (b), em particular, outra pessoa não obtém.

Consequência para a Etapa B: a legenda da Figura 3 precisa declarar a regra de
desempate e o ambiente, como os números da §4.2.1. A figura não é um problema a
corrigir; é um resultado a qualificar.

### Um campo de procedência que dizia "não sei"

A saída imprimiu `[pypdfium2 ?]` nas cinco linhas. O `pypdfium2` 5.x não expõe
`__version__`, e o meu `getattr(..., '?')` degradava para interrogação — um campo
de procedência relatando que não conhece a própria ferramenta, num script cuja
função é procedência. Corrigido para ler `importlib.metadata.version`.
