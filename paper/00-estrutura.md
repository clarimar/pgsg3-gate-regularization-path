# Estrutura do manuscrito e mapa de números — v3

Data: 2026-10-24
Status: **divergências numéricas resolvidas; nenhuma prosa escrita ainda**

Fixa, antes da redação, o que cada seção afirma, qual número vai nela e de qual
achado o número vem. A v1 (2026-10-23) foi revisada e as mudanças estão
marcadas como **[v2]**.

## Decisões do parecer, incorporadas

| decisão | resolução |
| --- | --- |
| título | **trocado** |
| artigo aceito | antecedente **e** objeto de reanálise |
| §6 e §8 | §6 reduzida, §8 preservada |
| figuras | as cinco, com os ajustes do parecer |
| divergências numéricas | **[v3] resolvidas**, as duas; ver abaixo |

Três correções científicas do parecer, aceitas integralmente, e uma devolvida
ao parecerista. Todas detalhadas em §§ próprias abaixo.

---

## Título **[v2]**

**When Spectral Attention Stability Reflects the Prior Rather Than the Data**

Substitui *Initialization Is Not Regularization: Separating the Two Roles of a
Spectral Prior*, que descrevia F001 — hoje a §3, mecanismo e não tese.

Rejeitada também a minha alternativa *A Quantised Prior Makes Interpretive
Stability Unmeasurable*: absoluta demais. O que fica problemático é **uma
métrica de sobreposição sob condições específicas**, não toda forma de
estabilidade interpretativa.

Ressalva pequena, registrada e não resolvida: "Rather Than the Data" pode ser
lido como se o gate nunca acompanhasse os dados, e §8 mostra que acompanha, nas
bandas do piso. Título não carrega tudo; o resumo precisa desfazer essa leitura
na primeira frase.

## Princípio de reporte

O programa é pré-registrado. **As vinte hipóteses pré-registradas aparecem no
manuscrito com o seu veredito**, inclusive H13b, cujo critério era mal
desenhado. Omitir veredito pré-registrado é o viés de reporte que o
pré-registro existe para impedir.

A prosa é seletiva na ênfase; a Tabela 1 é exaustiva na existência.

**[v2]** A Tabela 1 passa a ter **colunas separadas** para *veredito pelo
critério pré-registrado* e *interpretação científica posterior*. O parecer tem
razão: misturar as duas apaga a distinção justamente onde ela mais importa, em
H11a (suportada contra o confinamento errado) e H13b (não suportada por
critério mal desenhado).

---

## **[v3]** As duas divergências numéricas, resolvidas

**Contagem Raman: conciliada.** 6.472 analisados + **488 descartados** = 6.960
declarados. O carregador descarta espectros cujo alvo de glicose é `NaN` e
registra a contagem em `metadata["n_samples_dropped_missing_target"]`. Critério
documentado na fonte, não inferido. A §2 declara os três números.

**Faixa de Jaccard: o ADR estava certo, o erro era meu.** `gate_metrics.csv`
registra `q = 29` por linha, e ao q = 29 a recomputação casa exatamente com os
valores armazenados — faixa 0,9452--0,9867, que é o 0,945--0,987 da decisão 6.
O meu `check_gates_r2.py` usava `int(p × 0,10)` = 28, truncando, e foi essa
diferença de convenção que criou a falsa divergência. **Nada a corrigir no
ADR**; corrigido o F004, que reportava a divergência como se fosse dos dados.

### Consequência de métodos: duas convenções de decil no programa

| base | definição | q em p = 281 | E[J] exato, 34 bandas |
| --- | --- | --- | --- |
| `gate_metrics.csv` (pgsg_1 R2) | `ceil(0,10 p)` | **29** | **0,7445** |
| `pgsg_3` | `ceil(0,10 p)` | **29** | **0,7445** |
| ablação H4 publicada (pgsg_2) | `len(wl) // 10` | **28** | **0,7012** |

**[v3]** A coluna é a esperança hipergeométrica exata de J, não `q/(2L−q)`.
Essa razão é J avaliado no overlap esperado; J é estritamente convexa em k, logo
subestima E[J] por 0,0012 (q = 28) e 0,0009 (q = 29). A §2 reporta o exato e
nomeia a aproximação, porque a literatura de seleção de bandas usa a segunda.

A §2 **declara as duas** e diz qual vale para qual conjunto. Os números de
colapso por desempate são reportados **por protocolo**, nunca misturados: a
célula publicada do pgsg_2 em q = 28, os sete tamanhos do pgsg_1 R2 e tudo do
pgsg_3 em q = 29. É exatamente o que a Decisão 5 do parecer exigia.

