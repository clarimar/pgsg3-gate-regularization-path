# Correção em provas — proposta mínima

Data: 2026-10-24

Contexto: o artigo está **em provas**. Correção em provas é rotina de autor —
não é comunicação formal, não é corrigendum, não tramita como ocorrência
editorial.

**O que mudou na avaliação.** O manuscrito aceito **já contém** o controle que
responde à objeção: a seção *"Control: stability of the gate, or of what is
learned?"* enuncia a leitura alternativa (*"if the prior merely immobilized the
gate, the high reproducibility reported above would be trivial"*), mede o
deslocamento d = g_final − g₀, obtém ρ(d) = 0,9462 em NIR, e **já reporta** que
a identificação de bandas individuais é fraca ali (*Jaccard of the top decile of
|d|: 0.38 in NIR*).

ρ(d) usa valores sobre as 281 bandas, não postos de um bloco empatado, e
portanto **não é afetado** pelo artefato de desempate. A conclusão
interpretativa do artigo repousa nesse controle, não no 0,9418.

Logo não há conclusão a corrigir. Há um número que, no braço NIR, não mede o
que um leitor tomaria por seleção reprodutível de bandas.

---

## Proposta: uma frase na §4 (H4)

Depois do parágrafo que reporta os Jaccards — o que termina em *"0.9011 (Raman,
literature prior) versus 0.6545 (Raman, uninformed)"* — inserir:

> Under the literature prior in NIR, the top decile is drawn entirely from the
> 34 bands the prior places at its maximum, whose gate values coincide to
> machine precision after training; the Jaccard reported there therefore
> reflects the resolution of that tie rather than a choice among distinguishable
> bands, and should not be read as reproducibility of band selection. The
> displacement control below uses gate values rather than their order, so no
> tie-breaking rule enters it and the figure reported there is not affected by
> this; whether that correlation is also independent of the plateau is a
> separate question. In Raman the prior is continuous and its maximum is
> attained at a single band, so the decile is not plateau-bound and the
> mechanism described here does not arise.

Cinco linhas. Acrescenta, não retira. E reforça o artigo: mostra que os autores
sabem o que a própria métrica registra.

### Duas precisões exigidas pelo autor em 2026-10-26, e por quê

**A primeira redação dizia que o controle de deslocamento é *unaffected*.**
Forte demais. O `F007` mostra que ele não sofre o artefato de desempate — não
há operador de seleção nem ordem arbitrária — mas **não é independente do
platô**: sob prior na inicialização, 12% do espectro carrega um deslocamento
igual a menos de um milionésimo entre sementes, e excluir essas bandas baixa a
correlação em 0,018 (Pearson) ou 0,051 (Spearman) no maior tamanho amostral.
A inserção agora separa as duas propriedades e diz que a segunda é questão à
parte. **O artigo anterior não precisa resolvê-la**: a frase apenas não a
pré-julga.

**A segunda era o fecho sobre o Raman.** Dizer que lá o decil não é preso ao
platô é verdade e suficiente: elimina o mecanismo específico identificado em
NIR. Não garante validade interpretativa da seleção espectral em Raman, e a
redação original, ao parar no contraste, convidava a essa leitura. Acrescentado
*"and the mechanism described here does not arise"*, que é exatamente o escopo
da afirmação.

## A oração no resumo foi retirada

A primeira versão propunha também uma oração no resumo do artigo aceito.
**Retirada por decisão do autor:** a inserção localizada junto ao resultado de
Jaccard é suficiente e interfere menos nas provas. Mexer no resumo em estágio
de provas custa mais negociação com a produção do que o ganho justifica, e o
número vive na §4.

## O que eu não proporia mudar

Nada mais. Especificamente:

- **ρ(d) = 0,9462 e ρ(d) = 0,976** ficam como estão: medidas corretas e não
  afetadas.
- **O Jaccard de 0,38 em NIR** fica: o artigo já o reporta e já o interpreta
  corretamente como limite de resolução em banda individual.
- **Todos os R² e ρ(g)** ficam: usam valores, não ordem.
- **A conclusão sobre o valor do prior estar na estabilidade interpretativa**
  fica: é o controle de deslocamento que a sustenta, e ele está de pé.
- **O braço Raman** fica inteiro.

## Se produção recusar a inserção

Provas aceitam correção factual e tipográfica; uma inserção de quatro linhas em
resultados costuma passar, mas não é garantido. Se recusarem, aí sim a questão
volta a ser editorial, e a decisão do `ADR-0003` se aplica como está.
