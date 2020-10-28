import streamlit as st
import time
from plotly import graph_objs as go
from pathlib import Path
import base64
import pandas as pd
import random
import datetime


def run_inference(patient_data):
    time.sleep(3)
    _base = patient_data["meta"][-1]
    return {k:_base + random.randint(1, 20)for k in patient_data["pathways"]}

def plot_predictions(patient_data, preditions):
    x_size = len(patient_data["meta"])
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=list(range(x_size)),
            y = patient_data["meta"],
            mode="lines",
            name="Current"
            ))
    fig.add_traces([
        go.Scatter(
            x=[x_size-1, x_size],
            y= [patient_data["meta"][-1], preditions[k]],
            mode="lines",
            name = k) 
        for k in sorted(preditions.keys())
    ])
    fig.layout.xaxis.title= "Date"
    fig.layout.yaxis.title= "Pharmacy Margin Prediction"
    fig.update_layout(
        shapes=[
            dict(
                type= 'line',
                line=dict(
                    color = "Grey",
                    dash = "dash"),
                yref= 'paper', y0= 0, y1= 1,
                xref= 'x', x0= x_size-1, x1= x_size-1
            ),
    ])
    today = datetime.datetime.today()
    current_month = today.strftime("%b %Y")
    date_3m_later = (today+datetime.timedelta(days=90)).strftime("%b %Y")
    fig.update_layout(
    xaxis = dict(
        tickmode = 'array',
        tickvals = [4,5],
        ticktext = [current_month, date_3m_later],
        range = [0,5.3], 
    )
)
    return fig


def img_to_bytes(img_path):
    img_bytes = Path(img_path).read_bytes()
    encoded = base64.b64encode(img_bytes).decode()
    return encoded

@st.cache(show_spinner=False)
def load_local_data():
    """
    Loading static meta data
    Using dummy data now 
    """
    data = {}
    # Load facilities
    with open("data/facilities.txt", "r") as f:
        facilities = [line.strip() for line in f.readlines()]

    # Load disease and pathways
    meta = pd.read_csv("data/diseases_and_pathways.csv")
    _mapping = {
        disease : _df["pathway"].values
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
        return None
    time.sleep(1)
    return [10,20,30,40,50]

@st.cache(show_spinner=False)
def get_facility_list(meta_data, patient_data):
    return sorted(list(meta_data['meta'].keys()))


@st.cache(show_spinner=False)
def get_disease_list(meta_data, patient_data):
    return sorted(list(meta_data['meta'][patient_data["facility"]].keys()))


@st.cache(show_spinner=False)
def get_pathway_list(meta_data, patient_data):
    return sorted(meta_data['meta'][patient_data["facility"]][patient_data["disease"]])


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
            "Please specific facility:", 
            get_facility_list(meta_data, patient_data),
            key=f"{patient_mrn}_facility",
            )
        patient_data["disease"] = st.sidebar.selectbox(
            "Please specific disease type:",
            get_disease_list(meta_data, patient_data),
            key=f"{patient_mrn}_disease"
            )
        available_pathway = get_pathway_list(meta_data, patient_data)
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
    # with pred_container.beta_container():
    st.plotly_chart(plot_predictions(patient_data, predictions),use_container_width=True, config={"displaylogo":False} )
    df = pd.DataFrame.from_dict(predictions, orient='index', columns=['Pharmacy Margin Prediction'])
    df.index.name = "Pathway"
    df['Pharmacy Margin Prediction'] = df['Pharmacy Margin Prediction'].round().apply(int)
    st.dataframe(df.style.highlight_max(axis=0), width=900)

    with st.beta_expander("Learn about the methodology:"):
        st.write("""
        I'm a smart robot.
        """)
        st.image("static/SFLlogo.png")

    st.markdown(
        f'''
        <p align="right">
        Powered by 
        <a href="https://sflscientific.com/" target="_blank">
        {load_logo()}
        </a></p>''',
        unsafe_allow_html=True
        )


if __name__ == "__main__":
    main()