"""Frontend module for the flowforge AI package."""

from typing import Callable

import streamlit as st


def get_dynamic_streamlit_frontend(flow) -> Callable:

    def create_app():
        # Set page config
        st.set_page_config(
            page_title="FlowForge",
            page_icon="https://github.com/tsterbak/flowforge/raw/main/images/flowforge-logo.png",
            layout="wide",
            initial_sidebar_state="expanded",
            menu_items={},
        )

        # Hide the deploy button
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

        st.title("FlowForge")

    return create_app
