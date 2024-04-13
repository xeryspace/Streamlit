import streamlit as st
import plotly.graph_objects as go

def calc_positions(portfolio_size,  risk_level, entry_prices, stop_loss, entry_proportions, take_profit,
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


def print_results(entry_prices, positions, profits, full_profit, full_loss, liquidation_price):
    st.subheader("Results")
    for i, (price, pos, profit) in enumerate(zip(entry_prices, positions, profits), start=1):
        st.write(f"<div style='background-color: #f0f0f0; padding: 10px; border-radius: 5px; margin-bottom: 10px;'>"
                 f"<strong>Entry {i}:</strong> {price:.10f} -> Position: {pos:.2f}"
                 f"</div>", unsafe_allow_html=True)

    st.write(f"- Full Profit: {full_profit:.2f}")
    st.write(f"- Full Loss: {full_loss:.2f}")
    st.write(f"- <span style='color: red;'><strong>Max Liquidation Price!!:</strong> {liquidation_price:.10f}</span>",
             unsafe_allow_html=True)

def visualize_gains(entry_prices, profits, portfolio_size, full_profit, full_loss):
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
            go.Bar(x=['Win'], y=[win_all], text=[f"{win_all:.2f}"], textposition='auto',marker_color='green'),
            go.Bar(x=['Lose'], y=[lose_portfolio], text=[f"{lose_portfolio:.2f}"], textposition='auto',marker_color='red')
        ])
    elif len(profits) == 2:
        win_e1 = portfolio_size + profits[0]
        win_all = portfolio_size + full_profit
        lose_portfolio = portfolio_size - full_loss

        fig = go.Figure(data=[
            go.Bar(x=['Win (E1)'], y=[win_e1], text=[f"{win_e1:.2f}"], textposition='auto', marker_color='green'),
            go.Bar(x=['Win (All Entries)'], y=[win_all], text=[f"{win_all:.2f}"], textposition='auto',marker_color='green'),
            go.Bar(x=['Lose'], y=[lose_portfolio], text=[f"{lose_portfolio:.2f}"], textposition='auto',marker_color='red')
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

    fig.update_layout(title='Portfolio Size',
                      xaxis_title='Scenario',
                      yaxis_title='Portfolio Value',
                      showlegend=False)

    st.plotly_chart(fig)

def main():
    st.set_page_config(page_title="Position Calculator", page_icon=":calculator:", layout="centered")
    st.title("Position Calculator")

    user = st.radio("Select User", ("Igor", "Erik"))

    if user == "Igor":
        default_portfolio_size = 700.0
    else:
        default_portfolio_size = 100.0

    with st.expander("Input Parameters", expanded=True):
        portfolio_size = st.number_input("Portfolio Size", value=default_portfolio_size)
        risk_level = st.number_input("Risk Level", value=3.0)
        entry_prices = st.text_input("Entry Prices (comma-separated)")
        stop_loss = st.number_input("Stop Loss", step=0.0000001, format="%0.7f")
        take_profit = st.number_input("Take Profit", step=0.0000001, format="%0.7f")
        liquidation_buffer = st.number_input("Liquidation Buffer", value=10.0)

        num_entries = st.selectbox("Number of Entries", options=[1, 2, 3])
        if num_entries == 1:
            entry_proportions = [1]
        elif num_entries == 2:
            entry_proportions = [0.5, 0.5]
        else:
            proportion_option = st.selectbox("Entry Proportion Option", options=["1/3 Split", "Rising DCA"])
            if proportion_option == "1/3 Split":
                entry_proportions = [0.33, 0.33, 0.34]
            else:
                entry_proportions = [0.15, 0.35, 0.5]

    if st.button("Calculate"):
        if entry_prices and stop_loss and take_profit:
            entry_prices = [float(x.strip()) for x in entry_prices.split(",")]
            positions, profits, full_profit, full_loss, liquidation_price = calc_positions(
                portfolio_size, risk_level, entry_prices, stop_loss, entry_proportions, take_profit, liquidation_buffer
            )
            print_results(entry_prices, positions, profits, full_profit, full_loss, liquidation_price)
            visualize_gains(entry_prices, profits, portfolio_size, full_profit, full_loss)  # Add this line
        else:
            st.warning("Please fill in all the required fields.")


if __name__ == "__main__":
    main()
