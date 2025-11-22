import numpy as np
from scipy.stats import norm

def heston_model_sim(S0, v0, rho, kappa, theta, sigma, T, r, strike, option_type="call", num_paths=10000, num_steps=100):
    """
    Monte Carlo simulation for Heston Model.
    
    Parameters:
    S0: Initial asset price
    v0: Initial variance
    rho: Correlation between asset and variance Brownian motions
    kappa: Rate of mean reversion for variance
    theta: Long-run average variance
    sigma: Volatility of variance (vol of vol)
    T: Time to maturity (in years)
    r: Risk-free rate
    strike: Strike price
    option_type: "call" or "put"
    num_paths: Number of Monte Carlo paths
    num_steps: Number of time steps
    
    Returns:
    Option price
    """
    dt = T / num_steps
    
    # Generate correlated random numbers
    # dW1 and dW2 are correlated with rho
    Z1 = np.random.normal(size=(num_paths, num_steps))
    Z2 = rho * Z1 + np.sqrt(1 - rho**2) * np.random.normal(size=(num_paths, num_steps))
    
    S = np.zeros((num_paths, num_steps + 1))
    v = np.zeros((num_paths, num_steps + 1))
    
    S[:, 0] = S0
    v[:, 0] = v0
    
    for t in range(num_steps):
        # Euler-Maruyama discretization
        # Ensure variance stays positive (Full Truncation or Reflection)
        # Using Reflection here: abs(v)
        vt = np.maximum(v[:, t], 0)
        sqrt_vt = np.sqrt(vt)
        
        S[:, t+1] = S[:, t] * np.exp((r - 0.5 * vt) * dt + sqrt_vt * np.sqrt(dt) * Z1[:, t])
        v[:, t+1] = v[:, t] + kappa * (theta - vt) * dt + sigma * sqrt_vt * np.sqrt(dt) * Z2[:, t]
        
        # Reflection for next step variance
        # v[:, t+1] = np.abs(v[:, t+1]) 
        # Actually, standard Heston often uses Full Truncation for drift/diffusion but let's just clamp for next step
        # But the loop uses v[:, t] which is already clamped by np.maximum at start of loop
    
    # Payoff
    ST = S[:, -1]
    if option_type == "call":
        payoff = np.maximum(ST - strike, 0)
    else:
        payoff = np.maximum(strike - ST, 0)
        
    # Discount back
    option_price = np.exp(-r * T) * np.mean(payoff)
    
    return option_price

def calculate_greeks(S0, v0, rho, kappa, theta, sigma, T, r, strike, option_type="call"):
    """
    Calculates Delta, Gamma, Theta using finite differences.
    """
    # Perturbations
    dS = S0 * 0.01
    dT = 1/365.0 # 1 day
    
    # Base price
    # Use fewer paths for Greeks to be faster, or same? 
    # For stability, use same seeds if possible, but here we just re-run.
    # To reduce noise, we should ideally use Common Random Numbers, but for simplicity re-running with high N.
    # Let's use N=20000 for Greeks
    N = 20000
    
    P = heston_model_sim(S0, v0, rho, kappa, theta, sigma, T, r, strike, option_type, num_paths=N)
    
    # Delta & Gamma (Central Difference)
    P_up = heston_model_sim(S0 + dS, v0, rho, kappa, theta, sigma, T, r, strike, option_type, num_paths=N)
    P_down = heston_model_sim(S0 - dS, v0, rho, kappa, theta, sigma, T, r, strike, option_type, num_paths=N)
    
    delta = (P_up - P_down) / (2 * dS)
    gamma = (P_up - 2*P + P_down) / (dS**2)
    
    # Theta (Forward Difference: P(t) - P(t+dt)) / dt ? Or P(T-dt) - P(T)
    # Theta is usually negative, time decay.
    # Price with less time to maturity
    if T > dT:
        P_time_decay = heston_model_sim(S0, v0, rho, kappa, theta, sigma, T - dT, r, strike, option_type, num_paths=N)
        theta_val = (P_time_decay - P) / dT
    else:
        theta_val = 0 # Expiring
        
    return {
        "price": P,
        "delta": delta,
        "gamma": gamma,
        "theta": theta_val
    }
