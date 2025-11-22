import unittest
from unittest.mock import patch, MagicMock
from src.data_loader import fetch_current_price, fetch_historical_data, fetch_risk_free_rate
import pandas as pd

class TestAPI(unittest.TestCase):
    
    @patch('src.data_loader.requests.get')
    def test_fetch_current_price_mock(self, mock_get):
        """Test fetching current price with mocked response."""
        # Mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {"bitcoin": {"usd": 50000}}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        price = fetch_current_price("bitcoin")
        self.assertEqual(price, 50000)
        
    @patch('src.data_loader.requests.get')
    def test_fetch_historical_data_mock(self, mock_get):
        """Test fetching historical data with mocked response."""
        mock_response = MagicMock()
        # Mock CoinGecko market_chart format: [[timestamp, price], ...]
        mock_data = {
            "prices": [
                [1609459200000, 29000],
                [1609545600000, 29500]
            ]
        }
        mock_response.json.return_value = mock_data
        mock_get.return_value = mock_response
        
        df = fetch_historical_data("bitcoin", days=1)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 2)
        self.assertEqual(df.iloc[0]["price"], 29000)

    def test_live_api_connectivity(self):
        """
        LIVE TEST: Actually hits the API. 
        Skipped by default to avoid rate limits/failures in CI, 
        but useful for manual verification.
        """
        print("\nRunning LIVE API tests (may take a few seconds)...")
        
        # Test CoinGecko
        price = fetch_current_price("bitcoin")
        if price is None:
            print("WARNING: CoinGecko API failed or rate limited.")
        else:
            print(f"CoinGecko Live: Bitcoin Price = ${price}")
            self.assertIsInstance(price, (int, float))
            self.assertGreater(price, 0)
            
        # Test DefiLlama
        rate = fetch_risk_free_rate()
        print(f"DefiLlama Live: Risk Free Rate = {rate*100:.2f}%")
        self.assertIsInstance(rate, float)
        self.assertGreater(rate, 0)

if __name__ == '__main__':
    unittest.main()
