"""Frontend module for the flowforge AI package."""

import streamlit as st

st.set_page_config(
    page_title="FlowForge",
    page_icon="https://github.com/tsterbak/flowforge/raw/main/images/flowforge-logo.png",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={},
)

st.markdown(
    r"""
    <style>
    .stDeployButton {
            visibility: hidden;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def main():
    st.title("Hello Streamlit!")
    st.write("Welcome to my modular Streamlit app!")


if __name__ == "__main__":
    main()
