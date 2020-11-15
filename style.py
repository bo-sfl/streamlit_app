## Host Code modify default Streamlit CSS Style 
import streamlit as st


def custom_css():
    ## Hide the default humbugger manual
    hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        </style>
        """
    st.markdown(hide_menu_style, unsafe_allow_html=True)

    ## Reduce padding at top
    st.markdown("""<style>
            .sidebar .sidebar-content  {
                padding-top: 2rem;
                padding-right: 1rem;
                padding-bottom: 5rem;
                padding-left: 1rem;
            } </style>""", unsafe_allow_html=True)

    st.markdown("""<style>
            .reportview-container .main .block-container  {
                padding-top: 1rem;
                padding-right: 1rem;
                padding-bottom: 5rem;
                padding-left: 1rem;
            } </style>""", unsafe_allow_html=True)

    ## Remove checkbox label margin
    st.markdown("""<style>
            label[data-baseweb="checkbox"] {
                margin: 0;
            } </style>""", unsafe_allow_html=True)

    # Remove element-container margin
    st.markdown("""<style>
            .reportview-container .element-container {
                margin-bottom: 0.4rem;
            } </style>""", unsafe_allow_html=True)
    # st.markdown("""<style>
    #         .reportview-container .markdown-text-container {
    #             margin-bottom: 0.6rem;
    #         } </style>""", unsafe_allow_html=True)