# F002 — O que as métricas interpretativas do programa medem

Data: 2026-10-23
Protocolo: `docs/pre-registro-H7-H9.md` (H7, H8, H9)
Análise: `scripts/04_analise_controles.py` (vereditos), `scripts/05_diagnostico_jaccard.py` (descritivo)
Dados: `results/ctl_part0..4`, `ctl_blocks_part0..4`, `ctl_shuffled_part0..4`

Dois braços de controle sobre o prior, cinco partições agrupadas por fruto,
dez sementes, λ fixado em 1 pelo pré-registro. `blocks` realoca as regiões
elevadas para posições aleatórias preservando multiset, número de blocos,
comprimento e forma interna. `shuffled` permuta tudo. A permutação é sorteada
uma vez por partição e compartilhada entre sementes de modelo.

Verificação de pareamento: em λ = 0 o prior não entra na perda, e a
concordância em λ = 0 é idêntica entre os três braços nas cinco partições.
Partições mal pareadas seriam detectadas aqui.

## O prior

Quatro valores distintos sobre 281 bandas:

| nível | bandas |
| --- | --- |
| 0,1 | 223 |
| 0,6 | 7 |
| 0,8 | 17 |
| 1,0 | 34 |

É uma função escada. Três regiões elevadas somando 58 bandas, piso de 223
bandas. Toda a informação que esse prior carrega é **onde** os degraus estão e
**qual a largura** deles.

## A estrutura que invalida as duas métricas

Mediram-se, nas quinze células (5 partições × 3 braços), e com os mesmos
valores em todas:

- `p = 281`, decil superior `q = ceil(0,10 p) = 29`
- platô do prior (bandas empatadas no máximo) `= 34`
- fração do decil que cai dentro do platô `= 1,000`

**O decil superior nunca sai do platô do prior.** Em nenhum braço, em nenhuma
partição. Logo o Jaccard entre sementes não mede seleção de bandas: mede qual
subconjunto de 29 entre 34 bandas empatadas vence, e nada além disso. Não é
inferência, é aritmética de platô contra decil, e vale para qualquer prior
normalizado min–max cujo platô exceda `q`.

A mesma quantização degrada a outra métrica. O Spearman entre gate e
|coef PLS| sobre as 281 bandas é dominado pela separação **entre** níveis — se
os grupos elevados ficam acima do piso — e toda realocação reproduz isso por
construção. A ordenação dirigida pelos dados vive **dentro** de cada nível,
onde a separação entre níveis não contribui.

## Vereditos pré-registrados

**H7-blocks: não suportada (1/5).** Cláusula de refutação acionada: `blocks`
iguala ou supera `literature` em 4 partições. Concordância em λ = 1,
literatura contra blocks: +0,2676/+0,4641, +0,2072/+0,3757, +0,2083/+0,2654,
+0,2757/+0,2045, +0,2535/+0,3292. O ρ do próprio prior com a referência, antes
de treinar qualquer gate, é maior em `blocks` que em `literature` em 4/5
(+0,4208, +0,2746, +0,2013, +0,1207, +0,2268 contra +0,1503, +0,1314, +0,1269,
+0,1878, +0,1395).

**H7-shuffled: suportada (4/5).** Destruir contiguidade prejudica.

**H8: não suportada (0/5), nos dois braços.** Ancorar em prior sem conteúdo
eleva a concordância: de +0,031…+0,070 em λ = 0 para +0,087…+0,464 em λ = 1.
Pelo pré-registro, ancoragem e conteúdo passam a ser parcelas reportadas
separadamente.

**H9-blocks: não suportada (3/5).** **H9-shuffled: suportada (5/5).** Jaccard
em λ = 1: literatura 0,9867/0,9763/1,0000/0,9867/1,0000; blocks
0,9867/0,8786/0,9644/0,9867/0,9325; shuffled
0,9689/0,9570/0,9748/0,9585/0,9570. As dez diferenças de controle são
negativas ou nulas: nenhum braço de controle supera a literatura em
reprodutibilidade. Contra J = 0,6252 em λ = 0 na partição 0 — comparação
interna ao experimento.

A conclusão de H9 sobrevive por caminho diferente do previsto. Não porque os
controles empatam, mas porque `shuffled`, com ρ(prior, referência) **negativo**
em 4/5 partições, ainda atinge 0,957–0,975. Estabilidade entre sementes é
alcançável com o prior anticorrelacionado com a referência, e portanto **não
valida** a interpretação.

## Duas explicações mecânicas propostas e descartadas

Registradas porque o erro é informativo e porque ambas chegaram a ser escritas
como leitura dos dados antes de serem testadas.

**"A posição não compra nada."** Falsa. Compra reprodutibilidade: realocar os
blocos derruba o Jaccard em duas partições, e nenhum controle o supera em
nenhuma.

**"O decil seleciona as bandas às quais o regressor é indiferente."** Proposta
a partir de ρ(g em λ=0, contagem de vitórias no decil) negativo nas quinze
células (−0,220 a −0,663), com as bandas perdedoras tendo g₀ maior que as
vencedoras em 15/15 (significativo em 13/15). Descartada pela referência
externa: a mesma pergunta feita a |coef PLS| dá ρ **positivo** nas cinco
células do braço de literatura (+0,412, +0,234, +0,402, +0,434, +0,309), e as
bandas que mantêm vaga têm 2–3× a relevância PLS das que a perdem (5,93/2,33;
6,52/3,55; 6,82/2,11; 5,15/2,13; 5,97/2,62; significativo em 3/5).

