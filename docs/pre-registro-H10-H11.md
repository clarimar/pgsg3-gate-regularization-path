# Pré-registro — H10 (concordância intra-nível) e H11 (reprodutibilidade fora do platô)

Registrado em: **2026-10-23**
Status: **fechado antes de qualquer execução em `--split-seed 5..9`**

Complementa `docs/pre-registro-H5-H6.md` e `docs/pre-registro-H7-H9.md`. **Não
revisa nenhum veredito deles.** H5a, H7-blocks, H8 e H9-blocks ficam como
saíram, com os critérios que tinham.

---

## Declaração de motivação

Este pré-registro é **posterior aos dados** que o motivaram, e isso está
declarado aqui porque muda o quanto ele vale. O que o motivou está em
`findings/F002`:

1. O prior NIR é uma escada de quatro níveis (0,1 ×223; 0,6 ×7; 0,8 ×17;
   1,0 ×34). O Spearman entre gate e |coef PLS| sobre as 281 bandas é dominado
   pela separação **entre** níveis, que toda realocação de blocos reproduz por
   construção. É a métrica com que H7 foi avaliada, e ela pode ser cega à
   pergunta que H7 fazia.
2. O decil superior do gate está contido no platô do prior em 15/15 células.
   A métrica de reprodutibilidade nunca olha fora do nível de topo.
3. Na referência externa, o braço de literatura ordena melhor **dentro** do
   platô: ρ(|coef PLS|, vitórias no decil) positivo em 5/5 células do braço,
   contra 4/5 em `blocks` e padrão misto em `shuffled`.

Por isso as cinco partições já executadas **não** servem para testar isto: já
foram vistas três vezes. As hipóteses abaixo rodam em partições novas,
`--split-seed 5..9`, de modo que o teste seja confirmatório.

## O que não é registrado, e por quê

A **distribuição nula de posição** — centenas de realocações de blocos,
medindo onde a posição publicada cai — foi cogitada e não entra. Os cinco
sorteios de `blocks` já responderam que a posição publicada não é especial
contra realocação aleatória. Uma distribuição nula daria o percentil, que é
número descritivo para o texto, não hipótese. Registrar como teste uma
pergunta cuja resposta já está em mão seria registro decorativo.

---

## Desenho comum

Cinco partições novas agrupadas por fruto, `--split-seed 5,6,7,8,9`, três
braços (`literature`, `blocks`, `shuffled`), 10 sementes, grade de λ inalterada,
orçamento fixo de 500 épocas, Adam, `--init zero`. **λ = 1 fixado agora** para
todas as comparações primárias, pelo mesmo motivo de H7: escolher λ por braço
depois de ver os dados é a liberdade que derrubou H5a.

Referência de relevância recalibrada por partição (PLS, regra de 1 EP, grade
até 120), como nos pré-registros anteriores.

Permutação sorteada uma vez por partição, semente = semente da partição,
compartilhada entre sementes de modelo.

**A grade, os braços, as métricas e os limiares estão fechados. Nada será
refinado depois de ver os resultados.**

### Guarda de empate, fixada antes

Se os gates de qualquer célula tiverem empate exato dentro do nível sob
análise, a estatística daquela célula é **reportada como indefinida**, não
imputada e não substituída por outra. Esta guarda existe porque o artefato
documentado em F002 nasceu de empates exatos tratados como ordenação. Em
`pgsg_3` o prior entra só na penalidade (θ₀ = 0, `inert = 0` em todo λ por
F001), então não se esperam empates; a guarda cobre o caso de estarmos
errados sobre isso.

---

## H10 — o conteúdo do prior importa, medido dentro de um nível

**Enunciado.** Dentro de um nível do prior, onde o prior é constante e portanto
não impõe ordenação, o gate ancorado no prior de literatura ordena as bandas
de acordo com a referência externa melhor do que o gate ancorado em blocos
realocados.

**Métrica.** Spearman entre o gate e |coef PLS|, **restrito às bandas de um
nível do prior**. Comparação primária no **nível de topo** (o platô). Dentro
de um nível a separação entre níveis contribui zero, de modo que a estatística
mede só ordenação dirigida pelos dados.

**Critérios.**

