import random
import pandas as pd
import streamlit as st

import utils
from infer_dummy import run_inference, get_predictions_plot, get_data
from style import custom_css
from auth import authenticated


def get_predictions_dataframe(predictions):
    p_col = "Cumulative Pharmacy Margin Prediction"
    df = pd.DataFrame.from_dict(predictions, orient='index', columns=[p_col])
    df.index.name = "Pathway"
    df[p_col] = df[p_col].round(0).apply(utils.int_to_currency)
    df = df.style.apply(utils.highlight_max_margin, subset=[p_col])
    return df


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
    pic = utils.img_to_bytes("static/small_logo.png")
    return f"<img src='data:image/png;base64,{pic}' class='img-fluid', height='20rem'>"


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
        pathways_bool = [st.sidebar.checkbox(_pathway*8,True,key=str(patient_mrn)+_pathway) for _pathway in available_pathway]
        _pathways_bool = [st.checkbox(_pathway*8,True,key="main"+str(patient_mrn)+_pathway) for _pathway in available_pathway]
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
    '''Main App function'''
    ## Style update must happen before everything.
    st.beta_set_page_config(
        page_title="Cool App",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    
    custom_css()
    if True: #authenticated():
        app()


if __name__ == "__main__":

    main()

