import numpy as np
from sklearn.gaussian_process.kernels import RationalQuadratic, RBF, Kernel
from datetime import datetime, timedelta
import warnings
from typing import Tuple
from tasks.models import Task
from sklearn.metrics import mean_squared_error


class KRLSTracker_Executor:

    @staticmethod
    def calculateMSE(elem, kernel, lambda_, c, M, label, color):
        y = np.asarray(elem["monthly_searches"]["volumes"])
        Ntrain = 200
        Ntest = 60
        N = Ntrain + Ntest
        M = N + 100

        s = np.random.randn(M)
        s_mem = np.zeros((M, 10))
        for j in range(10):
            s_mem[j:M, j] = s[:M - j]

        s_train = s_mem[:Ntrain]
        y_train = y[:Ntrain]

        s_test = s_mem[Ntrain:N]
        y_test = y[Ntrain:N]

        mse_scores = []

        krlst = KRLST(kernel, l=lambda_, c=c, M=M)
        for j in range(0, Ntrain):
            krlst.observe(s_train[j], y_train[j], j)
            y_est, _ = krlst.predict(s_test)

            mse_scores.append(mean_squared_error(y_est, y_test))

        for j in range(0, Ntest):
            krlst.observe(s_test[j], y_test[j], j + Ntrain)

        y_est, y_var = krlst.predict(s_mem)
        max_mse = max(mse_scores)

        return {
            "label": label,
            "forecasts": np.ndarray.flatten(y_est).tolist(),
            "variance": np.ndarray.flatten(y_var).tolist(),
            "data": mse_scores,
            "borderColor": color,
            "borderWidth": 1
        }


    @staticmethod
    def forecastVolume(task_id, volume):
        result = []
        task = Task.objects.get(id=task_id)

        if len(task.forecasts_search_volume) > 0:
            result = task.forecasts_search_volume
        else:
            dates = volume[0]["monthly_searches"]["dates"]
            for j in range(0, 100):
                dates.append((datetime.strptime(dates[len(dates) - 1], "%d/%m/%Y") + timedelta(days=7)).strftime("%d/%m/%Y"))

            for i in range(0, len(volume)):

                y = np.asarray(volume[i]["monthly_searches"]["volumes"])

                s = np.random.randn(len(y) + 100)
                s_mem = np.zeros((len(y) + 100, 10))
                for j in range(10):
                    s_mem[j:len(y) + 100, j] = s[:len(y) + 100 - j]

                krlst = KRLST(RationalQuadratic(1), l=1, c=1e-4, M=300)

                for j in range(0, len(y)):
                    krlst.observe(s_mem[j], y[j], j)

                y_est, y_var = krlst.predict(s_mem)
                forecasts = np.ndarray.flatten(y_est).tolist()

                result.append({
                    "keyword": volume[i]["keyword"],
                    "average": sum(forecasts)/len(forecasts),
                    "monthly_searches": {
                        "dates": dates,
                        "trends": [
                            {
                                "label": "volume",
                                "data": volume[i]["monthly_searches"]["volumes"],
                                "borderColor": "blue",
                                "borderWidth": 1
                            },
                            {
                                "label": "forecasts",
                                "data": forecasts,
                                "variance": np.ndarray.flatten(y_var).tolist(),
                                "borderColor": "red",
                                "borderWidth": 1
                            }
                        ],
                        "mses": [
                            KRLSTracker_Executor.calculateMSE(volume[i], RBF(2), 1, 1e-4, 300, "ker=RBF(2), λ=1, c=1e-4, M=300", "green"),
                            KRLSTracker_Executor.calculateMSE(volume[i], RationalQuadratic(2), 0.99999, 1e-4, 300, "ker=RQ(2), λ=0.99999, c=1e-4, M=300", "red"),
                            KRLSTracker_Executor.calculateMSE(volume[i], RationalQuadratic(2), 1, 1e-4, 300, "ker=RQ(2), λ=1, c=1e-4, M=300", "orange"),
                            KRLSTracker_Executor.calculateMSE(volume[i], RationalQuadratic(2), 0.99999, 1e-4, 100, "ker=RQ(2), λ=0.99999, c=1e-4, M=100", "blue"),

                        ]
                    }
                })

            task.forecasts_search_volume = result
            task.save()


        return result


