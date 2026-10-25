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

## O Jaccard NIR publicado é artefato de desempate

Confirmado por reexecução, `scripts/check_decile_ties.py` no repositório
`pgsg_2`, reproduzindo o braço de literatura de H4 com as mesmas dez sementes,
mesmo pré-processamento, mesma divisão e `q = p // 10 = 28`:

| | |
| --- | --- |
| platô, em todas as 10 sementes | **1/34 valores distintos**, amplitude 0,0e+00 |
| s(1−s) médio no platô | 4,7×10⁻⁶ a 6,9×10⁻⁶ |
| decil dentro do platô | 28/28 |
| Jaccard, empates como o sort os deixa | **0,9418** |
| Jaccard, empates sorteados ao acaso (200 sorteios) | **0,7005 ± 0,0068** |
| nível de chance, 28 em 34 sorteados duas vezes | **0,7012** (exato); 0,7000 é J(E[k]) |
| figura publicada para este braço | 0,9418 |

As 34 bandas do platô têm valor bit-idêntico em **todas** as sementes, logo o
platô não carrega ordenação alguma, e as 28 bandas selecionadas saem todas
dele. Quais 28 das 34 ficam é decidido pelo caminho de partição do introsort —
e esse caminho depende dos valores **fora** do platô, que a métrica nunca
seleciona. Medido, mantendo o platô como treinado e perturbando só o resto:

| sd fora do platô | Jaccard |
| --- | --- |
| 0 | 1,0000 |
| 10⁻⁵ | 1,0000 |
| 10⁻⁴ | 0,9678 |
| 10⁻³ | 0,7812 |
| 10⁻² | 0,7500 |

O 0,9418 publicado corresponde a sd ≈ 1,5×10⁻⁴, coerente com o
`rho_pairwise = 0,9995` registrado no mesmo arquivo. Trocar apenas a regra de
desempate — mesmos gates, mesmo q, mesma fórmula — leva a figura ao acaso.

**A figura publicada de 0,9418 não mede seleção reprodutível de bandas.** Ela
mede quão parecidos os gates são nas bandas que a métrica não seleciona, lido
através do tratamento de empates do `argsort`. O número é exatamente
reproduzível; é a sua interpretação que não se sustenta.

A comparação honesta para o braço NIR seria 0,7005 contra 0,6002 de
`prior=None` — e mesmo 0,7005 é o nível de chance que a própria restrição a 34
bandas candidatas impõe, não evidência de estabilidade aprendida.

### Trilha desta hipótese, registrada por ter errado duas vezes

1. Levantada a partir do gate arquivado, com os empates exatos medidos.
2. **Retratada** com base em gates sintéticos que deram J = 0,7301, perto do
   acaso, de onde concluí que platô empatado deprimiria o Jaccard e que o
   0,9418 era portanto incompatível com artefato.
3. **Reinstaurada** pela reexecução real. O fixture sintético usava sd = 10⁻²
   fora do platô, setenta vezes o valor real; na escala correta dá 0,97–1,00. O
   número que o calibraria (`rho_pairwise = 0,9995`) estava no arquivo já lido.

A retratação foi o erro mais grave da sequência, porque afirmou ausência de
problema em resultado publicado. A lição é específica: fixture sintético
precisa ser calibrado por quantidade medida, não por escala arbitrária.

## O que fica estabelecido

1. O prior NIR é uma escada de quatro níveis; 223 de 281 bandas no piso.
2. O decil superior está contido no platô do prior em 15/15 células deste
   trabalho e no braço NIR do artigo aceito. O Jaccard ordena **apenas dentro
   do nível de topo do prior**, e não pode detectar se aquele nível é o lugar
   certo de olhar, porque nunca olha fora dele. Afirmação sobre o escopo da
   métrica.
3. No braço NIR do artigo aceito, essa restrição se agrava: por saturação na
   inicialização, as 34 bandas do platô ficam bit-idênticas em todas as
   sementes, de modo que o decil não ordena nada e o 0,9418 publicado vem do
   desempate do `argsort`. Afirmação sobre a **interpretação** de um resultado
   publicado, reproduzida por reexecução.
4. Vale para prior normalizado min–max cujo platô exceda `q` **e** com o prior
   na inicialização. Não vale, e nada aqui toca:
   - o braço **Raman** do artigo aceito — prior contínuo, 545 valores
     distintos, platô de 1 banda, decil 1/187 dentro dele; J = 0,9011 contra
     0,6545 é medida real;
   - nenhum **R²** de qualquer modalidade, em nenhum dos trabalhos;
   - os números deste trabalho (`pgsg_3`), que usa θ₀ = 0 em vez do prior na
     inicialização. Sem saturação, `inert = 0` em todo λ (F001), e
     `05_diagnostico_jaccard.py` verifica ausência de empate exato entre gates
     treinados em todas as células antes de reportar qualquer Jaccard.

