import streamlit as st
import random

def calc_positions(portfolio_size, risk_level, entry_prices, stop_loss, entry_proportions, take_profits, liquidation_buffer):
    risk_amount = portfolio_size * (risk_level / 100)
    risk_per_entry = [risk_amount * prop for prop in entry_proportions]
    positions = [risk / ((price - stop_loss) / price) for price, risk in zip(entry_prices, risk_per_entry)]
    avg_prices = [sum(price * pos for price, pos in zip(entry_prices[:i + 1], positions[:i + 1])) / sum(positions[:i + 1])
                  for i in range(len(entry_prices))]
    profits = [sum(positions[:i + 1]) * (
            take_profits[-1] - sum(price * pos for price, pos in zip(entry_prices[:i + 1], positions[:i + 1])) / sum(
        positions[:i + 1])) / (
                       sum(price * pos for price, pos in zip(entry_prices[:i + 1], positions[:i + 1])) / sum(
                   positions[:i + 1])) for i in range(len(entry_prices))]
    cumulative_shares = [sum(positions[:i + 1]) / avg_prices[i] for i in range(len(entry_prices))]
    full_profit, full_loss = profits[-1], portfolio_size * (risk_level / 100)
    liquidation_price = stop_loss * (1 - liquidation_buffer / 100)
    return positions, avg_prices, profits, full_profit, full_loss, liquidation_price, cumulative_shares

def print_results(entry_prices, positions, avg_prices, cumulative_shares, original_entry_prices=None):
    st.subheader("Results")
    total_position_size = 0
    for i, (price, pos, avg_price, shares) in enumerate(zip(entry_prices, positions, avg_prices, cumulative_shares), start=1):
        total_position_size += pos
        st.write(f"""
        <div style='background-color: #e0e0e0; padding: 10px; border-radius: 5px; margin-bottom: 10px;'>
        <strong style='font-size: 35px;'>Entry {i}</strong><br>
        <span style='font-size: 25px;'>E{i} Limitorder at: {str(price).rstrip('0').rstrip('.')} $</span><br>
        <span style='font-size: 25px;'>E{i} Positionsize: {pos:.2f}$</span><br>
        <span style='font-size: 25px;'>E{i} Avg Price: {avg_price:.5f} $</span><br>
        <span style='font-size: 25px;'>Total Shares: {shares:.5f}</span><br>
        <span style='font-size: 25px;'>Total Positionsize so far: {total_position_size:.2f}$</span>
        </div>
        """, unsafe_allow_html=True)

def calc_take_profits(entry_prices, positions, take_profits, cumulative_shares):
    st.subheader("Take Profits")
    total_shares = cumulative_shares[-1]
    remaining_shares = total_shares
    for i, tp in enumerate(take_profits, start=1):
        if i == 1:
            sell_shares = total_shares * 0.25
        elif i == 2:
            sell_shares = total_shares * 0.75
        else:
            sell_shares = remaining_shares

        profit = sell_shares * (tp - entry_prices[-1])
        remaining_shares -= sell_shares
        st.write(f"""
        <div style='background-color: #d0ffd0; padding: 10px; border-radius: 5px; margin-bottom: 10px;'>
        <strong>TP {i}</strong><br>
        Take Profit at: {str(tp).rstrip('0').rstrip('.')} $<br>
        Sell Shares: {sell_shares:.5f}<br>
        Profit: {profit:.2f} $<br>
        Remaining Shares: {remaining_shares:.5f}
        </div>
        """, unsafe_allow_html=True)

def main():
    st.set_page_config(page_title="Position Calculator", page_icon=":calculator:", layout="centered")
    st.title("Position Calculator")

    user = st.radio("Select Mode", ("Spot", "Leverage"))

    if user == "Spot":
        default_portfolio_size = 40000.0
        base_risk_level = 0.75
    else:
        default_portfolio_size = 5000.0
        base_risk_level = 2.0

    add_entries = st.checkbox("Add entries between provided ones", value=False)

    with st.expander("Input Parameters", expanded=True):
        portfolio_size = st.number_input("Current Portfolio Size", value=default_portfolio_size)
        previous_win_profit = st.number_input("Previous Winning Trade Profit (Optional)", value=0.0)
        entry_prices = st.text_input("Entry Prices (comma-separated)")
        stop_loss = st.number_input("Stop Loss", step=0.0000001, format="%0.7f")
        take_profit = st.text_input("Take Profits (comma-separated)", value="")
        liquidation_buffer = 1

    if st.button("Calculate"):
        if entry_prices and stop_loss and take_profit:
            original_entry_prices = [float(x.strip()) for x in entry_prices.split(",")]
            take_profits = [float(x.strip()) for x in take_profit.split(",")]

            if add_entries:
                entry_prices = []
                for i in range(len(original_entry_prices) - 1):
                    entry_prices.append(original_entry_prices[i])
                    price_diff = (original_entry_prices[i + 1] - original_entry_prices[i]) / 5
                    for j in range(1, 5):
                        entry_prices.append(original_entry_prices[i] + price_diff * j)
                entry_prices.append(original_entry_prices[-1])
            else:
                entry_prices = original_entry_prices

            # Calculate the risk tolerance based on the current portfolio value and previous winning trade's profit
            if previous_win_profit > 0:
                old_portfolio_size = portfolio_size - previous_win_profit
            else:
                old_portfolio_size = portfolio_size

            og_risk_value = old_portfolio_size * (1 - base_risk_level / 100)
            risk_tolerance = (portfolio_size - og_risk_value) / portfolio_size * 100

            num_entries = len(entry_prices)
            entry_proportions = [1/num_entries] * num_entries
            positions, avg_prices, profits, full_profit, full_loss, liquidation_price, cumulative_shares = calc_positions(
                portfolio_size, risk_tolerance, entry_prices, stop_loss, entry_proportions, take_profits, liquidation_buffer
            )
            print_results(entry_prices, positions, avg_prices, cumulative_shares, original_entry_prices)

        else:
            st.warning("Please fill in all the required fields.")

if __name__ == "__main__":
    main()