## Correção aceita A — a dependência de n não é regra **[v2]**

A v1 e o `findings/F004` afirmavam: *"medida genuína de estabilidade de seleção
tem de depender de n."* **Retirado como regra.** Uma medida legítima pode ficar
constante com n — seleção já estabilizada, sinal fraco demais, procedimento
estruturalmente insensível aos dados.

O enunciado que vai ao manuscrito é o específico: neste experimento a
estabilidade sem ancoragem cresce com n (ρ = +0,9286, p = 0,0025, variação de
39×) e a estabilidade sob prior na inicialização permanece em 0,95–1,00 e
praticamente invariável (ρ = −0,3063, p = 0,5040); isso é evidência de que a
métrica ancorada **não capta o mesmo fenômeno** que a condição de controle.

Serve como **sinal de alerta**, não como critério. F004 corrigido por nota
datada.

## Correção aceita B — PAC-Bayes sai do enquadramento **[v2]**

O KL age sobre valores determinísticos de gate, não sobre distribuição de
hipóteses, e na inferência o gate multiplica em vez de amostrar. Logo a
semelhança formal **não autoriza** dizer que o objetivo minimiza um limite
PAC-Bayes — e, consequentemente, **não autoriza** a minha jogada da v1 de
tratar o ΔR² nulo como previsão não realizada desse limite. Se não é limite,
não faz previsão, e nada é contrariado. Erro lógico meu no plano.

Enquadramento principal passa a ser **regularização em direção a um prior** e
**compromisso entre ajuste e restrição**. PAC-Bayes aparece em um parágrafo da
discussão e em trabalho futuro, dizendo o que teria de mudar: gate estocástico,
KL entre distribuições, amostragem na inferência.

## Correção aceita C — não há colapso formal de hierarquia **[v2]**

A v1 dizia que com θ₀ = logit(s) "a hierarquia SRM colapsa". **Impreciso.** Os
34 parâmetros do platô continuam livres na classe de hipóteses; o que acontece é
que a inicialização os põe numa região onde s(1−s) ≈ 10⁻⁶ e o gradiente não os
move dentro do orçamento. É **restrição de alcançabilidade pelo otimizador**,
não redução matemática da classe.

O que fica de SRM: a família indexada por λ **é** uma hierarquia de problemas
restritos, e essa parte se sustenta. O que sai: a afirmação de que a
inicialização reduz a classe.

## Correção devolvida ao parecerista — o desempate não é por índice

O parecer fala em "desempate determinístico" e "Jaccard determinístico", e a
Figura 2 proposta compara "Jaccard determinístico" com "desempate aleatório".
**Impreciso, e já foi fonte de um erro meu retratado em F002.**

`np.argsort` usa quicksort e **não é estável**. A ordem dentro de um bloco
empatado vem do caminho de partição, que depende dos valores **fora** do platô.
Medido: J vai de 1,0000 quando os gates são idênticos fora do platô a 0,7500
quando diferem por σ = 10⁻², e o 0,9418 publicado corresponde a σ ≈ 1,5×10⁻⁴.
Com `kind='stable'` seria ordem de índice e daria 1,0 por construção, mas não é
o que o código usa.

Afirmação correta, que vai ao texto e à legenda da Figura 2: **a estabilidade
aparente mede quão parecidos os gates são nas bandas que a métrica não
seleciona.** Se entrar como "desempate por índice", um parecerista que confira
acha o erro — eu afirmei isso, retratei com base em fixture mal calibrado, e
reinstaurei com o mecanismo certo; a trilha está em F002.

---

## Argumento, em seis passos

1. O prior cumpre dois papéis; fundi-los restringe a alcançabilidade de
   parâmetros (F001).
2. O prior NIR é escada de quatro níveis com platô maior que o decil, logo a
   métrica nunca sai do nível de topo (F002, F003).
3. Com o prior na inicialização o platô fica bit-idêntico, e a estabilidade
   reportada mede similaridade fora do platô através do tratamento de empates —
   em dez condições independentes (F002, F004).
4. A estabilidade sem ancoragem responde a n; a ancorada não (F004).
5. Com prior **contínuo**, mesma arquitetura e mesmo código, os dois defeitos
   desaparecem (F005).
6. O alinhamento que existe entre gate e referência externa é indiferente ao
   prior e concentra-se nas bandas que o prior rebaixa (F003, F006).

---

