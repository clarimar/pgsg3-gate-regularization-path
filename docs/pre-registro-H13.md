# Pré-registro — H13 (condicionar a métrica no prior)

Registrado em: **2026-10-23**
Status: **fechado antes de qualquer execução em `--split-seed 10..14`**

Complementa `pre-registro-H5-H6`, `H7-H9`, `H10-H11` e `H12-raman`. **Não revisa
veredito nenhum deles.** H5a, H7, H8, H9-blocks e H10a ficam como saíram.

---

## Declaração de motivação

Posterior aos dados, e isto muda o quanto vale. O que motiva:

1. Em NIR, o Spearman de espectro inteiro entre gate e |coef PLS| é
   **insensível à posição do prior**: `blocks` iguala ou supera a literatura em
   10 das 10 partições (F002, F003). A explicação oferecida é que a métrica é
   dominada pela separação **entre** níveis do prior, que toda realocação
   reproduz por construção.

   > **Correção de 2026-10-23, posterior ao fechamento deste documento.** O
   > "10 das 10" acima está **errado** e é erro de contagem meu, não dos dados.
   > Conferindo célula por célula: nas partições 0–4 a literatura supera
   > `blocks` na partição 3 (+0,2757 contra +0,2045, p = 0,0020, que é a única
   > célula em que H7-blocks foi suportada). Nas partições 5–9 `blocks` supera
   > em 5/5. O número correto é **9 das 10**.
   >
   > Nas cinco partições desta rodada (10–14), medido depois, a literatura
   > supera `blocks` na métrica crua em **3 de 5** (+0,3724/+0,3288;
   > +0,3418/+0,1517; +0,2914/+0,2141, contra +0,2692/+0,3540 e
   > +0,1843/+0,2932). Isso **enfraquece a premissa** de H13: nestas partições
   > a métrica crua já distingue em 3/5, de modo que "a métrica crua não
   > consegue ver" vale menos aqui do que nas dez anteriores.
   >
   > **Nenhum critério de H13 é alterado.** O erro está na motivação, não nos
   > enunciados, e a secundária 2 — o Spearman cru nas mesmas cinco partições —
   > foi declarada justamente para que a comparação crua-contra-condicionada
   > seja feita nos mesmos dados. É ela que decide se condicionar acrescentou
   > algo, e agora ela tem um alvo mais exigente do que eu supunha ao escrever
   > este documento.
   >
   > O texto original fica como está. O mesmo erro saiu nas mensagens dos
   > commits 8042bed e 4cd2119, que são história e não se corrigem; esta nota é
   > o registro.
2. Em Raman, com prior contínuo, a mesma métrica **distingue**: literatura
   supera `blocks` em 2 de 3 partições, e ρ(prior, referência) é +0,16 a +0,24
   na literatura contra ≈ 0 nos dois controles (F005). O sinal existe quando a
   métrica consegue vê-lo.
3. Em NIR, o sinal positivo mais consistente aparece **dentro do piso** do
   prior — 223 bandas, 5/5 com p = 0,0020 — e não dentro do platô (F003). Isso
   foi análise terceira declarada, não primária.

Se (1) é efeito de confundimento pelo prior, então remover a contribuição do
prior da métrica deve revelar em NIR o sinal que o Raman mostra. H13 testa isso
com uma métrica **definida pelo problema**, não escolhida pela saída, em
partições novas.

As dez partições já executadas não servem: foram lidas repetidas vezes.

---

## A métrica, e por que duas formas dela

O defeito comum às quatro métricas já testadas é não remover a contribuição do
próprio prior. Duas maneiras de removê-la, e as duas entram porque fazem
suposições diferentes:

**Forma contínua — Spearman parcial.** Correlação parcial de primeira ordem
sobre postos:

    ρ(g, r | s) = (ρ_gr − ρ_gs · ρ_rs) / sqrt((1 − ρ_gs²)(1 − ρ_rs²))

com g o gate, r a referência |coef PLS|, s o prior, e todos os ρ de Spearman.
Fórmula fechada, sem ajuste. Remove a componente **linear nos postos** do
prior.

**Primeira limitação, declarada agora.** Com prior de quatro níveis, o posto do
prior tem empates massivos e a remoção linear é grosseira: ela não elimina a
estrutura de níveis, apenas a sua parte linear. É por isso que a segunda forma
existe.

