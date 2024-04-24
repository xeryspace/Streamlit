import streamlit as st
import plotly.graph_objects as go
import random

def calc_positions(portfolio_size, risk_level, entry_prices, stop_loss, entry_proportions, take_profit,
                   liquidation_buffer):
    risk_amount = portfolio_size * (risk_level / 100)
    risk_per_entry = [risk_amount * prop for prop in entry_proportions]
    positions = [risk / ((price - stop_loss) / price) for price, risk in zip(entry_prices, risk_per_entry)]
    profits = [sum(positions[:i + 1]) * (
            take_profit - sum(price * pos for price, pos in zip(entry_prices[:i + 1], positions[:i + 1])) / sum(
        positions[:i + 1])) / (
                       sum(price * pos for price, pos in zip(entry_prices[:i + 1], positions[:i + 1])) / sum(
                   positions[:i + 1])) for i in range(len(entry_prices))]
    full_profit, full_loss = profits[-1], portfolio_size * (risk_level / 100)
    liquidation_price = stop_loss * (1 - liquidation_buffer / 100)
    return positions, profits, full_profit, full_loss, liquidation_price

def print_results(entry_prices, positions, profits, full_profit, full_loss, liquidation_price, original_entry_prices=None):
    st.subheader("Results")
    for i, (price, pos, profit) in enumerate(zip(entry_prices, positions, profits), start=1):
        if original_entry_prices and price in original_entry_prices:
            st.write(f"<div style='background-color: #f0f0f0; padding: 10px; border-radius: 5px; margin-bottom: 10px;'>"
                     f"<strong>Entry {i}:</strong> {price:.10f} -> Position: {pos:.2f}"
                     f"</div>", unsafe_allow_html=True)
        else:
            st.write(f"<div style='background-color: #e0e0e0; padding: 10px; border-radius: 5px; margin-bottom: 10px;'>"
                     f"<strong>Entry {i}:</strong> {price:.10f} -> Position: {pos:.2f}"
                     f"</div>", unsafe_allow_html=True)

    st.write(f"- Full Profit: {full_profit:.2f}")
    st.write(f"- Full Loss: {full_loss:.2f}")

def visualize_gains(entry_prices, profits, portfolio_size, full_profit, full_loss, original_entry_prices=None):
    scenarios = [f"Entry {i+1}" for i in range(len(entry_prices))]
    gains = [profit for profit in profits]

    fig = go.Figure(data=[go.Bar(x=scenarios, y=gains, text=[f"{gain:.2f}" for gain in gains], textposition='auto')])

    fig.update_layout(title='Gains by Entry Scenario',
                      xaxis_title='Scenario',
                      yaxis_title='Gain',
                      showlegend=False)

    st.plotly_chart(fig)

    if len(profits) == 1:
        win_all = portfolio_size + full_profit
        lose_portfolio = portfolio_size - full_loss
        fig = go.Figure(data=[
            go.Bar(x=['Win'], y=[win_all], text=[f"{win_all:.2f}"], textposition='auto', marker_color='green'),
            go.Bar(x=['Lose'], y=[lose_portfolio], text=[f"{lose_portfolio:.2f}"], textposition='auto', marker_color='red')
        ])
    elif len(profits) == 2:
        win_e1 = portfolio_size + profits[0]
        win_all = portfolio_size + full_profit
        lose_portfolio = portfolio_size - full_loss

        fig = go.Figure(data=[
            go.Bar(x=['Win (E1)'], y=[win_e1], text=[f"{win_e1:.2f}"], textposition='auto', marker_color='green'),
            go.Bar(x=['Win (All Entries)'], y=[win_all], text=[f"{win_all:.2f}"], textposition='auto', marker_color='green'),
            go.Bar(x=['Lose'], y=[lose_portfolio], text=[f"{lose_portfolio:.2f}"], textposition='auto', marker_color='red')
        ])
    else:
        win_e1 = portfolio_size + profits[0]
        win_e1_e2 = portfolio_size + profits[1]
        win_all = portfolio_size + full_profit
        lose_portfolio = portfolio_size - full_loss

        fig = go.Figure(data=[
            go.Bar(x=['Win (E1)'], y=[win_e1], text=[f"{win_e1:.2f}"], textposition='auto', marker_color='green'),
            go.Bar(x=['Win (E1+E2)'], y=[win_e1_e2], text=[f"{win_e1_e2:.2f}"], textposition='auto', marker_color='green'),
            go.Bar(x=['Win (All Entries)'], y=[win_all], text=[f"{win_all:.2f}"], textposition='auto', marker_color='green'),
            go.Bar(x=['Lose'], y=[lose_portfolio], text=[f"{lose_portfolio:.2f}"], textposition='auto', marker_color='red')
        ])

def calc_take_profit(entry_prices, stop_loss, risk_reward_ratio):
    avg_entry_price = sum(entry_prices) / len(entry_prices)
    risk = abs(avg_entry_price - stop_loss)
    take_profit = avg_entry_price + (risk * risk_reward_ratio)
    return take_profit

def simulate_trades(budget, winrate, risk, num_trades, rr_ratio):
    trades = []
    consecutive_wins = 0
    risk_amount = 0
    profit_amount = 0

    for _ in range(num_trades):
        if random.random() < winrate:
            if consecutive_wins == 0:
                risk_amount = budget * risk
                profit_amount = risk_amount * rr_ratio
                budget += profit_amount
                consecutive_wins = 1
            elif consecutive_wins == 1:
                total_risk = risk_amount + profit_amount
                profit_amount = total_risk * rr_ratio
                budget += profit_amount
                consecutive_wins = 2

            if consecutive_wins == 2:
                consecutive_wins = 0
                risk_amount = 0
                profit_amount = 0

            trades.append(budget)
        else:
            if consecutive_wins == 0:
                loss = budget * risk
            else:
                loss = risk_amount + profit_amount

            budget -= loss
            consecutive_wins = 0
            risk_amount = 0
            profit_amount = 0
            trades.append(budget)

    return trades