---

## Correção de 2026-10-24 — `q/(2L−q)` não é o acaso exato

A tabela acima dizia, do nível de chance, **0,7000**, e as notas deste programa
o chamavam em três lugares de *"o acaso combinatório exato de sortear 28 entre
34 duas vezes"*. **O adjetivo está errado.**

`q/(2L−q)` é **J avaliado no overlap esperado**, não a esperança de J. Sob
sorteio uniforme de dois subconjuntos de tamanho `q` entre `L` bandas, o overlap
`k` é hipergeométrico com E[k] = q²/L, e

    J(E[k]) = (q²/L) / (2q − q²/L) = q / (2L − q)

identicamente — a aproximação *é* essa substituição. Mas J(k) = k/(2q−k) tem
J''(k) = 4q/(2q−k)³ > 0 para k < 2q, logo é **estritamente convexa**, e por
Jensen **E[J] > J(E[k])**. A aproximação é limite inferior estrito.

O valor exato soma a hipergeométrica termo a termo:

    E[J] = Σₖ [C(q,k) C(L−q,q−k) / C(L,q)] · k/(2q−k)

| | q = 28, L = 34 | q = 29, L = 34 |
| --- | --- | --- |
| E[J] exato | **0,701177** | **0,744473** |
| q/(2L−q) | 0,700000 | 0,743590 |
| erro da aproximação | +0,001177 | +0,000884 |

**Nenhum veredito muda.** O medido na célula publicada, 0,7005 ± 0,0068, fica a
−0,10 sd do exato e a +0,07 sd da aproximação: a medida não discrimina entre os
dois, e o colapso ao acaso está igualmente sustentado. O que muda é que o
programa afirmava exatidão de um número que não a tem, enquanto o rascunho da §4
já usava o valor correto — os documentos de apoio contradiziam o manuscrito.

Corrigido aqui, em `F004`, no `ADR-0001` e em `paper/00-estrutura.md`. O
`check_gates_r2.py` passa a imprimir o exato e a aproximação lado a lado, com o
erro, para que a diferença não volte por descuido.

---

## Correção de 2026-10-25 — o alcance estava errado no mecanismo, e estreito

Esta nota afirma, em dois lugares, que o achado *"vale para qualquer prior
normalizado min–max cujo platô exceda `q`"* (§ do alcance, e item 4 do
fechamento). **A caracterização está errada, e por estar errada subestima o
alcance.** O `05_diagnostico_jaccard.py` repete o erro na docstring: *"The
prior is min-max normalized, so it has a FLAT PLATEAU at its maximum."*

O prior de literatura **não é normalizado min–max.** `make_literature_prior`
em `src/pgsg_3/m_model/pgsg_v2.py` atribui um valor constante por região
reportada e divide pelo máximo:

```python
prior = np.ones(len(wavelengths)) * 0.1
if 680 <= w <= 700:   prior[i] = 0.6
if 900 <= w <= 1000:  prior[i] = 1.0
if 1100 <= w <= 1200: prior[i] = 0.8
return prior / prior.max()
```

Duas consequências.

**1. A normalização não cria o platô.** `prior.max()` já é 1,0, logo
`prior / prior.max()` é a identidade. Min–max daria mínimo 0,0, e o mínimo
medido é 0,1 — o que por si só refuta a caracterização. O platô de 34 bandas
existe porque **um único constante foi atribuído a uma região de 100 nm**, e
existe antes de qualquer normalização.

**2. O alcance é maior do que eu escrevi.** Condicionar a "prior normalizado
min–max" restringe o achado a um esquema de normalização que o próprio
programa não usa. A condição verdadeira é de **construção**: todo prior escrito
na forma *estas regiões importam isto* tem conjuntos de nível tão grandes
quanto as regiões que nomeia, e a condição é violada sempre que a maior região
nomeada contiver mais bandas que o conjunto selecionado. Essa é a forma comum
de codificar atribuições de banda publicadas, e portanto o achado alcança mais
casos, não menos.

**Enunciado que substitui o anterior:** *vale para qualquer prior cujo maior
conjunto de nível exceda `q` — o que inclui, mas não se limita a, priors
construídos por atribuição de constante por região — **e** com o prior na
inicialização.* As exclusões do item 4 (braço Raman, condição não informada,
números do pgsg_3, R² e ρ) permanecem exatamente como estão.

**Como o erro entrou.** Eu propaguei a caracterização de uma nota minha
anterior em vez de ler `make_literature_prior`. É a mesma lição operacional já
registrada no `F004`: ler a fonte que o arquivo declara antes de caracterizá-la.
Terceiro erro deste tipo no programa, e o primeiro que **estreitava** um achado
em vez de exagerá-lo. Texto original preservado acima.