**Segunda limitação, e é quantitativa.** O denominador é
√((1−ρ_gs²)(1−ρ_rs²)), de modo que a estatística **amplifica** a correlação
residual por 1/√(1−ρ_gs²). Em λ = 1 o valor medido é ρ(gate, prior) = 0,9655,
o que dá amplificação de **3,8×**:

| ρ(gate, prior) | amplificação |
| --- | --- |
| 0,90 | 2,3× |
| **0,9655** (λ = 1, medido) | **3,8×** |
| 0,98 | 5,0× |
| 0,9983 (λ = 10) | 17,2× |

No limite em que o prior determina o gate exatamente, o parcial fica
**indefinido**, não zero — o denominador zera. Em λ = 10 ele seria inutilizável,
e é parte do motivo de a comparação primária estar fixada em λ = 1.

A análise reporta ρ_gs e o fator de amplificação por célula, para que o valor
parcial não seja lido ao pé da letra. O fator **não** é limiar: o critério é o
deste documento e não menciona amplificação.

> **Correção de 2026-10-23, posterior ao fechamento.** A tabela acima foi
> calculada com **Pearson** ρ(gate, prior) = 0,9655, que é o que a varredura
> reporta na coluna `rho(g,s)`. O parcial usa **Spearman**, e o valor medido é
> **0,7058**, logo a amplificação real é **1,41×** e não 3,8×. A estatística é
> muito melhor condicionada do que este documento alertava. Erro meu, e
> favorável.
>
> E o 0,7058 **não é medida**: saiu idêntico nas cinco partições, em toda
> semente e em todo braço. Quando o gate ordena as bandas estritamente por
> nível do prior, o posto do prior é constante dentro de cada nível e a
> correlação fica determinada pelos tamanhos dos níveis apenas — 223/7/17/34 dá
> 0,7058. Os braços de controle preservam o multiset e compartilham o valor.
> Registrado em `findings/F006` e fixado por teste.

**Forma exata — dentro de um nível.** Spearman entre gate e referência restrito
às bandas de um único nível do prior, onde o prior é constante e portanto
contribui **zero** por construção. É a mesma estatística de H10, aplicada ao
**piso** (223 bandas), que é o único nível com bandas suficientes e o único com
sinal consistente até aqui.

As duas respondem à mesma pergunta sob suposições diferentes. Concordarem é o
que torna a leitura robusta; discordarem localiza o problema na suposição
linear.

---

## Desenho

Cinco partições novas agrupadas por fruto, `--split-seed 10,11,12,13,14`, três
braços (`literature`, `blocks`, `shuffled`), 10 sementes, **λ ∈ {0; 1}**,
θ₀ = 0, Adam, 500 épocas fixas, decil 0,10.

A execução usa `02_lambda_sweep_controlled.py` **sem modificação**, com
`--lambdas 0,1`. Nenhum código novo de varredura: é o script já testado que
produziu todos os resultados anteriores. λ = 1 é a comparação primária, fixado
agora, e λ = 0 entra como linha de base.

Referência recalibrada por partição: `pls_reference_relevance` com dobras
agrupadas por fruto, regra de 1 EP, `H_MAX = 120`, como em todo o braço NIR.

`scripts/08_analise_condicional.py` aplica os critérios e é commitado junto com
este documento, antes de qualquer execução.

**A grade, os braços, as métricas e os limiares estão fechados.**

### Guarda de empate

Célula com empate exato entre gates é reportada como **indefinida**, nunca
imputada, dentro do nível sob análise e no espectro inteiro. Em `pgsg_3` não se
esperam empates (θ₀ = 0, `inert = 0` em 1500 execuções), e a guarda existe
porque o artefato de F002 nasceu de empates lidos como ordenação.

---

## H13a — a métrica condicionada acha sinal onde a crua não acha

**Enunciado.** No braço de literatura, o Spearman parcial ρ(gate, referência |
prior) em λ = 1 é positivo.

**Critério.** Pareado por semente contra zero, Wilcoxon bilateral p < 0,05, com
média positiva. *Suportada* se valer em ≥ 4 das 5 partições.

## H13b — e a posição do prior importa quando ela é a única coisa medida

**Enunciado.** O Spearman parcial do braço de literatura supera o do braço
`blocks`.

**Critério.** Pareado por semente, Wilcoxon bilateral p < 0,05. *Suportada* se
valer em ≥ 4 das 5.

