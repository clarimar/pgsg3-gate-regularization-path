# F005 — O controle Raman: os defeitos são da quantização

Data: 2026-10-23
Protocolo: `docs/pre-registro-H12-raman.md`
Execução e análise: `scripts/07_raman_lambda1.py`
Dados: `results/raman_h12/`

`bioprocess_substrates` (RamanBench, `chlange/SubstrateMixRaman`), alvo glicose.
Carregado n = 6472, p = 1870 após pré-processamento (raios cósmicos, baseline
ALS, SNV). Três partições não agrupadas, três braços, λ ∈ {0; 1}, dez sementes,
θ₀ = 0, Adam, 500 épocas fixas. q = p // 10 = 187. Tempo total 50,5 min.

Prior Raman em todas as partições: **545 valores distintos, platô de 1 banda no
máximo, maior grupo de empate 1326 bandas no piso 0,01.** Contra o NIR: quatro
níveis, platô de 34 contra q de 28.

Referência: `pls_reference_relevance` com dobras simples (não há identificador
de grupo), regra de 1 EP, `H_MAX = 120`. H(1se) = 5, 6, 6, com cvmin 7, 8, 7 —
longe da borda da grade, nenhum aviso de fronteira. Muito abaixo do NIR, onde
H ficou entre 46 e 72: a referência Raman é de ordem bem menor e portanto mais
suavizada, o que deve ser lembrado ao comparar magnitudes de concordância entre
as modalidades.

## Vereditos pré-registrados

| | | |
| --- | --- | --- |
| **H12a** decil não preso a grupo de empate | 3/3 | **suportada** |
| **H12b** sem colapso por desempate | 3/3 | **suportada** |
| **H12c** literatura supera `blocks` na concordância | 2/3 | **suportada** |

### H12a — o decil sai do grupo de empate

Fração do decil dentro do piso de 1326 bandas, braço de literatura em λ = 1:
**0,000 nas três partições.** Dentro do platô de uma banda: 0,005, isto é 1 de
187. Em NIR a fração no platô é 1,000 em 15/15 células.

### H12b — não há colapso

Empates exatos nos gates: 5, 4 e 8 em 1870 bandas. Jaccard com empates como o
sort os deixa: 0,9596; 0,9589; 0,9303. Com empates sorteados ao acaso: os
mesmos valores, diferença 0,0000 nas três. Em NIR o salto é +0,2413 no braço do
artigo aceito e da mesma ordem nas sete células do pgsg_1 R2.

**Os dois defeitos de F002 e F004 estão ausentes, na mesma arquitetura e no
mesmo código, trocando apenas a forma funcional do prior.** É o que a
explicação da quantização prevê, e é o controle mais forte que este trabalho
tem.

### H12c — a comparação entre braços, e a ressalva

| partição | literatura | `blocks` | delta | p |
| --- | --- | --- | --- | --- |
| 0 | +0,1964 | +0,0899 | **+0,1065** | 0,0020 |
| 1 | +0,1855 | +0,0855 | **+0,1000** | 0,0020 |
| 2 | +0,1584 | +0,1660 | **−0,0075** | 0,0098 |

Passou pelo critério de 2/3, mas a partição 2 é reversão **significativa**, e as
duas margens que apoiam são treze vezes maiores que a que contraria. O enunciado
que isto sustenta é: *a literatura supera claramente em duas de três partições,
e na terceira empata com `blocks` marginalmente à frente.* Não é "supera em
Raman", sem qualificação.

### O fato de apoio mais forte não está em veredito nenhum

ρ(prior, referência), sem treinar modelo algum:

| braço | partição 0 | 1 | 2 |
| --- | --- | --- | --- |
| literatura | **+0,2390** | **+0,1660** | **+0,1600** |
| `blocks` | +0,0064 | −0,0435 | +0,0533 |
| `shuffled` | −0,0045 | −0,0141 | +0,0190 |

