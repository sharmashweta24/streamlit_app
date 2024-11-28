from os.path import abspath, join, dirname
from sys import path, exc_info

base_dir = abspath(join(dirname(__file__), "../"))
path.append(base_dir)

from app import *
from core.binanry import *

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def dowload_binanry_by_user():
    if st.button("Logout"):
        logout(st)
    st.markdown("<h4 style='color:white'>Odecent Binary</h4>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:red'>Don't refresh page after login, it will logout you</h3>", unsafe_allow_html=True)
    username = st.text_input("Username")
    if st.button("Search"):
        if username == '':
            st.error("Please enter username")
            return
        else:
            binary_list = get_users_network_binary(username)
            df = pd.DataFrame(binary_list)
            csv_string = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv_string,
                file_name=f"{username}_user_binary.csv",
                mime="text/csv",
            )
            st.table(df)
if st.session_state.logged_in == False:
    login(st,'Adminname','Password')
else:
    dowload_binanry_by_user()