import math

def calculate_box_spread_arbitrage(k1: int, k2: int, leg_data: list[dict], btc_usd_price: float, transaction_fee_rate: float) -> float:
    """
    Calculates the arbitrage profit for a Box Spread using executable (Bid/Ask) prices.

    A Box Spread consists of four legs:
    - Long Call at K1 (Buy at Ask Price)
    - Short Put at K1 (Sell at Bid Price)
    - Short Call at K2 (Sell at Bid Price)
    - Long Put at K2 (Buy at Ask Price)

    Args:
        k1 (int): The lower strike price.
        k2 (int): The higher strike price.
        leg_data (list[dict]): A list of dictionaries, where each dictionary contains
                               'ask_price' and 'bid_price' for each of the four legs,
                               in the order: [LongCallK1, ShortPutK1, ShortCallK2, LongPutK2].
        btc_usd_price (float): The current conversion rate from BTC to USD.
        transaction_fee_rate (float): The transaction fee rate as a decimal (e.g., 0.0003 for 0.03%).

    Returns:
        float: The calculated arbitrage profit in USD. Returns -infinity if required
               bid/ask prices are missing for any leg.
    """
    # Ensure all required prices are available for each leg
    for i, leg in enumerate(leg_data):
        if leg.get('ask_price') is None or leg.get('bid_price') is None:
            # print(f"Warning: Missing bid/ask price in leg_data for Box Spread at index {i}.")
            return -math.inf # Indicate invalid data

    # Convert premiums from BTC to USD using appropriate bid/ask prices for each trade
    # Leg 0: Buy Call K1 - Cost is its Ask Price
    leg0_cost_usd = leg_data[0]['ask_price'] * btc_usd_price

    # Leg 1: Sell Put K1 - Revenue is its Bid Price
    leg1_revenue_usd = leg_data[1]['bid_price'] * btc_usd_price

    # Leg 2: Sell Call K2 - Revenue is its Bid Price
    leg2_revenue_usd = leg_data[2]['bid_price'] * btc_usd_price

    # Leg 3: Buy Put K2 - Cost is its Ask Price
    leg3_cost_usd = leg_data[3]['ask_price'] * btc_usd_price

    # Calculate Net Premium (initial cash flow for the strategy)
    # Net Premium = (Cost of Long Call K1 + Cost of Long Put K2) - (Revenue from Short Put K1 + Revenue from Short Call K2)
    net_premium_usd = (leg0_cost_usd + leg3_cost_usd) - (leg1_revenue_usd + leg2_revenue_usd)

    # Theoretical Value at Expiry: For a Box Spread, it's always the difference between the strikes (K2 - K1)
    theoretical_value_usd = k2 - k1

    # Calculate Total Transaction Fees
    # Fees are typically based on the total value of all executed trades.
    # We sum the prices at which each leg is traded.
    total_premiums_for_fees = leg0_cost_usd + leg1_revenue_usd + leg2_revenue_usd + leg3_cost_usd
    transaction_fees_usd = total_premiums_for_fees * transaction_fee_rate

    # Calculate Arbitrage Profit (Net Profit after all costs)
    arbitrage_profit_usd = theoretical_value_usd - net_premium_usd - transaction_fees_usd
    return arbitrage_profit_usd

def calculate_calendar_spread_arbitrage(option_type: str, strike: int, shorter_leg_data: dict, longer_leg_data: dict, btc_usd_price: float, transaction_fee_rate: float) -> float:
    """
    Calculates the arbitrage profit for a Calendar Spread using executable (Bid/Ask) prices.

    A Calendar Spread (or Time Spread) consists of two options of the same type (Call/Put)
    and strike price, but different expiry dates.
    - Short the shorter expiry option (Sell at Bid Price)
    - Long the longer expiry option (Buy at Ask Price)

    Args:
        option_type (str): The type of option ('CALL' or 'PUT').
        strike (int): The strike price for both options.
        shorter_leg_data (dict): Dictionary containing 'bid_price' and 'ask_price' for the shorter expiry leg.
        longer_leg_data (dict): Dictionary containing 'bid_price' and 'ask_price' for the longer expiry leg.
        btc_usd_price (float): The current conversion rate from BTC to USD.
        transaction_fee_rate (float): The transaction fee rate as a decimal (e.0.0003 for 0.03%).

    Returns:
        float: The calculated arbitrage profit (net credit received) in USD.
               Returns -infinity if required bid/ask prices are missing for any leg.
    """
    # Ensure both legs have required bid/ask prices
    if shorter_leg_data.get('bid_price') is None or shorter_leg_data.get('ask_price') is None or \
       longer_leg_data.get('bid_price') is None or longer_leg_data.get('ask_price') is None:
        # print("Warning: Missing bid/ask price in leg_data for Calendar Spread calculation.")
        return -math.inf # Indicate invalid data

    # Transaction prices:
    # Shorter Leg (Sell) - Revenue is its Bid Price
    shorter_leg_revenue_usd = shorter_leg_data['bid_price'] * btc_usd_price

    # Longer Leg (Buy) - Cost is its Ask Price
    longer_leg_cost_usd = longer_leg_data['ask_price'] * btc_usd_price

    # Premium Difference (Net Credit/Debit): Sell Shorter, Buy Longer
    # For a calendar spread, profit is typically measured as the initial net credit
    # received after entering the position, minus transaction fees.
    premium_diff_usd = shorter_leg_revenue_usd - longer_leg_cost_usd

    # Calculate Total Transaction Fees
    # Fees are based on the total value of premiums involved in the trade.
    total_premiums_for_fees = shorter_leg_revenue_usd + longer_leg_cost_usd
    transaction_fees_usd = total_premiums_for_fees * transaction_fee_rate

    # Arbitrage Profit (Net Credit after fees)
    arbitrage_profit_usd = premium_diff_usd - transaction_fees_usd
    return arbitrage_profit_usd
