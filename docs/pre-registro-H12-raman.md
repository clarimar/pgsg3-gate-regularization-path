# Pré-registro — H12 (o braço Raman como controle da quantização)

Registrado em: **2026-10-23**
Status: **fechado antes de qualquer execução em Raman**

As três decisões de desenho ao final foram revisadas e aceitas antes deste
fechamento.

Complementa `docs/pre-registro-H5-H6.md`, `H7-H9` e `H10-H11`. **Não revisa
veredito nenhum deles.**

---

## A pergunta

Os defeitos documentados em `findings/F002`, `F003` e `F004` foram todos
medidos em NIR, com um prior que é **função escada de quatro níveis** e platô
de 34 bandas contra decil de 28 ou 29. A explicação que oferecemos é que os
defeitos vêm dessa quantização:

- o decil não sai do nível de topo porque o platô é maior que `q`;
- a concordância de espectro inteiro é dominada pela separação entre níveis,
  e por isso realocar os blocos não piora;
- o Jaccard do braço com prior na inicialização é ordem de desempate, porque o
  platô satura e fica bit-idêntico.

Se a explicação está certa, os três defeitos **devem desaparecer** com um prior
contínuo na mesma arquitetura. O braço Raman é esse teste, e é o controle mais
forte disponível: mesma arquitetura, mesmo código, prior de forma funcional
diferente.

O prior Raman (`RamanGlucosePrior`, soma de 19 gaussianas com σ = 15 cm⁻¹,
normalizada pelo pico, `clip(0,01; 1,0)`) já foi medido no arquivo
`h1_raman_v2_result.npz` do artigo aceito: **p = 1870, q = p // 10 = 187, 545
valores distintos, platô no máximo de 1 banda, decil 1/187 dentro dele, e 1326
bandas empatadas no piso 0,01.** Essa parte não precisa de execução e é
reportada como estabelecida, não testada.

---

## Hipóteses

**H12a — o decil não é preso a grupo de empate.** A maior fração do decil
superior do gate que cai dentro do maior grupo de empate do prior (as 1326
bandas no piso) é **< 0,5**, em 3/3 partições, em λ = 1. Em NIR a fração no
platô é 1,000 em 15/15 células.

**H12b — não há colapso por desempate.** Sorteando os empates exatos ao acaso,
o Jaccard muda em **menos de 0,02** em 3/3 partições. Em NIR a mudança é
+0,2413 (0,9418 → 0,7005) e em todas as sete células do pgsg_1 R2 é da mesma
ordem.

**H12c — a comparação entre braços passa a ser informativa.** No braço de
literatura, a concordância de espectro inteiro com a referência de relevância
em λ = 1 **supera** a do braço `blocks`, pareado por semente, Wilcoxon
bilateral p < 0,05, em **2 das 3** partições.

Em NIR, `blocks` iguala ou supera a literatura em 10/10 partições. H12c é o
teste da explicação: se a insensibilidade da métrica em NIR vem da estrutura de
degraus, com prior contínuo ela deve desaparecer.

**Refutação de H12c, e ela é informativa nos dois sentidos.** Se `blocks`
igualar ou superar a literatura também em Raman, a insensibilidade **não** é
efeito de quantização, e a leitura (b) de H7 — o ganho de concordância não
depende de onde o prior aponta — ganha confirmação independente numa segunda
modalidade. Esse resultado é mais forte que H12c suportada, e precisa ser
reportado com o mesmo destaque.

---

## Desenho

| | |
| --- | --- |
| dados | `bioprocess_substrates` (RamanBench, `chlange/SubstrateMixRaman`), alvo glicose |
| pré-processamento | `RamanPreprocessor` do pgsg_2: remoção de raios cósmicos, baseline ALS, SNV |
| p após pré-processamento | 1870 (confirmar na execução) |
| q | `p // 10` = 187 |
| prior | `RamanGlucosePrior()` sobre o eixo em cm⁻¹ |
| braços | `literature`, `blocks`, `shuffled` |
| λ | **{0; 1}** apenas |
| sementes de modelo | 10 |
| partições | 3 (`--split-seed 0,1,2`) |
| inicialização | θ₀ = 0 |
| otimizador / épocas | Adam, 500 fixas |

λ = 0 entra como linha de base sem ancoragem, necessária para o Jaccard de
H12b ter contra o que ser comparado. A grade completa de λ **não** faz parte
deste pré-registro.

`permute_prior` não é modificado. Em prior contínuo, `base = prior.min()` é o
piso 0,01 e as regiões elevadas são as ~19 corcovas gaussianas, que `blocks`
realoca preservando forma e largura de cada uma. A ocupação é de 544 bandas
elevadas em 1870 (29%), contra 58 em 281 (21%) no NIR; se a realocação sem
sobreposição falhar, é falha de execução registrada no commit, pela regra de
sempre.

## O que este pré-registro NÃO afirma

**Nada sobre acurácia.** A ingestão Raman do pgsg_2 não expõe identificador de
lote, corrida ou réplica, e o pgsg_2 particionou com `train_test_split`
simples. Sem agrupamento não há defesa contra vazamento de réplica — que é
exatamente o erro que o pgsg_1 R2 corrigiu no NIR. Logo **nenhum R², ΔR² ou
comparação com PLS de acurácia sai desta rodada**, e o R² é registrado apenas
como sanidade de que o modelo treinou.

