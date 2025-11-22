# Crypto Options Pricing & Greeks Explainer

A "Bloomberg Terminal" lite interface for simulating crypto option prices and understanding the "Greeks" (Delta, Gamma, Theta).

![Status](https://img.shields.io/badge/Status-Active-success)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)

## 🚀 Features

- **Heston Model Simulation**: Uses Monte Carlo simulation with stochastic volatility (more accurate for crypto than Black-Scholes).
- **Real-Time Data**: Fetches spot prices from CoinGecko and risk-free rates (yields) from DefiLlama.
- **AI Teacher**: Uses LangChain + OpenAI to explain complex option Greeks in plain English.
- **Interactive UI**: Built with Dash & Plotly for a professional financial terminal look.

## 🛠️ Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Soham-1827/Crypto-Options-Pricing-Greeks-Explainer.git
    cd Crypto-Options-Pricing-Greeks-Explainer
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up Environment Variables:**
    Create a `.env` file in the root directory and add your OpenAI API Key (required for the "Teacher" agent):
    ```ini
    OPENAI_API_KEY=sk-your-api-key-here
    ```
    *(See `.env.example` for reference)*

## 🖥️ Usage

Run the application locally:

```bash
python app.py
```

Open your browser and navigate to `http://127.0.0.1:8050/`.

### How to use:
1.  **Select Asset**: Enter a CoinGecko ID (e.g., `bitcoin`, `ethereum`, `solana`).
2.  **Set Parameters**: Adjust the target date, strike price, and option type (Call/Put).
3.  **Run Simulation**: Click the button to run the Monte Carlo simulation.
4.  **Analyze**:
    - View the calculated **Fair Price** and **Greeks**.
    - Read the **AI Explanation** of what these numbers mean for your trade.
    - Visualize the **Payoff Diagram**.

## 🧪 Testing

Run the unit tests to verify the simulation logic and API connectivity:

```bash
# Run simulation logic tests
python -m unittest tests/test_simulation.py

# Run API connectivity tests (requires internet)
python -m unittest tests/test_api.py
```

## ☁️ Deployment (Hugging Face Spaces)

This project is ready for deployment on Hugging Face Spaces.

1.  Create a new Space (Select **Dash** as the SDK).
2.  Upload the files from this repository.
3.  Go to **Settings** > **Variables** and add `OPENAI_API_KEY`.

## ⚠️ Disclaimer

**This tool is for educational purposes only.** The prices generated are simulations based on mathematical models and do not represent guaranteed market prices. Crypto options are high-risk instruments.
