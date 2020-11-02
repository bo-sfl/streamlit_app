import streamlit as st
import time
from plotly import graph_objs as go
from pathlib import Path
import base64
import pandas as pd
import random
import datetime
from SessionState import session_get
import hashlib


def run_inference(patient_data):
    if patient_data["patient_mrn"] == "fake_id":
        return run_dummy_inference(patient_data)
    return run_dummy_inference(patient_data)


def get_predictions_plot(patient_data, preditions):
    if patient_data["patient_mrn"] == "fake_id":
        return get_dummy_predictions_plot(patient_data, preditions)
    return get_dummy_predictions_plot(patient_data, preditions)


def highlight_max_margin(data, color='yellow'):
    '''
    highlight the maximum in a currency string Series
    '''
    attr = 'background-color: {}'.format(color)
    is_max = data == data.max()
    return [attr if v else '' for v in is_max]

def int_to_(val):
    """
    Takes an int and cast to currency style
    """
    color = 'red' if val < 0 else 'black'
    return 'color: %s' % color

def int_to_currency(val):
    """
    Takes an int and cast to currency style
    """
    val = str(val)
    _start_pos = 0
    _end_pos = len(val)%3
    if _end_pos == 0:
        _end_pos = 3
    currency = ["$"]
    while _end_pos <= len(val): 
        currency.append(val[_start_pos:_end_pos] + ",")
        _start_pos = _end_pos
        _end_pos += 3
    
    return "".join(currency)[:-1]

def currency_to_int(val):
    """
    Convert an currency string to int
    """
    return int(val[1:].replace(",",""))

def get_predictions_dataframe(predictions):
    p_col = "Cumulative Pharmacy Margin Prediction"
    df = pd.DataFrame.from_dict(predictions, orient='index', columns=[p_col])
    df.index.name = "Pathway"
    df[p_col] = df[p_col].round(0).apply(int_to_currency)
    df = df.style.apply(highlight_max_margin, subset=[p_col])
    return df


def img_to_bytes(img_path):
    img_bytes = Path(img_path).read_bytes()
    encoded = base64.b64encode(img_bytes).decode()
    return encoded


def get_dummy_data(length=23):
    time.sleep(1)
    dummy_current = 0
    dummy_data = [dummy_current]
    for _ in range(length):
        dummy_current += random.randint(5, 20)*1000
        dummy_data.append(dummy_current)
    return dummy_data


def run_dummy_inference(patient_data):
    time.sleep(3)
    _base = patient_data["meta"][-1]
    return {k:_base + random.randint(5, 70)*5000 for k in patient_data["pathways"]}


def get_dummy_predictions_plot(patient_data, preditions):
    x_size = len(patient_data["meta"])
    today = datetime.datetime.today()
    x_dates = list([datetime.timedelta(days=x*14)+today for x in range(1-x_size,1,1)])
    date_3m_later = today+datetime.timedelta(days=90)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x = [_x.date() for _x in x_dates],
            y = patient_data["meta"],
            mode="lines",
            name="Current",
            hovertemplate =
            '<br><b>Date</b>: %{x}<br>'+
            '<b>Margin</b>: %{y}'+
            '<extra></extra>',
            ))
    fig.add_traces([
        go.Scatter(
            x = [today, date_3m_later],
            y = [patient_data["meta"][-1], preditions[k]],
            mode="lines",
            name = k,
            text = [k,k],
            hovertemplate =
            '<br><b>Pathway</b>: %{text}<br>'+
            '<b>Date</b>: %{x}<br>'+
            '<b>Margin</b>: %{y}'+
            '<extra></extra>',
            ) 
        for k in sorted(preditions.keys())
    ])
    fig.layout.xaxis.title= "Date"
    fig.layout.yaxis.title= "Cumulative Pharmacy Margin"
    # fig.layout.plot_bgcolor = "#FFFFFF"
    # fig.layout.paper_bgcolor='rgba(0,0,0,0)'
    fig.layout.plot_bgcolor='rgba(0,0,0,0)'

    fig.update_layout(
        shapes=[
            dict(
                type= 'line',
                line=dict(
                    color = "Grey",
                    dash = "dash"),
                yref= 'paper', y0= 0, y1= 1,
                xref= 'x', x0= x_dates[-1], x1= x_dates[-1],
            ),
    ])
    fig.update_yaxes(
        tickprefix="$",rangemode="nonnegative", 
        linecolor="black",tickcolor="black", ticks='inside',)
    
    fig.update_layout(
        xaxis = dict(
            tickmode = 'array',
            tickvals = [x_dates[-1], date_3m_later],
            ticktext = [x_dates[-1].strftime("%b %Y"), date_3m_later.strftime("%b %Y")],
            range = [x_dates[0], date_3m_later + datetime.timedelta(days=14)], 
            linecolor = "black", tickcolor="black", ticks='inside',
            )
        )
    return fig


def authentication(usr_name, password):
    m=hashlib.sha256()
    m.update(str(usr_name).encode())
    m.update(str(password).encode())
    if m.hexdigest() == '7bdc616cc8db6935847e5fb6add88de1f470f96cb5c92d0d0c6ee2ab8acab3a9':
        return True
    return False