As hipóteses acima são todas sobre geometria da métrica e comparação **interna**
entre braços, que compartilham a mesma partição e por isso são imunes a essa
limitação.

**Nada sobre o caminho de λ em Raman.** Dois pontos não são caminho.

**Nada sobre o braço Raman do artigo aceito.** Aquele usou prior na
inicialização; este usa θ₀ = 0. São parametrizações diferentes e os números não
são comparáveis.

## Referência de relevância

`pls_reference_relevance` de `src/pgsg_3/g_ingest/grouped.py`, com
`groups_tr=None`, que cai em K-fold simples de 5 dobras — consequência direta da
ausência de identificador de grupo, declarada acima. Regra de 1 EP, `H_MAX=120`,
calibrada **na partição de treino de cada partição**. É a mesma função e a mesma
regra do braço NIR; só as dobras deixam de ser agrupadas.

A referência é calculada **uma vez por partição** e compartilhada pelos três
braços, que dividem a mesma partição.

## Caminho de engenharia

O `02_lambda_sweep_controlled.py` **não é modificado** — é o script que produziu
todos os resultados já commitados, e os testes fixam a equivalência bit-exata
em λ = 0. A rodada Raman vai em script novo, `07_raman_lambda1.py`, que importa
`permute_prior` do `02` em vez de reimplementá-la, para que os braços sejam
produzidos pela mesma função já testada.

Os módulos Raman do pgsg_2 (`ingestion/raman_bioprocess`, `preprocessing/raman`,
`priors/raman`, `models/adapter`) **não são vendorizados**: usam import absoluto
de pacote (`from pgsg2.ingestion.base import …`), de modo que carregar por
caminho de arquivo exigiria reconstruir o pacote. São importados pondo
`<pgsg_2>/src` no `sys.path`, exatamente o mecanismo com que o `02` já depende
de `PGSG1_ROOT`.

Custo registrado dessa escolha: reproduzir esta rodada exige os dois
repositórios externos em disco, e não apenas o `pgsg_3`. A alternativa seria
vendorizar quatro módulos mais o `base.py` do pacote, considerada e rejeitada
por ser mais código copiado sem ganho real de reprodutibilidade — o dataset em
si já vem de download externo.

## Custo, declarado antes

Estimativa a partir do NIR: 225 s para 100 execuções com p = 281 e n = 1158,
≈ 2,3 s por execução. Em Raman p é 6,6× e n é 6×, então a estimativa é de
45 a 90 s por execução. O desenho tem 2 λ × 10 sementes × 3 braços × 3
partições = **180 execuções**, isto é, **2,5 a 4,5 horas**.

Acresce a calibração do PLS de referência: uma curva de CV com `H_MAX=120` em
5 dobras sobre ~5.568 × 1.870, uma vez por partição. Estimo 5 a 15 minutos por
partição, 15 a 45 minutos no total.

A estimativa é grosseira e pode errar por um fator de dois. Se a primeira
partição levar muito mais que 50 minutos, a execução é interrompida e o desenho
é renegociado **antes** de ver qualquer resultado, registrando a interrupção no
commit.

## Regra de execução

Três partições × três braços, rodadas **uma vez**, reportadas qualquer que seja
o resultado. Sem repetição, sem partição extra, sem troca de métrica. Falha de
execução é registrada e a rodada recomeça do zero, com este documento
inalterado.

`07_raman_lambda1.py` implementa os critérios e é commitado junto com a versão
fechada deste documento, antes de qualquer execução.

---

## Decisões de desenho, tomadas e registradas

1. **Três partições, não cinco.** Custo. Com cinco o critério seria 4/5 como
   nos anteriores; com três é 3/3 para H12a e H12b, que devem ser
   determinísticos, e 2/3 para H12c. Três é o mínimo que permite contagem;
   duas não permitiria.
2. **Partição não agrupada, com a limitação declarada.** A alternativa é
   investigar se `bioprocess_substrates` traz identificador de corrida que a
   ingestão do pgsg_2 descarta, e implementar agrupamento. Isso abriria a porta
   para afirmações de acurácia em Raman, mas é trabalho de ingestão de tamanho
   desconhecido e não está no caminho crítico deste artigo.
3. **λ ∈ {0; 1} apenas.** Suficiente para as três hipóteses. A grade completa
   custaria cinco vezes mais e responderia uma pergunta — o caminho de λ em
   Raman — que este artigo não precisa fazer. Os dois valores ficam fixos no
   código e **não** são expostos como argumento de linha de comando, para que a
   grade não possa derivar durante a execução.

### Validação antes da rodada longa

`07_raman_lambda1.py --quick` subamostra para 300 amostras e 200 bandas, com 30
épocas, só para confirmar que o encadeamento carrega, pré-processa, constrói o
prior e treina. O modo `--quick` imprime aviso em destaque e **não** escreve em
diretório de resultados. Nenhum número vindo dele entra em lugar algum.
