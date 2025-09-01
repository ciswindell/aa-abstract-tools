#!/usr/bin/env python3
"""
Tkinter UI adapter that implements the UIController interface.
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Any, List, Optional, Tuple

# Note: UIController Protocol imported where needed; not required here.
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
        filter_enabled = (
            getattr(self.gui, "get_filter_enabled", None)
            and self.gui.get_filter_enabled()
        )
        filter_column = (
            getattr(self.gui, "filter_column", None) if filter_enabled else None
        )
        filter_values = (
            list(getattr(self.gui, "filter_values", []) or [])
            if filter_enabled
            else None
        )

        merge_pairs = (
            list(getattr(self.gui, "merge_pairs", []) or [])
            if getattr(self.gui, "get_merge_enabled", None)
            and self.gui.get_merge_enabled()
            else None
        )

        return Options(
            backup=self.gui.get_backup_enabled(),
            sort_bookmarks=self.gui.get_sort_bookmarks_enabled(),
            reorder_pages=self.gui.get_reorder_pages_enabled(),
            check_document_images=self.gui.get_check_document_images_enabled(),
            sheet_name=None,  # Will be set separately
            filter_enabled=bool(filter_enabled),
            filter_column=filter_column,
            filter_values=filter_values,
            merge_pairs=merge_pairs,
        )

    def log_status(self, message: str) -> None:
        """Log a status message to the UI."""
        self.gui.log_status(message)

    def show_error(self, title: str, message: str) -> None:
        """Show an error message to the user."""
        self.gui.log_status(f"Error: {message}")

        # For validation errors (long messages with many lines), use custom dialog
        if len(message) > 300 or message.count("\n") > 10:
            self._show_scrollable_error(title, message)
        else:
            messagebox.showerror(title, message)

    def _show_scrollable_error(self, title: str, message: str) -> None:
        """Show error in a scrollable dialog for long messages."""
        dialog = tk.Toplevel(self.gui.root)
        dialog.title(title)
        dialog.transient(self.gui.root)
        dialog.grab_set()
        dialog.geometry("500x400")
        dialog.resizable(True, True)

        # Text widget with scrollbar
        frame = ttk.Frame(dialog)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        text = tk.Text(frame, wrap="word", font=("Arial", 9))
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=text.yview)
        text.configure(yscrollcommand=scrollbar.set)

        text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        text.insert("1.0", message)
        text.configure(state="disabled")

        # OK button
        ttk.Button(dialog, text="OK", command=dialog.destroy).pack(pady=10)

        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() - dialog.winfo_width()) // 2
        y = (dialog.winfo_screenheight() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")

    def show_success(self, message: str) -> None:
        """Show a success message to the user."""
        self.gui.log_status("Complete!")
        messagebox.showinfo("Processing Complete", message)

    def reset_gui(self) -> None:
        """Reset GUI to initial state after successful processing."""
        self.gui.reset_gui()

    def prompt_sheet_selection(
        self,
        file_path: str,
        sheet_names: List[str],
        default_sheet: Optional[str] = None,
    ) -> Optional[str]:
        """Prompt user to select a sheet from available options."""

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

        from pathlib import Path

        filename = Path(file_path).name

        dialog = tk.Toplevel(self.gui.root)
        dialog.title(f"Select Sheet - {filename}")
        dialog.transient(self.gui.root)
        dialog.grab_set()

        expected = default_sheet or "Index"
        msg = (
            f"Warning: The Excel file '{filename}' does not contain a worksheet named '{expected}'.\n\n"
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

    def prompt_filter_selection(self, df):
        """Prompt user to choose a column and values to filter by.

        Returns (column_name, values) or (None, []).
        """

        if df is None or df.empty:
            return None, []

        columns = [c for c in df.columns if str(c).strip()]
        if not columns:
            return None, []

        self.log_status("Select filter column and values (optional)...")
        self.gui.root.update()

        dialog = tk.Toplevel(self.gui.root)
        dialog.title("Filter Records")
        dialog.transient(self.gui.root)
        dialog.grab_set()

        ttk.Label(dialog, text="Column:").grid(
            row=0, column=0, padx=12, pady=(12, 6), sticky=tk.W
        )
        col_var = tk.StringVar(value=columns[0])
        col_combo = ttk.Combobox(
            dialog, state="readonly", values=columns, textvariable=col_var, width=40
        )
        col_combo.grid(row=0, column=1, padx=12, pady=(12, 6), sticky=(tk.W, tk.E))

        ttk.Label(dialog, text="Values (multi-select):").grid(
            row=1, column=0, padx=12, pady=(6, 6), sticky=tk.W
        )
        values_listbox = tk.Listbox(dialog, selectmode=tk.MULTIPLE, width=42, height=10)
        values_listbox.grid(row=1, column=1, padx=12, pady=(6, 6), sticky=(tk.W, tk.E))

        def refresh_values(*_):
            values_listbox.delete(0, tk.END)
            col = col_var.get()
            distinct = (
                sorted({str(v).strip() for v in df[col].unique()})
                if col in df.columns
                else []
            )
            for v in distinct:
                values_listbox.insert(tk.END, v)

        col_combo.bind("<<ComboboxSelected>>", refresh_values)
        refresh_values()

        chosen = {"column": None, "values": []}

        def on_ok():
            chosen["column"] = col_var.get()
            sel = [values_listbox.get(i) for i in values_listbox.curselection()]
            chosen["values"] = sel
            dialog.destroy()

        def on_cancel():
            chosen["column"] = None
            chosen["values"] = []
            dialog.destroy()

        btn_frame = ttk.Frame(dialog)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=(6, 12))
        ttk.Button(btn_frame, text="OK", command=on_ok).grid(
            row=0, column=0, padx=(0, 6)
        )
        ttk.Button(btn_frame, text="Cancel", command=on_cancel).grid(row=0, column=1)

        dialog.bind("<Return>", lambda _: on_ok())
        dialog.bind("<Escape>", lambda _: on_cancel())
        dialog.wait_window(dialog)

        return chosen["column"], chosen["values"]

    def prompt_merge_pairs(self):
        """Prompt user to add one or more (Excel, PDF) pairs for merge.

        Returns list of (excel_path, pdf_path) or None if canceled.
        """

        self.log_status("Select pairs to merge…")
        self.gui.root.update()

        dialog = tk.Toplevel(self.gui.root)
        dialog.title("Merge Pairs")
        dialog.transient(self.gui.root)
        dialog.grab_set()

        cols = ("Excel", "PDF")
        tree = ttk.Treeview(dialog, columns=cols, show="headings", height=8)
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=320, anchor=tk.W)
        tree.grid(
            row=0, column=0, columnspan=3, padx=12, pady=(12, 6), sticky=(tk.W, tk.E)
        )

        def add_pair():
            excel_path = filedialog.askopenfilename(
                title="Select Excel File",
                filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")],
            )
            if not excel_path:
                return
            pdf_path = filedialog.askopenfilename(
                title="Select PDF File",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            )
            if not pdf_path:
                return
            tree.insert("", tk.END, values=(excel_path, pdf_path))

        def remove_selected():
            for item in tree.selection():
                tree.delete(item)

        ttk.Button(dialog, text="Add Pair", command=add_pair).grid(
            row=1, column=0, padx=(12, 6), pady=(6, 6), sticky=tk.W
        )
        ttk.Button(dialog, text="Remove Selected", command=remove_selected).grid(
            row=1, column=1, padx=(6, 6), pady=(6, 6), sticky=tk.W
        )

        chosen = {"pairs": None}

        def on_ok():
            pairs = []
            for iid in tree.get_children(""):
                excel_path, pdf_path = tree.item(iid, "values")
                if excel_path and pdf_path:
                    pairs.append((excel_path, pdf_path))
            chosen["pairs"] = pairs
            dialog.destroy()

        def on_cancel():
            chosen["pairs"] = None
            dialog.destroy()

        ttk.Button(dialog, text="OK", command=on_ok).grid(
            row=1, column=2, padx=(6, 12), pady=(6, 6), sticky=tk.E
        )

        dialog.bind("<Return>", lambda _: on_ok())
        dialog.bind("<Escape>", lambda _: on_cancel())
        dialog.wait_window(dialog)

        return chosen["pairs"]