## Registro editorial — decisão de 2026-10-24 **[v4]**

Voz aprovada pelo autor: **C, prescritiva com o controle preservado.** O
sujeito do artigo é a **condição de validade da métrica**, não o achado. O
0,9418 é instância, não tese. Razão: a Tabela 1 reporta oito hipóteses não
suportadas em vinte e três critérios mal desenhados — a credibilidade vem do
método, e um registro que ponha o achado como sujeito lê como defesa.

**Sequência que todo o manuscrito segue**, prescrita pelo autor:

> condição de validade → mecanismo de falha → demonstração experimental →
> controle não afetado → limites da interpretação → recomendações de reporte

**Quatro exigências vinculantes**, as duas primeiras corrigindo a redação de C:

1. **Platô > q cria a possibilidade, não o defeito.** A formulação *"a
   sobreposição só é informativa quando todos os níveis são menores que o
   conjunto selecionado"* é forte demais e contradiz a frase seguinte do
   próprio resumo. O enunciado correto separa três coisas: a condição
   geométrica que cria a possibilidade; a persistência dos empates no
   treinamento; o desempate determinístico que produz a estabilidade
   artificial.
2. **O modelo nulo é explícito na própria frase.** `0,7012` é **q = 28**, a
   convenção do código que produziu o 0,9418, e o resumo tem de dizer
   *"drawing 28 of 34 plateau bands twice"*. Dar `0,7012` sem nomear q deixa
   um parecerista recomputar a q = 29, obter 0,7445, e concluir que erramos.
   O protocolo de q = 29 vale para os sete tamanhos do pgsg_1 R2, onde o
   acaso é 0,7445 e o medido 0,7442 ± 0,0063.
3. **A frase do controle de deslocamento permanece no resumo** e é sustentada
   **explicitamente na Discussão**, demonstrando por que aquele controle não
   depende da ordenação top-k nem do desempate. Isso cria uma subseção nova
   na §9, que não existia no plano v3.
4. **As oito refutações são resultado, não passivo.** O resumo as declara.

Resumo em **242 palavras** (`paper/02-resumo-C.md`). O limite do Chemolab
**não foi confirmado** — o guia de autores não é alcançável nesta sessão.
Cortar para 200 custaria a frase do tamanho amostral ou a do Raman; nenhuma
das duas sai sem o limite na mão.

## Seções

### 1. Introdução

Afirma: priors espectrais são avaliados por sobreposição top-k entre execuções,
e essa prática tem uma condição geométrica não examinada.

**Modelo formal de aprendizagem** — escrever o que a alegação interpretativa
teria de significar: existe suporte verdadeiro S\*? o objetivo é recuperá-lo?
sob que hipótese? Risco preditivo tem alvo populacional e garantia de
convergência; sobreposição entre sementes não tem estimando. Um parágrafo de
contraste com **convergência uniforme**.

**[v2]** Primeira frase do resumo e do fim da introdução precisa dizer que o
gate **sim** acompanha os dados em parte do espectro (§8), para o título não ser
lido como negação disso.

Sem números.

### 2. Dados e métodos

| item | valor | origem |
| --- | --- | --- |
| NIR | Mango DMC v3, safra 4, DOI 10.17632/46htwnp833.3 | ADR-0001 |
| p (NIR) | 281 | F002 |
| divisões NIR | agrupadas por fruto; 725 frutos, 723 medidos duas vezes | F001 |
| Raman | `bioprocess_substrates`, alvo glicose | ADR-0001 pgsg_2 |
| n Raman declarado / descartado / analisado | 6.960 / **488** / 6.472 | **[v3]** conciliado |
| critério de exclusão Raman | alvo de glicose ausente (`NaN`), contagem registrada na fonte | `raman_bioprocess.py` |
| **convenção de decil** | `ceil(0,10 p)` = 29 aqui; `// 10` = 28 na ablação publicada | **[v3]** declarar as duas |
| p (Raman) | 1870 | F005 |
| divisões Raman | não agrupadas; sem id de lote na ingestão | F005 |
| referência | \|coef PLS\|, 1 EP, H_MAX = 120, por partição | F001 |
| H (NIR) | 46 a 72 nas quinze partições | F003, F006 |
| H (Raman) | 5, 6, 6 | F005 |
| sementes | 10 por célula | todos |
| orçamento | 500 épocas fixas, Adam | todos |

**[v3]** Confirmado por execução: 488 descartados, 6.472 + 488 = 6.960. Três
números, não um conflito.

