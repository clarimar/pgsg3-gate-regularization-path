# F007 — O controle de deslocamento depende do platô, e pouco onde importa

Data: 2026-10-25
Verificação: `scripts/09_controle_deslocamento.py`
Dados: `data/processed/gates_r2/gates_n{30,60,100,200,400,700,1158}.npz`
Origem da pergunta: redação da §9.3, exigência 3 do registro editorial
Decisão editorial que a motivou: `ADR-0003` e a instrução do autor de
2026-10-25 — não declarar sustentação integral antes de medir

## A pergunta, e por que ninguém a tinha feito

O artigo aceito responde à objeção de que o prior poderia comprar
reprodutibilidade imobilizando o gate, medindo o **deslocamento**
d = g_final − g₀ e reportando ρ(d) = 0,9462 em NIR. `F002` mostra que a
sobreposição de decil naquele braço é ordem de desempate; o controle de
deslocamento não aplica operador de seleção e não consulta ordem dentro de
bloco empatado, logo é **imune àquele defeito**. Isso é demonstrável por
argumento e está demonstrado na §9.3.

O que não era demonstrável por argumento: sob prior na inicialização,
θ₀ = logit(s), portanto g₀ = σ(logit(s)) = s **exatamente**, e d = g_final − s.
No platô o prior é 1 e o gate treinado permanece em 1, logo **d ≡ 0 nas 34
bandas, em toda semente, por construção.** 12,1% do espectro concorda
trivialmente entre quaisquer duas sementes, e isso entra em ρ(d).

Não é o artefato de desempate — midranks são determinísticos, nenhum sort
decide nada, a fração é 34/281 e não o conjunto selecionado inteiro. Mas não é
nada, e **"não é afetado" era mais forte do que o programa havia medido.**

## Medido

Premissa confirmada. `max |d|` no platô: 1,19×10⁻⁶ a 6,68×10⁻⁶ sob prior na
inicialização; 1,64×10⁻² a 5,29×10⁻² sob θ₀ = 0. O platô está em d ≈ 0 no
braço ancorado e não está no outro, que é o que a saturação prevê.

Braço **prior na inicialização**:

| n | Pearson todas | fora do platô | queda | rel | Spearman todas | fora | queda | rel |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 30 | 0,2492 | 0,1358 | −0,1134 | −46% | 0,2073 | 0,0788 | −0,1285 | −62% |
| 60 | 0,2357 | 0,0605 | −0,1752 | −74% | 0,2056 | 0,0404 | −0,1652 | −80% |
| 100 | 0,2572 | 0,1233 | −0,1339 | −52% | 0,2141 | 0,0720 | −0,1421 | −66% |
| 200 | 0,7945 | 0,5888 | −0,2057 | −26% | 0,6541 | 0,5026 | −0,1515 | −23% |
| 400 | 0,8164 | 0,7259 | −0,0905 | −11% | 0,7537 | 0,6490 | −0,1047 | −14% |
| 700 | 0,8562 | 0,7990 | −0,0572 | −7% | 0,7811 | 0,6830 | −0,0981 | −13% |
| **1158** | **0,9369** | **0,9185** | **−0,0184** | **−2%** | **0,8879** | **0,8369** | **−0,0510** | **−6%** |

Cai em **7 de 7** células, nas duas definições.

Braço **θ₀ = 0**, que é a linha de base do que remover 34 de 281 bandas faz de
qualquer modo: quedas de −0,0240 a +0,0032, **média −0,0124**, contra média
**−0,1135** no braço ancorado. **Nove vezes.** O excesso é o platô, e é
específico da inicialização no prior.

## Três conclusões, e a terceira eu não previ

**1. A dependência existe e está confirmada.** O enunciado "não é afetado"
está retirado. O defensável é: imune ao artefato de desempate, por argumento;
dependente do platô, por medida.

**2. No regime que importa, é pequena.** A última linha é a relevante para o
0,9462 publicado, que vem do conjunto completo: −0,018 em Pearson, −0,051 em
Spearman. **Isso dissolve a primeira pendência da §9.3** — eu havia dito que
sem saber se ρ(d) é Pearson ou Spearman não se saberia se a pendência era
relevante. A conclusão é a mesma nas duas definições, logo a definição deixou
de bloquear o enunciado. Continua desejável registrá-la para exatidão de
métodos; não é mais pré-requisito.

