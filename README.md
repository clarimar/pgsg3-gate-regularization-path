# Initialization Is Not Regularization: Separating the Two Roles of a Spectral Prior

Repositório do trabalho sobre o caminho de regularização do gate, no programa
PGSG (Prior-Guided Spectral Gating). Título fixado em 2026-10-16.

## Pergunta científica

Um prior espectral cumpre dois papéis ao mesmo tempo no desenho corrente:
ponto de partida do gate e referência do que o gate deveria ser. Fundidos, o
primeiro **isola** — a normalização pelo máximo converte o topo plano em um
bloco de parâmetros que o gradiente não alcança. Separados, com o prior movido
da inicialização para a função de perda com peso λ, o mesmo prior **informa**
sem isolar.

Quanto de ancoragem o gate precisa para significar alguma coisa, e isso pode
ser medido contra uma referência que não seja o próprio prior?

O enquadramento é **caminho de regularização**, não AutoML/NAS. A busca
automática é método, não tese.

## Programa

Identificar os trabalhos por título ou assunto, nunca por número de pasta:
a numeração já se deslocou uma vez e os números de repositório não coincidem
com os de artigo.

| assunto | estado (out/2026) |
| --- | --- |
| Fundador, NIR interpretável | publicado no Chemolab; corrigendum proposto ao editor |
| Escala e amostras pequenas | **rejeitado**, não será ressubmetido |
| Modalidades NIR→Raman (*Gate Topology and Reproducibility…*) | **aceito** no Chemolab |
| **Caminho de regularização do gate (λ)** | **este repositório** |
| Incerteza (*Prior Specification Bounds What Spectral Attention Can Learn*) | em submissão |
| Multi-alvo | planejado |

Consequência de manutenção: a arquitetura `PGSGv2Model` não tem publicação
que a introduza, porque o manuscrito que faria isso foi rejeitado. Citar o
artigo de modalidades para a arquitetura.

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
