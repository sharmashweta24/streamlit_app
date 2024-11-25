from os.path import abspath, join, dirname
from sys import path, exc_info

base_dir = abspath(join(dirname(__file__), "../"))
path.append(base_dir)

from app import *
import pandas as pd

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def main_app():
    if st.button("Logout"):
        logout(st)
    st.markdown("<h4 style='color:white'>Odecent Withdrawal</h4>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:red'>Don't refresh page after login, it will logout you</h3>", unsafe_allow_html=True)
    # status = st.selectbox("Select Transaction Status", ['PENDING', 'APPROVED', 'FAILED'])
    # days = st.number_input("Select number of days", min_value=1, max_value=365, value=5)
    # network = st.selectbox("Select Network", ['BEP.20', 'TRC.20'])
    # enable = st.selectbox("Select Enable Withdrawal", [True,False])
    # onhold = st.selectbox("Select Onhold", [True,False])
    status = 'PENDING'
    days = 80
    network = 'BEP.20'
    enable = True
    onhold = False
    trans = get_transactions(days=days, status=status, network=network, enable=enable,onhold=onhold)
    df = pd.DataFrame(trans)
    selected_transactions = []

    table_col, payment_col = st.columns([3, 1])

    with table_col:
        st.header("Transaction Table")
        select_all = st.checkbox("Select All")
        header_cols = st.columns([0.5, 1, 1, 1, 1])
        header_cols[0].write("Select")
        header_cols[1].write("TransID")
        header_cols[2].write("Username")
        header_cols[3].write("Requested_Amount")
        header_cols[4].write("Amount")
        for index, row in df.iterrows():
            cols = st.columns([0.5, 1, 1, 1, 1])
            selected = cols[0].checkbox(f"Select {row['TransID']}", value=select_all, key=f"select_{index}", label_visibility="collapsed")
            if selected:
                selected_transactions.append(row['TransID'])
            cols[1].write(row['TransID'])
            cols[2].write(row['Username'])
            cols[3].write(row['Requested_Amount'])
            cols[4].write(row['Amount'])
    with payment_col:
        st.markdown("<h4 style='color: green;'>Payment Details</h4>", unsafe_allow_html=True)
        if selected_transactions:
            amount = calculate(selected_transactions)
            st.markdown(f"<h2 style='color: green;'>Total Transaction Amount: {amount}</h2>", unsafe_allow_html=True)
            with st.form(key="pay_form"):
                sender_wallet = st.text_input("Sender Wallet Address")
                private_key = st.text_input("Private Key")
                check_balance = st.form_submit_button("Check Balance")
                if check_balance:
                    if not sender_wallet:
                        st.markdown("<h3 style='color: red;'>Please enter a sender wallet address</h3>", unsafe_allow_html=True)
                        st.stop()
                    if not private_key:
                        st.markdown("<h3 style='color: red;'>Please enter a private key</h3>", unsafe_allow_html=True)
                        st.stop()
                    acc_bal = get_wallet_balances_bep20(sender_wallet)
                    if 'Error' in acc_bal:
                        st.markdown(f"<h2 style='color: red;'>{acc_bal['Error']}</h2>", unsafe_allow_html=True)
                    st.markdown(f"<h2 style='color: green;'>Available Balance in (USDT): {acc_bal['USDT']}</h2>", unsafe_allow_html=True)
                submit_button = st.form_submit_button("Submit Payment")
                if submit_button:
                    tt = muliple_withdrawal(st, sender_wallet, private_key, selected_transactions)
                    if not tt:
                        st.markdown("<h3 style='color: red;'>Payment failed</h3>", unsafe_allow_html=True)
                        st.stop()
                    else:
                        st.success("Payment successfully processed!")
                        try:
                            csv_file = pd.read_csv("withdrawal_transactions.csv")
                        except Exception as err:
                            st.markdown("<h3 style='color: red;'>No withdrawal transactions csv found</h3>", unsafe_allow_html=True)
                        st.download_button(
                            label="Download Withdrawal Transactions CSV",
                            data=csv_file,
                            file_name="withdrawal_transactions.csv",
                            mime="text/csv"
                        )
        else:
            st.markdown("<h6 style='color: red;'>No transactions selected</h6>", unsafe_allow_html=True)

if st.session_state.logged_in == False:
    login(st,'Adminname','Password')
else:
    main_app()