**3. ρ(d) responde a dados, e isso defende o controle.**
Spearman(ρ(d), n) = **+0,9643, p = 0,0005** sobre todas as bandas, e
**+0,8929, p = 0,0068** depois de remover o platô. O controle de deslocamento
**passa** no diagnóstico que a prescrição 5 da §9.4 propõe — variar n e ver se
a medida responde — enquanto a métrica de decil **falha** nele (−0,3214,
p = 0,4821).

Esta é a defesa mais forte daquele controle que o programa produziu, e ela não
existia antes desta medida. A pergunta nasceu de uma suspeita contra o artigo
anterior e terminou produzindo evidência a favor dele.

> **Limite desta conclusão, precisão do autor em 2026-10-25.** `+0,8929`
> estabelece **associação monotônica forte nas sete condições examinadas**, e
> nada além. **Não** estabelece que a estabilidade restante seja causada por
> aprendizado de bandas quimicamente relevantes: essa inferência exige suporte
> verdadeiro conhecido, que nenhum dos dois conjuntos oferece.
>
> E responder a n é **diagnóstico de sensibilidade aos dados**, não teste de
> validade interpretativa. O enunciado correto é: *o controle de deslocamento
> é sensível aos dados onde a métrica de decil não é* — evidência favorável
> sobre a medida, não validação da interpretação construída sobre ela. A
> redação de "passou no diagnóstico" foi estreitada na §9.3.2 por esta razão;
> eu havia escrito "passa" e "falha" como se fossem veredito de validade.

## Avaliação do autor, linha a linha

| resultado | interpretação sustentada |
| --- | --- |
| queda em 7/7 tamanhos, Pearson e Spearman | o platô contribui para a correlação de deslocamentos |
| queda média 0,1135 contra 0,0124 no controle | há efeito adicional associado à configuração com inicialização no prior |
| queda de 0,0184 e 0,0510 em n = 1158 | a contribuição do platô é relativamente pequena nesse tamanho |
| Spearman +0,8929, p = 0,0068, sem o platô | a associação entre estabilidade do deslocamento e tamanho amostral permanece |
| correlações baixas fora do platô em n ≤ 100 | a reprodutibilidade do deslocamento é limitada em amostra pequena |

Nenhuma linha desta tabela afirma recuperação de relevância química, e a
coluna da direita é o limite do que cada medida sustenta.

## A ressalva que sobra, e que o artigo anterior não afirmou

Em n ≤ 100, ρ(d) fora do platô é 0,04 a 0,14 e o total 0,21 a 0,26: a
reprodutibilidade do deslocamento ali é **majoritariamente platô**. É
limitação de regime, não defeito do controle, e o artigo aceito não faz
afirmação em amostra pequena. Vale como limitação declarada da §10 e como
argumento adicional para a prescrição 4 — não pôr o prior na inicialização.

## O que isto NÃO é

**Não é validação interpretativa.** Ver o limite declarado acima.

**Não é recomputação do 0,9462.** Aquele número vem da execução NIR do estudo
aceito, que não está neste repositório. Estes são os vetores herdados da
revisão R2 do pgsg_1: mesmo conjunto, mesmo prior, mesmo regime de
inicialização, dez sementes por tamanho. Restringem o que podemos **afirmar**
em geral; não reenunciam o número publicado.

**Nenhum resultado do fixture sintético é evidência sobre o artigo anterior.**
O fixture de `09` serviu para verificar que o script discrimina, e os seus
números são da minha construção. Instrução explícita do autor em 2026-10-25,
e a lição já registrada no `F002` sobre fixture descalibrado.

---

## Extensão de 2026-10-26 — P1, P2 e P3 separadas e medidas

A §9.3 afirmava que o deslocamento no platô é zero por construção. Revisão
externa apontou que `max |d|` fica entre 1,2×10⁻⁶ e 6,7×10⁻⁶, logo é desprezível
e **não nulo**, e que três propriedades estavam conflatadas na mesma frase:

| | definição | situação antes |
| --- | --- | --- |
| **P1** | as 34 bandas do platô têm o mesmo valor de gate **dentro** de uma execução | medida |
| **P2** | esse valor comum é igual **entre** execuções | **não medida por nenhum script** |
| **P3** | magnitude de d = g_final − s nas bandas do platô | medida |

O `check_gates_r2.py` computa `len(np.unique(g[idx]))` **por linha** e nunca
compara linhas entre si, logo media P1 e nunca P2.

### P1, medida por valor e por padrão de bits

Verdadeira em **10/10 execuções nas sete condições**, tanto por igualdade de
valor sobre os `float64` armazenados quanto por igualdade de bits via
`view(np.int64)`. No braço θ₀ = 0, falsa em 10/10 — sem saturação não há empate,
que é o previsto.

### P2, medida por condição e nunca agregada