@st.cache(show_spinner=False)
def load_local_data():
    """
    Loading static meta data
    Using dummy data now 
    """
    data = {}
    # Load facilities
    with open("data/facilities.txt", "r") as f:
        facilities = [line.strip().title() for line in f.readlines()]

    # Load disease and pathways
    meta = pd.read_csv("data/diseases_and_pathways.csv")
    meta.DiseaseType = meta.DiseaseType.apply(lambda x: x.title())
    _mapping = {
        disease : _df.head(4)["pathway"].values
        for disease, _df in meta.groupby("DiseaseType")
    }
    diseases = meta.DiseaseType.nunique()

    data["meta"] = {
        facility:{
            disease:_mapping[disease] 
            for disease in random.sample(list(_mapping),k=4)
        }
        for facility in facilities
    }

    return data


@st.cache(show_spinner=False)
def load_logo():
    pic = img_to_bytes("static/small_logo.png")
    return f"<img src='data:image/png;base64,{pic}' class='img-fluid', height='20rem'>"


@st.cache(show_spinner=False)
def get_data(patient_mrn):
    if patient_mrn == "fake_id":
        return get_dummy_data(23)
    return get_dummy_data(23)

@st.cache(show_spinner=False)
def get_facility_list(meta_data, patient_data):
    return sorted(list(meta_data['meta'].keys()))


@st.cache(show_spinner=False)
def get_disease_list(meta_data, patient_data):
    return sorted(list(meta_data['meta'][patient_data["facility"]].keys()))


@st.cache(show_spinner=False)
def get_pathway_list(meta_data, patient_data):
    return sorted(meta_data['meta'][patient_data["facility"]][patient_data["disease"]])


def app():
    st.markdown(
        """
        <style>.fullScreenFrame {margin: auto;}</style>
        """, unsafe_allow_html=True) 
    st.markdown(
        """<style> .block-container {padding-top: 1rem;}
        </style>
        """, unsafe_allow_html=True) # This doesn't work
    ## Loading
    meta_data = load_local_data()
    ## Main App
    st.sidebar.header('Inputs')
    patient_mrn = st.sidebar.text_input("Please enter the Patient MRN:")
    title_text = st.empty()

    if not patient_mrn:
        title_text.header('<-- Enter a Patient MRN to start')
        st.stop()

    with st.spinner("Fetching data ..."):
        patient_data = {"patient_mrn":patient_mrn}
        patient_data["meta"] = get_data(patient_mrn)
    if patient_data["meta"]:
        patient_data["facility"] = st.sidebar.selectbox(
            "Please specify facility:", 
            get_facility_list(meta_data, patient_data),
            key=f"{patient_mrn}_facility",
            )
        patient_data["disease"] = st.sidebar.selectbox(
            "Please specify disease type:",
            get_disease_list(meta_data, patient_data),
            key=f"{patient_mrn}_disease"
            )
        available_pathway = get_pathway_list(meta_data, patient_data)

        checkbox_head = """
        <span style='font-size: 12.8px;'>Please specify treatment pathways:</span>
        """
        st.sidebar.markdown(checkbox_head, unsafe_allow_html=True)
        pathways_bool = [st.sidebar.checkbox(_pathway,True,key=str(patient_mrn)+_pathway) for _pathway in available_pathway]
        patient_data["pathways"] = [_x for _x, _y in zip(available_pathway, pathways_bool) if _y]
        run_prediction = st.sidebar.button('Run')
    else:
        title_text.header('The Patient MRN is not valid')
        st.stop()

    # Run Prediction
    if run_prediction:
        with st.spinner("Runing predictions ..."):
            predictions = run_inference(patient_data)
    else:
        title_text.header('Click on the run button for predictions')
        st.stop()

    # Render the results 
    title_text.header(f'The cumulative pharmacy margin predictions for patient {patient_mrn} are:')
    st.write("")
    # with pred_container.beta_container():
    pred_df = get_predictions_dataframe(predictions)
    st.dataframe(pred_df, width=1200)
    st.plotly_chart(get_predictions_plot(patient_data, predictions),use_container_width=True, config={"displaylogo":False} )


    with st.beta_expander("Learn about the methodology:"):
        st.write("""
        XGBoost (Extreme Gradient Boosting) is a gradient boosting decision tree library designed to be 
        highly efficient and flexible. It uses an ensemble of decision trees that consist of classification 
        and regression trees. These trees are used to classify observations into different 
        leaves based on given input variables. 
        """)
        #st.image("static/SFLlogo.png")

    st.markdown(
        f'''
        <p align="right">
        Powered by 
        <a href="https://sflscientific.com/" target="_blank">
        {load_logo()}
        </a></p>''',
        unsafe_allow_html=True
        )

def main():
    ##Hacks for App layout and styles
    st.beta_set_page_config(
        page_title="Cool App",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    ## Hide the default humbugger manual
    hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        </style>
        """
    st.markdown(hide_menu_style, unsafe_allow_html=True)
    session_state = session_get(user_name='', password='')
    if not authentication(session_state.user_name, session_state.password):
        _, col2, _ = st.beta_columns(3)
        with col2:
            login_block = st.empty()
            with login_block.beta_container():
                session_state.user_name =  st.text_input("User Name:", value="", type="default")
                session_state.password = st.text_input("Password:", value="", type="password")
                _ = st.button("Login")
        if authentication(session_state.user_name, session_state.password):
            login_block.empty()
            app()
        elif session_state.password != "" and session_state.user_name != "":
            st.error("The user name and password combination you entered is incorrect")
        else:
            pass
    else:
        app()


if __name__ == "__main__":
    main()

