#!/usr/bin/env python3
"""
Tabbed workflow components for Abstract Renumber Tool Streamlit interface.

Contains shared tabbed interface components to provide consistent navigation
and workflow patterns across different pages.
"""

from typing import Callable, List, Optional

import streamlit as st


class TabbedWorkflowManager:
    """Manages tabbed workflow interfaces."""

    def __init__(self) -> None:
        """Initialize the TabbedWorkflowManager."""
        pass

    def create_workflow_tabs(
        self,
        tab_labels: List[str],
        tab_functions: List[Callable[[], None]],
        workflow_type: str = "single",
    ) -> None:
        """Create a tabbed workflow interface.

        Args:
            tab_labels: List of tab labels (with emojis)
            tab_functions: List of functions to call for each tab
            workflow_type: Type of workflow ('single' or 'merge')
        """
        if len(tab_labels) != len(tab_functions):
            raise ValueError("Number of tab labels must match number of tab functions")

        # Create tabs
        tabs = st.tabs(tab_labels)

        # Render each tab with its corresponding function
        for i, (tab, func) in enumerate(zip(tabs, tab_functions)):
            with tab:
                func()

    def show_workflow_progress_sidebar(self, workflow_type: str = "single") -> None:
        """Show workflow progress information in sidebar.

        Args:
            workflow_type: Type of workflow ('single' or 'merge')
        """
        with st.sidebar:
            st.markdown("### ℹ️ Processing Info")

            if workflow_type == "single":
                self._show_single_file_progress()
            elif workflow_type == "merge":
                self._show_merge_workflow_progress()

    def _show_single_file_progress(self) -> None:
        """Show progress for single file workflow."""
        # Check if files are uploaded
        if not (
            st.session_state.get("uploaded_excel")
            and st.session_state.get("uploaded_pdf")
        ):
            st.info("Upload your files to begin the guided workflow.")
            return

        # Show current step based on workflow state
        current_step = self._get_single_file_current_step()
        if current_step:
            st.info(current_step)
        else:
            st.info("📍 **Current Step:** Files Uploaded - Configure Filtering")

    def _show_merge_workflow_progress(self) -> None:
        """Show progress for merge workflow."""
        # Check primary pair status
        if not st.session_state.get("primary_pair"):
            st.info("Select your primary file pair to begin the guided workflow.")
            return

        # Show file pair count
        total_pairs = 1 + len(st.session_state.get("additional_pairs", []))
        if total_pairs == 1:
            st.info("📊 **File Pairs:** 1 (primary only)")
        else:
            additional_count = len(st.session_state.get("additional_pairs", []))
            st.info(
                f"📊 **File Pairs:** {total_pairs} (1 primary + {additional_count} additional)"
            )

        # Show current step
        st.info("📍 **Current Step:** Configure Processing Options")

    def _get_single_file_current_step(self) -> Optional[str]:
        """Get current step for single file workflow.

        Returns:
            String describing current step or None
        """
        if st.session_state.get("filter_decision_made"):
            if st.session_state.get("wants_filtering") and not st.session_state.get(
                "filter_configured"
            ):
                return "📍 **Current Step:** Filter Configuration"
            elif not st.session_state.get("processing_options_decided"):
                return "📍 **Current Step:** Processing Options"
            elif st.session_state.get("processing_options_decided"):
                return "📍 **Current Step:** Ready to Process"
        elif st.session_state.get("excel_temp_path") and st.session_state.get(
            "pdf_temp_path"
        ):
            return "📍 **Current Step:** Filter Decision"

        return None

    def show_tab_navigation_help(self, current_tab: str) -> None:
        """Show navigation help for the current tab.

        Args:
            current_tab: Name of the current tab
        """
        help_messages = {
            "files": "👉 **Next:** Click on the **Filtering** tab above to configure data filtering.",
            "filtering": "👉 **Next:** Click on the **Options** tab above to configure processing options.",
            "options": "👉 **Next:** Click on the **Process** tab above to review and start processing.",
            "process": "🚀 **Ready:** Review your settings and click Process Files to begin.",
        }

        message = help_messages.get(current_tab.lower())
        if message:
            st.info(message)

    def check_prerequisites_for_tab(
        self, tab_name: str, workflow_type: str = "single"
    ) -> bool:
        """Check if prerequisites are met for accessing a tab.

        Args:
            tab_name: Name of the tab to check
            workflow_type: Type of workflow ('single' or 'merge')

        Returns:
            True if prerequisites are met, False otherwise
        """
        if workflow_type == "single":
            return self._check_single_file_prerequisites(tab_name)
        elif workflow_type == "merge":
            return self._check_merge_prerequisites(tab_name)

        return False

    def _check_single_file_prerequisites(self, tab_name: str) -> bool:
        """Check prerequisites for single file workflow tabs.

        Args:
            tab_name: Name of the tab to check

        Returns:
            True if prerequisites are met
        """
        uploaded_excel = st.session_state.get("uploaded_excel")
        uploaded_pdf = st.session_state.get("uploaded_pdf")

        if tab_name.lower() in ["filtering", "options", "process"]:
            if not (uploaded_excel and uploaded_pdf):
                st.warning("⚠️ Please upload files in the **Files** tab first.")
                return False

        return True

    def _check_merge_prerequisites(self, tab_name: str) -> bool:
        """Check prerequisites for merge workflow tabs.

        Args:
            tab_name: Name of the tab to check

        Returns:
            True if prerequisites are met
        """
        primary_pair = st.session_state.get("primary_pair")

        if tab_name.lower() in ["filtering", "options", "process"]:
            if not primary_pair:
                st.warning(
                    "⚠️ Please select a primary file pair in the **Files** tab first."
                )
                return False

        return True

    def show_prerequisite_warning(
        self, tab_name: str, workflow_type: str = "single"
    ) -> None:
        """Show warning if tab prerequisites are not met.

        Args:
            tab_name: Name of the tab
            workflow_type: Type of workflow ('single' or 'merge')
        """
        if not self.check_prerequisites_for_tab(tab_name, workflow_type):
            if workflow_type == "single":
                st.warning("⚠️ Please upload files in the **Files** tab first.")
            elif workflow_type == "merge":
                st.warning(
                    "⚠️ Please select a primary file pair in the **Files** tab first."
                )
