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

## 2. Pendente de leitura no guia vigente — NÃO VERIFICADO

O manuscrito **não tem nenhum destes itens hoje**. A coluna "estado atual" é
inventário, não julgamento de conformidade, porque a exigência não foi lida.

| item | estado atual no manuscrito | o que falta saber |
| --- | --- | --- |
| resumo, limite de palavras | 251 palavras por espaço em branco; 246 tokens alfanuméricos (`paper/02-resumo-C.md`) | o limite vigente, e qual contagem a revista usa |
| highlights | ausentes | se são exigidos, quantos, e a extensão de cada um |
| palavras-chave | ausentes | quantidade permitida |
| declaração de disponibilidade de dados | ausente | forma exigida; o Mango DMC v3 é público e o repositório também |
| disponibilidade de código | ausente no manuscrito, presente de fato | se a revista exige declaração própria ou cobre no item anterior |
| declaração de IA generativa | ausente | nada: confirmada na seção 1 |
| CRediT, financiamento, conflito de interesses | ausentes | forma exigida |
| figuras, tabelas, suplementar | 5 figuras em PDF, 5 legendas, 1 tabela | formato, resolução, limite de quantidade |

**A instrução histórica de 50 a 250 palavras é de 1992 e não entra aqui.** Ela
fica registrada como a origem da escolha de 250 feita na redação, não como
regra vigente. Se o guia atual disser outro número, o resumo muda; se disser
250, a coincidência foi sorte e não validação.

**As duas contagens do resumo não são um menu.** 251 por espaço em branco e 246
por tokens alfanuméricos são duas medidas do mesmo texto, e escolher a menor
porque ela cabe seria decidir a regra depois de ver o resultado — o erro que
este programa recusa em toda parte. A ordem é: identificar a regra vigente;
então medir por ela. Se o limite confirmado for 250 e a revista não declarar
convenção de contagem, a recomendação é **reduzir com margem**, para algo em
torno de 240, preservando os resultados quantitativos essenciais: 0.9418,
0.7005 ± 0.0068, a condição do platô e a frase do controle de deslocamento.
251 não é uma infração demonstrada — é uma margem que não existe.

---

## 3. Um arquivo de declarações não é uma declaração pronta

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

## 4. Como fechar

O guia oficial recusa leitura automatizada. Com a página salva em PDF ou o texto
copiado, a conferência é item por item, em três colunas: **conforme**, **não
conforme** e **não verificável**. Nada entra como conforme por analogia.