A posição publicada do prior Raman correlaciona-se com a referência derivada dos
dados, e realocá-la ou embaralhá-la leva a correlação a zero. **É o oposto do
NIR**, onde o ρ de `blocks` superava o da literatura em 4 das 5 partições
(+0,4208; +0,2746; +0,2013; +0,1207; +0,2268 contra +0,1503; +0,1314; +0,1269;
+0,1878; +0,1395).

Candidato de explicação, **não testado**: o prior NIR tem três blocos largos
(7, 17 e 34 bandas) em 281, e realocá-los tem chance razoável de cair em região
que o PLS valoriza; o Raman tem ~19 corcovas estreitas em 1870, e realocá-las
raramente acerta. Se for isso, a diferença é de esparsidade e geometria, não de
qualidade química. Registrado como candidato: quatro explicações mecânicas
minhas caíram nesta linha de trabalho e esta não tem mais apoio do que elas
tinham.

## Verificação de integridade que o desenho embute

Em λ = 0 o prior não entra na perda. Concordância e Jaccard em λ = 0 saíram
**idênticos entre os três braços** dentro de cada partição (0,5804; 0,5604;
0,5738 de Jaccard, e +0,1642; +0,2279; +0,2127 de concordância). Diferença ali
significaria que os braços não compartilharam a partição.

Vale notar o contraste: sem ancoragem o Jaccard Raman é 0,56–0,58 e **com**
ancoragem vai a 0,93–0,98. Em Raman esse ganho é medida real — não há empate
para o `argsort` resolver. Foi exatamente essa a alegação que em NIR se revelou
ordem de desempate.

## Correção de relato, sem efeito em veredito

A coluna `in_group` era calculada sempre contra o piso do prior de
**literatura**. Para o braço de literatura — o único que H12a julga — está
correto. Para os braços de controle o número é enganoso: `blocks` aparecia com
0,978, 1,000 e 0,928 não porque o decil dele esteja preso ao grupo de empate do
seu próprio prior, mas porque as corcovas realocadas caíram onde a literatura
tinha piso. O script agora reporta `in_own_group`, contra o grupo de empate do
prior de cada braço, e documenta a distinção na própria saída. Nenhum veredito
muda.

## O que isto faz com o artigo

A crítica deixa de ser só destrutiva. A sequência completa é:

1. O prior NIR é quantizado, com platô maior que `q`. Daí o decil nunca sair do
   nível de topo (F002, F003), e daí a estabilidade reportada ser ordem de
   desempate quando o prior entra na inicialização (F002, F004, em dez
   condições: o braço do artigo aceito e sete tamanhos de treino).
2. Com prior contínuo, mesma arquitetura e mesmo código, **os dois defeitos
   desaparecem** e a estabilidade medida passa a ser real (3/3).
3. E onde a métrica consegue ver, a posição do prior carrega informação:
   ρ(prior, referência) positivo em 3/3 contra ≈ 0 nos controles, e
   concordância superior em 2 de 3 partições.

A prescrição passa a ter respaldo empírico em vez de ser inferência: **não
quantize o prior, não o ponha na inicialização, e confira o tamanho do platô
contra `q` antes de reportar sobreposição de decil.** O braço Raman é a
demonstração de que o método funciona quando essas três coisas são respeitadas.

## O que continua fora

Nenhuma afirmação de acurácia em Raman. A ingestão não expõe identificador de
lote ou réplica, a partição é não agrupada, e vazamento de réplica fica
indefeso — o mesmo erro que a revisão R2 do pgsg_1 corrigiu em NIR. R² não foi
reportado por isso.

Nenhuma afirmação sobre o caminho de λ em Raman: dois pontos não são caminho.

Nenhuma comparação com o braço Raman do artigo aceito, que usou prior na
inicialização contra θ₀ = 0 aqui.

## Pontas soltas

O ADR-0001 do pgsg_2 declara 6.960 espectros; a carga trouxe **6.472**. A
diferença precisa ser conciliada antes de o número entrar no texto.

A estimativa de custo do pré-registro foi de 2,5 a 4,5 horas mais 15 a 45
minutos de calibração; o real foi **50,5 minutos no total**, errando por um
fator de quatro na direção favorável. O pré-registro declarava tolerância de um
fator de dois.
