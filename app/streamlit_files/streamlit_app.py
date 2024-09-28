import streamlit as st
import requests
from streamlit import session_state
# from get_passport_data import get_passport_data
# from view_muballigs import view_muballigs
import warnings
import streamlit as st
import requests
from streamlit import session_state
from io import BytesIO
from datetime import date


warnings.filterwarnings("ignore")

def main():
    #make the layout wide
    st.set_page_config(layout="wide")
    st.sidebar.title("Sidebar")
    st.sidebar.text("This is the sidebar. You can put anything you want here.")

    if 'token' not in st.session_state:
        login_page()
    elif 'page' in st.session_state and st.session_state.page == "get_passport_data":
        get_passport_data()
    elif 'page' in st.session_state and st.session_state.page == "view_muballigs":
        view_muballigs()
    elif 'page' in st.session_state and st.session_state.page == "dashboard":
        dashboard()
    else:
        dashboard()

def on_click_functtion(selected_page):
    st.session_state.page = selected_page
        

def login_page():
    st.title("Muballig")
    username = st.text_input("Username")
    password = st.text_input("Password", type='password')
    login_button = st.button("Login")

    if login_button:
        response = requests.post(
            "http://localhost:8000/login",
            data={"username": username, "password": password}
        )

        if response.status_code == 200:
            st.session_state['token'] = response.json()['access_token']
            st.rerun()
            dashboard()
        else:
            st.error("Login failed. Please check your credentials.")

def dashboard():
    # use the get user info Endpoint to get the user into
    response = requests.get(
        "http://localhost:8000/users/get_userinfo",
        headers={"Authorization": f"Bearer {st.session_state['token']}"
        },
            allow_redirects=True

    )

    if response.status_code == 200:
        st.title(f"Welcome {response.json()['name']}!")

        #If the rule of the user is that operator then there should be two links in the sidebar one will one will be for getting passport data and another will be for visa application status
        if response.json()['role'] == "data_operator":
            st.sidebar.header("Data Operator")

            dashboard_btn = st.sidebar.button("Dashboard",on_click= on_click_functtion,args=("home",))
            get_passport_btn =  st.sidebar.button("Get Passport Data",on_click= on_click_functtion,args=("get_passport_data",))
            view_muballigs_btn = st.sidebar.button("View Muballigs",on_click= on_click_functtion,args=("view_muballigs",))
            

            # if get_passport_btn:
            #     st.session_state.page = "get_passport_data"
            # elif view_muballigs_btn:
            #     st.session_state.page = "view_muballigs"
            # elif dashboard_btn:
            #     st.session_state.page = "home"

            
    else:
        st.error("Something went wrong.")

def get_passport_data():
    st.title("Get Passport Data")
    st.text("Upload image of passport.")

    dashboard_btn = st.sidebar.button("Dashboard",on_click= on_click_functtion,args=("home",))
    get_passport_btn =  st.sidebar.button("Get Passport Data",on_click= on_click_functtion,args=("get_passport_data",))
    view_muballigs_btn = st.sidebar.button("View Muballigs",on_click= on_click_functtion,args=("view_muballigs",))


    # Create a form to get the arrival date, expiry date, and ticket time and the image of the passport
    form = st.form(key='my_form',clear_on_submit=True)
    uploaded_file = form.file_uploader("Choose an image...", type="jpg")
    arrival_date = form.date_input('Arrival Date')
    expiry_date = form.date_input('Expiry Date')
    ticket_time = form.date_input('Ticket Time')
    get_data_button = form.form_submit_button('Get Data')

    if get_data_button:
        if uploaded_file is not None:
            # Read the uploaded file
            img_bytes = uploaded_file.read()


            # Prepare the data for the post request
            data = {
                "arrival_date": arrival_date.strftime("%Y-%m-%d") if arrival_date else None,
                "expiry_date": expiry_date.strftime("%Y-%m-%d") if expiry_date else None,
                "ticket_time": ticket_time.strftime("%Y-%m-%d") if ticket_time else None,
            }

            #convert data to json
            files = {"file": ("image.jpg", BytesIO(img_bytes), "image/jpg")}

            # Send a post request to the get passport data endpoint
            response = requests.post(
                "http://localhost:8000/data_operators/get_traveller_data",
                headers={"Authorization": f"Bearer {st.session_state['token']}"},
                data=data,
                files=files,
            )


            if response.status_code == 200:
                st.success("Data successfully added to the database.")
            else:
                st.error("Something went wrong.")
        else:
            st.error("Please upload an image.")