**SRM / aprendizibilidade não-uniforme** — λ·KL(g‖s) é família de problemas
restritos indexada pela distância ao prior. Introduzir aqui, **sem** a
linguagem de colapso.

**[v2]** PAC-Bayes **não** entra aqui.

### 3. Resultados — os dois papéis do prior

| afirmação | número | origem |
| --- | --- | --- |
| prior na inicialização restringe alcançabilidade | 34 bandas, 12,1% de 281 | F001 |
| magnitude | s(1−s) ≈ 10⁻⁶; Fisher 8,6×10⁻⁹ contra 0,72 | F001 |
| λ inerte sob prior-init | ρ(gate,prior) de 0,9987 a 0,9999 em quatro ordens de λ | F001 |
| separar os papéis remove a restrição | `inert` = 0 em todo λ, sete grades | F001 |
| confirmação em escala | `inert` = 0 nas 1500 execuções de 5..9 | F003 |

Figura 1: o prior como escada, com o platô e `q` marcados — os quatro níveis,
as 34 bandas e o decil de 28 ou 29.

### 4. Resultados — o que a métrica de decil mede

| afirmação | número | origem |
| --- | --- | --- |
| prior NIR é escada | 0,1×223; 0,6×7; 0,8×17; 1,0×34 | F002 |
| decil contra platô | q = 29 (pgsg_3), 28 (código publicado), platô 34 | F002 |
| decil contido no platô | 1,000 em 15/15 células; 28/28 no gate arquivado | F002, F003 |
| platô bit-idêntico | 1/34 valores distintos, amplitude 0,0e+00 | F002, F004 |
| J publicado reproduzido | 0,9418, idêntico | F002 |
| colapso ao sortear empates, célula publicada (**q = 28**) | 0,7005 ± 0,0068 contra E[J] = 0,7012 | F002 |
| **[v3]** os sete tamanhos do pgsg_1 R2 (**q = 29**) | J 0,9452–0,9867 → **0,7442 ± 0,0063** contra E[J] = **0,7445** | F004 |
| **[v3]** o sorteado é idêntico nas 7 células | o gate não entra no cálculo: só (q, L) | F004 |
| **J rastreia similaridade fora do platô** | 1,0000 em sd = 0 a 0,7500 em sd = 10⁻²; publicado ≈ sd 1,5×10⁻⁴ | F002 |

Figura 2: J como o sort deixa os empates, J com empates sorteados, e o acaso —
para a célula publicada e os sete tamanhos. **[v2]** A legenda diz
explicitamente que o sort **não** é estável e que a ordem dos empates depende
dos valores fora do platô. A última linha da tabela é a que fecha o mecanismo e
não pode ficar de fora.

### 5. Resultados — a resposta ao tamanho amostral **[v2 reformulada]**

| afirmação | número | origem |
| --- | --- | --- |
| sem ancoragem, cresce com n | **[v3]** 0,0898 → 0,5658; ρ = +0,9286, p = 0,0025 | F004 |
| sob prior na inicialização, invariável | **[v3]** 0,9452–0,9867; ρ = −0,3214, p = 0,4821 | F004 |
| variação coberta | n de 30 a 1.158, fator 39 | F004 |

Afirmação: as duas condições **não captam o mesmo fenômeno**. Sinal de alerta
útil, não critério universal.

Figura 3: J contra n, os dois braços. **[v2]** Legenda sem a formulação de
regra.

### 6. Resultados — os controles de prior **[v2 reduzida]**

Vira **um parágrafo** com remissão à Tabela 1, afirmando: nenhuma das métricas
testadas separa conteúdo químico de ancoragem — em cada uma, um prior com
conteúdo destruído iguala ou supera o publicado em ao menos três partições.

Números que ficam no parágrafo: H8 em 0/5 nos dois braços (λ=0 dá +0,03..+0,07;
λ=1 dá +0,09..+0,46); `shuffled` atingindo J de 0,957–0,975 com ρ(prior,ref)
negativo em 4/5.

E a não-uniformidade, explícita: na métrica crua a literatura supera `blocks` em
**4 de 15** partições — 1/5, 0/5 e 3/5 nos três blocos de cinco.

### 7. Resultados — o controle Raman

| afirmação | número | origem |
| --- | --- | --- |
| prior contínuo | 545 valores distintos, platô de 1 banda | F005 |
| decil não preso a empate | 0,000 em 3/3; no platô 0,005 | F005 |
| sem colapso por desempate | empates 5, 4, 8 em 1870; gap 0,0000 em 3/3 | F005 |
| ancoragem com medida real | J de 0,56–0,58 em λ=0 para 0,93–0,98 em λ=1 | F005 |
| posição correlaciona com a referência | +0,2390; +0,1660; +0,1600 contra ≈ 0 nos controles | F005 |
| comparação entre braços | 2/3, **com a reversão significativa da partição 2** | F005 |

