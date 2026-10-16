# Pré-registro — H5 (concordância) e H6 (acurácia)

Registrado em: **2026-10-16**
Status: **fechado antes de qualquer execução em partição diferente de `split_seed=42`**

Este documento existe porque a métrica de concordância com o PLS calibrado foi
acrescentada em outubro/2026, **depois** das varreduras, e o máximo interior
observado em λ=1 foi visto antes de qualquer hipótese ser formulada sobre ele.
Uma observação dessa natureza não é evidência para si mesma. O que segue fixa,
antes de novos dados, o que contaria como confirmação e o que contaria como
refutação.

Nada aqui altera o critério de H0, pré-registrado em
`docs/protocolo_hipoteses.md` e já avaliado.

---

## O que foi observado (motivação, não evidência)

Partição canônica (`split_seed=42`, agrupada por fruto), 10 sementes, orçamento
fixo de 500 épocas, Adam e AdamW:

| condição | concordância com |coef PLS-1se| |
| --- | --- |
| gate sem ancoragem (λ=0) | +0,044 |
| prior de literatura sozinho | +0,170 |
| gate ancorado (λ=1) | **+0,274** |
| gate fortemente ancorado (λ=10) | +0,263 |

Pareado por semente: λ=1 supera λ=0 em 10/10 (p=0,002), supera o prior sozinho
em 10/10 (p=0,002) e supera λ=10 em 9/10 (p=0,006). R² em λ=1 supera λ=0 em
10/10 (+0,018, p=0,002).

Uma única partição. O trabalho "Prior Specification Bounds What Spectral
Attention Can Learn" mediu que, entre partições agrupadas por população de
colheita, a dispersão é **cinco a sete vezes** a dispersão entre sementes, com
R² variando de −0,61 a +0,66. A margem de λ=1 sobre λ=10 é +0,011, bem dentro
do que uma troca de partição pode mover.

---

## H5 — máximo interior na concordância

**Enunciado.** A concordância entre o gate ajustado e uma referência de
relevância derivada dos dados tem máximo no interior da grade de λ: a ancoragem
parcial concorda com a referência melhor do que o gate sem ancoragem e melhor
do que o prior sozinho.

**Referência.** Coeficientes absolutos de um PLS calibrado **na partição de
treino daquela partição**, H pela regra de 1 EP, grade até 120. A referência é
recalibrada por partição; usar a de outra partição seria vazamento. O H
selecionado é registrado por partição.

**Métrica.** Correlação de Spearman entre o vetor de gate e |coef PLS|.

**Desenho do teste.** Cinco partições novas agrupadas por fruto,
`--split-seed 0,1,2,3,4`, 10 sementes cada, mesma grade de λ
{0; 0,001; 0,01; 0,1; 0,2; 0,3; 0,5; 0,7; 1; 10}, otimizador Adam, orçamento
fixo de 500 épocas. **A grade de λ está fechada: não será refinada depois de
ver os resultados.**

**Critérios, fixados agora.**

- **H5a (existe máximo interior).** Em cada partição, o argmax de λ sobre a
  concordância média não está na borda da grade (nem λ=0 nem λ=10).
  *Suportada* se valer em ≥ 4 das 5 partições.
- **H5b (supera o prior).** Na partição, a concordância em λ* (o argmax) supera
  a concordância do prior sozinho com a referência daquela partição, pareado por
  semente, Wilcoxon bilateral p < 0,05.
  *Suportada* se valer em ≥ 4 das 5.
- **H5c (a posição é estável).** λ* cai a no máximo um passo de grade de λ=1
  (isto é, em {0,7; 1; 10}) em ≥ 3 das 5 partições.

**Refutação.** H5 é considerada **não suportada** se o argmax estiver na borda
em ≥ 2 partições, ou se H5b falhar em ≥ 2. Nesse caso o achado de outubro é
reportado como específico da partição em que foi medido, e assim descrito no
manuscrito.

**H5c pode falhar com H5a e H5b suportadas.** Isso seria resultado próprio: o
máximo interior existe e vale, mas sua posição depende da partição, de modo que
λ não é transportável e precisa ser escolhido por validação em cada aplicação.

---

## H6 — a penalidade melhora ligeiramente a acurácia

**Enunciado.** A penalidade KL(gate‖prior) melhora o R² fora da amostra em
relação a λ=0, de forma pequena mas consistente.

**Desenho.** Mesmas cinco partições. Comparação pareada por semente entre λ=0 e
λ*, com λ* definido como em H5.

**Critério.** *Suportada* se a diferença for positiva com Wilcoxon p < 0,05 em
≥ 4 das 5 partições.

**Nota de interpretação, fixada antes.** Um efeito positivo aqui é atribuível à
penalidade como **regularizador**, não ao conteúdo químico do prior. Separar as
duas coisas exigiria um prior embaralhado como controle, que **não** faz parte
deste pré-registro. Se H6 for suportada, o manuscrito dirá exatamente isso e
não mais.

---

## O que não é afirmado

Este trabalho **não** afirma que o modelo com gate é bom preditor nestes dados.
Na partição canônica, PLS calibrado atinge R² = 0,914 contra 0,821 do melhor λ,
coerente com o ΔR² = −0,108 ± 0,031 do artigo aceito. As hipóteses acima são
sobre o que o gate **significa**, não sobre o quanto ele acerta.

## Análise secundária, declarada agora e reportada à parte

Partições por **população de colheita** (coluna `Pop`), deixando uma população
de fora por vez. É teste mais duro que o agrupamento por fruto, porque
introduz deslocamento de distribuição. Declarado aqui para que não possa ser
apresentado depois como se tivesse sido planejado; será reportado como análise
secundária qualquer que seja o resultado, e **não** entra nos critérios de H5 e
H6 acima.

## Regra de execução

As cinco partições são rodadas **uma vez**, e o resultado é reportado qualquer
que seja. Sem repetição com outra semente de partição, sem refinamento de
grade, sem troca de métrica. Se algo der errado na execução (falha de
alinhamento, erro de código), a correção é registrada no commit e a rodada
recomeça do zero, com este documento inalterado.
