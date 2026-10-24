# ADR-0003 — Comunicação ao editor do artigo anterior

Data: 2026-10-24
Status: aceito
Decisão dos autores: **C. J. Coelho e G. Coelho**

## Contexto

`findings/F002` e `findings/F004` estabelecem, por reexecução, que a figura de
estabilidade interpretativa do braço NIR de *Gate Topology and Reproducibility
of Prior-Guided Spectral Gating Across Near-Infrared and Raman Spectroscopy*
(aceito, Chemometrics and Intelligent Laboratory Systems) **mede ordem de
desempate e não seleção reprodutível de bandas**:

- as 34 bandas do platô do prior têm valor bit-idêntico em todas as sementes;
- as 28 bandas do decil saem inteiramente de dentro desse platô;
- `J = 0,9418` é reproduzido exatamente, e cai a `0,7005 ± 0,0068` — o acaso de
  sortear 28 entre 34 — quando os empates são sorteados em vez de deixados ao
  `argsort`;
- o mesmo vale nos sete tamanhos de treino da revisão R2 do `pgsg_1`.

Não afetados, e verificados um a um: o braço **Raman** daquele artigo (prior
contínuo, platô de uma banda); **todos os R²**; e **ρ(gate, prior)**, que usa os
valores e não a sua ordem.

O número publicado está correto como cálculo. O que não se sustenta é lê-lo
como reprodutibilidade de **seleção de bandas** no braço NIR.

> **Correção de 2026-10-24, posterior à redação deste contexto e anterior à
> decisão ter sido executada.** O parágrafo acima, na sua primeira versão,
> dizia que a interpretação do artigo "não se sustenta". **Exagero meu, e
> retirado.**
>
> O manuscrito aceito **já contém** o controle que responde à objeção. A seção
> *"Control: stability of the gate, or of what is learned?"* enuncia a leitura
> alternativa — *"if the prior merely immobilized the gate, the high
> reproducibility reported above would be trivial"* — mede o deslocamento
> d = g_final − g₀, obtém ρ(d) = 0,9462 em NIR e 0,976 em Raman, e **já
> reporta** que a identificação de bandas individuais é fraca em NIR (*Jaccard
> of the top decile of |d|: 0.38*), concluindo que *"the shape of the
> displacement is reproducible; the identification of individually most mobile
> bands is less so."*
>
> ρ(d) usa valores sobre as 281 bandas, não postos de um bloco empatado, e
> **não é afetado** pelo artefato. A conclusão interpretativa do artigo repousa
> nesse controle, não no 0,9418. **Não há conclusão publicada a corrigir.**
>
> O que o achado acrescenta é estreito: o 0,9418, e a faixa 0,90--0,94 do
> resumo, não medem seleção reprodutível de bandas no braço NIR. É ressalva
> sobre o que o número registra.
>
> Consequência: a premissa de "erro material em resultado publicado", que
> motivou tanto a minha recomendação quanto a ressalva de G. Coelho, **era mais
> forte do que o texto do artigo autoriza**. A decisão de não comunicar
> formalmente fica correspondentemente melhor fundamentada do que parecia. O
> erro é meu, por ter recomendado sem ler a seção de controle.

## Decisão

**Prosseguir com o novo artigo, sem comunicação formal ao editor do artigo
anterior.**

Três cuidados, exigidos pela decisão e vinculantes para a redação:

1. Apresentar os resultados da reanálise com transparência, incluindo as
   divergências identificadas.
2. Distinguir claramente as contribuições do novo manuscrito das do artigo
   anterior.
3. **Não apresentar a publicação do novo artigo como substituta de uma correção
   do registro científico anterior.**

## Divergência registrada

Dois pareceres recomendaram comunicar, e ambos ficam registrados aqui porque a
decisão foi tomada contra eles:

**G. Coelho, 2026-10-24:** *"se houver erro material confirmado em resultados
publicados, a ausência de comunicação ao editor deixa essa questão editorial
pendente. Minha recomendação científica continua sendo comunicar o problema,
embora a decisão de não fazê-lo esteja clara."*

**Assistente (Claude), 2026-10-23 e 2026-10-24:** reanálise em outro artigo não
descarrega a obrigação quando há problema material em resultado publicado; a
recomendação foi comunicar.

A decisão é dos autores. Este registro existe para que ela não pareça, mais
tarde, não ter sido deliberada.

## Terceira via, confirmada e disponível

**O artigo está em provas** (confirmado em 2026-10-24). Correção em provas é
rotina de autor: não constitui relato de erro, não tramita como ocorrência
editorial e não tem o peso de um corrigendum.

Proposta mínima em `paper/correcao-em-provas.md`: quatro linhas na §4 (H4)
registrando que, no braço NIR sob o prior de literatura, o decil sai
inteiramente do platô de 34 bandas empatadas, de modo que o Jaccard ali reflete
a resolução desse empate e não escolha entre bandas distinguíveis; e que o
controle de deslocamento, que usa valores e não ordem, não é afetado.
Opcionalmente uma oração no resumo.

Acrescenta, não retira. Nenhuma conclusão muda. Se produção recusar a inserção,
a questão volta a ser editorial e esta decisão se aplica como está.

## Consequências para o texto do manuscrito

A ressalva 3 é verificável, não declarativa. O manuscrito, por construção:

- **relata** a propriedade da métrica e os números medidos, com o artigo
  anterior citado como fonte dos dados e da arquitetura;
- **não afirma** que as conclusões do artigo anterior estão corrigidas,
  retratadas ou substituídas;
- **não afirma** tampouco que permanecem válidas na parte NIR — o
  silêncio é sobre o estatuto editorial, não sobre a medida;
- **não usa** verbos de correção do registro ("corrigimos", "retificamos",
  "este trabalho corrige") em relação ao artigo anterior;
- deixa a medida falar. Um leitor que conheça o artigo anterior tira a
  conclusão; o manuscrito não a enuncia como ato editorial.

Isto é compatível com a transparência exigida na ressalva 1: nada é omitido do
que foi medido. O que se omite é a pretensão de que o artigo novo resolva uma
pendência editorial — que é precisamente o que a ressalva 3 proíbe.

## Nota de conformidade

Os achados, os scripts de verificação e este registro estão em repositório
público desde 2026-10-23. Nada do que está documentado aqui depende de
publicação para ser verificável por terceiros, e a reprodução do número leva
vinte segundos (`scripts/check_decile_ties.py`, no repositório do `pgsg_2`).
