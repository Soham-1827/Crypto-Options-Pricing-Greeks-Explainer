import pandas as pd
import numpy as np
from .data_loader import fetch_historical_data, fetch_current_price, fetch_risk_free_rate
from .simulation import calculate_greeks
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import os

# Volatility Agent
def volatility_agent(state):
    """
    Analyzes historical data to estimate Heston parameters.
    """
    coin_id = state["coin_id"]
    days = 365
    
    # Fetch data
    df = fetch_historical_data(coin_id, days=days)
    if df is None or df.empty:
        # Fallback defaults
        return {
            "parameters": {
                "v0": 0.04,
                "theta": 0.04,
                "kappa": 2.0,
                "sigma": 0.3,
                "rho": -0.5
            },
            "current_price": 100.0 # Dummy
        }
        
    # Calculate returns
    df["returns"] = df["price"].pct_change().dropna()
    
    # Simple estimation
    # Current variance v0
    # Estimate from last 30 days volatility
    recent_vol = df["returns"].tail(30).std() * np.sqrt(365)
    v0 = recent_vol ** 2
    
    # Long run variance theta
    # Estimate from full year volatility
    long_run_vol = df["returns"].std() * np.sqrt(365)
    theta = long_run_vol ** 2
    
    # Kappa (mean reversion): Hard to estimate simply, use default
    kappa = 2.0
    
    # Vol of Vol (sigma): Hard to estimate, use default
    sigma = 0.5
    
    # Rho (correlation): Correlation between returns and variance changes?
    # Proxy: Correlation between returns and squared returns (leverage effect)
    # Or just default -0.5 for crypto (inverse correlation usually)
    rho = -0.5
    
    current_price = df["price"].iloc[-1]
    
    return {
        "parameters": {
            "v0": v0,
            "theta": theta,
            "kappa": kappa,
            "sigma": sigma,
            "rho": rho
        },
        "current_price": current_price
    }

# Pricer Agent
def pricer_agent(state):
    """
    Runs the Heston simulation.
    """
    params = state["parameters"]
    S0 = state["current_price"]
    T = state["target_date_days"] / 365.0 # Convert days to years
    r = fetch_risk_free_rate()
    strike = state["strike_price"]
    option_type = state.get("option_type", "call")
    
    results = calculate_greeks(
        S0=S0,
        v0=params["v0"],
        rho=params["rho"],
        kappa=params["kappa"],
        theta=params["theta"],
        sigma=params["sigma"],
        T=T,
        r=r,
        strike=strike,
        option_type=option_type
    )
    
    return {"results": results}

# Teacher Agent
def teacher_agent(state):
    """
    Explains the Greeks using an LLM.
    """
    results = state["results"]
    coin_id = state["coin_id"]
    
    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        return {"explanation": "OpenAI API Key not found. Here are the raw Greeks:\n" + str(results)}
        
    try:
        llm = ChatOpenAI(model="gpt-3.5-turbo", api_key=api_key)
        
        prompt = ChatPromptTemplate.from_template("""
        You are a helpful crypto options teacher.
        Explain the following option Greeks for a {coin_id} option to a beginner.
        
        Data:
        Price: ${price:.2f}
        Delta: {delta:.4f}
        Gamma: {gamma:.4f}
        Theta: {theta:.4f}
        
        Explain what each means in practical terms (e.g., "If Bitcoin goes up $1...").
        Keep it concise and fun.
        """)
        
        chain = prompt | llm
        
        response = chain.invoke({
            "coin_id": coin_id,
            "price": results["price"],
            "delta": results["delta"],
            "gamma": results["gamma"],
            "theta": results["theta"]
        })
        
        return {"explanation": response.content}
        
    except Exception as e:
        return {"explanation": f"Error generating explanation: {e}. Raw results: {results}"}
