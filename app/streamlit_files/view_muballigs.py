# import streamlit as st
# import requests
# from streamlit import session_state
# from io import BytesIO
# from datetime import date


# def view_muballigs():
#     st.title("Muballigs")

#     #add a form for searching for muballigs. There should be a search button and a reset button and a search bar.there should be filters for the search bar such as staying status , country , lower date , upper date
#     form = st.form(key='my_form',clear_on_submit=True)
#     search_bar = form.text_input("Search")
#     search_button = form.form_submit_button('Search')
#     reset_button = form.form_submit_button('Reset')
#     #add a select box for staying status
#     staying_status = form.selectbox("Staying Status",["stay","left"])
#     #add a select box for country
#     country = form.selectbox("Country",["Pakistan","Saudi Arabia","United Arab Emirates"])
#     #add a date input for lower date
#     lower_date = form.date_input("Lower Date")
#     #add a date input for upper date
#     upper_date = form.date_input("Upper Date")

#     if search_button:
#         # Prepare the data for the post request
#         data = {
#             "staying_status": staying_status,
#             "country": country,
#             "lower_date": lower_date.strftime("%Y-%m-%d") if lower_date else None,
#             "upper_date": upper_date.strftime("%Y-%m-%d") if upper_date else None,
#         }

#         # Send a post request to the get passport data endpoint
#         response = requests.get(
#             "http://localhost:8000/security/get_staying_travellers",
#             headers={"Authorization": f"Bearer {st.session_state['token']}"},
#             params=data,
#         )
#         print("Status code:", response.status_code)
#         print("Response text:", response.text)

#         if response.status_code == 200:
#             st.success("Data successfully added to the database.")
#         else:
#             st.error("Something went wrong.")
#     elif reset_button:
#         # Prepare the data for the post request
#         data = {
#             "staying_status": None,
#             "country": None,
#             "lower_date": None,
#             "upper_date": None,
#         }

#         # Send a post request to the get passport data endpoint
#         response = requests.get(
#             "http://localhost:8000/security/get_staying_travellers",
#             headers={"Authorization": f"Bearer {st.session_state['token']}"},
#             params=data,
#         )
#         print("Status code:", response.status_code)
#         print("Response text:", response.text)

#         if response.status_code == 200:
#             st.success("Data successfully added to the database.")
#         else:
#             st.error("Something went wrong.")

