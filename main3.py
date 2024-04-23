import streamlit as st

def calculate_position_size(portfolio, risk_tolerance, entry_price, stop_loss_percentage):
    risk_amount = portfolio * risk_tolerance
    position_size = risk_amount / (entry_price * stop_loss_percentage)
    return position_size

def calculate_trade_details(portfolio, risk_tolerance, rr_ratio, trade_type, last_profit, entry_price):
    if trade_type == "Normal":
        risk_amount = portfolio * risk_tolerance
    else:
        risk_amount = last_profit

    stop_loss_percentage = risk_tolerance
    take_profit_percentage = risk_tolerance * rr_ratio

    position_size = calculate_position_size(portfolio, risk_tolerance, entry_price, stop_loss_percentage)
    stop_loss_price = entry_price * (1 - stop_loss_percentage)
    take_profit_price = entry_price * (1 + take_profit_percentage)

    return position_size, stop_loss_price, take_profit_price

def main():
    st.title("Trade Calculator")

    portfolio = st.number_input("Portfolio Size", min_value=1, value=1000, step=1)
    rr_ratio = st.number_input("Risk/Reward Ratio", min_value=0.1, value=1.5, step=0.1)
    trade_type = st.radio("Trade Type", ("Normal", "Chained"))
    risk_tolerance = st.number_input("Risk Tolerance", min_value=0.01, max_value=1.0, value=0.02, step=0.01)
    entry_price = st.number_input("Entry Price", min_value=0.0001, value=100.0, step=0.0001)

    last_profit = 0
    if trade_type == "Chained":
        last_profit = st.number_input("Last Profit", min_value=0, value=0, step=1)

    if st.button("Calculate"):
        position_size, stop_loss, take_profit = calculate_trade_details(portfolio, risk_tolerance, rr_ratio, trade_type, last_profit, entry_price)

        st.subheader("Trade Details")
        st.write(f"Position Size: {position_size:.4f}")
        st.write(f"Stop Loss: {stop_loss:.4f}")
        st.write(f"Take Profit: {take_profit:.4f}")

        risk_amount = portfolio * risk_tolerance if trade_type == "Normal" else last_profit
        potential_loss = risk_amount
        potential_profit = risk_amount * rr_ratio

        st.subheader("Potential Outcomes")
        st.write(f"Potential Loss: {potential_loss:.2f}")
        st.write(f"Potential Profit: {potential_profit:.2f}")

if __name__ == "__main__":
    main()