**Não nula em todas as sete.** Amplitude do valor comum sobre as dez sementes:

| n | P2 | max \|d\| (P3) | P2 em ulps de float32 |
| --- | --- | --- | --- |
| 30 | 2,384×10⁻⁷ | 1,192×10⁻⁶ | 2 |
| 60 | 3,576×10⁻⁷ | 1,311×10⁻⁶ | 3 |
| 100 | 2,384×10⁻⁷ | 1,192×10⁻⁶ | 2 |
| 200 | 3,576×10⁻⁷ | 1,550×10⁻⁶ | 3 |
| 400 | 1,192×10⁻⁶ | 2,623×10⁻⁶ | 10 |
| 700 | 2,027×10⁻⁶ | 4,292×10⁻⁶ | 17 |
| 1158 | 4,053×10⁻⁶ | 6,676×10⁻⁶ | 34 |

Spearman(P2, n) = +0,9092 (p = 0,0045), **associação exploratória**: sete
condições não sustentam que aumentar n afaste as sementes, e a leitura causal
não está disponível.

**E não uso a correlação entre P2 e max |d| como evidência independente.** As
duas são construídas dos mesmos valores de platô — P2 é a amplitude de
(s − d_r) sobre as execuções, logo P2 ≤ 2·max |d| por construção. Correlacionam
porque compartilham dependência matemática, não porque um mecanismo as una.

### O desfecho, e por que não reabre a hipótese

É o segundo dos três casos possíveis: **P1 verdadeira e P2 > 0.** As duas
propriedades se separam, e o artefato de desempate repousa na primeira — um
empate dentro de uma execução não exige que duas execuções empatem entre si.
A caracterização empírica do mecanismo mudou; a validade da pergunta, não.
P2 entra como diagnóstico complementar e **não** como requisito retrospectivo
da hipótese originalmente investigada.

### Resolução das medidas — e dois erros meus na primeira redação

**Erro 1: o espaçamento.** Eu usei 2⁻²³ = 1,192093×10⁻⁷, que é o espaçamento
do `float32` **acima** de 1,0. Um gate é σ(θ) < 1, logo o platô fica em
[0,5 , 1,0), onde o espaçamento é **2⁻²⁴ = 5,960464×10⁻⁸** — 1,0 é potência de
dois e está na fronteira entre duas regiões. Conferido:
`np.spacing(np.float32(0.999998808))` = 5,960464×10⁻⁸. No espaçamento correto,
P2 dá **4, 6, 4, 6, 20, 34 e 68** passos, o dobro do que eu havia reportado.

E a resolução **não** é piso universal de detecção de P2: depende da região
numérica que os valores ocupam, e seria outra se o platô estivesse em 0,5 ou
em 0,1.

Por isso o `09` passou a ler o espaçamento nas **duas pontas** do intervalo
observado e a **recusar** a contagem de passos quando as pontas discordam —
valores que atravessam a fronteira de uma binade não têm resolução única, e ler
o espaçamento num extremo para aplicá-lo ao intervalo inteiro é exatamente o
erro que eu acabei de cometer, uma casa adiante. Encontrei isso com um fixture
cujo platô cruzava 1,0; nos dados reais σ(θ) < 1 e as sete condições ficam
inteiras em [0,5 , 1,0), então a contagem vale — mas vale porque foi conferida,
não porque σ é limitada.

**Erro 2: representabilidade não é proveniência.** `exactly representable in
float32: True` nas sete condições demonstra que os `float64` armazenados
**pertencem à grade do `float32`**. Não demonstra que foram calculados em
precisão simples: arredondamento, conversão explícita ou quantização antes do
armazenamento deixariam o mesmo traço. Três níveis, mantidos separados:

| | |
| --- | --- |
| **demonstrado** | os valores são exatamente representáveis em `float32` |
| **hipótese explicativa** | aritmética em precisão simples em algum ponto a montante |
| **proveniência confirmada** | exigiria rastrear os dtypes em treino, exportação e carregamento |

O `09` passou a imprimir essa ressalva junto do resultado, para que ninguém leia
a representabilidade como proveniência — eu li. E a comparação de bits passou a
exigir `dtype == float64` explicitamente: `view(np.int64)` pressupõe essa
largura, e uma suposição que vale a pena enunciar vale a pena conferir.

### Erro meu

Eu havia reduzido P2 a `np.ptp` sobre as **médias** do platô por execução. Uma
média atribui valor único ao platô mesmo quando P1 falha — exatamente quando a
quantidade não significa nada. Apanhado por revisão externa antes de rodar.
