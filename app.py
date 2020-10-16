import streamlit as st
import time
from plotly import graph_objs as go

def run_inference(input_data, pathways = None):
    time.sleep(5)
    predictions = {
        "Pathway A":6,
        "Pathway B":5.5,
        "Pathway C":5.1,
        "Pathway D":7,
    }
    if pathways:
        return {k:predictions[k] for k in pathways}
    else:
        return predictions

@st.cache
def get_data(pid):
    time.sleep(5)
    return [1,2,3,4,5]

def plot_predictions(input_data, preditions):
    x_size = len(input_data)
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=list(range(x_size)),
            y = input_data,
            mode="lines",
            name="Current"
            ))
    fig.add_traces([
        go.Scatter(
            x=[x_size-1, x_size],
            y= [input_data[-1], preditions[k]],
            mode="lines",
            name = k) 
        for k in sorted(preditions.keys())
    ])
    fig.layout.xaxis.title= "Date"
    fig.layout.xaxis.title= "Prediction"
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

def main():
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

    ## Main App
    st.sidebar.header('Inputs')
    patient_id = st.sidebar.text_input("Please enter the Patient ID")
    if st.sidebar.checkbox('Select Pathways:'):
        pathways = st.sidebar.multiselect( 'Select treatment pathways',
            ["Pathway A", "Pathway B", "Pathway C", "Pathway D"])
    else:
        pathways = None
    if patient_id:
        input_data = get_data(patient_id)
        if st.sidebar.button('Run'):
            st.header('Predictions')
            predictions = run_inference(input_data, pathways)
        else:
            st.header('Click on the run button for predictions')
            predictions = None

        
        if predictions:
            st.write(f'The Predictions for {patient_id} is')
            st.plotly_chart(plot_predictions(input_data, predictions),use_container_width=True, config={"displaylogo":False} )
            # st.markdown("![App first page](static/SFLlogo.png)", unsafe_allow_html=True)
            st.markdown(
                '''
                <p align="right">
                Powered by 
                <a href="https://sflscientific.com/" target="_blank">
                SFL Scientific
                </a></p>''',
                unsafe_allow_html=True
                )
    else:
        st.header('<-- Enter a Patient ID to start')


if __name__ == "__main__":
    main()