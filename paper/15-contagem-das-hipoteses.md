# A contagem de hipóteses não suportadas — medida e resolvida

Data: 2026-11-09
Status: **RESOLVIDO em 2026-11-09**, pela terceira saída, decisão do autor.

## A decisão

O autor escolheu a terceira saída, que eu propus depois de medir que a (b)
não cabia no limite: **o resumo diz `six`** — a contagem literal pelo critério,
e o resumo continua com 249 palavras — **e a §2.6 carrega as duas contagens**,
porque não tem limite de palavras e é onde a Tabela 1 é apresentada. A redação
aprovada, aplicada literalmente:

> Six were not supported. Two more met their criterion only formally or on a
> narrow reading, and Table 1 records both the verdict and that reading.

Nada mais do resumo foi tocado: o autor instruiu explicitamente *"não alterar
os demais trechos protegidos do resumo"*, e o único corte gramatical que eu
tinha encontrado — tirar um `that` — **não** foi aplicado, porque deixou de ser
necessário.

O teste que antes guardava este registro passa a ser a conferência
aritmética: o numeral do texto é **contado** da tabela que o consolidador
emite, não escrito no teste, de modo que editar um sem o outro falha.

## O que o manuscrito afirma

Em dois lugares, e um deles é o resumo:

| onde | a frase |
| --- | --- |
| `02-resumo-C.md:69-70` (resumo) | *"We pre-registered twenty hypotheses, **eight** of which our criteria did not support"* |
| `03-rascunho-s1-s2-s3.md:280-282` (§2.6) | *"Table 1 lists all twenty hypotheses with their verdicts and, in a separate column, the interpretation we reached afterwards. **Eight** were not supported."* |

A segunda frase cita a Tabela 1 como a lista dos vereditos. É a própria frase
que torna a contagem verificável.

## O que a Tabela 1 registra

Contado por extração da coluna `veredito pelo critério` da tabela que o
consolidador emite, em `00-estrutura.md`:

- 20 linhas de hipótese;
- **6** começam com `não suportada`: **H5a, H7-blocks, H8, H9-blocks, H10a,
  H13b**;
- 14 começam com `suportada`;
- nenhuma linha fica fora dessas duas formas.

A tradução proposta em `13-tabela1.md` preserva as duas contagens: 6 e 14, com
os mesmos rótulos, e nenhuma das vinte razões `k/n` diverge entre as duas
línguas.

## O que os pré-registros registram

Concordam com a tabela, e nomeiam os mesmos rótulos:

| onde | o que diz |
| --- | --- |
| `docs/pre-registro-H10-H11.md:7` | *"H5a, H7-blocks, H8 e H9-blocks ficam como saíram"* |
| `docs/pre-registro-H13.md:7` | *"H5a, H7, H8, H9-blocks e H10a ficam como saíram"* |
| `docs/pre-registro-H13.md:192` | *"O critério e o veredito ficam como saíram — 0/5, não suportada"* (H13b) |

União dos rótulos citados: os mesmos seis.

## O número nunca foi oito na tabela

Conferido no histórico, porque a hipótese mais confortável seria que dois
vereditos mudaram depois e a contagem ficou para trás. Não foi isso.

- `d407f3a` é o commit que escreveu `eight` no resumo e `Eight were not
  supported` na §2.6. Nesse mesmo commit, a Tabela 1 já tinha **20 linhas e
  seis** `não suportada`, com exatamente os mesmos seis rótulos.
- A coluna de vereditos só foi tocada uma vez depois disso, em `b3b1f85`, e
  continuou com seis.

Então não é uma contagem que envelheceu: ela não correspondeu à tabela em
nenhum momento.

## As três saídas, e por que nenhuma é minha

**(a) O número é seis.** Troca de uma palavra em cada um dos dois lugares.
É a leitura literal de *"our criteria did not support"*: pelo critério
pré-registrado, seis não passaram.

**(b) O número oito vem de outra conta, e a frase é que está errada.** Duas
linhas passaram pelo critério sem passar em substância, e as duas estão entre
as quatro formulações vinculantes que você impôs:

| rótulo | veredito | o que a coluna de interpretação diz |
| --- | --- | --- |
| H5c | `suportada, 5/5 **(formal)**` | passou formalmente |
| H10b | `suportada, 5/5` | *leitura estreita:* `blocks` é negativo, não o prior de literatura positivo |

Seis mais essas duas dão oito. Se essa era a conta, o defeito não é o número:
é dizer *"our criteria did not support"* sobre duas hipóteses que o critério
**suportou**. Nesse caso a frase precisa separar as duas contagens — algo como
"seis não suportadas pelo critério, e duas suportadas apenas formalmente" — e
o número oito sozinho não pode ficar.

**(c) Dois vereditos da Tabela 1 estão errados.** É a menos provável das três,
porque os pré-registros concordam com a tabela, e porque mexer em veredito
depois do dado contraria a sua regra: o texto original fica e a correção entra
como nota datada.

## O que eu não fiz

Não alterei o resumo, não alterei a §2.6, não alterei um único veredito. O
resumo tem 249 palavras e as duas trocas de (a) não mudam a contagem de
palavras; a reformulação de (b) muda, e aí o limite de 250 volta a importar.

Também registro como achei: não foi leitura. Foi uma contagem automática da
coluna de vereditos, feita ao montar a página de revisão da Tabela 1 lado a
lado. A leitura integral de 2026-10-28 não pegou isto, e a Tabela 1 é citada
cinco vezes no corpo.
