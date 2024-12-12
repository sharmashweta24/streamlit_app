# from os.path import abspath, join, dirname
# from sys import path, exc_info

# base_dir = abspath(join(dirname(__file__), "../"))
# path.append(base_dir)

# from app import *
# from core.binanry import *

# if "logged_in" not in st.session_state:
#     st.session_state.logged_in = False

# def dowload_binanry_by_user():
#     if st.button("Logout"):
#         logout(st)
#     st.markdown("<h4 style='color:white'>Odecent Binary</h4>", unsafe_allow_html=True)
#     st.markdown("<h3 style='color:red'>Don't refresh page after login, it will logout you</h3>", unsafe_allow_html=True)
#     st.markdown("<h3 style='color: yellow;'>Binary Business Volume</h3>", unsafe_allow_html=True)
#     username = st.text_input("Username")
#     if st.button("Search"):
#         if username == '':
#             st.error("Please enter username")
#             return
#         else:
#             df, total_user_df = get_users_network_binary(username)

#             st.write(total_user_df)
#             st.table(df)

#             csv_string = df.to_csv(index=False)
#             st.download_button(
#                 label="Download CSV",
#                 data=csv_string,
#                 file_name=f"{username}_user_binary.csv",
#                 mime="text/csv",
#             )
#             st.table(df)
# if st.session_state.logged_in == False:
#     login(st,'Adminname','Password')
# else:
#     dowload_binanry_by_user()



from os.path import abspath, join, dirname
from sys import path, exc_info

base_dir = abspath(join(dirname(__file__), "../"))
path.append(base_dir)

from app import *
from core.binanry import *
import streamlit as st
import time  

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def dowload_binanry_by_user():
    if st.button("Logout"):
        logout(st)
    
    st.markdown("<h4 style='color:white'>Odecent Binary</h4>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:red'>Don't refresh the page after login; it will log you out</h3>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: yellow;'>Binary Business Volume</h3>", unsafe_allow_html=True)
    
    username = st.text_input("Username")
    
    if st.button("Search"):
        if username == '':
            st.error("Please enter a username")
            return
        else:
            progress_bar = st.progress(0)
            status_message = st.empty()  # Placeholder for status messages
            status_message.info("Processing data, please wait...")

            try:
                # Simulating progress steps
                progress_bar.progress(20)
                time.sleep(0.5)
                
                # Fetch data
                df, total_user_df = get_users_network_binary(username)
                progress_bar.progress(70)
                
                if not df.empty and not total_user_df.empty:
                    progress_bar.progress(100)
                    status_message.success("Data retrieved successfully!")

                                        # Download CSV
                    csv_string = df.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv_string,
                        file_name=f"{username}_user_binary.csv",
                        mime="text/csv",
                    )
                    st.balloons()

                    # Show Total User Data
                    st.markdown("### Total User Data")
                    st.write(total_user_df)

                    # Show User Network Data
                    st.markdown("### User Network Data")
                    st.table(df)


                else:
                    status_message.warning("No data found for the given username.")
                    progress_bar.progress(100)
            except Exception as e:
                status_message.error(f"An error occurred: {str(e)}")
                progress_bar.empty()


if st.session_state.logged_in == False:
    login(st, 'Adminname', 'Password')
else:
    dowload_binanry_by_user()
