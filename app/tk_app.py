#!/usr/bin/env python3
"""
Tkinter application wiring for the Abstract Renumber Tool.
"""

import os
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, ttk
from typing import Optional, Tuple

from adapters.ui_tkinter import TkinterUIAdapter
from core.app_controller import AppController


class AbstractRenumberGUI:
    """Handles the GUI components and user interactions."""

    def __init__(self, root: tk.Tk, controller: "AbstractRenumberTool") -> None:
        self.root = root
        self.controller = controller
        self.excel_file: Optional[str] = None
        self.pdf_file: Optional[str] = None
        self.backup_enabled: tk.BooleanVar = tk.BooleanVar(
            value=True
        )  # Backup enabled by default
        self.sort_bookmarks_enabled: tk.BooleanVar = tk.BooleanVar(
            value=False
        )  # Sort bookmarks disabled by default
        self.reorder_pages_enabled: tk.BooleanVar = tk.BooleanVar(
            value=False
        )  # Reorder pages disabled by default

        # Filter UI state (selection will be prompted during processing)
        self.filter_enabled: tk.BooleanVar = tk.BooleanVar(value=False)
        self.filter_column: Optional[str] = None
        self.filter_values: list[str] = []
        self._filter_prompt_requested: bool = False

        # Merge UI state
        self.merge_enabled: tk.BooleanVar = tk.BooleanVar(value=False)
        self.merge_pairs: list[tuple[str, str]] = []

        # Initialize GUI components
        self.excel_label: Optional[ttk.Label] = None
        self.pdf_label: Optional[ttk.Label] = None
        self.process_button: Optional[ttk.Button] = None
        self.status_text: Optional[tk.Text] = None
        self.backup_checkbox: Optional[ttk.Checkbutton] = None
        self.backup_info_label: Optional[ttk.Label] = None
        self.sort_bookmarks_checkbox: Optional[ttk.Checkbutton] = None
        self.reorder_pages_checkbox: Optional[ttk.Checkbutton] = None
        self.reorder_pages_info_label: Optional[ttk.Label] = None

        self.setup_window()
        self.setup_gui()

    def setup_window(self) -> None:
        """Setup main window properties."""
        self.root.title("Abstract Renumber Tool")
        self.root.geometry("900x700")
        self.root.resizable(True, True)

        # Center window
        self._center_window()

        # Configure grid weights
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

    def _center_window(self) -> None:
        """Center the main window on the screen."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        pos_x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        pos_y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{pos_x}+{pos_y}")

    def setup_gui(self) -> None:
        """Initialize GUI components."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.grid_rowconfigure(6, weight=1)  # Updated for new row
        main_frame.grid_columnconfigure(1, weight=1)

        # Title
        title_label = ttk.Label(
            main_frame, text="Abstract Renumber Tool", font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # File selection
        self._create_file_selection(main_frame)

        # Backup options
        self._create_backup_options(main_frame)

        # Process button
        self.process_button = ttk.Button(
            main_frame,
            text="Process Files",
            command=self.controller.process_files,
            state="disabled",
        )
        self.process_button.grid(row=5, column=0, columnspan=2, pady=20)

        # Status area
        self._create_status_area(main_frame)

        # Initial status
        self.log_status("Ready. Please select Excel and PDF files.")

    def _create_file_selection(self, parent: ttk.Frame) -> None:
        """Create file selection components."""
        # Section header
        ttk.Label(parent, text="Select Files:", font=("Arial", 12, "bold")).grid(
            row=1, column=0, columnspan=2, sticky=tk.W, pady=(0, 10)
        )

        # Excel file
        ttk.Label(parent, text="Excel File:").grid(row=2, column=0, sticky=tk.W, pady=5)
        excel_frame = ttk.Frame(parent)
        excel_frame.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        excel_frame.grid_columnconfigure(1, weight=1)

        ttk.Button(excel_frame, text="Browse...", command=self._select_excel_file).grid(
            row=0, column=0, sticky=tk.W
        )
        self.excel_label = ttk.Label(
            excel_frame, text="No file selected", foreground="gray"
        )
        self.excel_label.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))

        # PDF file
        ttk.Label(parent, text="PDF File:").grid(row=3, column=0, sticky=tk.W, pady=5)
        pdf_frame = ttk.Frame(parent)
        pdf_frame.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        pdf_frame.grid_columnconfigure(1, weight=1)

        ttk.Button(pdf_frame, text="Browse...", command=self._select_pdf_file).grid(
            row=0, column=0, sticky=tk.W
        )
        self.pdf_label = ttk.Label(
            pdf_frame, text="No file selected", foreground="gray"
        )
        self.pdf_label.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))

    def _create_backup_options(self, parent: ttk.Frame) -> None:
        """Create backup options section with checkbox."""
        # Options frame
        options_frame = ttk.LabelFrame(parent, text="Processing Options", padding="10")
        options_frame.grid(
            row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0)
        )
        options_frame.grid_columnconfigure(0, weight=1)

        # Backup checkbox with description
        backup_frame = ttk.Frame(options_frame)
        backup_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        backup_frame.grid_columnconfigure(1, weight=1)

        self.backup_checkbox = ttk.Checkbutton(
            backup_frame,
            text="Create backup files before processing",
            variable=self.backup_enabled,
            command=self._on_backup_option_changed,
        )
        self.backup_checkbox.grid(row=0, column=0, sticky=tk.W)

        # Info label for backup option
        self.backup_info_label = ttk.Label(
            backup_frame,
            text="✅ Recommended: Creates timestamped backups for safety",
            foreground="green",
            font=("Arial", 9),
        )
        self.backup_info_label.grid(
            row=1, column=0, sticky=tk.W, padx=(20, 0), pady=(2, 0)
        )

        # Sort PDF Bookmarks checkbox
        sort_bookmarks_frame = ttk.Frame(options_frame)
        sort_bookmarks_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(15, 5))
        sort_bookmarks_frame.grid_columnconfigure(1, weight=1)

        self.sort_bookmarks_checkbox = ttk.Checkbutton(
            sort_bookmarks_frame,
            text="Sort PDF Bookmarks",
            variable=self.sort_bookmarks_enabled,
            command=self._on_sort_bookmarks_option_changed,
        )
        self.sort_bookmarks_checkbox.grid(row=0, column=0, sticky=tk.W)

        # Reorder Pages checkbox (initially disabled)
        reorder_pages_frame = ttk.Frame(options_frame)
        reorder_pages_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=5)
        reorder_pages_frame.grid_columnconfigure(1, weight=1)

        self.reorder_pages_checkbox = ttk.Checkbutton(
            reorder_pages_frame,
            text="Reorder Pages to Match Bookmarks",
            variable=self.reorder_pages_enabled,
            state="disabled",  # Initially disabled
        )
        self.reorder_pages_checkbox.grid(row=0, column=0, sticky=tk.W, padx=(20, 0))

        # Info label for reorder pages option
        self.reorder_pages_info_label = ttk.Label(
            reorder_pages_frame,
            text="Requires 'Sort PDF Bookmarks' to be enabled",
            foreground="gray",
            font=("Arial", 9),
        )
        self.reorder_pages_info_label.grid(
            row=1, column=0, sticky=tk.W, padx=(40, 0), pady=(2, 0)
        )

        # Filter controls
        filter_frame = ttk.Frame(options_frame)
        filter_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(15, 5))
        filter_frame.grid_columnconfigure(2, weight=1)

        ttk.Checkbutton(
            filter_frame,
            text="Enable Filter (choose values during processing)",
            variable=self.filter_enabled,
        ).grid(row=0, column=0, sticky=tk.W)

        self.filter_summary_label = ttk.Label(
            filter_frame,
            text="",
            foreground="gray",
            font=("Arial", 9),
        )
        self.filter_summary_label.grid(
            row=1, column=0, columnspan=2, sticky=tk.W, padx=(20, 0)
        )

        def on_filter_toggle(*_args):
            if self.filter_enabled.get():
                self.filter_summary_label.config(
                    text="Will prompt for column and values after loading Excel",
                    foreground="green",
                )
            else:
                self.filter_summary_label.config(text="", foreground="gray")

        self.filter_enabled.trace_add("write", on_filter_toggle)

        # Merge controls
        merge_frame = ttk.Frame(options_frame)
        merge_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(5, 5))
        merge_frame.grid_columnconfigure(2, weight=1)

        ttk.Checkbutton(
            merge_frame,
            text="Enable Merge (select pairs)",
            variable=self.merge_enabled,
        ).grid(row=0, column=0, sticky=tk.W)

        merge_btn = ttk.Button(
            merge_frame,
            text="Pairs…",
            command=self._on_choose_merge_pairs,
            state="disabled",
            width=10,
        )
        merge_btn.grid(row=0, column=1, padx=(12, 0), sticky=tk.W)

        self.merge_summary_label = ttk.Label(
            merge_frame,
            text="",
            foreground="gray",
            font=("Arial", 9),
        )
        self.merge_summary_label.grid(
            row=1, column=0, columnspan=2, sticky=tk.W, padx=(20, 0)
        )

        def on_merge_toggle(*_args):
            if self.merge_enabled.get():
                merge_btn.config(state="normal")
                # Disable backups while merge is enabled
                self.backup_enabled.set(False)
                self.backup_checkbox.config(state="disabled")
                self.backup_info_label.config(
                    text="Backups disabled during merge (originals untouched)",
                    foreground="gray",
                )
                self.merge_summary_label.config(
                    text="Select one or more (Excel, PDF) pairs",
                    foreground="green",
                )
            else:
                merge_btn.config(state="disabled")
                self.backup_checkbox.config(state="normal")
                self.backup_info_label.config(
                    text="✅ Recommended: Creates timestamped backups for safety",
                    foreground="green",
                )
                self.merge_summary_label.config(text="", foreground="gray")

        self.merge_enabled.trace_add("write", on_merge_toggle)

    def _on_backup_option_changed(self) -> None:
        """Handle changes to the backup option checkbox."""
        if self.backup_enabled.get():
            self.backup_info_label.config(
                text="✅ Recommended: Creates timestamped backups for safety",
                foreground="green",
            )
        else:
            self.backup_info_label.config(
                text="⚠️  Warning: Original files will be overwritten directly",
                foreground="orange",
            )

    def _on_sort_bookmarks_option_changed(self) -> None:
        """Handle changes to the sort bookmarks option checkbox."""
        if self.sort_bookmarks_enabled.get():
            # Enable and check the reorder pages checkbox when sort bookmarks is checked
            self.reorder_pages_checkbox.config(state="normal")
            self.reorder_pages_enabled.set(True)  # Auto-check by default
            self.reorder_pages_info_label.config(
                text="Optional: Physically reorder pages to match sorted bookmarks",
                foreground="green",
            )
        else:
            # Disable and uncheck the reorder pages checkbox when sort bookmarks is unchecked
            self.reorder_pages_enabled.set(False)
            self.reorder_pages_checkbox.config(state="disabled")
            self.reorder_pages_info_label.config(
                text="Requires 'Sort PDF Bookmarks' to be enabled", foreground="gray"
            )

    # choose button removed; filter will be prompted during processing when enabled

    def _on_choose_merge_pairs(self) -> None:
        """Open pairs dialog via adapter and store results on the GUI."""
        try:
            pairs = self.controller.ui_adapter.prompt_merge_pairs()
        except Exception:
            pairs = None
        self.merge_pairs = list(pairs or [])
        if self.merge_pairs:
            preview = len(self.merge_pairs)
            self.merge_summary_label.config(
                text=f"Pairs selected: {preview}", foreground="green"
            )
        else:
            self.merge_summary_label.config(text="No pairs selected", foreground="gray")

    def _create_status_area(self, parent: ttk.Frame) -> None:
        """Create status text area with scrollbar."""
        status_frame = ttk.LabelFrame(parent, text="Status", padding="10")
        status_frame.grid(
            row=6,
            column=0,
            columnspan=2,
            sticky=(tk.W, tk.E, tk.N, tk.S),
            pady=(20, 0),  # Updated row number
        )
        status_frame.grid_rowconfigure(0, weight=1)
        status_frame.grid_columnconfigure(0, weight=1)

        self.status_text = tk.Text(status_frame, height=8, width=70, wrap=tk.WORD)
        self.status_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        scrollbar = ttk.Scrollbar(
            status_frame, orient="vertical", command=self.status_text.yview
        )
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.status_text.configure(yscrollcommand=scrollbar.set)

    def _get_default_directory(self) -> str:
        """Get the user's Downloads directory."""
        downloads_path = Path.home() / "Downloads"
        return str(downloads_path) if downloads_path.exists() else str(Path.home())

    def _select_excel_file(self) -> None:
        """Handle Excel file selection."""
        file_path = filedialog.askopenfilename(
            title="Select Excel File",
            initialdir=self._get_default_directory(),
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")],
        )

        if file_path:
            self.excel_file = file_path
            self.excel_label.config(
                text=os.path.basename(file_path), foreground="black"
            )
            self._check_files_ready()

    def _select_pdf_file(self) -> None:
        """Handle PDF file selection."""
        file_path = filedialog.askopenfilename(
            title="Select PDF File",
            initialdir=self._get_default_directory(),
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
        )

        if file_path:
            self.pdf_file = file_path
            self.pdf_label.config(text=os.path.basename(file_path), foreground="black")
            self._check_files_ready()

    def _check_files_ready(self) -> None:
        """Enable process button if both files are selected."""
        if self.excel_file and self.pdf_file:
            self.process_button.config(state="normal")
            self.log_status("Ready to process!")
        else:
            self.process_button.config(state="disabled")

    def log_status(self, message: str) -> None:
        """Add a timestamped message to the status text."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.status_text.see(tk.END)
        self.root.update()

    def get_selected_files(self) -> Tuple[Optional[str], Optional[str]]:
        """Return the selected file paths."""
        return self.excel_file, self.pdf_file

    def get_backup_enabled(self) -> bool:
        """Return whether backup creation is enabled."""
        return self.backup_enabled.get()

    def get_sort_bookmarks_enabled(self) -> bool:
        """Return whether PDF bookmark sorting is enabled."""
        return self.sort_bookmarks_enabled.get()

    def get_reorder_pages_enabled(self) -> bool:
        """Return whether page reordering is enabled."""
        return self.reorder_pages_enabled.get()

    # Accessors for filter state (used by UI adapter/controller later)
    def get_filter_enabled(self) -> bool:
        return self.filter_enabled.get()

    def get_filter_prompt_requested(self) -> bool:
        return self._filter_prompt_requested

    def set_filter_selection(self, column: Optional[str], values: list[str]) -> None:
        self.filter_column = column
        self.filter_values = list(values or [])
        if column and values:
            preview = ", ".join(values[:3]) + (" …" if len(values) > 3 else "")
            self.filter_summary_label.config(
                text=f"Filter: {column} ∈ [{preview}]", foreground="green"
            )
        else:
            self.filter_summary_label.config(text="", foreground="gray")

    def get_merge_enabled(self) -> bool:
        return self.merge_enabled.get()

    def get_merge_pairs(self) -> list[tuple[str, str]]:
        return list(self.merge_pairs)

    def reset_gui(self) -> None:
        """Reset GUI to initial state after successful processing."""
        # Reset file selections
        self.excel_file = None
        self.pdf_file = None

        # Reset file labels
        self.excel_label.config(text="No file selected", foreground="gray")
        self.pdf_label.config(text="No file selected", foreground="gray")

        # Reset filter state
        self.filter_enabled.set(False)
        self.filter_column = None
        self.filter_values = []
        self._filter_prompt_requested = False

        # Reset merge state
        self.merge_enabled.set(False)
        self.merge_pairs = []

        # Reset filter summary label
        if hasattr(self, "filter_summary_label"):
            self.filter_summary_label.config(text="", foreground="gray")

        # Reset merge summary label
        if hasattr(self, "merge_summary_label"):
            self.merge_summary_label.config(text="", foreground="gray")

        # Disable process button
        self.process_button.config(state="disabled")

        # Clear status log but keep recent completion message
        if self.status_text:
            # Keep the last few lines (completion messages)
            content = self.status_text.get("1.0", tk.END)
            lines = content.strip().split("\n")

            # Keep last 3 lines if they exist (completion, success, etc.)
            keep_lines = lines[-3:] if len(lines) >= 3 else lines

            # Clear and add kept lines plus reset message
            self.status_text.delete("1.0", tk.END)
            for line in keep_lines:
                if line.strip():  # Only add non-empty lines
                    self.status_text.insert(tk.END, f"{line}\n")

        # Log reset
        self.log_status("GUI reset - ready for new files!")

        # Note: We keep backup/sort/reorder settings as they are user preferences


class AbstractRenumberTool:
    """Main application that wires up GUI and controller."""

    def __init__(self):
        """Initialize the Abstract Renumber Tool."""
        self.root = tk.Tk()
        self.gui = AbstractRenumberGUI(self.root, self)

        # Wire up UI abstraction
        self.ui_adapter = TkinterUIAdapter(self.gui)
        self.controller = AppController(self.ui_adapter)

    def process_files(self):
        """Delegate to the controller."""
        self.controller.process_files()

    def run(self) -> None:
        """Start the GUI application."""
        self.root.mainloop()