Seção que torna o artigo construtivo: mesma arquitetura, mesmo código, forma
funcional do prior trocada, defeitos ausentes.

Figura 4: o prior contínuo com a posição do decil, e J(sort) contra J(sorteado).

### 8. Resultados — onde está o alinhamento **[preservada]**

| afirmação | número | origem |
| --- | --- | --- |
| piso, partições 5–9 | +0,2982; +0,1679; +0,1457; +0,3418; +0,2147; p = 0,0020 | F003 |
| piso, replicação primária 10–14 (H13c) | +0,2705; +0,3168; +0,1491; +0,2901; +0,2063; p = 0,0020 | F006 |
| platô, mesmo braço | sinal inconsistente, 2 de 5 negativos | F003 |
| indiferente ao prior | +0,12 a +0,37 nos três braços | F006 |

Nota obrigatória no corpo, reforçada pelo parecer: isto **não** é evidência de
recuperação de relevância química verdadeira. A referência é coeficiente
absoluto de PLS calibrado — referência operacional.

Figura 5: ρ intra-nível por nível do prior, com dispersão entre sementes.

### 9. Discussão

**Trade-off ajuste–restrição, com inversão.** λ→∞ é viés alto, λ→0 é variância
alta, e o caminho é **plano em risco**: R² equivalente em toda a faixa, nas duas
modalidades, nos sete tamanhos. O compromisso é entre estabilidade irrelevante
para o risco e nada.

**[v2] PAC-Bayes, um parágrafo.** A forma do objetivo lembra a de um limite
PAC-Bayes, e não é um. O que teria de mudar para que fosse: gate estocástico, KL
entre distribuições sobre hipóteses, amostragem na inferência. Nenhuma previsão
é extraída daqui.

**Prescrição:**

1. Confira `|platô|` contra `q` antes de reportar sobreposição de decil; e
   verifique se há empates exatos nos valores ordenados.
2. Não ponha o prior na inicialização — θ₀ = 0 preserva a restrição sem tornar
   parâmetros inalcançáveis.
3. Varie n e veja se a sobreposição responde. Insensibilidade a variação grande
   de n é motivo para investigar a causa.
4. Reporte a sobreposição com empates sorteados ao lado da convencional. A
   diferença entre as duas é o tamanho do artefato, e custa uma linha.
5. Condicionar a métrica no prior **não** serve para testar o conteúdo do prior
   (§10).

### 10. Limitações

| limitação | origem |
| --- | --- |
| a referência é \|coef PLS\| calibrado — referência operacional, não verdade química | F003, F006 |
| Raman sem agrupamento: nenhuma afirmação de acurácia, R² não reportado | F005 |
| H13b condiciona na variável que distingue os braços e premia prior anticorrelacionado; critério mal desenhado, veredito mantido, leitura retirada | F006 |
| H11a testou saída do platô, não ausência de confinamento; o decil foi para o piso | F003 |
| a leitura conjunta de H10a e H10b não foi especificada no pré-registro | F003 |
| a dependência de n é observação deste experimento, não regra | **[v2]** F004 |
| PAC-Bayes é semelhança formal, não limite | **[v2]** §9 |
| **[v3]** duas convenções de decil no programa; declaradas e não misturadas | F004 |
| cinco explicações mecânicas propostas e descartadas durante o trabalho | F002, F003, F005, F006 |

**[v3]** Resolvida: o ADR citou o protocolo correto (q = 29) e a divergência
vinha do meu verificador, que truncava para 28. O que resta como limitação não
é divergência mas **inconsistência de convenção entre as três bases**, e ela é
declarada na §2. Nenhum número é reabilitado por isso: platô empatado torna
todos eles artefato de desempate, em qualquer q.

### 11. Trabalho futuro

- Escala e amostras pequenas: o prior não melhora acurácia em sete tamanhos —
  resultado real do pgsg_1 R2 que a rejeição deixou sem casa.
- Suporte verdadeiro conhecido, por dado sintético: único desenho em que se mede
  recuperação em vez de concordância com proxy.
- Rademacher empírica por ajuste a rótulos aleatórios, para quantificar
  restrição de alcançabilidade em vez de argumentá-la.
