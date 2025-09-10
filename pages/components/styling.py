#!/usr/bin/env python3
"""
Styling components for Abstract Renumber Tool Streamlit interface.

Contains shared CSS injection functionality to eliminate duplication
across different pages.
"""

import streamlit as st


class StyleManager:
    """Manages CSS styling for Streamlit pages."""

    def __init__(self) -> None:
        """Initialize the StyleManager."""
        pass

    def inject_custom_css(self) -> None:
        """Inject custom CSS for button styling and UI components."""
        st.markdown(
            """
            <style>
            /* Download button - Green primary style */
            .stDownloadButton > button {
                background-color: #28a745 !important;
                color: white !important;
                border: none !important;
                border-radius: 6px !important;
                font-weight: 600 !important;
                transition: all 0.3s ease !important;
            }
            
            .stDownloadButton > button:hover {
                background-color: #218838 !important;
                transform: translateY(-1px) !important;
                box-shadow: 0 4px 8px rgba(40, 167, 69, 0.3) !important;
            }
            
            /* Alternative selector for download button */
            button[kind="primary"] {
                background-color: #28a745 !important;
                color: white !important;
                border: none !important;
                border-radius: 6px !important;
                font-weight: 600 !important;
                transition: all 0.3s ease !important;
            }
            
            button[kind="primary"]:hover {
                background-color: #218838 !important;
                transform: translateY(-1px) !important;
                box-shadow: 0 4px 8px rgba(40, 167, 69, 0.3) !important;
            }
            
            /* Process button - Red primary style - Multiple selectors to ensure it works */
            .stButton > button[kind="primary"]:not([data-testid*="download"]) {
                background-color: #dc3545 !important;
                color: white !important;
                border: none !important;
                border-radius: 6px !important;
                font-weight: 600 !important;
                transition: all 0.3s ease !important;
            }
            
            .stButton > button[kind="primary"]:not([data-testid*="download"]):hover {
                background-color: #c82333 !important;
                transform: translateY(-1px) !important;
                box-shadow: 0 4px 8px rgba(220, 53, 69, 0.3) !important;
            }
            
            /* Alternative selector for process button */
            button[data-testid="baseButton-primary"] {
                background-color: #dc3545 !important;
                color: white !important;
                border: none !important;
                border-radius: 6px !important;
                font-weight: 600 !important;
                transition: all 0.3s ease !important;
            }
            
            button[data-testid="baseButton-primary"]:hover {
                background-color: #c82333 !important;
                transform: translateY(-1px) !important;
                box-shadow: 0 4px 8px rgba(220, 53, 69, 0.3) !important;
            }

            /* Reset button - Orange secondary style */
            .stButton > button[kind="secondary"] {
                background-color: #fd7e14 !important;
                color: white !important;
                border: none !important;
                border-radius: 6px !important;
                font-weight: 500 !important;
                transition: all 0.3s ease !important;
            }
            
            .stButton > button[kind="secondary"]:hover {
                background-color: #e8690b !important;
                transform: translateY(-1px) !important;
                box-shadow: 0 4px 8px rgba(253, 126, 20, 0.3) !important;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
