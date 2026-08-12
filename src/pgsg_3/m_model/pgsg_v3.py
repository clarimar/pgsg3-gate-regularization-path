"""PGSGv3Model — Prior-Guided Spectral Gating com prior como restrição suave.

O QUE MUDA EM RELAÇÃO À v2
--------------------------
Na `PGSGv2Model`, o prior entra em um único ponto: a inicialização dos
logits do gate, θ₀ = logit(s), de modo que g começa exatamente em s. Não
há nenhum termo na função de perda que mantenha g próximo de s; a partir
da primeira atualização, o gradiente é livre para afastá-lo.

Empiricamente, ele quase não se afasta (ρ(g,s) ≥ 0,9987 em NIR com 10
sementes; ≥ 0,978 em Raman). Mas isso é uma *observação*, não uma
propriedade imposta: sem prior, o modelo converge para um gate quase não
correlacionado (ρ ≤ 0,28) com acurácia estatisticamente equivalente.

A `PGSGv3Model` torna a ancoragem explícita e controlável, somando à
perda um termo λ · KL(g ‖ s):

    L(θ, W) = MSE(ŷ, y) + λ · KL_Bernoulli(σ(θ) ‖ s)

- λ = 0  → recupera a `PGSGv2Model` EXATAMENTE (garantido por teste).
- λ → ∞  → congela o gate no prior.
- λ intermediário → o objeto de estudo do pgsg_3.

DOIS MODOS DE INICIALIZAÇÃO (`init_from_prior`)
-----------------------------------------------
A primeira varredura (2026-08-12, `results/sweep_nir/`) mostrou que, com
θ₀ = logit(s), λ é praticamente inerte: ρ(g,s) vai de 0,9987 (λ=0) a
0,9999 (λ=10) — varia pouco e na direção oposta à do H0. A razão é que a
penalidade é redundante com a inicialização: o gate já parte de s e o
gradiente do MSE não o afasta; um termo que puxa de volta para s não
altera um equilíbrio que já está em s.

O caminho de regularização informativo é o outro:

    init_from_prior=True   θ₀ = logit(s).  λ = redundante (varredura 1).
    init_from_prior=False  θ₀ = 0.         λ = ancoragem genuína.

No segundo modo, λ interpola entre os dois extremos que pgsg_1 (R2) mediu
com 10 sementes: λ=0 reproduz a condição não informada (ρ ≈ 0,03--0,28,
Jaccard 0,09--0,57) e λ grande deve recuperar a condição de literatura
(ρ ≈ 0,999, Jaccard ≈ 0,95). Os extremos do diagrama de fase ficam assim
ancorados em resultado já publicado.

POR QUE KL DE BERNOULLI
-----------------------
O gate é uma sigmoide independente por banda: Σᵢ gᵢ ≠ 1, logo g não é uma
distribuição categórica e a KL categórica exigiria normalizar g e s —
descartando a magnitude, que é justamente o que o gate codifica (pgsg_2
§4.5 normaliza o gate só para calcular entropia, pela mesma razão).

Tratando cada banda como uma Bernoulli independente de parâmetro gᵢ
contra sᵢ:

    KL(g ‖ s) = (1/p) Σᵢ [ gᵢ log(gᵢ/sᵢ) + (1-gᵢ) log((1-gᵢ)/(1-sᵢ)) ]

Essa forma respeita a arquitetura, é ≥ 0, anula-se se e somente se g = s,
e a média sobre p torna λ comparável entre modalidades com números de
bandas muito diferentes (281 em NIR contra 1.870 em Raman) — sem isso, o
mesmo λ teria efeitos ~6,6x distintos entre os dois ramos do estudo.

DEPENDÊNCIA
-----------
`pgsg_v2.py` (vendorizado) importa `pgsg_1.ingestion` e
`pgsg_1.models.base`. O pgsg_3 não é autocontido nesse aspecto: o pacote
`pgsg_1` precisa estar importável (instalado ou no PYTHONPATH). Ver
`ensure_pgsg1_importable()` abaixo, que falha com mensagem explícita em
vez de um ImportError opaco.
"""

from __future__ import annotations

import copy
import os
import sys
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn

_EPS = 1e-6
_VAL_FRAC = 0.2