- **H10a (há ordenação intra-platô).** No braço `literature`, a estatística é
  positiva, pareada por semente contra zero, Wilcoxon bilateral p < 0,05.
  *Suportada* se valer em ≥ 4 das 5 partições.
- **H10b (a posição importa).** `literature` supera `blocks` na estatística,
  pareado por semente, Wilcoxon bilateral p < 0,05. *Suportada* se valer em
  ≥ 4 das 5.

**Refutação.** Se H10b falhar em ≥ 2 partições, então a posição do prior não
carrega conteúdo nem na única métrica desenhada para enxergá-la, e a leitura
(b) de H7 se confirma por um segundo caminho independente — resultado mais
forte do que o atual, não mais fraco.

**Análise secundária, declarada agora.** A mesma estatística com os dois braços
restritos às **mesmas** 34 bandas (o platô da literatura), que separa "quais
bandas estão no nível" de "quão bem são ordenadas". Reportada à parte, não
entra no veredito.

**Terceira análise, declarada agora.** A estatística nos outros níveis do prior
(0,8 com 17 bandas; 0,6 com 7 bandas; o piso com 223). O piso é o único com
bandas suficientes para ser informativo por si; 7 bandas não sustentam
Spearman e serão reportadas como tal, não interpretadas.

## H11 — uma métrica de reprodutibilidade que sai do platô

**Enunciado.** O decil superior do **resíduo intra-nível** não fica confinado
ao platô do prior, e a sua reprodutibilidade entre sementes distingue os
braços.

**Motivação.** O gate é quase monótono no prior (ρ(g, s) = 0,97 em λ = 1), de
modo que o decil do gate cru é o nível de topo do prior e nada mais.

**Métrica, e por que não é |g − s|.** O resíduo é
|g_j − média{g_k : mesmo nível de prior que j}|, e o Jaccard médio par-a-par do
seu decil superior, q = ceil(0,10 p) = 29, nas mesmas 10 sementes.

Deslocamento em relação ao prior, |g − s|, foi a primeira candidata e **não
serve**. O gate é aproximadamente função afim comprimida do prior, de modo que
|g − s| é maior onde o prior é menor: medido em gates sintéticos no regime
observado, o decil de |g − s| cai 29/29 no piso de 223 bandas. Isso move o
confinamento do platô para o piso em vez de removê-lo. Centrar cada banda na
média do seu próprio nível elimina a estrutura de níveis, e uma banda entra no
decil por se destacar **contra o seu próprio nível** — qualquer nível pode
contribuir.

**Critérios.**

- **H11a (a métrica escapa do platô).** A fração do decil de resíduo que cai
  dentro do platô do prior é **< 0,5** em ≥ 4 das 5 partições, no braço
  `literature`. Isto é verificação de sanidade da métrica, não resultado sobre
  o prior: se falhar, o resíduo intra-nível não resolveu o problema e H11b não
  deve ser lido.
- **H11b (a reprodutibilidade distingue conteúdo).** J(`literature`) >
  J(`blocks`) em ≥ 4 das 5 partições. Jaccard é um escalar por célula, não há
  pareamento por semente, de modo que este critério é de contagem e
  deliberadamente fraco.

A guarda de empate vale também aqui: célula cujo resíduo tenha empate exato é
reportada como indefinida.

**Nota de interpretação, fixada antes.** Se H11a for suportada e H11b não, a
leitura é que uma métrica capaz de sair do platô não distingue os braços — o
que reforça, e não enfraquece, a conclusão de que a estabilidade creditada ao
prior é consequência da restrição do conjunto candidato.

---

## O que este pré-registro não testa

Não testa se o prior de literatura é ótimo, nem propõe prior melhor.

Não testa o braço Raman. O prior Raman é contínuo (545 valores distintos,
platô de uma banda) e nada do que motiva este documento se aplica a ele.

Não revisita o artefato de desempate documentado em F002, que é propriedade da
parametrização com prior na inicialização e não ocorre aqui.

## Regra de execução

Os três braços × cinco partições são rodados **uma vez** e reportados qualquer
que seja o resultado. Sem repetição com outra semente, sem refinamento de
grade, sem troca de métrica. Falha de execução é registrada no commit e a
rodada recomeça do zero, com este documento inalterado.

`scripts/06_analise_plato.py` implementa estes critérios e é commitado junto
com este documento, antes de qualquer execução em `--split-seed 5..9`.