O sinal negativo de ρ(g₀, vitórias) é fato sobre a saída do modelo de gate em
λ = 0, **não** sobre as bandas. Usar o gate em λ = 0 como definição de "o que
os dados queriam" fecha um laço pela própria arquitetura sob exame; é por isso
que a coluna de referência externa existe.

## Consequência, e o que ela não autoriza

O braço de literatura é o que ordena melhor **dentro** do platô contra a
referência externa: 5/5 em sinal, contra 4/5 em `blocks` e padrão misto em
`shuffled`. Isso levanta a possibilidade de que H7 tenha sido refutada por
insensibilidade da métrica, não por ausência de conteúdo.

**Essa possibilidade não revisa H7.** O veredito pré-registrado fica como
saiu. A observação é posterior aos dados, motivada por tê-los visto, e a
maneira honesta de refazer a pergunta é pré-registrar uma métrica intra-nível
e executá-la em partições novas (`--split-seed 5..9`), de modo que o teste seja
confirmatório e não a terceira leitura dos mesmos quinze diretórios.

## Verificação no artigo aceito

Feita sobre os arquivos arquivados do próprio `pgsg_2`, sem treinar nada.

**NIR.** `nir_gate_v2_extraction.npz`: p = 281, `q = p // 10 = 28` (divisão
inteira, definição do código publicado), prior com os mesmos quatro níveis
(0,1 ×223; 0,6 ×7; 0,8 ×17; 1,0 ×34), platô de 34, **decil 28/28 dentro do
platô**. Toda banda fora do platô está estritamente abaixo dele. O prior NIR
oficial é o mesmo: a docstring de `src/pgsg2/priors/nir_gaussian.py` registra
que `make_literature_prior` de `pgsg_1` é função degrau e que *"é o prior que
gerou os resultados publicados"*; a versão gaussiana existe só como ablação de
H3.

**Raman.** `h1_raman_v2_result.npz`: p = 1870, q = 187, prior **contínuo**
(soma de 19 gaussianas, σ = 15 cm⁻¹, normalizada pelo pico), 545 valores
distintos, platô no máximo de **1 banda**, decil 1/187 dentro dele. O
mecanismo não se aplica ao braço Raman.

**A condição de comparação publicada é `prior=None`**, não prior aleatório,
apesar do nome das variáveis (`r2_rand_*`, `jaccard_rand_*`):
`run_h4_prior_ablation.py` documenta *"init não-informada (prior=None — theta
inicia em zeros, gate uniforme)"*. Números publicados: NIR J = 0,9418 contra
0,6002; Raman J = 0,9011 contra 0,6545; R² praticamente idêntico nas duas
condições e nas duas modalidades. A ablação, como executada, compara prior
contra ausência de prior, e por isso não separa conteúdo de ancoragem — que é
o que os braços de controle deste trabalho fazem.

## Terceira explicação mecânica proposta e descartada

Registrada pelo mesmo motivo que as duas anteriores.

**"O Jaccard NIR publicado é artefato de ordenação."** No gate NIR arquivado,
as 34 bandas do platô têm valor **bit-idêntico** (0,99999380, amplitude
0,0e+00, s(1−s) = 6,2×10⁻⁶ contra 0,133 fora) — a saturação por inicialização
no prior de F001. Daí a hipótese de que `argsort` escolheria 28 entre 34
valores iguais por ordem de índice, fixando o conjunto e inflando o Jaccard.

**Falsa, e pelo sinal oposto.** `np.argsort` usa quicksort por default e **não
é estável**: um bloco empatado é ordenado pela partição e a seleção muda com os
valores do entorno. Medido em gates sintéticos com platô totalmente empatado:
J = 0,7301, contra nível de chance 0,7000 para 28 em 34 (núcleo comum 19/28,
união 34). Com `kind='stable'` seria 1,0 por construção, mas não é o que o
código usa.

Um platô empatado portanto **deprime** o Jaccard na direção do acaso. O número
publicado, 0,9418, está muito acima de 0,70, logo nas dez execuções da ablação
o platô carregava ordenação real. **Não há erro nos números publicados por esta
via**, e a hipótese era descartável por aritmética antes de ser levantada.

Verificação direta disponível em `check_decile_ties.py` (repositório `pgsg_2`):
reexecuta o braço de literatura de H4 e compara o Jaccard publicado com o
mesmo cálculo tendo os empates exatos sorteados ao acaso.

## O que fica estabelecido sem depender de modelo

1. O prior NIR é uma escada de quatro níveis; 223 de 281 bandas no piso.
2. O decil superior está contido no platô do prior em 15/15 células deste
   trabalho e no gate NIR arquivado do artigo aceito. O Jaccard ordena
   **apenas dentro do nível de topo do prior**.
3. Isso é afirmação sobre o **escopo** da métrica, não sobre a correção de
   nenhum resultado: a métrica não pode detectar se o nível de topo do prior é
   o lugar certo para olhar, porque nunca olha fora dele.
4. Vale para qualquer prior normalizado min–max cujo platô exceda `q`. Não
   vale para o braço Raman do artigo aceito, cujo prior é contínuo — ali o
   decil não é preso a platô, e as conclusões daquele braço não são tocadas
   por nada aqui.