def ensure_pgsg1_importable(hint: str | None = None) -> None:
    """Garante que o pacote `pgsg_1` seja importável, ou falha com clareza.

    Procura, nesta ordem: import direto; variável de ambiente PGSG1_ROOT;
    caminhos usuais. Não instala nada e não altera o sistema.
    """
    try:
        import pgsg_1  # noqa: F401
        return
    except ImportError:
        pass

    candidatos = []
    if hint:
        candidatos.append(Path(hint))
    if os.environ.get("PGSG1_ROOT"):
        candidatos.append(Path(os.environ["PGSG1_ROOT"]))
    candidatos += [
        Path.home() / "Dropbox/pgsg/pgsg_1",
        Path.home() / "Dropbox/pgsg/pgsg_1/src",
        Path.home() / "pgsg/pgsg_1_repo",
        Path.home() / "pgsg/pgsg_1_repo/src",
    ]
    for c in candidatos:
        for raiz in (c, c / "src"):
            if (raiz / "pgsg_1").is_dir():
                sys.path.insert(0, str(raiz))
                try:
                    import pgsg_1  # noqa: F401
                    return
                except ImportError:
                    sys.path.pop(0)

    raise ImportError(
        "o modelo vendorizado `pgsg_v2.py` importa o pacote `pgsg_1`, que não "
        "foi encontrado.\nDefina PGSG1_ROOT apontando para o diretório que "
        "contém `pgsg_1/` (por exemplo:\n"
        "  export PGSG1_ROOT=~/Dropbox/pgsg/pgsg_1/src\n"
        "), ou instale o pacote com `pip install -e`."
    )


ensure_pgsg1_importable()

from .pgsg_v2 import (  # noqa: E402
    PGSGv2Model,
    _GatedMLP,
    _val_split,
    make_literature_prior,  # noqa: F401  (reexportado por conveniência)
)


# ---------------------------------------------------------------- KL
def kl_bernoulli(gate: torch.Tensor, prior: torch.Tensor) -> torch.Tensor:
    """KL(gate ‖ prior) tratando cada banda como Bernoulli independente.

    Média sobre as p bandas, de modo que λ seja comparável entre datasets
    com dimensionalidades diferentes.

    Retorna escalar ≥ 0, nulo se e somente se gate == prior.
    """
    g = gate.clamp(_EPS, 1.0 - _EPS)
    s = prior.clamp(_EPS, 1.0 - _EPS)
    termo = g * torch.log(g / s) + (1.0 - g) * torch.log((1.0 - g) / (1.0 - s))
    return termo.mean()


def kl_bernoulli_np(gate: np.ndarray, prior: np.ndarray) -> float:
    """Versão NumPy, para análise fora do laço de treino."""
    g = np.clip(np.asarray(gate, dtype=np.float64), _EPS, 1 - _EPS)
    s = np.clip(np.asarray(prior, dtype=np.float64), _EPS, 1 - _EPS)
    return float(np.mean(g * np.log(g / s) + (1 - g) * np.log((1 - g) / (1 - s))))


