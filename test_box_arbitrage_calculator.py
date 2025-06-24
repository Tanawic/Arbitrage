import pytest
from arbitrage_logic import calculate_box_spread_arbitrage
import math

@pytest.fixture
def common_test_data():
    """Fixture to provide common test data for arbitrage calculations."""
    return {
        "btc_usd_price": 70000.0,
        "transaction_fee_rate": 0.0003 # 0.03%
    }

# --- Test Cases for Box Spread Arbitrage ---

def test_box_spread_positive_profit(common_test_data: dict[str, float]):
    """
    Tests a scenario where a Box Spread should yield a clear positive arbitrage profit.
    """
    k1 = 60000
    k2 = 61000
    leg_data = [
        {'ask_price': 0.0050, 'bid_price': 0.0049},  # Long Call K1: Buy at Ask
        {'ask_price': 0.0021, 'bid_price': 0.0020},  # Short Put K1: Sell at Bid
        {'ask_price': 0.0011, 'bid_price': 0.0010},  # Short Call K2: Sell at Bid
        {'ask_price': 0.0041, 'bid_price': 0.0040}   # Long Put K2: Buy at Ask
    ]

    # Manual calculation for expected profit (for verification)
    # Costs: (0.0050 + 0.0041) * 70000 = 0.0091 * 70000 = 637 USD
    # Revenues: (0.0020 + 0.0010) * 70000 = 0.0030 * 70000 = 210 USD
    # Net Premium (initial cash flow) = Costs - Revenues = 637 - 210 = 427 USD (This is a net debit/cost)
    # Theoretical Value = K2 - K1 = 61000 - 60000 = 1000 USD
    # Total premiums for fees: (0.0050 + 0.0020 + 0.0010 + 0.0041) * 70000 = 0.0121 * 70000 = 847 USD
    # Transaction Fees = 847 * 0.0003 = 0.2541 USD
    # Arbitrage Profit = Theoretical Value - Net Premium - Fees = 1000 - 427 - 0.2541 = 572.7459 USD

    expected_profit = 572.7459

    actual_profit = calculate_box_spread_arbitrage(
        k1, k2, leg_data, common_test_data['btc_usd_price'], common_test_data['transaction_fee_rate']
    )
    assert actual_profit == pytest.approx(expected_profit, abs=1e-5) # Using higher precision for floats

def test_box_spread_negative_profit(common_test_data: dict[str, float]):
    """
    Tests a scenario where a Box Spread should yield a negative arbitrage profit (no opportunity).
    """
    k1 = 60000
    k2 = 61000
    # Adjust prices to create a guaranteed loss (e.g., wider bid-ask spreads, unfavorable prices)
    leg_data = [
        {'ask_price': 0.0055, 'bid_price': 0.0054},  # Long Call K1: Higher Ask
        {'ask_price': 0.0015, 'bid_price': 0.0014},  # Short Put K1: Lower Bid
        {'ask_price': 0.0008, 'bid_price': 0.0007},  # Short Call K2: Lower Bid
        {'ask_price': 0.0048, 'bid_price': 0.0047}   # Long Put K2: Higher Ask
    ]
    actual_profit = calculate_box_spread_arbitrage(
        k1, k2, leg_data, common_test_data['btc_usd_price'], common_test_data['transaction_fee_rate']
    )
    assert actual_profit < 0

def test_box_spread_missing_price_data(common_test_data: dict[str, float]):
    """
    Tests that calculate_box_spread_arbitrage returns -infinity if required bid/ask prices are missing.
    """
    k1 = 60000
    k2 = 61000
    leg_data = [
        {'ask_price': 0.0050, 'bid_price': 0.0049},
        {'ask_price': 0.0021, 'bid_price': 0.0020},
        {'ask_price': 0.0011, 'bid_price': '*' }, # Missing bid_price for leg 2
        {'ask_price': 0.0041, 'bid_price': 0.0040}]
    actual_profit = calculate_box_spread_arbitrage(
        k1, k2, leg_data, common_test_data['btc_usd_price'], common_test_data['transaction_fee_rate']
    )
    assert actual_profit == -math.inf