def main():
    st.set_page_config(page_title="Trading Tools", page_icon=":calculator:", layout="centered")
    st.title("Trading Tools")

    # Create a sidebar with a selectbox
    script_options = ["Position Calculator", "Risk-Reward Calculator", "Compounding Trade Simulator"]
    selected_script = st.sidebar.selectbox("Select a script", script_options)

    if selected_script == "Position Calculator":
        position_calculator()
    elif selected_script == "Risk-Reward Calculator":
        risk_reward_calculator()
    elif selected_script == "Compounding Trade Simulator":
        compounding_trade_simulator()

def position_calculator():
    st.subheader("Position Calculator")

    user = st.radio("Select User", ("Igor", "Erik"))

    if user == "Igor":
        default_portfolio_size = 500.0
    else:
        default_portfolio_size = 100.0

    add_entries = st.checkbox("Add entries between provided ones", value=True)

    with st.expander("Input Parameters", expanded=True):
        portfolio_size = st.number_input("Current Portfolio Size", value=default_portfolio_size)
        previous_win_profit = st.number_input("Previous Winning Trade Profit (Optional)", value=0.0)
        base_risk_level = st.number_input("Base Risk Level (%)", value=3.0)
        entry_prices = st.text_input("Entry Prices (comma-separated)")
        stop_loss = st.number_input("Stop Loss", step=0.0000001, format="%0.7f")
        risk_reward_ratio = st.slider("Risk-Reward Ratio", min_value=1.0, max_value=5.0, value=2.0, step=0.1)
        liquidation_buffer = 1

    if st.button("Calculate"):
        if entry_prices and stop_loss:
            original_entry_prices = [float(x.strip()) for x in entry_prices.split(",")]

            if add_entries:
                entry_prices = []
                for i in range(len(original_entry_prices) - 1):
                    entry_prices.append(original_entry_prices[i])
                    price_diff = (original_entry_prices[i + 1] - original_entry_prices[i]) / 5
                    for j in range(1, 3):
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

            take_profit = calc_take_profit(entry_prices, stop_loss, risk_reward_ratio)

            num_entries = len(entry_prices)
            entry_proportions = [1/num_entries] * num_entries
            positions, profits, full_profit, full_loss, liquidation_price = calc_positions(
                portfolio_size, risk_tolerance, entry_prices, stop_loss, entry_proportions, take_profit, liquidation_buffer
            )
            print_results(entry_prices, positions, profits, full_profit, full_loss, liquidation_price, original_entry_prices)
            visualize_gains(entry_prices, profits, portfolio_size, full_profit, full_loss, original_entry_prices)

            # Display the calculated take profit price
            st.write(f"<strong>Take Profit:</strong> {take_profit:.10f}", unsafe_allow_html=True)

            # Display the summary for Tradingview
            st.subheader("Summary for Tradingview")
            for i, price in enumerate(entry_prices, start=1):
                st.write(f"Entry {i}: {price:.10f}")
            st.write(f"Stop Loss: {stop_loss:.10f}")
            st.write(f"Take Profit: {take_profit:.10f}")

        else:
            st.warning("Please fill in all the required fields.")

def risk_reward_calculator():
    st.subheader("Risk-Reward Calculator")

    with st.expander("Input Parameters", expanded=True):
        entry_price = st.number_input("Entry Price", value=100.0, step=0.0001)
        stop_loss = st.number_input("Stop Loss", value=98.0, step=0.0001)
        take_profit = st.number_input("Take Profit", value=105.0, step=0.0001)

    if st.button("Calculate Risk-Reward"):
        if entry_price and stop_loss and take_profit:
            risk = abs(entry_price - stop_loss)
            reward = abs(take_profit - entry_price)
            risk_reward_ratio = reward / risk

            st.write(f"<strong>Risk:</strong> {risk:.4f}", unsafe_allow_html=True)
            st.write(f"<strong>Reward:</strong> {reward:.4f}", unsafe_allow_html=True)
            st.write(f"<strong>Risk-Reward Ratio:</strong> {risk_reward_ratio:.2f}", unsafe_allow_html=True)
        else:
            st.warning("Please fill in all the required fields.")

def compounding_trade_simulator():
    st.subheader("Compounding Trade Strategy Simulator")

    budget = st.number_input("Portfolio Size", min_value=1, value=100, step=1)
    winrate = st.number_input("Winrate", min_value=0.0, max_value=1.0, value=0.6, step=0.01)
    risk = st.number_input("Risk", min_value=0.0, max_value=1.0, value=0.05, step=0.01)
    num_trades = st.number_input("Number of Trades", min_value=1, value=10, step=1)
    rr_ratio = st.number_input("Risk/Reward Ratio", min_value=0.1, value=2.0, step=0.1)

    if st.button("Simulate"):
        trades = simulate_trades(budget, winrate, risk, num_trades, rr_ratio)

        fig = go.Figure()
        fig.add_trace(go.Scatter(y=trades, mode='lines+markers', name='Portfolio Value'))
        fig.update_layout(title='Portfolio Value Over Trades', xaxis_title='Trade Number', yaxis_title='Portfolio Value')
        st.plotly_chart(fig)

        final_portfolio = trades[-1]
        st.subheader(f"Final Portfolio: {final_portfolio:.2f}")

if __name__ == "__main__":
    main()