import streamlit as st
import random
import plotly.graph_objects as go

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
    st.title("Compounding Trade Strategy Simulator")

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