import streamlit as st


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


def print_results(entry_prices, positions, profits, full_profit, full_loss, liquidation_price):
    st.subheader("Results")
    for i, (price, pos, profit) in enumerate(zip(entry_prices, positions, profits), start=1):
        st.write(f"<div style='background-color: #f0f0f0; padding: 10px; border-radius: 5px; margin-bottom: 10px;'>"
                 f"<strong>Entry {i}:</strong> {price:.5f} -> Position: {pos:.2f} // Profit: {profit:.2f}"
                 f"</div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Full Profit", value=f"{full_profit:.2f}", delta=None, delta_color="normal")
    with col2:
        st.metric(label="Full Loss", value=f"{full_loss:.2f}", delta=None, delta_color="normal")

    st.write(f"<div style='background-color: #f0f0f0; padding: 10px; border-radius: 5px;'>"
             f"<strong>Liquidation Price:</strong> {liquidation_price:.5f}"
             f"</div>", unsafe_allow_html=True)


def login():
    st.sidebar.subheader("Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        if username == "admin" and password == "password":
            st.session_state.logged_in = True
            st.session_state.username = username
            st.experimental_rerun()
        else:
            st.sidebar.error("Invalid username or password")

def main():
    st.set_page_config(page_title="Position Calculator", page_icon=":calculator:", layout="centered")
    st.title("Position Calculator")

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        login()
    else:
        st.sidebar.subheader(f"Welcome, {st.session_state.username}!")
        logout_button = st.sidebar.button("Logout")
        if logout_button:
            st.session_state.logged_in = False
            st.experimental_rerun()

        if "portfolio_size" not in st.session_state:
            st.session_state.portfolio_size = 5000.0

        with st.expander("Input Parameters", expanded=True):
            portfolio_size = st.number_input("Portfolio Size", value=st.session_state.portfolio_size)
            st.session_state.portfolio_size = portfolio_size
            risk_level = st.number_input("Risk Level", value=3.0)
            entry_prices = st.text_input("Entry Prices (comma-separated)")
            stop_loss = st.number_input("Stop Loss")
            take_profit = st.number_input("Take Profit")
            liquidation_buffer = st.number_input("Liquidation Buffer", value=12.0)

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
            else:
                st.warning("Please fill in all the required fields.")


if __name__ == "__main__":
    main()