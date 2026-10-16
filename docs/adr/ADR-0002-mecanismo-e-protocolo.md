# ADR-0002 — PGSGv3Model e correção de protocolo

Data: 2026-10-16
Status: aceito
Fecha a referência pendente na decisão 3 do ADR-0001.

## Contexto

Em agosto/2026 foram executadas quatro varreduras de λ (`results/sweep_*`).
Entre aquela data e hoje, dois trabalhos do programa mudaram o que se sabe
sobre o mecanismo e sobre o protocolo, e ambos invalidam parte do desenho
daquelas varreduras:

1. **"Gate Topology and Reproducibility of Prior-Guided Spectral Gating
   Across Near-Infrared and Raman Spectroscopy"** (aceito, Chemolab).
   Estabelece que (i) os 1.448 espectros NIR da safra 4 vêm de 725 frutos,
   723 medidos duas vezes, de modo que um split aleatório coloca as duas
   medidas do mesmo fruto em lados opostos; e (ii) com PLS calibrado na
   partição de treino (regra de 1 EP, H entre 46 e 73), o modelo com gate
   **não** supera o PLS em NIR — ΔR² = −0,108 ± 0,031 em dez divisões
   agrupadas, negativo em todas. A vantagem de +0,23 era baseline com H=10.

2. **"Prior Specification Bounds What Spectral Attention Can Learn"**
   (em submissão). Estabelece que o gradiente que chega a θⱼ é proporcional
   a σ'(θⱼ) = sⱼ(1 − sⱼ), de modo que bandas inicializadas nos extremos do
   intervalo unitário ficam isoladas dos dados; que normalizar um prior pelo
   seu máximo converte o topo plano em um bloco de parâmetros inertes (34
   bandas, informação de Fisher 8,6×10⁻⁹ contra 0,72 nas ativas); e que, sob
   Adam com decaimento acoplado, o deslocamento de um gate saturado é a
   integral da taxa de aprendizado, previsível sem referência aos dados.

## Decisões

1. **`PGSGv3Model` como subclasse.** O prior entra na perda como
   λ·KL_Bernoulli(g ‖ s), média sobre as p bandas (λ comparável entre
   modalidades com p diferentes). λ=0 reproduz a `PGSGv2Model` bit a bit,
   verificado por `test_lambda_zero_reproduz_v2`. O arquivo vendorizado
   `pgsg_v2.py` não é alterado e seu hash segue válido.

2. **Separação dos dois papéis do prior (`init_from_prior`).** O prior pode
   servir de ponto de partida (θ₀ = logit s) ou de referência da penalidade,
   e os dois papéis eram fundidos. A varredura de agosto com `init=prior`
   mostrou λ inerte (ρ de 0,9987 a 0,9999); o mecanismo, agora documentado
   pelo trabalho 2, é que ∂KL/∂θ = (θ − logit s)·σ'(θ) começa exatamente em
   zero em toda banda e permanece em zero nas 34 do platô, onde σ' ≈ 10⁻⁶.
   A penalidade é inerte justamente nas bandas que o prior declara mais
   importantes. Com `init_from_prior=False` nenhuma banda está isolada na
   inicialização (σ'(0) = 0,25 em todas) e o prior continua restringindo
   pela penalidade. **É a única parametrização, entre as testadas no
   programa, em que o prior informa sem isolar** — as mitigações do
   trabalho 2 (prior gaussiano, recorte em [0,1; 0,9], reescala dos logits,
   AdamW) mantêm o prior na inicialização.

3. **Quatro controles acrescentados ao protocolo** (`02_lambda_sweep_controlled.py`):

   | controle | motivo | antes |
   | --- | --- | --- |
   | split agrupado por fruto | réplicas do mesmo fruto em lados opostos | aleatório |
   | orçamento de passos fixo | deslocamento ∝ nº de passos; variava 246–499 | early stopping |
   | otimizador declarado | forma do decaimento muda o gate ajustado | Adam implícito |
   | concordância com PLS calibrado | ρ(g, prior) mede aderência ao ponto de partida, não acerto | ausente |

   O agrupamento, o split e a calibração do PLS são vendorizados de
   `pgsg2-nir-raman-gating@63b0bd9` em `src/pgsg_3/g_ingest/grouped.py`,
   sem mudança de lógica, para que o protocolo seja idêntico ao do artigo
   aceito e o pgsg_3 não adquira um segundo repositório como dependência.

4. **A métrica de concordância é exploratória.** O critério de H0 foi
   pré-registrado em `docs/protocolo_hipoteses.md` antes de qualquer rodada
   (ρ < 0,95 **e** R² a menos de 1 DP do melhor **e** Jaccard ≥ 0,90) e
   permanece intacto. A concordância de Spearman entre o gate e os
   coeficientes absolutos do PLS calibrado foi acrescentada em outubro/2026,
   depois das varreduras, e é reportada **como exploratória**. Não é usada
   para declarar H0 suportada. Mudar um critério pré-registrado à luz dos
   dados é precisamente o erro que a revisão do trabalho de amostras
   pequenas corrigiu.

5. **As varreduras de agosto não são descartadas.** Elas são o registro do
   que o protocolo anterior produz, e a varredura 1 (`results/sweep_nir/`)
   é evidência direta da inércia da penalidade sob inicialização ancorada.
   Ficam em `results/` com esta ADR explicando sob que protocolo foram
   obtidas.

## Consequências

O resultado de H0 obtido em agosto (suportada em λ ∈ [0,2; 0,5]) **não
transita** para o protocolo corrigido: foi medido com split vazado,
orçamento variável e sem referência não-circular. Precisa ser remedido antes
de qualquer redação.

A premissa comercial do projeto também muda. Com PLS calibrado, o modelo com
gate não é o melhor preditor nestes dados NIR, então o trabalho não pode ser
apresentado como ajuste de um modelo vencedor. O enquadramento honesto é
sobre o mecanismo: quanto de ancoragem o prior precisa para que o gate
signifique alguma coisa, medido contra uma referência que não é o próprio
prior.
