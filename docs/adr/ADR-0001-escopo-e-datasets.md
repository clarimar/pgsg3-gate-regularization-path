# ADR-0001 — Escopo, numeração e datasets do pgsg_3

Data: 2026-08-11
Status: aceito

## Contexto

A proposta de trabalho futuro nº 4 (otimização de λ, τ e largura da rede)
foi promovida a pgsg_3. Multi-alvo desce para pgsg_4; incerteza segue em
pgsg_5.

## Decisões

1. **Numeração.** pgsg_3 = hiperparâmetros. Pendência de manutenção: a
   proposta CNPq/FNDCT 06/2026 já submetida descreve pgsg_3 como multi-alvo
   ao justificar a câmera HSI. Corrigir para pgsg_4 em relatório ou nova
   submissão.

2. **Enquadramento.** Caminho de regularização, não AutoML/NAS. Motivo: a
   pergunta sobre λ é específica da PGSG e quimiometricamente interpretável;
   "rodamos Optuna" não é contribuição para o Chemolab.

3. **Espaço de busca.** PENDENTE — depende da inspeção de `pgsg_v2.py`
   (script `scripts/00_preflight.py`). O documento de origem assume um τ de
   softmax que pertence à `PGSGModel` superseded, não à `PGSGv2Model`
   (sigmoide independente por banda). O espaço deve ser fixado sobre os
   hiperparâmetros que existem de fato: λ (KL), hidden, lr, weight_decay,
   epochs.

4. **Datasets.** Mango DMC v3 (NIR) e bioprocess_substrates (Raman), ambos
   reusados. Rejeitados nesta fase: Corn (reservado para pgsg_4);
   LUCAS/OSSL (projeto próprio, escala não é hipótese aqui); RRUFF
   (identificação mineral, sem alvo quantitativo); MassBank e NIST WebBook
   (eixo m/z discreto ou espectros qualitativos sem concentração — o
   conceito de prior sobre bandas não transfere).

5. **Modelo.** `PGSGv2Model` vendorizada em `src/pgsg_3/m_model/`,
   sha256 `3f6bd21109b4e1249fa9f33cc5eb3a05b7b7af68a398c1c6442e008917f3df33`. Ver PROVENANCE.md.

## Consequências

O risco de dados é nulo (operadores e baselines já validados), e λ fica
como única variável do estudo. Em troca, o projeto não produz evidência
sobre escala ou multi-alvo — deliberadamente, esses são pgsg_4 e adiante.
