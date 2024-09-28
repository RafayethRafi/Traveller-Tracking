import streamlit as st
import requests
from streamlit import session_state
from io import BytesIO
from datetime import date


# def get_passport_data():
#     st.title("Get Passport Data")
#     st.text("Upload image of passport.")

#     home_page_btn =  st.sidebar.button("Dashboard")
#     view_muballigs_btn = st.sidebar.button("View Muballigs")

#     if home_page_btn:
#         st.session_state.page = "get_passport_data"
#     elif view_muballigs_btn:
#         st.session_state.page = "view_muballigs"


#     # Create a form to get the arrival date, expiry date, and ticket time and the image of the passport
#     form = st.form(key='my_form',clear_on_submit=True)
#     uploaded_file = form.file_uploader("Choose an image...", type="jpg")
#     arrival_date = form.date_input('Arrival Date')
#     expiry_date = form.date_input('Expiry Date')
#     ticket_time = form.date_input('Ticket Time')
#     get_data_button = form.form_submit_button('Get Data')

#     if get_data_button:
#         if uploaded_file is not None:
#             # Read the uploaded file
#             img_bytes = uploaded_file.read()

#             print("Arrival Date:", arrival_date)
#             print(type(arrival_date))

#             # Prepare the data for the post request
#             data = {
#                 "arrival_date": arrival_date.strftime("%Y-%m-%d") if arrival_date else None,
#                 "expiry_date": expiry_date.strftime("%Y-%m-%d") if expiry_date else None,
#                 "ticket_time": ticket_time.strftime("%Y-%m-%d") if ticket_time else None,
#             }

#             print("Data:", data)
#             print(type(data["arrival_date"]))
#             #convert data to json
#             files = {"file": ("image.jpg", BytesIO(img_bytes), "image/jpg")}

#             # Send a post request to the get passport data endpoint
#             response = requests.post(
#                 "http://localhost:8000/data_operators/get_traveller_data",
#                 headers={"Authorization": f"Bearer {st.session_state['token']}"},
#                 data=data,
#                 files=files,
#             )
#             print("Status code:", response.status_code)
#             print("Response text:", response.text)

#             if response.status_code == 200:
#                 st.success("Data successfully added to the database.")
#             else:
#                 st.error("Something went wrong.")
#         else:
#             st.error("Please upload an image.")