# ---------------------------------------------------------------- modelo
class PGSGv3Model(PGSGv2Model):
    """PGSG v3: v2 mais penalidade λ·KL(gate ‖ prior).

    Parâmetros
    ----------
    lam : float
        Peso da penalidade KL. `lam=0.0` reproduz a `PGSGv2Model`
        exatamente (mesma sequência de operações, mesmas sementes).
    Demais parâmetros: idênticos à `PGSGv2Model`.

    Notas
    -----
    `lam > 0` exige `prior` em `fit()`. Sem prior, a penalidade não tem
    referência e a chamada é um erro de especificação, não um caso a
    tratar silenciosamente.

    O laço de treino é uma cópia do da v2 com uma única linha acrescentada
    (o termo KL). A duplicação é deliberada: o arquivo vendorizado não é
    modificado, preservando o hash de proveniência. O teste
    `test_lambda_zero_reproduz_v2` é a proteção contra divergência — se a
    v2 mudar, ele falha.
    """

    def __init__(
        self, *, lam: float = 0.0, init_from_prior: bool = True, **kwargs
    ) -> None:
        super().__init__(**kwargs)
        if lam < 0:
            raise ValueError(f"lam deve ser >= 0, recebido {lam}")
        self.lam = float(lam)
        self.init_from_prior = bool(init_from_prior)
        self._kl_history: list[float] | None = None

    @property
    def name(self) -> str:
        init = "lit" if self.init_from_prior else "zero"
        return f"PGSGv3(lam={self.lam:g},init={init})"

    def _fit_impl(self, train, prior: np.ndarray | None) -> None:
        if self.lam > 0 and prior is None:
            raise ValueError(
                "lam > 0 exige um prior: a penalidade KL(gate‖prior) não tem "
                "referência sem ele. Use lam=0 para a condição não-informada."
            )
        if not self.init_from_prior and self.lam == 0 and prior is not None:
            # não é erro, mas é fácil de fazer sem querer: nesta combinação o
            # prior é ignorado por completo e o resultado é a condição não
            # informada, com o prior guardado apenas para as métricas.
            pass

        torch.manual_seed(self.seed)
        X = train.X.astype(np.float32)
        y = train.y.astype(np.float32)
        p = X.shape[1]

        self._y_mean = float(y.mean())
        self._y_std = float(y.std()) or 1.0
        y_norm = (y - self._y_mean) / self._y_std

        self._prior = prior.copy() if prior is not None else None

        net = _GatedMLP(p, self.hidden)

        prior_t: torch.Tensor | None = None
        if prior is not None:
            s = np.clip(prior.astype(np.float64), _EPS, 1 - _EPS)
            # o prior sempre serve de REFERÊNCIA para a penalidade; só entra
            # na INICIALIZAÇÃO se init_from_prior=True. Separar os dois papéis
            # é o que torna λ informativo (ver docstring do módulo).
            if self.init_from_prior:
                with torch.no_grad():
                    net.theta.copy_(
                        torch.tensor(np.log(s / (1 - s)), dtype=torch.float32)
                    )
            prior_t = torch.tensor(s, dtype=torch.float32)

        X_tr, y_tr, X_val, y_val = _val_split(X, y_norm, _VAL_FRAC, self.seed)
        X_tr_t = torch.from_numpy(X_tr)
        y_tr_t = torch.from_numpy(y_tr).unsqueeze(1)
        X_val_t = torch.from_numpy(X_val)
        y_val_t = torch.from_numpy(y_val).unsqueeze(1)

        optimizer = torch.optim.Adam(
            net.parameters(), lr=self.lr, weight_decay=self.weight_decay
        )
        criterion = nn.MSELoss()

        best_val = float("inf")
        best_state = copy.deepcopy(net.state_dict())
        best_epoch = 0
        no_improve = 0
        train_losses: list[float] = []
        val_losses: list[float] = []
        kl_history: list[float] = []
        n_tr = len(X_tr)

        usa_kl = self.lam > 0 and prior_t is not None

        for epoch in range(self.max_epochs):
            net.train()
            perm = torch.randperm(n_tr)
            epoch_loss = 0.0
            for i in range(0, n_tr, self.batch_size):
                b = perm[i:i + self.batch_size]
                optimizer.zero_grad()
                loss = criterion(net(X_tr_t[b]), y_tr_t[b])
                if usa_kl:
                    # >>> ÚNICA diferença em relação à PGSGv2Model <<<
                    loss = loss + self.lam * kl_bernoulli(
                        torch.sigmoid(net.theta), prior_t
                    )
                loss.backward()
                optimizer.step()
                epoch_loss += loss.item() * len(b)
            train_losses.append(epoch_loss / n_tr)

            net.eval()
            with torch.no_grad():
                # early stopping por MSE puro, SEM o termo KL: o critério de
                # parada deve medir capacidade preditiva, não aderência ao
                # prior — caso contrário λ alteraria o significado de
                # best_epoch e as curvas não seriam comparáveis entre λ.
                val_loss = criterion(net(X_val_t), y_val_t).item()
                if prior_t is not None:
                    kl_history.append(
                        float(kl_bernoulli(torch.sigmoid(net.theta), prior_t))
                    )
            val_losses.append(val_loss)

            if val_loss < best_val - 1e-8:
                best_val = val_loss
                best_state = copy.deepcopy(net.state_dict())
                best_epoch = epoch
                no_improve = 0
            else:
                no_improve += 1
                if no_improve >= self.patience:
                    break

        net.load_state_dict(best_state)
        self._net = net
        self._kl_history = kl_history or None
        self._train_history = {
            "best_epoch": best_epoch,
            "best_val_loss": best_val,
            "train_losses": train_losses,
            "val_losses": val_losses,
            "kl_history": kl_history,
            "lam": self.lam,
            "init_from_prior": self.init_from_prior,
        }

    # ------------------------------------------------------------ análise
    @property
    def kl_final(self) -> float | None:
        """KL(gate ‖ prior) no estado final (melhor época)."""
        if self._net is None or self._prior is None:
            return None
        return kl_bernoulli_np(self._net.gates_np(), self._prior)

    @property
    def kl_history(self) -> list[float] | None:
        return self._kl_history
