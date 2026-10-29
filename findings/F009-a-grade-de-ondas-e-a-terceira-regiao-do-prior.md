# F009 — A grade de comprimentos de onda, e a terceira região do prior está truncada

Data: 2026-10-29
Medido em: `data/processed/gates_r2/gates_n1158.npz`, campo `wavelengths`
Status: medição; a consequência para o texto é decisão do autor

## Como isto apareceu

Ao conferir a entrada do conjunto de dados para a lista de referências
(`paper/12-referencias.md`), o registro do Mendeley descreve espectros de
**309 a 1149 nm**. O manuscrito declara que o prior atribui 0,8 à região de
**1100–1200 nm**. Os dois não cabem juntos, e a verificação foi direta: a
grade está versionada no repositório.

## O que foi medido

```
grade: 309,0 a 1149,0 nm, 281 bandas, passo de 3,00 nm

prior 1,0:  34 bandas,  900,0–999,0 nm
prior 0,8:  17 bandas, 1101,0–1149,0 nm
prior 0,6:   7 bandas,  681,0–699,0 nm
prior 0,1: 223 bandas,  309,0–1098,0 nm
```

As três regiões declaradas, confrontadas com o que a grade pode cobrir:

| região declarada | nível | bandas presentes | estado |
| --- | --- | --- | --- |
| 680–700 nm | 0,6 | 7 | coberta |
| 900–1000 nm | 1,0 | 34 | coberta |
| 1100–1200 nm | 0,8 | 17 | **truncada em 1149 nm** |

O construtor (`src/pgsg_3/m_model/pgsg_v2.py`, `make_literature_prior`) aplica
`1100 <= w <= 1200`. A condição está certa; a grade termina antes. Metade da
terceira região não existe nos dados, e o prior não tem como atribuí-la.

## O que isto afeta, e o que não afeta

**Não afeta nenhum resultado.** O platô do artigo é o nível 1,0, em 900–999 nm,
com as 34 bandas inteiras dentro da grade. A condição geométrica central —
|platô| = 34 > q, com q = 28 ou 29 — é medida nesse nível e não depende da
terceira região. Os 0,9418, 0,7005 ± 0,0068, 0,7012 e as faixas do F008 ficam
onde estão.

**Afeta o que o texto declara.** A legenda da Figura 1 diz *"0.8 to 1100–1200
nm"* e imprime o número de bandas de cada degrau; quem conferir 17 bandas
contra uma janela de 100 nm a passo de 3 nm encontra a discrepância, porque
100 nm dariam cerca de 34. A §2.1 declara `p = 281` sem declarar a faixa. As
duas coisas juntas deixam ao leitor a tarefa de descobrir o truncamento.

**Não é erro de construção do prior, e não deve ser corrigido no código.** A
região de 1100–1200 nm é o primeiro sobretom C–H na literatura, e é isso que
o prior codifica; o instrumento é que mede até 1149 nm. Reescrever a região
para 1100–1149 nm faria o prior depender do instrumento e apagaria a origem
da escolha. O que falta é dizer a faixa.

## Correção proposta ao texto, para decisão do autor

Duas frases, as duas de fato medido, nenhuma retirando afirmação aprovada:

1. **§2.1**, depois de `with p = 281 wavelengths`: declarar a grade —
   309 a 1149 nm em passos de 3 nm.
2. **Legenda da Figura 1**: depois da enumeração das regiões, dizer que a
   terceira é truncada pela faixa do instrumento, com as 17 bandas que
   restam.

Sem a primeira, a segunda não tem onde se apoiar; com as duas, a contagem de
bandas da figura passa a ser verificável pelo leitor.
