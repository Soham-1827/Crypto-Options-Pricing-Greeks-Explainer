import unittest
import numpy as np
from src.simulation import heston_model_sim, calculate_greeks

class TestHestonModel(unittest.TestCase):
    def test_call_price_increases_with_spot(self):
        """Test that call option price increases as spot price increases."""
        params = {
            "v0": 0.04, "rho": -0.5, "kappa": 2.0, "theta": 0.04, "sigma": 0.3,
            "T": 1.0, "r": 0.05, "strike": 100, "option_type": "call", "num_paths": 1000
        }
        
        price_low = heston_model_sim(S0=90, **params)
        price_high = heston_model_sim(S0=110, **params)
        
        self.assertGreater(price_high, price_low)

    def test_put_price_decreases_with_spot(self):
        """Test that put option price decreases as spot price increases."""
        params = {
            "v0": 0.04, "rho": -0.5, "kappa": 2.0, "theta": 0.04, "sigma": 0.3,
            "T": 1.0, "r": 0.05, "strike": 100, "option_type": "put", "num_paths": 1000
        }
        
        price_low = heston_model_sim(S0=90, **params)
        price_high = heston_model_sim(S0=110, **params)
        
        self.assertGreater(price_low, price_high)

    def test_greeks_sanity(self):
        """Test that Greeks are calculated and have reasonable signs for a Call."""
        # ATM Call: Delta ~ 0.5, Gamma > 0, Theta < 0
        greeks = calculate_greeks(
            S0=100, v0=0.04, rho=-0.5, kappa=2.0, theta=0.04, sigma=0.3,
            T=1.0, r=0.05, strike=100, option_type="call"
        )
        
        self.assertAlmostEqual(greeks["delta"], 0.5, delta=0.2) # Wide tolerance for MC
        self.assertGreater(greeks["gamma"], 0)
        self.assertLess(greeks["theta"], 0) # Time decay hurts calls

if __name__ == '__main__':
    unittest.main()
