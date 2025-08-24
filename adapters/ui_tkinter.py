#!/usr/bin/env python3
"""
Tkinter UI adapter that implements the UIController interface.
"""

from typing import Any, List, Optional, Tuple

from core.interfaces import UIController
from core.models import Options


class TkinterUIAdapter:
    """Tkinter implementation of UIController interface."""

    def __init__(self, gui: Any) -> None:
        """Initialize with existing GUI instance."""
        self.gui = gui

    def get_file_paths(self) -> Tuple[Optional[str], Optional[str]]:
        """Get selected Excel and PDF file paths."""
        return self.gui.get_selected_files()

    def get_options(self) -> Options:
        """Get processing options from UI."""
        return Options(
            backup=self.gui.get_backup_enabled(),
            sort_bookmarks=self.gui.get_sort_bookmarks_enabled(),
            reorder_pages=self.gui.get_reorder_pages_enabled(),
            sheet_name=None,  # Will be set separately
        )

    def log_status(self, message: str) -> None:
        """Log a status message to the UI."""
        self.gui.log_status(message)

    def show_error(self, title: str, message: str) -> None:
        """Show an error message to the user."""
        from tkinter import messagebox

        self.gui.log_status(f"Error: {message}")
        messagebox.showerror(title, message)

    def show_success(self, message: str) -> None:
        """Show a success message to the user."""
        from tkinter import messagebox

        self.gui.log_status("Complete!")
        messagebox.showinfo("Processing Complete", message)

    def prompt_sheet_selection(
        self,
        file_path: str,
        sheet_names: List[str],
        default_sheet: Optional[str] = None,
    ) -> Optional[str]:
        """Prompt user to select a sheet from available options."""
        import tkinter as tk
        from tkinter import ttk

        if not sheet_names:
            return None

        # Determine default selection
        default_index = 0
        if default_sheet:
            desired = default_sheet.lower()
            for i, name in enumerate(sheet_names):
                if name.lower() == desired:
                    default_index = i
                    break

        # Modal dialog with dropdown
        self.log_status("Select processing sheet...")
        self.gui.root.update()

        dialog = tk.Toplevel(self.gui.root)
        dialog.title("Select Sheet")
        dialog.transient(self.gui.root)
        dialog.grab_set()

        expected = default_sheet or "Index"
        msg = (
            f"Warning: The Excel file does not contain a worksheet named '{expected}'.\n\n"
            "Please select the worksheet that needs to be processed."
        )
        ttk.Label(dialog, text=msg, wraplength=420, justify=tk.LEFT).grid(
            row=0, column=0, columnspan=2, padx=12, pady=(12, 6), sticky=tk.W
        )

        selected_var = tk.StringVar(value=sheet_names[default_index])
        combo = ttk.Combobox(
            dialog,
            state="readonly",
            values=sheet_names,
            textvariable=selected_var,
            width=40,
        )
        combo.grid(
            row=1,
            column=0,
            columnspan=2,
            padx=12,
            pady=(0, 12),
            sticky=(tk.W, tk.E),
        )
        combo.current(default_index)

        chosen = {"value": None}

        def on_ok():
            chosen["value"] = selected_var.get()
            dialog.destroy()

        def on_cancel():
            chosen["value"] = None
            dialog.destroy()

        ok_btn = ttk.Button(dialog, text="OK", command=on_ok)
        cancel_btn = ttk.Button(dialog, text="Cancel", command=on_cancel)
        ok_btn.grid(row=2, column=0, padx=(12, 6), pady=(0, 12), sticky=tk.E)
        cancel_btn.grid(row=2, column=1, padx=(6, 12), pady=(0, 12), sticky=tk.W)

        dialog.bind("<Return>", lambda _: on_ok())
        dialog.bind("<Escape>", lambda _: on_cancel())
        dialog.wait_window(dialog)

        return chosen["value"]
