# ADR-0001 — Escopo, numeração e datasets do pgsg_3

Data: 2026-08-11
Revisado: 2026-08-12 (decisão 3 fechada; decisões 1 e 6 atualizadas)
Status: aceito

## Contexto

A proposta de trabalho futuro nº 4 (otimização de λ, τ e largura da rede)
foi promovida a pgsg_3. Multi-alvo desce para pgsg_4; incerteza segue em
pgsg_5.

## Decisões

1. **Numeração.** pgsg_3 = hiperparâmetros / caminho de regularização.
   Pendência de manutenção: o texto `pgsg_CNPq_C.tex` (Universal 06/2026,
   Faixa C) descreve pgsg_3 como multi-alvo em sete pontos (linhas 54, 71,
   72, 104, 153, 156, 172), incluindo a justificativa da câmera HSI-SWIR
   ("múltiplos analitos por amostra física"), que pertence a pgsg_4. O
   documento `pgsg_2_proposta.tex` repete a numeração antiga em três pontos
   (linhas 53, 54, 184). Ambos ainda não submetidos — corrigir antes.
   A proposta PGSG-Bio (CT-Biotec 24/2026) não menciona pgsg_3--5 e não
   requer correção nesse aspecto.

2. **Enquadramento.** Caminho de regularização, não AutoML/NAS. Motivo: a
   pergunta sobre λ é específica da PGSG e quimiometricamente interpretável;
   "rodamos Optuna" não é contribuição para o Chemolab.

3. **Espaço de busca — FECHADO** (2026-08-12). A inspeção de `pgsg_v2.py`
   confirmou por evidência no código, e não por memória, os hiperparâmetros
   que a `PGSGv2Model` de fato expõe:

   ```
   PGSGv2Model(*, hidden=32, lr=0.001, weight_decay=0.0001,
               max_epochs=500, patience=30, batch_size=256, seed=42)
   ```

   Duas consequências:

   - **Não existe τ.** O documento de origem assume uma temperatura de
     softmax que pertence à `PGSGModel` superseded. A busca por `tau` e
     `temperature` no código retorna zero ocorrências; `softmax` aparece
     apenas em comentário, justificando por que a sigmoide foi escolhida
     (gradiente ~58x maior em p=281). O teste `test_sem_tau_de_softmax`
     em `tests/test_smoke.py` é sentinela: se falhar, esta decisão precisa
     ser revista.
   - **Não existe λ.** Não há termo de regularização na `PGSGv2Model`. O
     prior entra exclusivamente pela inicialização dos logits do gate
     (θ₀ = logit(s)), como o §3.2 do pgsg_1 descreve. Logo pgsg_3 não
     otimiza um λ existente: **introduz** λ como peso de uma penalidade
     KL(gate ‖ prior) na função de perda, em uma subclasse `PGSGv3Model`.
     λ → 0 recupera a `PGSGv2Model` exatamente; λ → ∞ congela o gate no
     prior. Ver ADR-0002.

   Grade de λ e demais hiperparâmetros: ver `docs/protocolo_hipoteses.md`.

4. **Datasets.** Mango DMC v3 (NIR) e bioprocess_substrates (Raman), ambos
   reusados. Rejeitados nesta fase: Corn (reservado para pgsg_4);
   LUCAS/OSSL (projeto próprio, escala não é hipótese aqui); RRUFF
   (identificação mineral, sem alvo quantitativo); MassBank e NIST WebBook
   (eixo m/z discreto ou espectros qualitativos sem concentração — o
   conceito de prior sobre bandas não transfere).

5. **Modelo.** `PGSGv2Model` vendorizada em `src/pgsg_3/m_model/`,
   sha256 `3f6bd21109b4e1249fa9f33cc5eb3a05b7b7af68a398c1c6442e008917f3df33`.
   Ver PROVENANCE.md. O arquivo vendorizado **não é modificado**; a
   `PGSGv3Model` é subclasse em arquivo separado, e o hash continua
   validando o ponto λ=0.

6. **Dados de partida herdados** (novo, 2026-08-12). A revisão R2 do pgsg_1
   produziu, sob o protocolo publicado (p=281, 7 tamanhos de treino, 10
   sementes genuínas), os vetores de gate nas duas condições de
   inicialização. Estão em `data/processed/gates_r2/` (cópia de
   `prior-guided-spectral-gating/revision_r2/results/rerun_gates/`) e
   fornecem os dois extremos do caminho de regularização antes de qualquer
   rodada de pgsg_3:

   | condição | ρ(gate,prior) | Jaccard entre sementes | corresponde a |
   | --- | --- | --- | --- |
   | prior de literatura | 0,9987--1,0000 | 0,945--0,987 | ancoragem total |
   | não informada | 0,025--0,280 | 0,090--0,566 | ausência de ancoragem |

   Com R² estatisticamente equivalente entre as duas em todos os tamanhos
   (Wilcoxon pareado, 10 sementes). Isso estabelece, antes de pgsg_3
   começar, que o problema admite soluções de acurácia equivalente com
   gates quase não correlacionados — que é precisamente o espaço que λ
   deve percorrer.

## Consequências

O risco de dados é nulo (operadores e baselines já validados), e λ fica
como única variável do estudo. Em troca, o projeto não produz evidência
sobre escala ou multi-alvo — deliberadamente, esses são pgsg_4 e adiante.

A decisão 3 muda a natureza da contribuição: pgsg_3 deixa de ser um estudo
de ajuste de hiperparâmetros e passa a ser uma **extensão arquitetural**
(introdução de λ) acompanhada do estudo do caminho que ela abre. Isso é
mais publicável no Chemolab e responde a uma pergunta que pgsg_1 e pgsg_2
deixaram explicitamente em aberto.
