# Proveniência do modelo

Arquivo: `pgsg_v2.py` (classe `PGSGv2Model`)
Origem : `/home/clarimar/Dropbox/pgsg/pgsg_1/pgsg_v2.py` (repositório prior-guided-spectral-gating)
SHA-256: `3f6bd21109b4e1249fa9f33cc5eb3a05b7b7af68a398c1c6442e008917f3df33`
Copiado: 2026-08-11

Este é o **único** modelo válido do programa PGSG. Gerou todos os
resultados publicados de pgsg_0/pgsg_1 e todos os de pgsg_2.

NÃO usar, sob nenhuma circunstância:
  - `src/pgsg_1/models/pgsg.py` (PGSGModel — softmax + PLS + diferenças
    finitas + SGD). Órfã superseded. Nunca gerou resultado publicado.
  - `pgsg_torch.py` (PGSGModelTorch). Experimento descartado.

Verificar integridade antes de qualquer rodada:
    sha256sum src/pgsg_3/m_model/pgsg_v2.py
