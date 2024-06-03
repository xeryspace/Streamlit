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
    entries = []
    stats = []

    for i, (price, pos, avg_price, shares) in enumerate(zip(entry_prices, positions, avg_prices, cumulative_shares),
                                                        start=1):
        total_position_size += pos
        entry_html = f"""
        <div>
        <strong style='font-size: 35px;'>Entry {i} Bids</strong><br>
        <span style='font-size: 25px;'>Order at: {str(price).rstrip('0').rstrip('.')} $</span><br>
        <span style='font-size: 25px;'>Amount: {pos:.2f}$</span>
        <span></span><br> 
        <span></span><br> 
        </div>
        """
        entries.append(entry_html)

        stats_html = f"""
        <div>
        <strong style='font-size: 35px;'>Stats after Entry {i} ({str(price).rstrip('0').rstrip('.')} $)</strong><br>
        <span style='font-size: 25px;'>Avg Price: {avg_price:.5f} $</span><br>
        <span style='font-size: 25px;'>Total Shares: {shares:.5f}</span><br>
        <span style='font-size: 25px;'>Total Amount so far: {total_position_size:.2f}$</span>
        <span></span><br> 
        <span></span><br> 
        </div>
        """
        stats.append(stats_html)

    # Print all the entries in a single div
    entries_html = "".join(entries)
    entries_container = f"""
        <div style='background-color: #e2f0f1; padding: 10px; border-radius: 5px; margin-bottom: 15px;'>
        {entries_html}
        </div>
        """
    st.markdown(entries_container, unsafe_allow_html=True)

    divider_container = f"""
            <div>
            -----------------------------
            <span></span><br> 
            <span></span><br> 
            </div>
            """
    st.markdown(divider_container, unsafe_allow_html=True)

    # Wrap all the stats in a single div with background color
    stats_html = "".join(stats)
    stats_container = f"""
        <div style='background-color: #e2f0f1; padding: 10px; border-radius: 5px; margin-bottom: 15px;'>

        {stats_html}
        </div>
        """
    st.markdown(stats_container, unsafe_allow_html=True)

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
        default_portfolio_size = 38000.0
        base_risk_level = 1
    else:
        default_portfolio_size = 5000.0
        base_risk_level = 2.0

    add_entries = st.checkbox("Add entries between provided ones", value=False)
    evenly_distributed_entries = st.checkbox("Evenly distributed entries", value=False)

    with st.expander("Input Parameters", expanded=True):
        portfolio_size = st.number_input("Current Portfolio Size", value=default_portfolio_size)
        base_risk_level = st.number_input("Base Risk", value=base_risk_level)
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
                    price_diff = (original_entry_prices[i + 1] - original_entry_prices[i]) / 2
                    entry_prices.append(original_entry_prices[i] + price_diff)
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
            if evenly_distributed_entries:
                entry_proportions = [1/num_entries] * num_entries
            else:
                if num_entries == 2:
                    entry_proportions = [0.35, 0.65]
                elif num_entries == 3:
                    entry_proportions = [0.15, 0.35, 0.50]
                elif num_entries == 4:
                    entry_proportions = [0.10, 0.15, 0.25, 0.50]
                elif num_entries == 5:
                    entry_proportions = [0.05, 0.10, 0.15, 0.25, 0.45]
                elif num_entries == 6:
                    entry_proportions = [0.05, 0.08, 0.12, 0.15, 0.25, 0.35]
                elif num_entries == 7:
                    entry_proportions = [0.03, 0.05, 0.07, 0.10, 0.15, 0.25, 0.35]
                elif num_entries == 8:
                    entry_proportions = [0.02, 0.03, 0.05, 0.07, 0.10, 0.15, 0.25, 0.33]
                elif num_entries == 9:
                    entry_proportions = [0.02, 0.03, 0.05, 0.07, 0.08, 0.10, 0.15, 0.20, 0.30]
                elif num_entries == 10:
                    entry_proportions = [0.02, 0.03, 0.05, 0.06, 0.07, 0.08, 0.09, 0.15, 0.20, 0.25]
                elif num_entries == 11:
                    entry_proportions = [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.14, 0.20, 0.30]
                elif num_entries == 12:
                    entry_proportions = [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.15, 0.20, 0.20]
                else:
                    st.warning(
                        f"This script currently supports up to 12 entries for non-even distribution. You provided {num_entries} entries.")
                    return

            positions, avg_prices, profits, full_profit, full_loss, liquidation_price, cumulative_shares = calc_positions(
                portfolio_size, risk_tolerance, entry_prices, stop_loss, entry_proportions, take_profits, liquidation_buffer
            )
            print_results(entry_prices, positions, avg_prices, cumulative_shares, original_entry_prices)

        else:
            st.warning("Please fill in all the required fields.")

if __name__ == "__main__":
    main()