class KRLST:
    """Kernel Recursive Least-Squares Tracker Algorithm
    Maintains a fixed budget via growing and pruning and regularization.
    Assumes a fixed value for the lengthscale, the regularization factor and the signal and
    noise powers.
    """

    def __init__(
            self, kernel: Kernel, l: float, c: float, M: int, forgetmode: str = "B2P", jitter=1e-10
    ):
        """
        Args:
            kernel (Kernel): Kernel object
            l (float): Forgetting factor. l \in [0,1]
            c (float): Noise-to-signal ratio (regularization)
            M (int): Budget, i.e., maximum size of dictionary
            forgetmode (str): Either back-to-prior ('B2P') or uncertainty injection ('UI')
        """
        self._kernel = kernel

        if l < 0 or l > 1:
            raise ValueError("Parameter `l` is out of allowed range of [0,1].")
        self._lambda = l

        self._c = c
        self._M = M

        if not (forgetmode in ["B2P", "UI"]):
            raise ValueError("Parameter `forgetmode` can either be 'B2P' or 'UI'.")
        self._forgetmode = forgetmode

        self._jitter = jitter
        self._is_init = False

    def fit(self, X: np.ndarray, Y: np.ndarray, T: np.ndarray):
        """Observes a single data point and label and updates model with this new observations.
        The update procedure includes forgetting of past information, adding new basis elements
        and reducing the size of the basis if its size becomes larger as the specified `M`.
        Args:
            X (np.ndarray): Array of data points with shape (n_data_points, n_features). Can be
                of any type.
            Y (np.ndarray): Float array of labels with shape (n_data_points,). Does not support
                multilabels.
            T (np.ndarray): Int array of time indices with shape (n_data_points,).
        """
        for x, y, t in zip(X, Y, T):
            self.observe(x, y, t)
        return self

    def observe(self, x: np.ndarray, y: float, t: int):
        """Observes a single data point and label and updates model with this new observations.
        The update procedure includes forgetting of past information, adding new basis elements
        and reducing the size of the basis if its size becomes larger as the specified `M`.
        Args:
            x (np.ndarray): Single data point with shape (1, n_features). Can be of any type
            y (float): Single regression target
            t (int): time index
        """
        if not self._is_init:  # Initialize model

            kss = self._kernel(x) + self._jitter
            self.Q = 1 / kss
            self.mu = (y * kss) / (kss + self._c)
            self.Sigma = kss - ((kss ** 2) / (kss + self._c))  # Check this

            self.basis = 0  # Dictionary indicies
            self.Xb = x  # Dictionary
            self.m = 1  # Dict size

            self.nums02ML = y ** 2 / (kss + self._c)
            self.dens02ML = 1
            self.s02 = self.nums02ML / self.dens02ML

            self._is_init = True

        else:  # Update model

            if self._lambda < 1:
                # Forgetting

                if self._forgetmode == "B2P":  # Back-to-prior
                    Kt = self._kernel(self.Xb)
                    self.Sigma = self._lambda * self.Sigma + (1 - self._lambda) * Kt
                    self.mu = np.sqrt(self._lambda) * self.mu

                elif self._forgetmode == "UI":  # Uncertainty injection
                    self.Sigma = self.Sigma / self._lambda
                else:
                    raise ValueError(
                        "Undefined forgetting strategy.\nSupported forgetting strategies"
                        + "are 'B2P' and 'UI'."
                    )

            # Predict new sample
            kbs = self._kernel(self.Xb, np.atleast_2d(x))
            kss = self._kernel(x) + self._jitter

            q = self.Q @ kbs
            ymean = q.T @ self.mu
            gamma2 = kss - kbs.T @ q
            gamma2[gamma2 < 0] = 0

            h = self.Sigma @ q
            sf2 = gamma2 + q.T @ h
            sf2[sf2 < 0] = 0

            sy2 = self._c + sf2

            # Include new sample and add new basis
            Q_old = self.Q.copy()
            p = np.block([[q], [-1]])
            self.Q = np.block(
                [[self.Q, np.zeros((self.m, 1))], [np.zeros((1, self.m)), 0]]
            ) + (1 / gamma2) * (p @ p.T)

            p = np.block([[h], [sf2]])
            self.mu = np.block([[self.mu], [ymean]]) + ((y - ymean) / sy2) * p
            self.Sigma = np.block([[self.Sigma, h], [h.T, sf2]]) - (1 / sy2) * (p @ p.T)
            self.basis = np.block([[self.basis], [t]])
            self.m = self.m + 1
            self.Xb = np.block([[self.Xb], [x]])

            # Estimate s02 via maximum likelihood
            self.nums02ML = self.nums02ML + self._lambda * (y - ymean) ** 2 / sy2
            self.dens02ML = self.dens02ML + self._lambda
            self.s02 = self.nums02ML / self.dens02ML

            # Remove basis if necessary
            if (self.m > self._M) or (gamma2 < self._jitter):

                if gamma2 < self._jitter:
                    if gamma2 < self._jitter / 10:
                        warnings.warn(
                            "Numerical roundoff error is too high. Try increasing jitter noise."
                        )
                    criterium = np.block([np.ones((self.m - 1)), 0])
                else:  # MSE pruning
                    errors = (self.Q @ self.mu).reshape(-1) / np.diag(self.Q)
                    criterium = np.abs(errors)

                r = np.argmin(criterium)
                smaller = criterium > criterium[r]

                if r == self.m:  # remove the element we just added
                    self.Q = Q_old
                else:
                    Qs = self.Q[smaller, r]
                    qs = self.Q[r, r]
                    self.Q = self.Q[smaller][:, smaller]
                    self.Q = self.Q - (Qs.reshape(-1, 1) * Qs.reshape(1, -1)) / qs

                self.mu = self.mu[smaller]
                self.Sigma = self.Sigma[smaller][:, smaller]
                self.basis = self.basis[smaller]
                self.m = self.m - 1
                self.Xb = self.Xb[smaller, :]

    def predict(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Predicts mean and variance for potentially unseen data X
        Args:
            X (np.ndarray): Array of data points with shape (n_data_points, n_features)
        Returns:
            mean_est (np.ndarray), var_est (np.ndarray): Predicted mean and variance
        """
        kbs = self._kernel(self.Xb, np.atleast_2d(X))
        mean_est = kbs.T @ self.Q @ self.mu
        sf2 = (1 + self._jitter + np.sum(kbs * ((self.Q @ self.Sigma @ self.Q - self.Q) @ kbs), axis=0).reshape(-1, 1))
        sf2[sf2 < 0] = 0
        var_est = self.s02 * (self._c + sf2)

        return mean_est, var_est
