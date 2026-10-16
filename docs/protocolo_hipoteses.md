# Protocolo de hipóteses — pgsg_3

Registrado ANTES de qualquer rodada, para que nenhum desfecho possa ser
lido como racionalização posterior.

Revisado em 2026-08-12 à luz da revisão R2 do trabalho de amostras
pequenas, que mediu com 10 sementes genuínas o que antes era conhecido
apenas com réplicas degeneradas.

Revisado em 2026-10-16 (ADR-0002): o **protocolo de execução** mudou — split
agrupado por fruto, orçamento de passos fixo, otimizador declarado, e uma
referência de relevância não-circular. **As hipóteses e o critério de H0
abaixo NÃO mudaram** e permanecem como foram pré-registrados. A
concordância com o PLS calibrado, acrescentada em outubro, é exploratória e
está identificada como tal na seção própria.

## Ponto de partida estabelecido (não é hipótese — é dado)

Antes de pgsg_3 começar, sabe-se, de pgsg_1 (R2) e pgsg_2, ambos com 10
sementes por condição:

1. O prior **não** melhora acurácia em nenhum tamanho de treino
   (Δ_prior não significativo em n = 30 … 1.159; Wilcoxon pareado).
2. O gate inicializado pelo prior praticamente não se move dele
   (ρ ≥ 0,9987 em NIR; ≥ 0,978 em Raman).
3. Sem prior, o gate converge para uma solução de **acurácia equivalente**
   mas quase não correlacionada com a química conhecida (ρ ≤ 0,28) e
   instável entre sementes (Jaccard 0,09--0,57 contra 0,945--0,987).

Ou seja: o problema admite muitas soluções igualmente boas em erro, e a
inicialização escolhe entre elas em vez de melhorá-las. **λ é o parâmetro
que deveria controlar essa escolha de forma contínua.** É isso que pgsg_3
testa.

## Mecanismo introduzido

`PGSGv3Model` acrescenta à perda um termo λ · KL(gate ‖ prior):

- λ = 0 recupera a `PGSGv2Model` exatamente (verificável por teste).
- λ → ∞ congela o gate no prior.
- A condição não-informada de pgsg_1 corresponde a λ = 0 com θ₀ = 0.

## H0 — coração do projeto (falsificável)

Existe uma faixa de λ em que o gate se descola mensuravelmente do prior
SEM perda de R² **e sem perda de reprodutibilidade entre sementes**.

- Descolamento: ρ(gate, prior), Spearman e Pearson.
- Reprodutibilidade: Jaccard do decil superior entre pares de sementes.
- Critério: existe λ com ρ < 0,95, R² dentro de 1 DP do melhor observado,
  e Jaccard ≥ 0,90.

A terceira condição é nova e é o que distingue H0 de uma pergunta já
respondida: sabe-se que existe solução com ρ baixo e R² equivalente (a
condição não-informada), mas ela tem Jaccard ≤ 0,57. A pergunta é se λ
permite ocupar o espaço intermediário — descolamento com estabilidade —
ou se as duas propriedades são inseparáveis.

## H1

R²(λ) tem ótimo interior, não monotonia.

## H2

ρ(gate,prior), Jaccard, entropia, TV e esparsidade de Hoyer variam de
forma suave e monotônica em λ, permitindo escolher λ por critério de
interpretabilidade e não apenas por erro.

## H3

A curva λ→topologia difere entre NIR e Raman de modo consistente com
H2/H3 de pgsg_2 (Raman mais esparso, transição mais abrupta).

ATENÇÃO: comparações de suavidade entre modalidades exigem normalização
em unidade física (cm⁻¹), nunca índice de banda. Lição de pgsg_2 H3.

## H4

Busca automática sobre o espaço real NÃO supera significativamente o
ajuste manual de pgsg_1/pgsg_2. Resultado negativo esperado e reportável.

## Desfechos antecipados — nenhum é fracasso

**(a) Existe faixa intermediária.** H0 suportada: λ dá controle contínuo
sobre o trade-off descolamento/estabilidade, e o diagrama de fase é a
contribuição.

**(b) Transição abrupta.** O gate salta da ancoragem total para o regime
não-informado sem estágio intermediário útil. Isso significa que as duas
propriedades são inseparáveis nesta arquitetura — resultado forte, que
explica por que pgsg_1 e pgsg_2 só observaram os extremos.

**(c) Diagrama degenerado.** O gate permanece colado ao prior em toda a
faixa. O mecanismo da PGSG é focalização espectral guiada por prior, e
não refinamento a partir dos dados, e a penalidade KL é redundante com a
inicialização.

Os três são publicáveis e os três estavam previstos antes da execução.

## Protocolo de execução

- Mínimo de **10 sementes por configuração**, com a semente do modelo
  variando junto com a do cenário. Lição direta do trabalho de amostras
  pequenas: fixar `seed=42` nas fábricas produziu réplicas idênticas no
  maior n e intervalos de confiança de largura zero.
- Dispersão reportada como desvio padrão sobre as sementes; comparações
  entre condições por teste pareado por semente (Wilcoxon), nunca por
  comparação de médias independentes.
- Grade de λ: logarítmica, ancorada em λ=0 como controle exato da
  `PGSGv2Model`, refinada entre 0,1 e 1 onde a transição ocorre.
- **Split agrupado por fruto.** Os 1.448 espectros da safra 4 vêm de 725
  frutos, 723 medidos duas vezes. Divisão por frutos inteiros.
- **Orçamento de passos fixo.** Todas as configurações rodam o mesmo número
  de épocas e o estado medido é o final, não o de melhor val_loss. Sem isso,
  o deslocamento das bandas saturadas — proporcional ao número de passos —
  confunde λ com contagem de passos.
- **Otimizador declarado e varrido.** Adam (L2 acoplado) e AdamW
  (desacoplado) produzem gates diferentes; a escolha é variável de desenho.
- Demais hiperparâmetros fixos (hidden=32, lr=1e-3, weight_decay=1e-4,
  batch_size=256), para que λ seja a única variável.

## Métrica exploratória (acrescentada em 2026-10-16)

ρ(gate, prior) mede aderência ao ponto de partida, que λ controla por
construção — ela não diz se o gate está **certo**. A concordância de Spearman
entre o gate e os coeficientes absolutos de um PLS calibrado na partição de
treino é uma referência derivada dos dados, não do prior.

Esta métrica **não entra no critério de H0**, que foi fixado antes das
rodadas. É reportada à parte, identificada como exploratória. A pergunta que
ela abre — existe λ em que o gate concorda com a referência melhor do que em
qualquer dos extremos? — é para ser pré-registrada antes de ser testada como
hipótese, não decidida depois de olhar a curva.

## Regra de parada

Se duas normalizações igualmente válidas de uma métrica produzirem
conclusões opostas, a metodologia é não confiável — reportar como tal e
parar, sem refinar. Lição de pgsg_2 H5.
