# pgsg_3 — Gate Regularization Path

Terceiro projeto do programa PGSG (Prior-Guided Spectral Gating).

## Pergunta científica

Como o peso da regularização KL (λ) governa a transição entre um gate que
replica o prior e um gate orientado por dados — e onde nessa transição fica
o melhor compromisso entre acurácia e interpretabilidade?

O enquadramento é **caminho de regularização**, não AutoML/NAS. A busca
automática é método, não tese.

## Programa

| projeto | eixo que varia            | estado          |
| ------- | ------------------------- | --------------- |
| pgsg_0  | arquitetura (fundador)    | aceito Chemolab |
| pgsg_1  | escala (n)                | submetido       |
| pgsg_2  | modalidade (NIR→Raman)    | submetido       |
| pgsg_3  | hiperparâmetros (λ)       | **ativo**       |
| pgsg_4  | múltiplos alvos           | reservado       |
| pgsg_5  | incerteza                 | reservado       |

## Datasets

Reuso, sem aquisição nova:
- Mango DMC v3 (NIR) — DOI 10.17632/46htwnp833.3, de pgsg_1
- bioprocess_substrates (Raman) — via RamanBench, de pgsg_2

Baselines e operadores já validados nos projetos anteriores; λ é a única
variável do estudo.

## Modelo

`src/pgsg_3/m_model/pgsg_v2.py` — `PGSGv2Model`, vendorizada.
Ver `PROVENANCE.md` no mesmo diretório antes de rodar qualquer coisa.

## Estrutura

    src/pgsg_3/{g_ingest,t_transform,p_prior,m_model,i_interp,sigma_report}/
    scripts/              executáveis; usam a lib, não são importados por ela
    scripts/deprecated/   superseded, movidos e não apagados
    tests/
    docs/adr/             decisões de arquitetura e dataset
    findings/             resultados como snippets .tex
    paper/                manuscrito elsarticle

## Instalação

    conda activate base
    pip install -e .

## Dependência do pacote pgsg_1

O modelo vendorizado `pgsg_v2.py` importa `pgsg_1.ingestion` e
`pgsg_1.models.base`. Antes de rodar testes ou experimentos:

    export PGSG1_ROOT=~/Dropbox/pgsg/pgsg_1/src

`pgsg_v3.py` procura nos caminhos usuais e falha com instrução explícita
se não encontrar.
