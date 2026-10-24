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
> displacement control below, which uses gate values rather than their order, is
> unaffected. In Raman the prior is continuous and its maximum is attained at a
> single band, so the decile is not plateau-bound.

Quatro linhas. Acrescenta, não retira. E reforça o artigo: mostra que os autores
sabem o que a própria métrica registra.

## Opcional: uma oração no resumo

Onde está *"(pairwise Jaccard similarity $0.90$--$0.94$ versus
$0.60$--$0.65$)"*, acrescentar após o fecho do parêntese:

> ; in NIR this overlap is evaluated within the prior's own plateau of tied
> bands, and the displacement control rather than this figure supports the
> claim

Se produção reclamar de extensão no resumo, a frase da §4 basta — ela é onde o
número vive.

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
