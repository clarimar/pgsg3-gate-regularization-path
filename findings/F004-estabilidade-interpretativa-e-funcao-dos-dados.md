# F004 — Estabilidade interpretativa é função dos dados, não do prior

Data: 2026-10-23
Verificação: `check_gates_r2.py`
Dados: `data/processed/gates_r2/gates_n{30,60,100,200,400,700,1158}.npz`
Corrige: `docs/adr/ADR-0001-escopo-e-datasets.md`, decisão 6

Vetores de gate herdados da revisão R2 do pgsg_1 (manuscrito **rejeitado**, não
será ressubmetido), sob o protocolo publicado: p = 281, sete tamanhos de treino,
dez sementes genuínas por célula, duas condições de inicialização. Nenhum
treinamento novo: a verificação lê os vetores armazenados, reconstrói o prior de
literatura a partir do eixo de ondas e mede.

`q = p // 10 = 28`, a definição do código publicado.

## Medido

| n | platô, valores distintos | decil dentro do platô | J INDEX | J empates sorteados |
| --- | --- | --- | --- | --- |
| 30 | 1 de 34 | 28/28 | 0,9586 | 0,7005 ± 0,0068 |
| 60 | 1 de 34 | 28/28 | 0,9632 | 0,7005 ± 0,0068 |
| 100 | 1 de 34 | 28/28 | 0,9678 | 0,7005 ± 0,0068 |
| 200 | 1 de 34 | 28/28 | 1,0000 | 0,7005 ± 0,0068 |
| 400 | 1 de 34 | 28/28 | 0,9755 | 0,7005 ± 0,0068 |
| 700 | 1 de 34 | 28/28 | 0,9479 | 0,7005 ± 0,0068 |
| 1158 | 1 de 34 | 28/28 | 0,9479 | 0,7005 ± 0,0068 |

Condição **prior na inicialização**. Em todas as 70 execuções o platô do prior
tem um único valor distinto, amplitude 0,0e+00, s(1−s) entre 9,5×10⁻⁷ e
6,7×10⁻⁶. O gate não carrega ordenação alguma ali, e as 28 bandas do decil saem
inteiramente de dentro do platô. O que a sobreposição mede é a ordem que o
`np.argsort` deixa num bloco empatado.

Sorteando os empates ao acaso — mesmos gates, mesmo q, mesma fórmula — o valor
cai a 0,7005 ± 0,0068 em **todas as sete células**, e 0,7005 é o acaso
combinatório exato de sortear 28 entre 34 duas vezes (0,7000).

| n | platô, valores distintos | decil dentro do platô | J (INDEX = sorteado) |
| --- | --- | --- | --- |
| 30 | 3–34 de 34 | 0,000–0,143 | 0,1141 |
| 60 | 2–34 | 0,000–0,250 | 0,0886 |
| 100 | 2–34 | 0,000–0,286 | 0,1634 |
| 200 | 34 | 0,071–0,357 | 0,3124 |
| 400 | 34 | 0,143–0,321 | 0,4365 |
| 700 | 34 | 0,143–0,321 | 0,3703 |
| 1158 | 34 | 0,250–0,393 | 0,5646 |

Condição **não informada** (θ₀ = 0). Sem empate: INDEX e sorteado coincidem até
o último dígito, porque não há empate para desempatar. O decil não é preso ao
platô. Estes são números genuínos.

## A assinatura diagnóstica

| | prior na inicialização | não informada |
| --- | --- | --- |
| faixa de J | 0,9479–1,0000 | 0,0886–0,5646 |
| Spearman(J, n) | −0,3063 (p = 0,5040) | **+0,9286 (p = 0,0025)** |

O braço não informado melhora com dados, monotonamente, numa variação de 39
vezes em n. O braço com prior **não se move**: J fica entre 0,95 e 1,00 com
n = 30 e com n = 1.158, sem relação com o tamanho de treino.

Isso dá um critério que dispensa qualquer conhecimento do mecanismo:
**medida genuína de estabilidade de seleção tem de depender de n.** Se a
sobreposição entre sementes é a mesma com trinta amostras e com mil e cento e
cinquenta e oito, ela não está medindo seleção. A insensibilidade a n é
evidência de artefato, e é verificável por quem só tenha os números.

> **Correção de 2026-10-24, em revisão externa.** A frase em negrito acima é
> **generalização indevida** e está retirada como regra. Uma medida legítima
> pode permanecer constante com n — por exemplo quando a seleção já
> estabilizou, quando o sinal é fraco demais para que mais dados o resolvam, ou
> quando o procedimento é estruturalmente insensível aos dados. "Tem de
> depender de n" não é teorema.
>
> O que os dados sustentam é o enunciado específico: **neste experimento, a
> estabilidade sem ancoragem cresce com o tamanho amostral (ρ = +0,9286,
> p = 0,0025, numa variação de 39×), enquanto a estabilidade sob prior na
> inicialização permanece em 0,95–1,00 e praticamente invariável (ρ = −0,3214,
> p = 0,4821 no protocolo destes dados).** Isso é evidência de que a métrica
> ancorada **não está captando o mesmo fenômeno** que a condição de controle —
> o que basta para o argumento e não exige a regra universal.
>
> O diagnóstico continua útil como **sinal de alerta**, não como critério:
> sobreposição insensível a uma variação grande de n merece investigação da
> causa, e aqui a causa está medida (platô empatado, F002).
>
> Primeiro erro meu neste programa encontrado por revisão externa antes de mim,
> e é do tipo que eu produzo com mais facilidade: transformar observação real em
> regra. Texto original preservado.

