#!/usr/bin/env python3
"""
Column mapping module for the Abstract Renumber Tool.
Handles column validation and mapping dialog functionality.
"""

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any, Dict, List, Optional


class ColumnMappingDialog:
    """Dialog for mapping Excel columns to required columns."""

    def __init__(
        self, parent: tk.Tk, available_columns: List[str], missing_columns: List[str]
    ) -> None:
        """Initialize the column mapping dialog.

        Args:
            parent: Parent tkinter window
            available_columns (List[str]): List of column names available in the Excel file
            missing_columns (List[str]): List of required column names that are missing
        """
        self.window = tk.Toplevel(parent)
        self.window.title("Column Mapping")
        self.window.geometry("500x400")
        self.window.transient(parent)
        self.window.grab_set()

        # Center the dialog on parent window
        self.center_on_parent(parent)

        self.available_columns = available_columns
        self.missing_columns = missing_columns
        self.combo_vars = {}
        self.result: Optional[Dict[str, str]] = None

        self.setup_dialog()

    def center_on_parent(self, parent: tk.Tk) -> None:
        """Center the dialog on the parent window.

        Args:
            parent: Parent tkinter window to center on
        """
        self.window.update_idletasks()
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()

        dialog_width = 500
        dialog_height = 400

        pos_x = parent_x + (parent_width // 2) - (dialog_width // 2)
        pos_y = parent_y + (parent_height // 2) - (dialog_height // 2)

        self.window.geometry(f"{dialog_width}x{dialog_height}+{pos_x}+{pos_y}")

    def setup_dialog(self) -> None:
        """Setup the column mapping dialog."""
        # Main frame
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = ttk.Label(
            main_frame, text="Map Excel Columns", font=("Arial", 14, "bold")
        )
        title_label.pack(pady=(0, 10))

        # Instructions
        instructions = ttk.Label(
            main_frame,
            text="The Excel file is missing some required columns.\n"
            "Please map the existing columns to the required column names:",
            wraplength=450,
            justify=tk.CENTER,
        )
        instructions.pack(pady=(0, 20))

        # Create scrollable mapping area
        self._create_mapping_area(main_frame)

        # Buttons
        self._create_buttons(main_frame)

    def _create_mapping_area(self, parent: ttk.Frame) -> None:
        """Create scrollable area for column mappings."""
        canvas = tk.Canvas(parent, height=200)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Create mapping controls
        self._create_mapping_controls(scrollable_frame)

    def _create_mapping_controls(self, parent: ttk.Frame) -> None:
        """Create mapping controls for each missing column."""
        for i, missing_col in enumerate(self.missing_columns):
            # Create frame for this mapping
            mapping_frame = ttk.Frame(parent)
            mapping_frame.pack(fill=tk.X, pady=5, padx=10)

            # Required column label
            req_label = ttk.Label(
                mapping_frame,
                text=f"Required: {missing_col}",
                font=("Arial", 10, "bold"),
            )
            req_label.pack(anchor=tk.W)

            # Mapping selection
            map_frame = ttk.Frame(mapping_frame)
            map_frame.pack(fill=tk.X, pady=(5, 0))

            ttk.Label(map_frame, text="Map to:").pack(side=tk.LEFT)

            # Dropdown for available columns
            combo_var = tk.StringVar()
            combo = ttk.Combobox(
                map_frame,
                textvariable=combo_var,
                values=["-- Select Column --"] + self.available_columns,
                state="readonly",
                width=30,
            )
            combo.set("-- Select Column --")
            combo.pack(side=tk.LEFT, padx=(10, 0))

            self.combo_vars[missing_col] = combo_var

            # Add separator
            if i < len(self.missing_columns) - 1:
                ttk.Separator(parent, orient=tk.HORIZONTAL).pack(
                    fill=tk.X, pady=10, padx=10
                )

    def _create_buttons(self, parent: ttk.Frame) -> None:
        """Create OK and Cancel buttons."""
        button_frame = ttk.Frame(parent)
        button_frame.pack(pady=(20, 0))

        ttk.Button(button_frame, text="OK", command=self._ok_clicked).pack(
            side=tk.LEFT, padx=(0, 10)
        )
        ttk.Button(button_frame, text="Cancel", command=self._cancel_clicked).pack(
            side=tk.LEFT
        )

    def _ok_clicked(self) -> None:
        """Handle OK button click with validation."""
        result = {}
        unmapped_columns = []
        used_columns = {}  # Track which Excel columns have been used

        # Validate mappings
        for required_col, combo_var in self.combo_vars.items():
            selected = combo_var.get()
            if selected and selected != "-- Select Column --":
                # Check for duplicate mappings
                if selected in used_columns:
                    self._show_duplicate_error(
                        [selected], used_columns[selected], required_col
                    )
                    return

                result[selected] = required_col
                used_columns[selected] = required_col
            else:
                unmapped_columns.append(required_col)

        # Check for unmapped columns
        if unmapped_columns:
            self._show_unmapped_error(unmapped_columns)
            return

        self.result = result
        self.window.destroy()

    def _show_duplicate_error(
        self, target_columns: List[str], source_column: str, new_mapping: str
    ) -> None:
        """Show error for duplicate column mapping."""
        messagebox.showerror(
            "Duplicate Mapping",
            f"Column '{source_column}' is already mapped to '{target_columns[0]}'.\n"
            f"Each Excel column can only be mapped to one required column.\n\n"
            f"Please select a different column for '{new_mapping}'.",
        )

    def _show_unmapped_error(self, unmapped_columns: List[str]) -> None:
        """Show error for unmapped columns."""
        messagebox.showerror(
            "Incomplete Mapping",
            f"Please map all required columns. Unmapped:\n"
            + "\n".join(f"• {col}" for col in unmapped_columns),
        )

    def _cancel_clicked(self) -> None:
        """Handle Cancel button click."""
        self.result = None
        self.window.destroy()


class ColumnMapper:
    """Handles column validation and mapping operations."""

    def __init__(self, required_columns: List[str]):
        """Initialize the column mapper.

        Args:
            required_columns (List[str]): List of column names that are required
        """
        self.required_columns = required_columns

    def show_mapping_dialog(
        self, parent, available_columns: List[str], missing_columns: List[str]
    ) -> Optional[Dict[str, str]]:
        """Show column mapping dialog and return results.

        Args:
            parent: Parent tkinter window
            available_columns (List[str]): List of column names available in the Excel file
            missing_columns (List[str]): List of required column names that are missing

        Returns:
            Optional[Dict[str, str]]: Dictionary mapping available column names to required
                                    column names, or None if dialog was cancelled
        """
        dialog = ColumnMappingDialog(parent, available_columns, missing_columns)
        parent.wait_window(dialog.window)
        return dialog.result