**Refutação, informativa nos dois sentidos.** Se `blocks` igualar ou superar a
literatura em ≥ 2 partições, então a insensibilidade da métrica crua em NIR
**não** era confundimento pelo prior: o prior NIR simplesmente não carrega
informação posicional, e a diferença em relação ao Raman está nos priors e não
nas métricas. Esse resultado é mais forte que H13b suportada, porque explica a
discrepância NIR/Raman sem apelar a propriedade de métrica.

> **Retratação de 2026-10-23, posterior à execução.** A cláusula de refutação
> acima **está errada** e a sua leitura é retirada. H13b condiciona na variável
> que distingue os braços: com ρ_gs estruturalmente fixo, o parcial é
> proporcional a ρ_gr − 0,7058·ρ_rs, de modo que **subtrai** um múltiplo da
> correlação entre o prior de cada braço e a referência. Um braço cujo prior
> aponta para a referência é penalizado; um cujo prior é anticorrelacionado tem
> o termo **somado**. Medido na partição 13: literatura perde 0,1659 e `blocks`
> ganha 0,0700.
>
> A estatística portanto **premia um prior que aponta para o lugar errado**, e
> não pode testar se a posição do prior carrega conteúdo. Que `blocks` a supere
> em 5/5 não autoriza concluir nada sobre o prior NIR.
>
> O critério e o veredito ficam como saíram — 0/5, não suportada — porque
> emendar critério depois dos dados é o que este documento existe para impedir.
> O que muda é a **interpretação**, e o erro é de desenho meu: escrevi uma
> pergunta que a estatística escolhida não podia responder. As estatísticas que
> podem são a crua (secundária 2) e as intra-nível (H13c, e H10b em F003).
> Registrado em `findings/F006` e fixado por teste.

## H13c — o achado do piso, promovido a primário

**Enunciado.** No braço de literatura, o Spearman entre gate e referência
restrito às 223 bandas do **piso** do prior é positivo em λ = 1.

**Critério.** Pareado por semente contra zero, Wilcoxon bilateral p < 0,05,
média positiva, em ≥ 4 das 5 partições.

Em F003 isto deu 5/5 com p = 0,0020 em todas, como análise terceira declarada.
H13c é o teste confirmatório em partições novas, e é o único critério deste
documento que repete uma observação anterior em vez de abrir pergunta nova.

**Nota de interpretação, fixada antes.** Sinal positivo no piso é afirmação
sobre onde o gate encontra estrutura que a referência externa sustenta. **Não**
é afirmação de que o prior está errado sobre quais bandas importam: a
referência é |coef PLS| de um PLS calibrado, que é proxy operacional e não
verdade química. Essa distinção vale para todo este documento.

---

## Análises secundárias, declaradas agora

1. **As duas formas uma contra a outra.** Spearman parcial e Spearman no piso,
   lado a lado por célula. Concordância em sinal é o que sustenta a leitura.
2. **`shuffled` nas três estatísticas**, reportado ao lado de `blocks`.
3. **O Spearman cru de espectro inteiro nas mesmas cinco partições**, para que
   a comparação entre métrica crua e condicionada seja feita nos **mesmos**
   dados e não contra as dez partições anteriores.
4. **ρ(prior, referência) por braço**, sem modelo, como em F005.

Nenhuma entra nos vereditos.

## O que não é afirmado

Nada sobre acurácia: o estudo todo já estabeleceu que o prior não compra R².

Nada sobre o prior ser quimicamente certo ou errado. A referência é proxy.

Nada em Raman: `pre-registro-H12-raman.md` encerrou aquele braço, e λ = 1 com
prior contínuo já foi medido lá.

## Regra de execução

Cinco partições × três braços, rodadas **uma vez**, reportadas qualquer que
seja o resultado. Sem repetição com outra semente, sem partição extra, sem
refinamento de grade, sem troca de métrica. Falha de execução é registrada no
commit e a rodada recomeça do zero, com este documento inalterado.

Custo: 15 execuções de `02` com dois pontos de λ. A varredura de dez pontos
levou 225 s por partição, então a estimativa é de 45 a 60 s por célula mais a
calibração do PLS, isto é **15 a 25 minutos no total**. A estimativa anterior
de custo errou por um fator de quatro na direção favorável (F005); se esta
passar de uma hora, a execução é interrompida e registrada.
