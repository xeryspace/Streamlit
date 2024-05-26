import streamlit as st
import pandas as pd
import random


def calc_positions(portfolio_size, risk_level, entry_prices, stop_loss, entry_proportions, take_profits,
                   liquidation_buffer, additional_risk, is_long):
    if additional_risk > 0:
        temp_portfolio_size = portfolio_size - additional_risk
        risk_amount = (temp_portfolio_size * (risk_level / 100))
        total_risk = risk_amount + additional_risk
    else:
        risk_amount = (portfolio_size * (risk_level / 100))
        total_risk = risk_amount

    risk_per_entry = [total_risk * prop for prop in entry_proportions]

    if is_long:
        positions = [risk / ((price - stop_loss) / price) for price, risk in zip(entry_prices, risk_per_entry)]
    else:
        positions = [risk / ((stop_loss - price) / price) for price, risk in zip(entry_prices, risk_per_entry)]

    profits = []
    for i in range(len(entry_prices)):
        total_invested = sum(positions[:i + 1])
        avg_buy_price = sum(entry_prices[:i + 1]) / (i + 1)
        total_coins = total_invested / avg_buy_price

        entry_profits = []
        remaining_coins = total_coins
        for tp in take_profits:
            if tp != take_profits[-1]:
                coins_to_trim = remaining_coins * 0.25
                if is_long:
                    trim_profit = coins_to_trim * (tp - avg_buy_price)
                else:
                    trim_profit = coins_to_trim * (avg_buy_price - tp)
                remaining_coins -= coins_to_trim
            else:
                if is_long:
                    trim_profit = remaining_coins * (tp - avg_buy_price)
                else:
                    trim_profit = remaining_coins * (avg_buy_price - tp)
            entry_profits.append((trim_profit, coins_to_trim if tp != take_profits[-1] else remaining_coins))
        profits.append(entry_profits)

    full_profit = profits[-1][-1][0]
    full_loss = total_risk
    if is_long:
        liquidation_price = stop_loss * (1 - liquidation_buffer / 100)
    else:
        liquidation_price = stop_loss * (1 + liquidation_buffer / 100)
    return positions, profits, full_profit, full_loss, liquidation_price


def print_results(entry_prices, positions, profits, full_profit, full_loss, liquidation_price, take_profits,
                  portfolio_size):
    st.subheader("Results")

    tp_headers = [""] + [f"TP {i + 1}: {tp:.4f}" for i, tp in enumerate(take_profits)]
    table_data = []

    for i in range(len(entry_prices)):
        row = [f"Entry {i + 1} ({entry_prices[i]:.2f}) - Position: {positions[i]:.2f}"]
        row.extend([f"{profit:.4f}" for profit, coins in profits[i]])
        table_data.append(row)

    df = pd.DataFrame(table_data, columns=tp_headers)
    st.table(df)

    st.markdown("---")  # Add a horizontal line

    # Use markdown for the results
    for i in range(len(entry_prices)):
        portfolio_after_tp = portfolio_size + profits[i][-1][0]
        st.markdown(f"- **Portfolio after E{i + 1} -> Full TP:** {portfolio_after_tp:.2f}")

    st.markdown(f"- **Full Loss:** {full_loss:.2f}")
    st.markdown(f"- **Portfolio after Loss:** {portfolio_size - full_loss:.2f}")


def main():
    st.set_page_config(page_title="Position Calculator", page_icon=":calculator:", layout="centered")
    st.title("Position Calculator")

    user = st.radio("Select User", ("Igor", "Erik"))
    is_long = st.radio("Position Type", ("Long", "Short")) == "Long"

    if user == "Igor":
        default_portfolio_size = 300.0
    else:
        default_portfolio_size = 100.0

    with st.expander("Input Parameters", expanded=True):
        portfolio_size = st.number_input("Portfolio Size", value=default_portfolio_size)
        risk_level = st.number_input("Risk Level", value=3.0)
        additional_risk = st.number_input("Additional Risk ($)", value=0.0)
        entry_prices = st.text_input("Entry Prices (comma-separated)")
        stop_loss = st.number_input("Stop Loss", step=0.0000001, format="%0.7f")
        take_profits = st.text_input("Take Profits (comma-separated)")
        liquidation_buffer = 1

    if st.button("Calculate"):
        if entry_prices and stop_loss and take_profits:
            entry_prices = [float(x.strip()) for x in entry_prices.split(",")]
            take_profits = [float(x.strip()) for x in take_profits.split(",")]
            num_entries = len(entry_prices)
            entry_proportions = [1 / num_entries] * num_entries
            positions, profits, full_profit, full_loss, liquidation_price = calc_positions(
                portfolio_size, risk_level, entry_prices, stop_loss, entry_proportions, take_profits,
                liquidation_buffer, additional_risk, is_long
            )
            print_results(entry_prices, positions, profits, full_profit, full_loss, liquidation_price, take_profits,
                          portfolio_size)
        else:
            st.warning("Please fill in all the required fields.")


if __name__ == "__main__":
    main()