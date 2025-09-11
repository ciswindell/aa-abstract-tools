#!/usr/bin/env python3
"""
Simplified styling for responsive Streamlit interface.

Contains minimal CSS focused only on button styling while leveraging
Streamlit's native responsive layout system.
"""

import streamlit as st


class StyleManager:
    """Manages minimal CSS styling for responsive Streamlit pages."""

    def __init__(self) -> None:
        """Initialize the StyleManager."""
        pass

    def inject_custom_css(self) -> None:
        """Inject minimal custom CSS for button styling only."""
        st.markdown(
            """
            <style>
            /* Minimal button styling - let Streamlit handle responsiveness */
            .stButton > button {
                border-radius: 6px !important;
                font-weight: 500 !important;
                transition: all 0.2s ease !important;
                height: 40px !important;
                font-size: 14px !important;
                padding: 8px 16px !important;
                box-sizing: border-box !important;
                line-height: 1.4 !important;
            }
            
            /* Primary button (Process) - Red */
            .stButton > button[kind="primary"] {
                background-color: #dc3545 !important;
                color: white !important;
                border: none !important;
            }
            
            .stButton > button[kind="primary"]:hover {
                background-color: #c82333 !important;
                transform: translateY(-1px) !important;
                box-shadow: 0 4px 8px rgba(220, 53, 69, 0.3) !important;
            }
            
            /* Alternative selector for primary button */
            button[data-testid="baseButton-primary"] {
                background-color: #dc3545 !important;
                color: white !important;
                border: none !important;
                border-radius: 6px !important;
                font-weight: 500 !important;
                transition: all 0.2s ease !important;
                height: 40px !important;
                font-size: 14px !important;
                padding: 8px 16px !important;
            }
            
            button[data-testid="baseButton-primary"]:hover {
                background-color: #c82333 !important;
                transform: translateY(-1px) !important;
                box-shadow: 0 4px 8px rgba(220, 53, 69, 0.3) !important;
            }
            
            /* Download button - Green */
            .stDownloadButton > button {
                background-color: #28a745 !important;
                color: white !important;
                border: none !important;
                border-radius: 6px !important;
                font-weight: 500 !important;
                transition: all 0.2s ease !important;
                height: 40px !important;
                font-size: 14px !important;
                padding: 8px 16px !important;
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
                font-weight: 500 !important;
                transition: all 0.2s ease !important;
                height: 40px !important;
                font-size: 14px !important;
                padding: 8px 16px !important;
            }
            
            button[kind="primary"]:hover {
                background-color: #218838 !important;
                transform: translateY(-1px) !important;
                box-shadow: 0 4px 8px rgba(40, 167, 69, 0.3) !important;
            }
            
            /* Secondary button (Reset) - Orange */
            .stButton > button[kind="secondary"] {
                background-color: #fd7e14 !important;
                color: white !important;
                border: none !important;
                border-radius: 6px !important;
                font-weight: 500 !important;
                transition: all 0.2s ease !important;
                height: 40px !important;
                font-size: 14px !important;
                padding: 8px 16px !important;
            }
            
            .stButton > button[kind="secondary"]:hover {
                background-color: #e8690b !important;
                transform: translateY(-1px) !important;
                box-shadow: 0 4px 8px rgba(253, 126, 20, 0.3) !important;
            }
            
            /* Compact spacing for better layout */
            .stMarkdown {
                margin-bottom: 0.5rem !important;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
