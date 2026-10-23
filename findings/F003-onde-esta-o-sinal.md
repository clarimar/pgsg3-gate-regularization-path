# F003 — Onde está o sinal, e onde o prior aponta

Data: 2026-10-23
Protocolo: `docs/pre-registro-H10-H11.md` (H10, H11)
Análise: `scripts/06_analise_plato.py`
Dados: `results/p{5,6,7,8,9}_{literature,blocks,shuffled}`

Cinco partições novas agrupadas por fruto (`--split-seed 5..9`), três braços,
10 sementes, λ = 1 fixado pelo pré-registro, `--init zero`, 500 épocas. PLS de
referência recalibrado por partição: H = 46, 70, 72, 53, 71.

`inert = 0` nas 1500 execuções, e nenhuma célula com empate exato dentro de
nível em H10 — a guarda de empate não disparou ali. Disparou uma vez em H11
(`p5 / shuffled`, 1 empate no resíduo), e aquela célula é reportada como
indefinida, não imputada.

## Vereditos pré-registrados

| | | |
| --- | --- | --- |
| **H10a** ordenação intra-platô existe | 3/5 | **não suportada** |
| **H10b** literatura ordena melhor que blocos | 5/5 | **suportada** |
| **H11a** o decil de resíduo sai do platô | 5/5 | **suportada** |
| **H11b** reprodutibilidade do resíduo distingue os braços | 4/5 | **suportada** |

## H10a e H10b têm de ser lidas juntas

ρ intra-platô, braço de literatura: −0,1495; +0,3578; +0,1962; −0,1257;
+0,2908. Sinal inconsistente, duas partições negativas — é por isso que H10a
caiu.

Braço `blocks`, nas mesmas células: −0,8372; −0,1823; −0,2414; −0,5822;
−0,1928. **Todos negativos.**

Logo H10b é suportada em 5/5 não porque a literatura ordena bem, mas porque
ordena **menos mal**. A afirmação que estes números sustentam é estreita:
realocar os blocos torna a ordenação intra-platô anticorrelacionada com a
referência externa; manter a posição da literatura deixa a ordenação perto de
zero, com sinal que varia por partição. **A posição não é neutra, e também não
produz alinhamento.**

"O prior de literatura carrega conteúdo químico" é mais do que isto autoriza.

### A análise secundária morde H10b

Os dois braços restritos às **mesmas** 34 bandas (o platô da literatura):
−0,1266; +0,6457; +0,3206; −0,4547; +0,4971. **3/5**, não 5/5. Parte do efeito
de H10b vem de **quais bandas estão no nível**, não de como são ordenadas. Isso
estava declarado como secundária antes da execução, e é reportado como tal.

## O sinal está no piso do prior

Análise terceira, declarada antes, por nível de prior. ρ(gate, |coef PLS|)
dentro de cada nível, braço de literatura:

| nível | n | p5 | p6 | p7 | p8 | p9 |
| --- | --- | --- | --- | --- | --- | --- |
| 0,1 (piso) | 223 | **+0,2982** | **+0,1679** | **+0,1457** | **+0,3418** | **+0,2147** |
| 0,6 | 7 | +0,2714 | +0,3214 | +0,0250 | +0,1786 | −0,4000 |
| 0,8 | 17 | −0,2370 | −0,6002 | −0,0059 | +0,1025 | −0,4721 |
| 1,0 (platô) | 34 | −0,1495 | +0,3578 | +0,1962 | −0,1257 | +0,2908 |

O piso é o **único** nível com sinal positivo consistente: 5/5, p = 0,0020 em
todas as cinco. São as 223 bandas que o prior declara sem importância. O nível
0,8 é misto a negativo. O nível 0,6 tem 7 bandas e não sustenta Spearman — está
na tabela por ter sido declarado, não para ser interpretado.

Dentro de um nível o prior é constante, logo essa ordenação é inteiramente
dirigida pelos dados. O gate encontra, nas bandas que o prior rebaixa, uma
ordenação que concorda com a referência externa — e não encontra nas bandas que
o prior eleva.

## H11a passou contra o confinamento errado

Fração do decil de resíduo dentro do platô: 0,000 nas cinco. Saiu do platô
completamente. Mas a composição por nível mostra onde foi:

| nível | participação nas bandas | fração no decil (p5…p9) |
| --- | --- | --- |
| 0,1 | 0,794 | 1,000 / 0,997 / 0,993 / 1,000 / 0,993 |
| 0,6 | 0,025 | 0,000 nas cinco |
| 0,8 | 0,060 | 0,000 / 0,003 / 0,007 / 0,000 / 0,007 |
| 1,0 | 0,121 | 0,000 nas cinco |

O decil deixou o platô e **foi todo para o piso**, acima da participação do
piso no total de bandas. H11a testou saída do platô, não ausência de
confinamento, e passou por isso. Não invalida o critério — ele era exatamente
o que o documento fixou — mas o critério cobria menos do que eu supunha ao
escrevê-lo.

## H11b não é sinal de conteúdo

Jaccard par-a-par do decil de resíduo:

| | p5 | p6 | p7 | p8 | p9 |
| --- | --- | --- | --- | --- | --- |
| literatura | 0,6985 | 0,7294 | 0,6847 | 0,7140 | 0,7098 |
| `blocks` | 0,6381 | 0,5515 | 0,7002 | 0,6002 | 0,6931 |
| `shuffled` | indefinida | 0,7792 | 0,7674 | 0,7284 | 0,6779 |

H11b compara literatura com `blocks` e passa em 4/5. Mas `shuffled` supera a
literatura em **3 das 4** células definidas. Um prior integralmente embaralhado
produz resíduos mais reprodutíveis que o prior publicado em três partições, de
modo que esta métrica também não separa conteúdo.

Os valores, 0,55 a 0,78, são bem menores que o Jaccard do gate cru
(0,81 a 1,00) nas mesmas células — coerente com ter removido o confinamento
trivial no platô.

## Consistência com as cinco primeiras partições

Não é teste; H7 e H9 já foram julgados. Nas cinco novas, `blocks` iguala ou
supera a literatura em concordância de espectro inteiro em 5/5, e a literatura
tem o maior Jaccard de gate cru em 5/5. Mesmo padrão das cinco primeiras, nas
duas direções. **Dez partições independentes.**

## Observação sem mecanismo

As duas partições de ρ intra-platô negativo (p5 e p8) são as duas de H do PLS
muito menor: 46 e 53, contra 70, 72 e 71. Spearman entre H e ρ intra-platô
nestas cinco: **+0,6000**, que com n = 5 não sustenta nada (p = 0,2848).

Candidato de explicação, **não testado**: com H menor o PLS é mais encolhido e
a referência muda de caráter entre partições, o que poderia inverter o sinal de
uma correlação intra-nível. Registrado como candidato e nada mais. Três
explicações mecânicas minhas caíram nesta linha de trabalho (F002), e esta não
tem mais apoio do que as três tinham quando as propus.

## Duas lacunas no meu próprio pré-registro

Registradas porque são defeito de desenho, não resultado.

1. **A leitura conjunta de H10 não foi especificada.** O documento fixou
   critérios separados para H10a e H10b e não disse como lê-los juntos. A
   primeira versão de `06_analise_plato.py` imprimia "the prior's position does
   carry content" condicionando só em H10b, conclusão que um H10a falho não
   sustenta. Corrigido no script; o pré-registro fica como estava, porque
   emendá-lo depois dos dados é precisamente o que ele existe para impedir.
2. **H11a cobria menos do que eu supunha.** Testou saída do platô, e o decil
   saiu do platô para dentro do piso. A composição por nível, acrescentada
   depois e marcada como descritiva, é o que torna isso visível.

## Para o manuscrito

O que dez partições sustentam, em ordem decrescente de firmeza:

1. O decil superior do gate cru está contido no platô do prior sempre. A
   métrica de reprodutibilidade do programa ordena dentro do nível de topo do
   prior e não olha fora dele.
2. Na concordância de espectro inteiro, realocar os blocos do prior não piora
   e em geral melhora. Essa métrica é dominada pela separação entre níveis.
3. Realocar os blocos torna a ordenação intra-platô anticorrelacionada com a
   referência externa, 5/5. A posição importa, no sentido de que destruí-la
   piora.
4. O alinhamento positivo consistente com a referência externa está no **piso**
   do prior, 5/5 com p = 0,0020 — nas bandas que o prior rebaixa.
5. Nenhuma das métricas testadas separa conteúdo químico de ancoragem: em cada
   uma, um prior com conteúdo destruído iguala ou supera o publicado em ao
   menos três partições.

O eixo do trabalho deixou de ser o caminho de regularização de λ. É que as
métricas interpretativas deste programa medem estrutura do prior, e o sinal que
existe está onde o prior não aponta.
