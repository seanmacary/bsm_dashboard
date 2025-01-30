import numpy as np
import scipy.stats as si


class BlackScholesModel:
    def __init__(self, S: float, K: float, T: float, r: float, sigma: float) -> None:
        """
            S: Underlying asset price
            K: Option strike price
            T: Time to expirate (in years)
            r: Risk-free interest rate
            sigma: Observed/historical volatility of the underlying asset
        """
        self.S = S
        self.K = K
        self.T = T
        self.r = r
        self.sigma = sigma

    def d1(self) -> float:
        """
        Calculates the potential benefit from buying the asset, considering the chance it will be profitable
        """
        return (np.log(self.S / self.K) + (self.r + 0.5 * self.sigma ** 2) * self.T) / (self.sigma * np.sqrt(self.T))

    def d2(self) -> float:
        """
        Calculates the cost of exercising the option, adjusted for the time value of money and probability of it being worth it to exercise the contract
        """
        return self.d1() - self.sigma * np.sqrt(self.T)

    def call_option_price(self) -> float:
        """
        Calculates the theoretical price of a call option based on provided inputs and BSM
        """
        return max (0, (self.S * si.norm.cdf(self.d1(), 0.0, 1.0)) - (
                    self.K * np.exp(-self.r * self.T) * si.norm.cdf(self.d2())))

    def put_option_price(self):
        """
        Calculates the theoretical price of a put option based on provided inputs and BSM
        """
        return max(0, (self.K * np.exp(-self.r * self.T) * si.norm.cdf(-self.d2(), 0.0, 1.0) - self.S * si.norm.cdf(-self.d1(),
                                                                                                             0.0, 1.0)))