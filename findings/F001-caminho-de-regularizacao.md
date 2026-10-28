# F001 — O caminho de regularização do gate

Data: 2026-10-16
Protocolo: `docs/protocolo_hipoteses.md` (H0), `docs/pre-registro-H5-H6.md` (H5, H6)
Dados: `results/ctl_adam`, `ctl_adamw`, `ctl_part0..4`

NIR, Mango DMC v3 safra 4, 281 bandas após pré-processamento. Divisões 80/20
agrupadas por fruto (725 frutos, 723 medidos duas vezes), pré-processamento
ajustado só no treino, orçamento fixo de 500 épocas, 10 sementes por célula.
Referência de relevância: coeficientes absolutos de um PLS calibrado na
partição de treino (regra de 1 EP; H selecionado entre 66 e 71).

## O mecanismo

O prior entra na `PGSGv2Model` por um único ponto, a inicialização dos logits:
θ₀ = logit(s). Como o gradiente que chega a θ é proporcional a σ'(θ) = s(1−s),
as bandas que o prior marca com s = 1,0 nascem isoladas dos dados. O prior de
literatura é normalizado por `prior.max()`, o que produz um platô em 1,0 e,
sobre o eixo de 281 bandas, **34 parâmetros inertes** — 12,1% do espectro,
precisamente as bandas que o prior declara mais importantes.

A penalidade sofre a mesma atenuação: ∂KL/∂θ = (θ − logit s)·σ'(θ). Com
θ₀ = logit(s) esse termo começa em zero em toda banda e permanece em zero no
platô, onde σ' ≈ 10⁻⁶. **Com o prior na inicialização, λ é inerte** — medido:
ρ(gate, prior) vai de 0,9987 a 0,9999 ao longo de quatro ordens de grandeza de
λ (`results/sweep_nir`).

Separando os dois papéis — θ₀ = 0, prior apenas na penalidade — nenhuma banda
nasce isolada (σ'(0) = 0,25 em todas) e o prior continua restringindo. Nessa
parametrização, **`inert` é zero em todo λ testado, inclusive λ = 10**, nas
sete grades executadas. O prior informa sem isolar.

## O que foi confirmado

**H0 (pré-registrada antes das rodadas).** Existe λ em que o gate se afasta
mensuravelmente do prior mantendo reprodutibilidade: ρ < 0,95, R² a menos de
um DP do melhor, Jaccard ≥ 0,90. Suportada em λ ∈ {0,2; 0,3; 0,5} na partição
canônica sob Adam **e** sob AdamW, e nas cinco partições novas.

**H5b (pré-registrada).** O gate ancorado concorda com a referência de
relevância melhor do que o prior sozinho — **5/5 partições**, pareado por
semente, Wilcoxon p < 0,05. Os dados sozinhos não encontram as bandas certas
(concordância +0,03 a +0,07); o prior sozinho acerta pouco (+0,13 a +0,19); a
combinação chega a +0,21 a +0,28.

**H6 (pré-registrada).** A penalidade melhora o R² fora da amostra em 4/5
partições. Atribuível à penalidade como regularizador, **não** ao conteúdo
químico do prior: separar as duas coisas exigiria um controle de prior
embaralhado, deliberadamente fora do pré-registro.

## O que foi refutado

**H5a (pré-registrada).** O máximo interior **não transporta**. Em 3 das 5
partições o argmax fica em λ = 10, a borda da grade; o critério exigia máximo
interior em ≥ 4. O achado da partição canônica é específico dela.

Diagnóstico: a curva **satura em vez de picar**. As diferenças entre λ = 1 e
λ = 10 nas partições novas são +0,0001, −0,0017, +0,0055 e +0,0015, contra
desvios entre sementes de 0,013 a 0,018. Acima de λ ≈ 0,5 a concordância para
de subir e qual ponto da grade vence é ruído dentro do platô. Na partição
canônica a margem era 0,0109, cerca do dobro da maior das cinco — foi isso que
fez o máximo parecer real.

**Ressalva sobre H5c.** O critério passou 5/5 mas passa trivialmente: a
vizinhança de λ=1 foi definida como {0,7; 1; 10} e λ=10 é ao mesmo tempo o
vizinho de grade e a borda, de modo que o teste não distingue "estável em 1" de
"encostado no teto". Não conta como confirmação. Falha de redação do critério,
registrada aqui para não ser reaproveitada.

## O que não é afirmado

O modelo com gate **não** é bom preditor nestes dados. PLS calibrado atinge
R² de 0,885 a 0,923 nas cinco partições contra 0,764 a 0,817 do melhor λ,
coerente com o ΔR² = −0,108 ± 0,031 do artigo de modalidades. As conclusões
acima são sobre o que o gate **significa**, não sobre o quanto ele acerta.

A grade de λ está fechada pelo pré-registro. Se a saturação virar objeto de
estudo, precisa de pré-registro novo e separado.

## Confirmação cruzada

Adam e AdamW são indistinguíveis em toda a grade — concordância em λ=1 de
+0,2736 contra +0,2709, R² de 0,8211 contra 0,8209. Isso é o esperado: a
diferença entre decaimento acoplado e desacoplado age sobre gates saturados, e
nesta parametrização não há nenhum. O trabalho de incerteza mede o contraste em
+0,435 no prior em degrau (34 bandas inertes) e praticamente zero na condição
neutra; esta é aquela condição neutra, reproduzida por outro caminho de código.

---

## Nota de rastreabilidade, 2026-10-28 — o 2/5 de H5a

A Tabela 1 registra H5a como **não suportada, 2/5**. Este achado escreve que
"em 3 das 5 partições o argmax fica em λ = 10, a borda da grade" e que o
critério exigia máximo interior em ≥ 4. O **2/5** da tabela é portanto o
complemento aritmético do 3/5 registrado aqui, e não um número que este achado
tenha enunciado.

O complemento é válido porque a classificação das cinco partições é
**exaustiva e mutuamente exclusiva**: o argmax de cada uma está na borda da
grade (λ = 10) ou no interior, sem terceira possibilidade e sem empate entre
as duas. Registrado para que a tabela não pareça citar um número medido aqui.
