# F006 — O que sobrevive ao condicionamento, e um critério que não podia funcionar

Data: 2026-10-23
Protocolo: `docs/pre-registro-H13.md`
Análise: `scripts/08_analise_condicional.py`
Dados: `results/p{10,11,12,13,14}_{literature,blocks,shuffled}`

Cinco partições novas agrupadas por fruto, três braços, λ ∈ {0; 1}, dez
sementes, θ₀ = 0, Adam, 500 épocas. PLS de referência por partição:
H(1se) = 70, 56, 70, 61, 62. Pareamento verificado: concordância em λ = 0
idêntica entre os três braços nas cinco partições.

## Vereditos pré-registrados

| | | |
| --- | --- | --- |
| **H13a** Spearman parcial positivo na literatura | 5/5 | **suportada** |
| **H13b** literatura supera `blocks` no parcial | **0/5** | **não suportada** |
| **H13c** o achado do piso, promovido a primário | 5/5 | **suportada** |

## H13b não podia funcionar, e o defeito é de desenho

`blocks` supera a literatura nas cinco partições, significativamente
(p entre 0,0020 e 0,0273). O pré-registro lia isso como "o prior NIR não
carrega informação posicional". **Essa leitura está retirada.** Ela não segue,
porque H13b condiciona na variável que distingue os braços.

### A constante estrutural

`Spearman(gate, prior)` saiu **0,7058 nas cinco partições, aos quatro
decimais** — e em toda semente e todo braço. Não é medida. Quando o gate ordena
as bandas estritamente por nível do prior, sem sobreposição entre níveis, o
posto do prior é constante dentro de cada nível e a correlação fica determinada
pelos **tamanhos dos níveis** apenas. Para 223/7/17/34 é 0,7058. Os braços de
controle preservam o multiset, logo compartilham o valor.

### O mecanismo que inverte a comparação

Com ρ_gs fixo, o parcial é proporcional a ρ_gr − 0,7058·ρ_rs. Partição 13:

| | ρ_gr (cru) | ρ_rs (prior vs. ref) | parcial |
| --- | --- | --- | --- |
| literatura | +0,3418 | **+0,2351** | (0,3418 − 0,1659)/0,6886 = **+0,2554** |
| `blocks` | +0,1517 | **−0,0991** | (0,1517 **+** 0,0700)/0,7049 = **+0,3145** |

O prior do `blocks` é anticorrelacionado com a referência, de modo que o
condicionamento **soma** 0,0700 ao seu numerador; o da literatura é
correlacionado e **perde** 0,1659. **A estatística parcial premia um prior que
aponta para o lugar errado.** Quanto melhor o prior, pior ele pontua.

Logo H13b não testa o que foi escrito para testar. As estatísticas que podem
testá-lo são a **crua** (secundária 2) e as **intra-nível** (H13c aqui, H10b em
F003).

### O que H13b estabelece, lido como o que mede

O alinhamento do gate com a referência **além** da contribuição linear-em-postos
do prior não é maior no braço de literatura. Isso é afirmação sobre o resíduo,
não sobre o prior.

## O que sobrevive, e é coerente

**H13a, 5/5:** parcial positivo na literatura, +0,1430 a +0,2802, p = 0,0020 em
todas. O gate alinha-se com a referência além do que o prior lhe dá.

**Secundária 3:** o mesmo parcial no braço `shuffled` dá +0,2714; +0,3140;
+0,1175; +0,3124; +0,2173 — igual ou acima da literatura. E no piso: +0,3159;
+0,3689; +0,1482; +0,3525; +0,2513, também igual ou acima.

As duas juntas dizem uma coisa só: **removida a contribuição do prior, o
alinhamento do gate com a referência é o mesmo qualquer que seja o prior
usado.** Entre +0,12 e +0,37 nos três braços. O gate extrai a mesma estrutura
dirigida pelos dados sob prior publicado, realocado ou embaralhado, e o papel do
prior fica confinado ao que o condicionamento removeu.

**H13c, 5/5:** Spearman no piso, braço de literatura: +0,2705; +0,3168; +0,1491;
+0,2901; +0,2063, p = 0,0020 em todas. **O achado do piso de F003 replica em
partições novas**, agora como critério primário e não como análise terceira
declarada. Nas 223 bandas que o prior rebaixa, a ordenação dirigida pelos dados
concorda com a referência externa.

**Secundária 1:** parcial e piso concordam em sinal em 5/5, e as magnitudes são
próximas — o que era de esperar, já que o piso é 223 das 281 bandas e portanto
domina o resíduo. As duas formas de condicionar dão a mesma resposta.

## A métrica crua nestas partições

Secundária 2, declarada antes justamente para isto:

| partição | literatura | `blocks` | delta | `shuffled` | delta |
| --- | --- | --- | --- | --- | --- |
| 10 | +0,2692 | +0,3540 | −0,0849 | +0,1257 | +0,1434 |
| 11 | +0,3724 | +0,3288 | **+0,0435** | +0,2293 | +0,1431 |
| 12 | +0,1843 | +0,2932 | −0,1089 | +0,1187 | +0,0656 |
| 13 | +0,3418 | +0,1517 | **+0,1901** | +0,2570 | +0,0848 |
| 14 | +0,2914 | +0,2141 | **+0,0773** | +0,2052 | +0,0863 |

A literatura supera `blocks` em **3 de 5** e `shuffled` em **5 de 5**. Isso
difere das dez partições anteriores, onde `blocks` igualava ou superava em 9 de
10 (ver a correção datada em `pre-registro-H13.md`: eu havia escrito 10 de 10).

Somando as quinze partições NIR: a literatura supera `blocks` na métrica crua em
**4 de 15**. O padrão não é uniforme entre partições, e qualquer afirmação sobre
ele precisa dizer isso.

## Erro aritmético no pré-registro, corrigido

A tabela de amplificação do pré-registro foi calculada com
**Pearson** ρ(gate, prior) = 0,9655, que é o que a varredura reporta, e deu
3,8×. O parcial usa **Spearman**, 0,7058, e o fator real é **1,41×**. A
estatística é muito melhor condicionada do que aquele documento alertava. O erro
é meu e favorável; está corrigido por nota no documento e por teste.

## Pontas, e o que eu não faria

Quatro métricas interpretativas foram testadas em NIR e nenhuma separa conteúdo
de ancoragem; a quinta, o parcial, não podia separar por construção. **Não
proporia uma sexta nestes dados.** O que falta não é métrica: é um desenho em
que o suporte verdadeiro seja conhecido, e isso exige dado sintético, que não é
deste artigo.

O que o artigo pode afirmar sobre o prior NIR, com quinze partições: a sua
posição não produz vantagem consistente em nenhuma das métricas testadas, e o
alinhamento do gate com a referência externa é indiferente a ela. O que **não**
pode afirmar é que o prior não carregue informação — H13b não mostra isso, e a
métrica crua o favorece em 3 das 5 partições mais recentes.
