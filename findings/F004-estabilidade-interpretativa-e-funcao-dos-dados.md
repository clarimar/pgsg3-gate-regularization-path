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

## Ponta solta

A decisão 6 do `ADR-0001` declara a faixa de Jaccard do braço de literatura
como 0,945--0,987. A recomputação dá 0,9479--1,0000, e o 1,0000 em n = 200 está
fora da faixa declarada. `gate_metrics.csv` no mesmo diretório guarda
`jaccard_lit` por tamanho e deve conciliar isso — não foi lido aqui porque o
script o descartou como não numérico, e o número conciliado não muda nenhuma
conclusão acima, já que o artefato vale em todas as sete células
independentemente do quarto decimal.