- H contra ρ intra-platô: ρ = +0,6000, n = 5, p = 0,2848 — nomeado, declarado,
  não rodado.
- **[v2]** Gate estocástico, que tornaria a análise PAC-Bayes possível.

---

## Tabela 1 — as vinte hipóteses pré-registradas **[v2: colunas separadas]**

No corpo, não em suplementar.

| | enunciado | veredito pelo critério | interpretação posterior |
| --- | --- | --- | --- |
| H0 | existe λ com descolamento e estabilidade | suportada | — |
| H5a | o máximo interior transporta | não suportada, 2/5 | a curva satura em vez de picar |
| H5b | o gate ancorado supera o prior sozinho | suportada, 5/5 | — |
| H5c | a posição de λ\* é estável | suportada, 5/5 | — |
| H6 | a penalidade melhora o R² | suportada, 4/5 | efeito de regularizador, não de conteúdo |
| H7-blocks | o conteúdo do prior importa | não suportada, 1/5 | cláusula de refutação acionada |
| H7-shuffled | idem, contra embaralhado | suportada, 4/5 | contiguidade importa |
| H8 | ancoragem sozinha compra pouco | não suportada, 0/5 | ancoragem compra muito |
| H9-blocks | reprodutibilidade independe do conteúdo | não suportada, 3/5 | nenhum controle supera a literatura |
| H9-shuffled | idem | suportada, 5/5 | estabilidade com ρ(prior,ref) negativo |
| H10a | há ordenação intra-platô | não suportada, 3/5 | sinal inconsistente |
| H10b | a literatura ordena melhor que blocos | suportada, 5/5 | **leitura estreita:** blocks é negativo, não a literatura positiva |
| H11a | o decil de resíduo sai do platô | suportada, 5/5 | **o critério cobria menos do que supus:** o decil foi para o piso |
| H11b | o resíduo distingue os braços | suportada, 4/5 | `shuffled` supera a literatura em 3/4 |
| H12a | decil não preso a empate (Raman) | suportada, 3/3 | defeito ausente com prior contínuo |
| H12b | sem colapso por desempate (Raman) | suportada, 3/3 | idem |
| H12c | a literatura supera blocos (Raman) | suportada, 2/3 | reversão significativa na partição 2 |
| H13a | o parcial é positivo | suportada, 5/5 | e é igual nos três braços |
| H13b | a literatura supera blocos no parcial | não suportada, 0/5 | **critério mal desenhado:** condiciona na variável que distingue os braços |
| H13c | o achado do piso replica | suportada, 5/5 | replica como critério primário |

---

## O que falta antes da prosa

1. ~~Rodar `resolver_divergencias.py`~~ — **[v3] feito**, as duas conciliadas.
2. **A rota com o editor**, que decide se a §4 carrega uma correção ou uma
   reanálise. O parecer é explícito e eu concordo: se o manuscrito identifica
   problema material em resultado já publicado, reanálise em outro artigo
   **não substitui** comunicação formal ao periódico de origem. Isso precisa
   estar resolvido, não em paralelo.

   > **Correção de 2026-10-24 — resolvido, e o texto acima ficou
   > desatualizado.** O `docs/adr/ADR-0003-comunicacao-ao-editor.md` decidiu:
   > prosseguir com o novo artigo **sem** comunicação formal ao editor do
   > artigo anterior, com três ressalvas vinculantes para a redação. Logo este
   > item **não é mais bloqueante**, e a §4 carrega uma reanálise, não uma
   > correção.
   >
   > A premissa do texto acima — *"se o manuscrito identifica problema
   > material em resultado já publicado"* — **não se verificou**. O manuscrito
   > aceito já contém o controle de deslocamento que responde à objeção, mede
   > ρ(d) = 0,9462 em NIR e já reporta Jaccard do decil de |d| = 0,38. Aquele
   > controle usa valores, não postos, e não é afetado. Não há problema
   > material identificado; há um número que, no braço NIR, não mede seleção
   > reprodutível de bandas. Retratação minha registrada no próprio ADR-0003.
   >
   > O artigo está **em provas**, e `paper/correcao-em-provas.md` propõe uma
   > inserção de quatro linhas, que é rotina de autor e não tramita como
   > ocorrência editorial. Minha recomendação científica de comunicar, citada
   > acima, está **retirada** por ter sido feita sem ler a seção de controle.
   > Texto original preservado, por ser registro.
3. **As cinco figuras**, propostas e não desenhadas. Sem títulos nos gráficos;
   identificação nas legendas.