## Alcance

O artefato está presente em **todo experimento NIR com prior na inicialização
que o programa executou**:

- braço NIR do artigo aceito (`findings/F002`): platô 1/34, J = 0,9418,
  sorteado 0,7005;
- sete tamanhos da revisão R2 do pgsg_1 (aqui): platô 1/34 em todos,
  J = 0,9479–1,0000, sorteado 0,7005.

Não está presente, e nada aqui o alcança:

- braço **Raman** do artigo aceito — prior contínuo, 545 valores distintos,
  platô de uma banda, decil 1/187 dentro dele;
- condição **não informada**, em nenhum tamanho;
- os números do **pgsg_3**, que usa θ₀ = 0 (`inert = 0` nas 1500 execuções de
  `--split-seed 5..9`, e `05_diagnostico_jaccard.py` verifica ausência de
  empate exato antes de reportar qualquer Jaccard);
- qualquer **R²** ou **ρ(gate,prior)**, que usam valores e não ordem.

## O que isto faz com a alegação central do programa

A alegação era que o prior de literatura compra reprodutibilidade
interpretativa, com acurácia equivalente. A parte da acurácia equivalente
está medida e permanece. A parte da reprodutibilidade, em NIR, era ordem de
desempate.

A leitura que os dados sustentam é a inversa: **estabilidade de seleção de
bandas é função da quantidade de dados.** Sem prior ela vai de 0,09 a 0,56
entre n = 30 e n = 1.158. Com o prior na inicialização ela não é medida.

## Convenção de decil, e uma divergência que era minha

**Correção de 2026-10-24.** A primeira versão desta nota tratava a faixa de
Jaccard da decisão 6 do `ADR-0001` (0,945--0,987) como divergente da
recomputação (0,9479--1,0000). **O ADR estava certo; o erro era meu.**

`gate_metrics.csv` registra `q = 29` por linha, e ao q = 29 a recomputação casa
exatamente com os valores armazenados: 0,9600; 0,9556; 0,9689; 0,9867; 0,9763;
0,9452; 0,9496 — faixa 0,9452--0,9867, que é o 0,945--0,987 declarado. O
`check_gates_r2.py` usava `int(p × 0,10)` = 28, truncando, e foi essa diferença
de convenção que produziu a falsa divergência. Verificado por
`scripts/resolver_divergencias.py`.

**Isso expõe inconsistência real no programa: duas convenções de decil em três
bases de código.**

| base | definição | q em p = 281 |
| --- | --- | --- |
| `gate_metrics.csv` (pgsg_1 R2) | `ceil(0,10 p)` | **29** |
| `pgsg_3`, `jaccard_medio` | `ceil(0,10 p)` | **29** |
| ablação H4 do pgsg_2 (publicada) | `len(wl) // 10` | **28** |

Os dois protocolos dão números diferentes e **níveis de chance diferentes**:
29 de 34 dá 0,7436; 28 de 34 dá 0,7000. Não se misturam, e o manuscrito declara
qual vale para qual conjunto.

### Os números desta nota, por protocolo

As tabelas acima foram computadas a **q = 28**, isto é, na convenção do pgsg_2
aplicada aos dados do pgsg_1. Os valores no protocolo próprio destes dados
(q = 29) são: 0,9600; 0,9556; 0,9689; 0,9867; 0,9763; 0,9452; 0,9496 no braço
de literatura, e 0,1121; 0,0898; 0,1663; 0,3068; 0,4328; 0,3855; 0,5658 no
braço não informado.

**As conclusões não mudam, e isso é verificável:**

| | q = 29 (protocolo destes dados) | q = 28 (como reportado acima) |
| --- | --- | --- |
| sem ancoragem, Spearman com n | **+0,9286 (p = 0,0025)** | **+0,9286 (p = 0,0025)** |
| prior na init, Spearman com n | −0,3214 (p = 0,4821) | −0,3063 (p = 0,5040) |
| faixa sem ancoragem | 0,0898--0,5658 | 0,0886--0,5646 |
| faixa com prior na init | 0,9452--0,9867 | 0,9479--1,0000 |

O manuscrito usa a coluna de q = 29 para estes dados e a de q = 28 para a
célula publicada do pgsg_2, que é a convenção do código que a gerou. O colapso
por desempate daquela célula — 0,9418 para 0,7005 contra acaso 0,7000 — está
em q = 28 e permanece correto como está.

### Erro meu, do tipo espelhado

Nos casos anteriores eu afirmei coisas erradas sobre os meus próprios
resultados. Aqui apontei divergência num documento de 2026-08-12 que estava
correto, por usar convenção diferente da que os dados registram. A lição é
operacional: **ler o protocolo que o arquivo declara antes de recomputar**, e
não impor o do script.
