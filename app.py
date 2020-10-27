import streamlit as st
import time
from plotly import graph_objs as go
from pathlib import Path
import base64
import pandas as pd


def run_inference(patient_data):
    time.sleep(3)
    predictions = {
        "Pathway A":60,
        "Pathway B":55,
        "Pathway C":51,
        "Pathway D":70,
    }
    if patient_data["pathways"]:
        return {k:predictions[k] for k in patient_data["pathways"]}
    else:
        return predictions


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
    fig.layout.yaxis.title= "Prediction"
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
    return fig


def img_to_bytes(img_path):
    img_bytes = Path(img_path).read_bytes()
    encoded = base64.b64encode(img_bytes).decode()
    return encoded


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
def get_facility_list(data):
    return [
        "PA-ERMC",
        "GA-SERMC",
        "AZ-WRMC",
        "IL-MRMC",
        "OK-SRMC",
            ]


@st.cache(show_spinner=False)
def get_disease_list(data):
    return ["A", "B", "C"]


@st.cache(show_spinner=False)
def get_pathway_list(data):
    return ["Pathway A", "Pathway B", "Pathway C", "Pathway D"]


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
            get_facility_list(patient_data),
            key=f"{patient_mrn}_facility",
            )
        patient_data["disease"] = st.sidebar.selectbox(
            "Please specific disease type:",
            get_disease_list(patient_data),
            key=f"{patient_mrn}_disease"
            )
        available_pathway = get_pathway_list(patient_data)
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
    df['Pharmacy Margin Prediction'] = df['Pharmacy Margin Prediction'].round().apply(int)
    st.dataframe(df.style.highlight_max(axis=0),width=900)

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