def view_muballigs():
   
    
    # position the st.title("Muballigs") in the top left corner of the page
    st.title("Muballigs")

    dashboard_btn = st.sidebar.button("Dashboard",on_click= on_click_functtion,args=("home",))
    get_passport_btn =  st.sidebar.button("Get Passport Data",on_click= on_click_functtion,args=("get_passport_data",))
    view_muballigs_btn = st.sidebar.button("View Muballigs",on_click= on_click_functtion,args=("view_muballigs",))

    
    #add a form for searching for muballigs. There should be a search button and a reset button and a search bar.there should be filters for the search bar such as staying status , country , lower date , upper date
    form = st.form(key='my_form',clear_on_submit=False)
    search = form.text_input("Search")
    search_button = form.form_submit_button('Search')
    # reset_button = form.form_submit_button('Reset')
    #add a select box for staying status
    staying_status = form.selectbox("Staying Status",["None","stay","return"])
    # staying_status = form.selectbox("Staying Status",["stay","return"])
    #add a select box for country
    country = form.selectbox("Country",["None","Pakistan","Saudi Arabia","United Arab Emirates"])
    #add a date input for lower date
    lower_date = form.date_input("Lower Date",value=None)
    #default lower date should be none
    #add a date input for upper date
    upper_date = form.date_input("Upper Date",value=None)
    
    if staying_status == "None":
        staying_status = None
    if country == "None":
        country = None

    if search_button:
        # Prepare the data for the post request
        data = {
            "search": search,
            "status": staying_status,
            "country": country,
            "lower_date": lower_date.strftime("%Y-%m-%d") if lower_date else None,
            "upper_date": upper_date.strftime("%Y-%m-%d") if upper_date else None,
        }

        # Send a post request to the get passport data endpoint
        response = requests.post(
            "http://localhost:8000/data_operators/search_travellers",
            headers={"Authorization": f"Bearer {st.session_state['token']}"},
            data=data,
        )

        if response.status_code == 200:
            # st.write(response.json())
            travellers = response.json()["travellers_info"]
            #make a card for each traveller having their info like name,muballig_id,staying status,visa_application_status_country
            for traveller in travellers:
                # Create a container for each card
                with st.container():
                    # Create a row of columns for the card
                    col1, col2, col3, col4 = st.columns([2,1, 2, 2])  # Adjust column widths as needed

                    with col1:
                        st.text(f"{traveller['first_name']}")  # Replace 'name' with the actual key for the name in your data

                    with col2:
                        st.text(f"{traveller['muballig_id']}")  # Replace 'muballig_id' with the actual key for the muballig_id in your data

                    with col3:
                        st.text(f"{traveller['staying_status']}")  # Replace 'staying_status' with the actual key for the staying_status in your data

                    with col4:
                        st.text(f"{traveller['visa_application_status']}")  # Replace 'visa_application_status_country' with the actual key for the visa_application_status_country in your data

        else:
            st.error("Something went wrong.")
    # elif reset_button:
    #     # Prepare the data for the post request
    #     data = {
    #         "staying_status": None,
    #         "country": None,
    #         "lower_date": None,
    #         "upper_date": None,
    #     }

    #     # Send a post request to the get passport data endpoint
    #     response = requests.get(
    #         "http://localhost:8000/security/get_staying_travellers",
    #         headers={"Authorization": f"Bearer {st.session_state['token']}"},
    #         params=data,
    #     )

    #     if response.status_code == 200:
    #         st.success("Data successfully added to the database.")
    #     else:
    #         st.error("Something went wrong.")



if __name__ == "__main__":
    main()