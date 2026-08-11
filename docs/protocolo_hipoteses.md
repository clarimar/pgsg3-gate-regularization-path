# Protocolo de hipóteses — pgsg_3

Registrado ANTES de qualquer rodada, para que o resultado degenerado (ver
"Risco antecipado") não possa ser lido como racionalização posterior.

## H0 — coração do projeto (falsificável)

Existe uma faixa de λ em que o gate se descola mensuravelmente do prior
SEM perda de R².

- Métrica de descolamento: ρ(gate, prior) de Spearman.
- Critério: existe λ com ρ < 0,95 e R² dentro de 1 DP do melhor R² observado.

## H1

R² em função de λ tem ótimo interior, não monotonia.

## H2

ρ(gate, prior), entropia, TV e esparsidade de Hoyer variam de forma suave e
monotônica em λ, permitindo escolher λ por critério de interpretabilidade e
não apenas por erro.

## H3

A curva λ→topologia difere entre NIR e Raman de modo consistente com H2/H3
de pgsg_2 (Raman mais esparso, transição mais abrupta).

ATENÇÃO: comparações de suavidade entre modalidades exigem normalização em
unidade física (cm⁻¹), nunca índice de banda. Lição de pgsg_2 H3.

## H4

Busca automática sobre o espaço real NÃO supera significativamente o ajuste
manual de pgsg_1/pgsg_2. Resultado negativo esperado e reportável.

## Risco antecipado — diagrama degenerado

Em pgsg_2, ρ(gate, prior) ≥ 0,978 nas duas modalidades. É plausível que o
gate permaneça colado ao prior em toda a faixa de λ e o diagrama de fase
saia degenerado.

Isso NÃO é fracasso. É a evidência quantitativa de H0 no sentido negativo:
o mecanismo da PGSG seria focalização espectral guiada por prior, e não
refinamento data-driven do gate. Conclusão forte, publicável, e já
antecipada como cientificamente válida nos dois sentidos na proposta CNPq.

## Regra de parada

Se duas normalizações igualmente válidas de uma métrica produzirem
conclusões opostas, a metodologia é não confiável — reportar como tal e
parar, sem refinar. Lição de pgsg_2 H5.
