#!/usr/bin/env python3
"""
Abstract Renumber Tool
A class-based application for sorting Excel data and renumbering PDF bookmarks.
"""

import os
import shutil
import time
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Dict, List, Optional, Tuple

from column_mapper import ColumnMapper

# Import our modular classes
from excel_processor import ExcelProcessor
from pdf_processor import PDFProcessor


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

        self.setup_window()
        self.setup_gui()

    def setup_window(self) -> None:
        """Setup main window properties."""
        self.root.title("Abstract Renumber Tool")
        self.root.geometry("600x500")
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

    def _on_backup_option_changed(self) -> None:
        """Handle changes to the backup option checkbox."""
        if self.backup_enabled.get():
            self.backup_info_label.config(
                text="✅ Recommended: Creates timestamped backups for safety",
                foreground="green",
            )
            self.log_status("Backup files will be created before processing")
        else:
            self.backup_info_label.config(
                text="⚠️  Warning: Original files will be overwritten directly",
                foreground="orange",
            )
            self.log_status(
                "Warning: Backup creation disabled - original files will be overwritten"
            )

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
            self.log_status(f"Excel file selected: {os.path.basename(file_path)}")
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
            self.log_status(f"PDF file selected: {os.path.basename(file_path)}")
            self._check_files_ready()

    def _check_files_ready(self) -> None:
        """Enable process button if both files are selected."""
        if self.excel_file and self.pdf_file:
            self.process_button.config(state="normal")
            self.log_status("Both files selected. Ready to process!")
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


class AbstractRenumberTool:
    """Main application controller that orchestrates the components."""

    def __init__(self):
        """Initialize the Abstract Renumber Tool with required configuration."""
        # Configuration
        self.required_columns = [
            "Index#",
            "Document Type",
            "Legal Description",
            "Grantee",
            "Grantor",
            "Document Date",
            "Received Date",
        ]

        # Initialize components
        self.root = tk.Tk()
        self.excel_processor = ExcelProcessor(self.required_columns)
        self.column_mapper = ColumnMapper(self.required_columns)
        self.gui = AbstractRenumberGUI(self.root, self)

    def process_files(self):
        """Main processing function that orchestrates Excel and PDF file processing.

        Raises:
            Exception: If processing fails at any stage, logged via GUI with user feedback
        """
        try:
            excel_file, pdf_file = self.gui.get_selected_files()

            # Process Excel file
            if not self._process_excel_file(excel_file):
                return

            self.gui.log_status("Excel validation completed successfully!")

            # Perform Excel processing (sorting, renumbering)
            self._perform_excel_processing()

        except Exception as e:
            self.gui.log_status(f"Processing failed: {str(e)}")

            # Attempt rollback only if backups were created
            if (
                self.gui.get_backup_enabled()
                and self.gui.excel_file
                and self.gui.pdf_file
            ):
                self._attempt_rollback(
                    self.gui.excel_file,
                    self.gui.pdf_file,
                    self.gui.excel_file,
                    self.gui.pdf_file,
                )

            # Update error message based on backup status and rollback result
            error_message = self._generate_error_message(
                e, self.gui.get_backup_enabled(), self.gui.excel_file, self.gui.pdf_file
            )
            messagebox.showerror("Processing Error", error_message)
            raise ValueError(f"Processing failed: {str(e)}")

    def _process_excel_file(self, file_path: str) -> bool:
        """Process Excel file with validation and mapping."""
        try:
            # Load file
            self.gui.log_status("Loading Excel file...")
            self.excel_processor.load_file(file_path)

            # Get file info
            info = self.excel_processor.get_column_info()
            self.gui.log_status(
                f"✓ Excel file loaded: {info['rows']} rows, {info['columns']} columns"
            )

            # Check for duplicate columns
            duplicates = self.excel_processor.check_duplicate_columns()
            if duplicates:
                self.gui.log_status(
                    f"Warning: Found duplicate column names: {duplicates}"
                )
                messagebox.showwarning(
                    "Duplicate Columns",
                    f"The Excel file has duplicate column names:\n"
                    + "\n".join(f"• {col}" for col in duplicates)
                    + "\n\nThis may cause issues.",
                )

            # Validate columns
            missing_columns = self.excel_processor.validate_columns()
            if missing_columns:
                return self._handle_missing_columns(
                    missing_columns, info["column_names"]
                )

            self.gui.log_status("✓ All required columns are present.")
            return True

        except FileNotFoundError as e:
            self._handle_error("File Not Found", str(e))
            return False
        except PermissionError as e:
            self._handle_error(
                "Permission Error",
                f"Cannot access Excel file:\n{str(e)}\n\n"
                "Please check file permissions and ensure the file is not open.",
            )
            return False
        except ValueError as e:
            self._handle_error("Invalid File", str(e))
            return False
        except Exception as e:
            self._handle_error(
                "Error",
                f"Failed to load Excel file:\n{str(e)}\n\n"
                "Please ensure the file is a valid Excel file.",
            )
            return False

    def _handle_missing_columns(
        self, missing_columns: List[str], available_columns: List[str]
    ) -> bool:
        """Handle missing columns with mapping dialog."""
        self.gui.log_status(f"Missing required columns: {missing_columns}")
        self.gui.log_status("Opening column mapping dialog...")

        mapping = self.column_mapper.show_mapping_dialog(
            self.root, available_columns, missing_columns
        )

        if mapping:
            try:
                self.gui.log_status(f"Applying {len(mapping)} column mappings...")
                for old_name, new_name in mapping.items():
                    self.gui.log_status(f"Mapping '{old_name}' → '{new_name}'")

                self.excel_processor.apply_column_mapping(mapping)
                self.gui.log_status("✓ Column mapping applied successfully!")
                self.gui.log_status("✓ All required columns are now present.")
                return True

            except Exception as e:
                self._handle_error("Mapping Error", f"Column mapping failed:\n{str(e)}")
                return False
        else:
            self.gui.log_status("Column mapping cancelled.")
            return False

    def _handle_error(self, title: str, message: str):
        """Handle errors with consistent logging and user feedback."""
        self.gui.log_status(f"Error: {message}")
        messagebox.showerror(title, message)

    def _perform_excel_processing(self) -> bool:
        """Perform Excel file processing after validation.

        Returns:
            bool: True if processing completed successfully

        Raises:
            ValueError: If Excel processing fails
        """
        excel_backup_path = None
        pdf_backup_path = None

        try:
            self.gui.log_status("Starting data processing...")

            # Get source file paths
            excel_file, pdf_file = self.gui.get_selected_files()

            # Check if backup is enabled
            backup_enabled = self.gui.get_backup_enabled()

            # Step 1: Comprehensive file access validation (including backup permissions)
            if not self._validate_comprehensive_file_access(
                excel_file, pdf_file, backup_enabled
            ):
                self.gui.log_status(
                    "Processing stopped due to file access validation failures"
                )
                return False

            self.gui.log_status(
                "Creating timestamped backup copies before processing..."
            )
            self.gui.log_status("This ensures your original files are never lost.")

            # Step 2: Generate backup filenames with enhanced validation
            excel_backup_path, pdf_backup_path = self._generate_backup_filenames(
                excel_file, pdf_file
            )

            if backup_enabled:
                # Step 3: Create backup files
                excel_backup_path, pdf_backup_path = self._create_backup_files(
                    excel_file, pdf_file
                )
            else:
                self.gui.log_status(
                    "⚠️  Backup creation disabled - proceeding without backups"
                )
                self.gui.log_status("Original files will be overwritten directly")

            # Step 4: Sort the data according to PRD requirements
            self.gui.log_status(
                "Sorting data by: Legal Description, Grantee, Grantor, Document Type, Document Date, Received Date"
            )
            self.excel_processor.sort_data()
            self.gui.log_status("✓ Data sorted successfully")

            # Step 5: Generate output filenames (now uses original names)
            excel_output_path, pdf_output_path = self._generate_output_filenames(
                excel_file, pdf_file
            )
            self.gui.log_status(
                f"Output files will be: {os.path.basename(excel_output_path)}, {os.path.basename(pdf_output_path)}"
            )

            # Step 6: Save processed Excel file (overwrites original)
            if not self._save_processed_excel_file(excel_output_path):
                self.gui.log_status("Processing stopped due to Excel file save failure")
                # Rollback if Excel file was partially modified and backups exist
                if (
                    backup_enabled
                    and excel_backup_path
                    and os.path.exists(excel_backup_path)
                ):
                    self._attempt_rollback(
                        excel_backup_path, pdf_backup_path, excel_file, pdf_file
                    )
                return False

            # Step 7: Save updated PDF file (overwrites original)
            if not self._save_updated_pdf_file(pdf_output_path):
                self.gui.log_status("Processing stopped due to PDF file save failure")
                # Rollback both files since Excel was successfully saved and backups exist
                if backup_enabled and excel_backup_path and pdf_backup_path:
                    self._attempt_rollback(
                        excel_backup_path, pdf_backup_path, excel_file, pdf_file
                    )
                return False

            # Step 8: Provide success feedback with backup information
            self._show_completion_success(
                excel_output_path, pdf_output_path, excel_backup_path, pdf_backup_path
            )

            return True

        except Exception as e:
            self.gui.log_status(f"Processing failed: {str(e)}")

            # Attempt rollback only if backups were created
            if backup_enabled and excel_backup_path and pdf_backup_path:
                self._attempt_rollback(
                    excel_backup_path, pdf_backup_path, excel_file, pdf_file
                )

            # Update error message based on backup status and rollback result
            error_message = self._generate_error_message(
                e, backup_enabled, excel_backup_path, pdf_backup_path
            )
            messagebox.showerror("Processing Error", error_message)
            raise ValueError(f"Processing failed: {str(e)}")

    def _attempt_rollback(
        self,
        excel_backup_path: str,
        pdf_backup_path: str,
        excel_path: str,
        pdf_path: str,
    ) -> None:
        """Attempt to rollback files with logging."""
        try:
            rollback_success = self._rollback_backup_files(
                excel_backup_path, pdf_backup_path, excel_path, pdf_path
            )

            if rollback_success:
                self.gui.log_status("Original files successfully restored from backup")
            else:
                self.gui.log_status(
                    "Rollback failed - manual file restoration may be needed"
                )

        except Exception as rollback_error:
            self.gui.log_status(f"Rollback also failed: {str(rollback_error)}")

    def _generate_error_message(
        self,
        error: Exception,
        backup_enabled: bool,
        excel_backup_path: str,
        pdf_backup_path: str,
    ) -> str:
        """Generate appropriate error message based on backup status."""
        base_message = (
            f"An unexpected error occurred during processing:\n\n{str(error)}\n\n"
            "Please check the status log for details.\n\n"
        )

        # Handle backup creation failures specifically
        if backup_enabled and "Backup creation failed" in str(error):
            return (
                "Backup creation failed during processing.\n\n"
                f"Error: {str(error)}\n\n"
                "Recovery options:\n"
                "• Check the status log for detailed guidance\n"
                "• Try disabling backup creation and processing again\n"
                "• Resolve the underlying issue (permissions, disk space, etc.)\n\n"
                "No files have been modified since backup creation failed."
            )

        if not backup_enabled:
            return (
                base_message
                + "⚠️  Note: Backup creation was disabled, so files may have been partially modified."
            )

        if excel_backup_path and pdf_backup_path:
            # Check if rollback was attempted and get result from logs
            if "successfully restored from backup" in self.gui.status_text.get(
                "1.0", tk.END
            ):
                return (
                    base_message + "✅ Original files have been restored from backup."
                )
            else:
                return base_message + (
                    f"⚠️  Automatic file restoration failed.\n"
                    f"Backup files are available:\n"
                    f"• {os.path.basename(excel_backup_path) if excel_backup_path else 'N/A'}\n"
                    f"• {os.path.basename(pdf_backup_path) if pdf_backup_path else 'N/A'}\n"
                    "You may need to manually restore these files."
                )

        return base_message

    def _show_completion_success(
        self,
        excel_output_path: str,
        pdf_output_path: str,
        excel_backup_path: str = None,
        pdf_backup_path: str = None,
    ) -> None:
        """Show completion success message with output file paths and backup information.

        Args:
            excel_output_path (str): Path to the saved Excel file
            pdf_output_path (str): Path to the saved PDF file
            excel_backup_path (str, optional): Path to Excel backup file
            pdf_backup_path (str, optional): Path to PDF backup file
        """
        # Log status messages with enhanced backup information
        self.gui.log_status("=" * 70)
        self.gui.log_status("🎉 PROCESSING COMPLETED SUCCESSFULLY! 🎉")
        self.gui.log_status("=" * 70)

        if excel_backup_path and pdf_backup_path:
            self.gui.log_status("🛡️  BACKUP FILES CREATED FOR SAFETY:")
            self.gui.log_status(
                f"  📊 Excel backup: {os.path.basename(excel_backup_path)}"
            )
            self.gui.log_status(
                f"  📄 PDF backup:   {os.path.basename(pdf_backup_path)}"
            )
            self.gui.log_status("")
        else:
            self.gui.log_status("⚠️  NO BACKUP FILES CREATED (backup was disabled)")
            self.gui.log_status("")

        self.gui.log_status("📝 FILES PROCESSED AND SAVED:")
        self.gui.log_status(f"  📊 Excel: {os.path.basename(excel_output_path)}")
        self.gui.log_status(f"  📄 PDF:   {os.path.basename(pdf_output_path)}")
        self.gui.log_status(f"📂 Location: {os.path.dirname(excel_output_path)}")
        self.gui.log_status("=" * 70)

        # Show simple success dialog
        title = "Processing Complete!"

        # Get basic counts for summary
        bookmark_count = ""
        if hasattr(self, "pdf_processor") and self.pdf_processor.bookmarks:
            try:
                excel_data = self.excel_processor.get_dataframe().to_dict("records")
                index_mapping = self.excel_processor.get_original_index_mapping()
                new_titles = self.pdf_processor.generate_new_bookmark_titles(
                    excel_data, index_mapping
                )
                summary = self.pdf_processor.get_bookmark_update_summary(new_titles)
                bookmark_count = (
                    f"Updated {summary['total_bookmarks_updated']} bookmarks"
                )
            except:
                bookmark_count = "PDF bookmarks updated"

        # Simple backup notice
        backup_notice = ""
        if excel_backup_path and pdf_backup_path:
            backup_notice = "\n✅ Backup files created for safety"

        message = (
            f"Excel data sorted and renumbered\n"
            f"{bookmark_count}\n"
            f"{backup_notice}\n\n"
            f"Files saved to: {os.path.dirname(excel_output_path)}"
        )

        messagebox.showinfo(title, message)

    def _validate_file_access(self, file_path: str, operation: str = "write") -> bool:
        """Validate that we can access the file for the specified operation.

        Args:
            file_path (str): Path to the file to check
            operation (str): Type of operation ("read" or "write"). Defaults to "write".

        Returns:
            bool: True if file access is available, False otherwise
        """
        try:
            if operation == "write":
                # Check if we can write to the directory
                parent_dir = Path(file_path).parent
                if not parent_dir.exists():
                    self._handle_file_access_error(
                        "Directory Not Found",
                        f"The output directory does not exist:\n{parent_dir}\n\nPlease ensure the source file location is accessible.",
                        "directory_missing",
                    )
                    return False

                if not os.access(parent_dir, os.W_OK):
                    self._handle_file_access_error(
                        "Permission Denied",
                        f"Cannot write to directory:\n{parent_dir}\n\nPlease check folder permissions or choose a different location.",
                        "directory_permission",
                    )
                    return False

                # Check if file exists and is writable
                if os.path.exists(file_path):
                    if not os.access(file_path, os.W_OK):
                        self._handle_file_access_error(
                            "File Permission Error",
                            f"Cannot write to file:\n{os.path.basename(file_path)}\n\nThe file may be:\n• Open in another application\n• Read-only\n• Protected by system permissions\n\nPlease close the file and try again.",
                            "file_permission",
                        )
                        return False

            elif operation == "read":
                if not os.path.exists(file_path):
                    self._handle_file_access_error(
                        "File Not Found",
                        f"Source file not found:\n{os.path.basename(file_path)}\n\nPlease ensure the file exists and try again.",
                        "file_missing",
                    )
                    return False

                if not os.access(file_path, os.R_OK):
                    self._handle_file_access_error(
                        "File Access Error",
                        f"Cannot read file:\n{os.path.basename(file_path)}\n\nPlease check file permissions.",
                        "file_read_permission",
                    )
                    return False

            return True

        except Exception as e:
            self._handle_file_access_error(
                "File System Error",
                f"Unexpected file system error:\n{str(e)}\n\nPlease try again or contact support.",
                "system_error",
            )
            return False

    def _handle_file_access_error(
        self, title: str, message: str, error_type: str
    ) -> None:
        """Handle file access errors with specific user guidance."""
        self.gui.log_status(f"File Access Error ({error_type}): {message}")

        # Show user-friendly error dialog
        messagebox.showerror(title, message)

    def _save_processed_excel_file(self, excel_output_path: str) -> bool:
        """Save the processed Excel file with formatting to the output path.

        Args:
            excel_output_path (str): Path where the processed Excel file should be saved

        Returns:
            bool: True if file was saved successfully, False otherwise
        """
        try:
            self.gui.log_status("Saving processed Excel file...")

            # Save Excel file with all formatting preserved
            self.excel_processor.save_with_formulas(excel_output_path)

            self.gui.log_status(
                f"✓ Excel file saved: {os.path.basename(excel_output_path)}"
            )
            return True

        except PermissionError as e:
            self._handle_save_error(
                "Excel File Permission Error",
                f"Cannot save Excel file:\n{os.path.basename(excel_output_path)}\n\nThe file may be open in Excel or another application.\nPlease close the file and try again.",
                str(e),
            )
            return False
        except FileNotFoundError as e:
            self._handle_save_error(
                "Excel File Path Error",
                f"Invalid file path for Excel output:\n{excel_output_path}\n\nPlease check that the directory exists.",
                str(e),
            )
            return False
        except Exception as e:
            self._handle_save_error(
                "Excel File Save Error",
                f"Failed to save Excel file:\n{os.path.basename(excel_output_path)}\n\nError: {str(e)}\n\nThis may be due to:\n• Insufficient disk space\n• File corruption\n• Excel format issues",
                str(e),
            )
            return False

    def _handle_save_error(
        self, title: str, user_message: str, technical_error: str
    ) -> None:
        """Handle save errors with user-friendly messaging and logging."""
        # Log technical details for debugging
        self.gui.log_status(f"Save Error - {title}: {technical_error}")

        # Show user-friendly error dialog
        messagebox.showerror(title, user_message)

    def _save_updated_pdf_file(self, pdf_output_path: str) -> bool:
        """Save the updated PDF file with new bookmark structure.

        Args:
            pdf_output_path (str): Path where the updated PDF file should be saved

        Returns:
            bool: True if PDF was saved successfully, False otherwise
        """
        try:
            self.gui.log_status("Saving updated PDF file...")

            # Initialize PDFProcessor if not done already
            if not hasattr(self, "pdf_processor"):
                self.pdf_processor = PDFProcessor()

            # Load PDF file
            excel_file, pdf_file = self.gui.get_selected_files()
            self.gui.log_status("Loading PDF and extracting bookmarks...")
            self.pdf_processor.load_pdf(pdf_file)

            # Get initial bookmark info
            bookmark_info = self.pdf_processor.get_bookmark_info()
            self.gui.log_status(
                f"Found {bookmark_info['bookmarks_count']} existing bookmarks in PDF"
            )

            # Copy pages to writer
            self.gui.log_status("Copying PDF pages...")
            self.pdf_processor.copy_pages_to_writer()

            # Get Excel data and index mapping for bookmark generation
            excel_data = self.excel_processor.get_dataframe().to_dict("records")
            index_mapping = self.excel_processor.get_original_index_mapping()

            # Generate new bookmark titles
            self.gui.log_status("Generating new bookmark titles...")
            new_titles = self.pdf_processor.generate_new_bookmark_titles(
                excel_data, index_mapping
            )

            # Update bookmarks with new titles
            self.gui.log_status(f"Updating {len(new_titles)} bookmark titles...")
            self.pdf_processor.update_bookmarks_with_new_titles(new_titles)

            # Save the updated PDF
            self.pdf_processor.save_pdf(pdf_output_path)

            # Get bookmark processing summary
            summary = self.pdf_processor.get_bookmark_update_summary(new_titles)
            self.gui.log_status(
                f"✓ PDF file saved: {os.path.basename(pdf_output_path)}"
            )
            self.gui.log_status(
                f"  • Updated: {summary['total_bookmarks_updated']} bookmarks"
            )
            self.gui.log_status(
                f"  • Preserved: {summary['total_bookmarks_preserved']} bookmarks"
            )

            return True

        except PermissionError as e:
            self._handle_save_error(
                "PDF File Permission Error",
                f"Cannot save PDF file:\n{os.path.basename(pdf_output_path)}\n\nThe file may be open in a PDF viewer.\nPlease close the file and try again.",
                str(e),
            )
            return False
        except FileNotFoundError as e:
            self._handle_save_error(
                "PDF File Path Error",
                f"Invalid file path for PDF output:\n{pdf_output_path}\n\nPlease check that the directory exists.",
                str(e),
            )
            return False
        except Exception as e:
            self._handle_save_error(
                "PDF File Save Error",
                f"Failed to save PDF file:\n{os.path.basename(pdf_output_path)}\n\nError: {str(e)}\n\nThis may be due to:\n• PDF file corruption\n• Insufficient disk space\n• PDF processing issues",
                str(e),
            )
            return False

    def _generate_backup_filename(self, original_path: str) -> str:
        """Generate backup filename with datetime stamp.

        Format: filename_backup_YYYY-MM-DD_HH-MM-SS.ext

        Args:
            original_path (str): Path to the original file

        Returns:
            str: Path to the backup file with datetime stamp

        Example:
            document.xlsx -> document_backup_2024-01-15_14-30-45.xlsx
        """
        try:
            original_file = Path(original_path)
            file_stem = original_file.stem  # filename without extension
            file_suffix = original_file.suffix  # file extension
            file_dir = original_file.parent

            # Generate datetime stamp in format: YYYY-MM-DD_HH-MM-SS
            datetime_stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

            # Create backup filename: filename_backup_YYYY-MM-DD_HH-MM-SS.ext
            backup_filename = f"{file_stem}_backup_{datetime_stamp}{file_suffix}"
            backup_path = file_dir / backup_filename

            return str(backup_path)

        except Exception as e:
            raise ValueError(
                f"Failed to generate backup filename for {original_path}: {str(e)}"
            )

    def _ensure_unique_backup_filename(self, backup_path: str) -> str:
        """Enhanced backup filename uniqueness with validation and user feedback.

        Args:
            backup_path (str): Proposed backup file path

        Returns:
            str: Unique backup file path (may have sequence number appended)

        Example:
            If document_backup_2024-01-15_14-30-45.xlsx exists,
            returns document_backup_2024-01-15_14-30-45_001.xlsx
        """
        original_backup_path = backup_path

        # First check - if file doesn't exist, we're good
        if not os.path.exists(backup_path):
            return backup_path

        # File exists, need to find unique name
        self.gui.log_status(f"⚠️  Backup file exists: {os.path.basename(backup_path)}")

        backup_file = Path(backup_path)
        file_stem = backup_file.stem
        file_suffix = backup_file.suffix
        file_dir = backup_file.parent

        # Enhanced validation: check if existing file is actually a backup we can overwrite
        if self._is_safe_to_replace_backup(backup_path):
            self.gui.log_status(
                f"✅ Existing backup can be safely replaced: {os.path.basename(backup_path)}"
            )
            return backup_path

        # Find next available sequence number with better feedback
        sequence = 1
        attempted_names = []

        while sequence < 1000:  # Safety limit increased
            sequence_str = f"{sequence:03d}"  # 001, 002, 003, etc.
            unique_filename = f"{file_stem}_{sequence_str}{file_suffix}"
            unique_path = file_dir / unique_filename
            attempted_names.append(unique_filename)

            if not os.path.exists(str(unique_path)):
                self.gui.log_status(f"✅ Using unique backup name: {unique_filename}")
                return str(unique_path)

            sequence += 1

        # If we've tried many sequences, something may be wrong
        if sequence >= 1000:
            self.gui.log_status("⚠️  Many backup files exist - using timestamp fallback")

        # Fallback with enhanced uniqueness
        timestamp_microsec = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        fallback_filename = f"{file_stem}_{timestamp_microsec}{file_suffix}"
        fallback_path = str(file_dir / fallback_filename)

        self.gui.log_status(
            f"✅ Using timestamp-based backup name: {fallback_filename}"
        )
        return fallback_path

    def _is_safe_to_replace_backup(self, backup_path: str) -> bool:
        """Check if an existing backup file can be safely replaced.

        Args:
            backup_path (str): Path to existing backup file

        Returns:
            bool: True if file can be safely replaced
        """
        try:
            # Check if file is very recent (within last minute) - might be from previous run
            file_stat = os.stat(backup_path)
            file_age = time.time() - file_stat.st_mtime

            if file_age < 60:  # Less than 1 minute old
                return True

            # Check if file size suggests it's incomplete (very small)
            file_size = file_stat.st_size
            if file_size < 1024:  # Less than 1KB suggests incomplete backup
                return True

            # Don't replace older, larger files - they may be important
            return False

        except (OSError, ValueError):
            # If we can't check the file safely, don't replace it
            return False

    def _generate_output_filenames(
        self, excel_path: str, pdf_path: str
    ) -> Tuple[str, str]:
        """Generate output filenames using original names (no '_renumbered' suffix).

        The new strategy uses the original filenames for output, while the original
        files will be backed up with datetime stamps before processing.

        Args:
            excel_path (str): Path to source Excel file
            pdf_path (str): Path to source PDF file

        Returns:
            Tuple[str, str]: Tuple of (excel_output_path, pdf_output_path)
                           Both paths will be the same as the original paths

        Raises:
            ValueError: If filename generation fails
        """
        try:
            # New strategy: output files use original filenames
            # The original files will be backed up before processing
            return excel_path, pdf_path

        except Exception as e:
            raise ValueError(f"Failed to generate output filenames: {str(e)}")

    def _generate_backup_filenames(
        self, excel_path: str, pdf_path: str
    ) -> Tuple[str, str]:
        """Generate backup filenames for original files with datetime stamps.

        Args:
            excel_path (str): Path to source Excel file
            pdf_path (str): Path to source PDF file

        Returns:
            Tuple[str, str]: Tuple of (excel_backup_path, pdf_backup_path)

        Raises:
            ValueError: If backup filename generation fails
        """
        try:
            # Generate backup filenames with datetime stamps
            excel_backup = self._generate_backup_filename(excel_path)
            pdf_backup = self._generate_backup_filename(pdf_path)

            # Ensure uniqueness to prevent overwrites
            excel_backup = self._ensure_unique_backup_filename(excel_backup)
            pdf_backup = self._ensure_unique_backup_filename(pdf_backup)

            return excel_backup, pdf_backup

        except Exception as e:
            raise ValueError(f"Failed to generate backup filenames: {str(e)}")

    def _validate_rollback_capability(
        self,
        excel_backup_path: str,
        pdf_backup_path: str,
        excel_path: str,
        pdf_path: str,
    ) -> bool:
        """Validate that rollback operations can be performed successfully.

        Args:
            excel_backup_path (str): Path to Excel backup file
            pdf_backup_path (str): Path to PDF backup file
            excel_path (str): Path to original Excel file location
            pdf_path (str): Path to original PDF file location

        Returns:
            bool: True if rollback can be performed, False otherwise
        """
        try:
            # Check if backup files exist and are readable
            if not os.path.exists(excel_backup_path):
                self.gui.log_status(
                    f"Warning: Excel backup file not found: {excel_backup_path}"
                )
                return False

            if not os.path.exists(pdf_backup_path):
                self.gui.log_status(
                    f"Warning: PDF backup file not found: {pdf_backup_path}"
                )
                return False

            if not os.access(excel_backup_path, os.R_OK):
                self.gui.log_status(
                    f"Warning: Cannot read Excel backup file: {excel_backup_path}"
                )
                return False

            if not os.access(pdf_backup_path, os.R_OK):
                self.gui.log_status(
                    f"Warning: Cannot read PDF backup file: {pdf_backup_path}"
                )
                return False

            # Check if target directories are writable
            excel_dir = Path(excel_path).parent
            pdf_dir = Path(pdf_path).parent

            if not os.access(excel_dir, os.W_OK):
                self.gui.log_status(
                    f"Warning: Cannot write to Excel directory: {excel_dir}"
                )
                return False

            if not os.access(pdf_dir, os.W_OK):
                self.gui.log_status(
                    f"Warning: Cannot write to PDF directory: {pdf_dir}"
                )
                return False

            # Verify backup file integrity by checking sizes
            try:
                excel_backup_size = os.path.getsize(excel_backup_path)
                pdf_backup_size = os.path.getsize(pdf_backup_path)

                if excel_backup_size == 0:
                    self.gui.log_status(
                        f"Warning: Excel backup file is empty: {excel_backup_path}"
                    )
                    return False

                if pdf_backup_size == 0:
                    self.gui.log_status(
                        f"Warning: PDF backup file is empty: {pdf_backup_path}"
                    )
                    return False

            except OSError as e:
                self.gui.log_status(
                    f"Warning: Cannot verify backup file sizes: {str(e)}"
                )
                return False

            return True

        except Exception as e:
            self.gui.log_status(f"Warning: Rollback validation failed: {str(e)}")
            return False

    def _perform_atomic_file_operation(
        self, source_path: str, target_path: str, operation_name: str
    ) -> bool:
        """Perform atomic file operation with temporary file to ensure consistency.

        Args:
            source_path (str): Path to source file
            target_path (str): Path to target file
            operation_name (str): Description of operation for logging

        Returns:
            bool: True if operation succeeded, False otherwise
        """
        temp_path = None
        try:
            # Create temporary file path
            target_dir = Path(target_path).parent
            temp_filename = (
                f".tmp_{os.path.basename(target_path)}_{datetime.now().strftime('%f')}"
            )
            temp_path = target_dir / temp_filename

            # Copy to temporary file first
            shutil.copy2(source_path, str(temp_path))

            # Verify copy was successful
            if not os.path.exists(str(temp_path)):
                raise OSError("Temporary file was not created")

            source_size = os.path.getsize(source_path)
            temp_size = os.path.getsize(str(temp_path))
            if source_size != temp_size:
                raise OSError(
                    f"File size mismatch - source: {source_size}, temp: {temp_size}"
                )

            # Atomically move temporary file to target location
            if os.path.exists(target_path):
                # Create backup of existing target for safety
                backup_target = f"{target_path}.backup_before_restore"
                if os.path.exists(backup_target):
                    os.remove(backup_target)
                shutil.move(target_path, backup_target)

            # Move temp file to final location
            shutil.move(str(temp_path), target_path)

            # Verify final operation
            if not os.path.exists(target_path):
                raise OSError("Final file was not created")

            self.gui.log_status(f"  ✓ {operation_name} completed successfully")
            return True

        except Exception as e:
            self.gui.log_status(f"  ✗ {operation_name} failed: {str(e)}")

            # Clean up temporary file if it exists
            if temp_path and os.path.exists(str(temp_path)):
                try:
                    os.remove(str(temp_path))
                except:
                    pass  # Best effort cleanup

            return False

    def _rollback_backup_files(
        self,
        excel_backup_path: str,
        pdf_backup_path: str,
        excel_path: str,
        pdf_path: str,
    ) -> bool:
        """Enhanced rollback with validation and atomic operations.

        Args:
            excel_backup_path (str): Path to Excel backup file
            pdf_backup_path (str): Path to PDF backup file
            excel_path (str): Path to original Excel file location
            pdf_path (str): Path to original PDF file location

        Returns:
            bool: True if rollback was successful, False otherwise
        """
        try:
            self.gui.log_status("Rolling back files due to processing failure...")

            # Step 1: Validate rollback capability
            if not self._validate_rollback_capability(
                excel_backup_path, pdf_backup_path, excel_path, pdf_path
            ):
                self.gui.log_status(
                    "Rollback validation failed - cannot proceed with rollback"
                )
                return False

            # Step 2: Perform atomic rollback operations
            rollback_success = True

            # Rollback Excel file with atomic operation
            if not self._perform_atomic_file_operation(
                excel_backup_path, excel_path, "Excel file rollback"
            ):
                rollback_success = False

            # Rollback PDF file with atomic operation
            if not self._perform_atomic_file_operation(
                pdf_backup_path, pdf_path, "PDF file rollback"
            ):
                rollback_success = False

            # Step 3: Verify rollback results
            if rollback_success:
                self.gui.log_status("✓ File rollback completed successfully")

                # Verify restored files exist and have correct sizes
                try:
                    if os.path.exists(excel_path) and os.path.exists(pdf_path):
                        excel_size = os.path.getsize(excel_path)
                        pdf_size = os.path.getsize(pdf_path)
                        backup_excel_size = os.path.getsize(excel_backup_path)
                        backup_pdf_size = os.path.getsize(pdf_backup_path)

                        if (
                            excel_size == backup_excel_size
                            and pdf_size == backup_pdf_size
                        ):
                            self.gui.log_status(
                                "✓ Rollback verification successful - file sizes match backups"
                            )
                        else:
                            self.gui.log_status(
                                "Warning: Rollback verification - file sizes don't match backups"
                            )
                    else:
                        self.gui.log_status(
                            "Warning: Some restored files not found after rollback"
                        )

                except Exception as verify_error:
                    self.gui.log_status(
                        f"Warning: Rollback verification failed: {str(verify_error)}"
                    )
            else:
                self.gui.log_status("✗ File rollback partially failed")

            return rollback_success

        except Exception as e:
            self.gui.log_status(f"Critical error during rollback: {str(e)}")
            return False

    def _validate_comprehensive_file_access(
        self, excel_path: str, pdf_path: str, backup_enabled: bool = True
    ) -> bool:
        """Comprehensive validation of file access permissions including backup operations.

        Args:
            excel_path (str): Path to Excel file
            pdf_path (str): Path to PDF file
            backup_enabled (bool): Whether backup creation is enabled

        Returns:
            bool: True if all necessary permissions are available
        """
        try:
            self.gui.log_status(
                "🔍 Validating comprehensive file access permissions..."
            )

            # Step 1: Validate source file read access
            if not self._validate_file_access(excel_path, "read"):
                self.gui.log_status("❌ Excel file read access validation failed")
                return False

            if not self._validate_file_access(pdf_path, "read"):
                self.gui.log_status("❌ PDF file read access validation failed")
                return False

            # Step 2: Validate output file write access (for overwriting originals)
            if not self._validate_file_access(excel_path, "write"):
                self.gui.log_status("❌ Excel file write access validation failed")
                return False

            if not self._validate_file_access(pdf_path, "write"):
                self.gui.log_status("❌ PDF file write access validation failed")
                return False

            # Step 3: Validate backup permissions if backup is enabled
            if backup_enabled:
                if not self._validate_backup_permissions(excel_path, pdf_path):
                    self.gui.log_status("❌ Backup permission validation failed")
                    return False

                self.gui.log_status("✅ Backup permissions validated successfully")
            else:
                self.gui.log_status(
                    "ℹ️  Backup permission validation skipped (backup disabled)"
                )

            self.gui.log_status("✅ All file access permissions validated successfully")
            return True

        except Exception as e:
            self.gui.log_status(f"❌ File access validation error: {str(e)}")
            self._handle_file_access_error(
                "File Access Validation Error",
                f"Failed to validate file access permissions:\n{str(e)}\n\nPlease check file and directory permissions.",
                "validation_error",
            )
            return False

    def _validate_backup_permissions(self, excel_path: str, pdf_path: str) -> bool:
        """Validate permissions specifically for backup file creation.

        Args:
            excel_path (str): Path to Excel file
            pdf_path (str): Path to PDF file

        Returns:
            bool: True if backup permissions are sufficient
        """
        try:
            self.gui.log_status("🔍 Validating backup file creation permissions...")

            # Get directories for backup files (same as source files)
            excel_dir = Path(excel_path).parent
            pdf_dir = Path(pdf_path).parent

            # Validate directory exists and is writable
            directories_to_check = {excel_dir, pdf_dir}  # Remove duplicates with set

            for directory in directories_to_check:
                if not directory.exists():
                    self._handle_file_access_error(
                        "Backup Directory Not Found",
                        f"Backup directory does not exist:\n{directory}\n\nBackup files cannot be created.",
                        "backup_directory_missing",
                    )
                    return False

                if not os.access(directory, os.W_OK):
                    self._handle_file_access_error(
                        "Backup Permission Denied",
                        f"Cannot create backup files in directory:\n{directory}\n\nPlease check folder permissions or disable backup creation.",
                        "backup_directory_permission",
                    )
                    return False

            # Test backup filename generation to ensure no conflicts
            try:
                test_excel_backup, test_pdf_backup = self._generate_backup_filenames(
                    excel_path, pdf_path
                )

                # Check if we can create files with these names
                self._test_backup_file_creation(test_excel_backup, "Excel")
                self._test_backup_file_creation(test_pdf_backup, "PDF")

            except Exception as e:
                self._handle_file_access_error(
                    "Backup File Creation Test Failed",
                    f"Cannot create backup files:\n{str(e)}\n\nThis may be due to:\n• Long filenames\n• Special characters\n• File system limitations\n\nConsider disabling backup creation.",
                    "backup_creation_test",
                )
                return False

            return True

        except Exception as e:
            self.gui.log_status(f"❌ Backup permission validation error: {str(e)}")
            return False

    def _test_backup_file_creation(self, backup_path: str, file_type: str) -> None:
        """Test if we can create a backup file at the specified path.

        Args:
            backup_path (str): Path where backup file would be created
            file_type (str): Type of file for error messages

        Raises:
            PermissionError: If backup file cannot be created
            OSError: If file system operation fails
        """
        try:
            # Test by creating and immediately removing a test file
            test_path = f"{backup_path}.test"

            # Try to create test file
            with open(test_path, "w") as test_file:
                test_file.write("test")

            # Verify test file was created
            if not os.path.exists(test_path):
                raise OSError(f"Test backup file was not created: {test_path}")

            # Clean up test file
            os.remove(test_path)

            self.gui.log_status(f"✅ {file_type} backup creation test passed")

        except PermissionError as e:
            raise PermissionError(f"Cannot create {file_type} backup file: {str(e)}")
        except OSError as e:
            raise OSError(f"{file_type} backup file creation test failed: {str(e)}")
        except Exception as e:
            raise Exception(
                f"Unexpected error testing {file_type} backup creation: {str(e)}"
            )
        finally:
            # Ensure test file is cleaned up
            test_path = f"{backup_path}.test"
            if os.path.exists(test_path):
                try:
                    os.remove(test_path)
                except:
                    pass  # Best effort cleanup

    def _create_backup_files(self, excel_path: str, pdf_path: str) -> Tuple[str, str]:
        """Create backup copies of original files before processing.

        Args:
            excel_path (str): Path to original Excel file
            pdf_path (str): Path to original PDF file

        Returns:
            Tuple[str, str]: Tuple of (excel_backup_path, pdf_backup_path)

        Raises:
            ValueError: If backup creation fails
            PermissionError: If insufficient permissions for backup operations
            OSError: If file system operations fail
        """
        try:
            self.gui.log_status("🛡️  CREATING BACKUP FILES FOR SAFETY")
            self.gui.log_status("=" * 60)
            self.gui.log_status(
                "Creating timestamped backup copies before processing..."
            )
            self.gui.log_status("This ensures your original files are never lost.")

            # Step 1: Generate backup filenames with enhanced validation
            excel_backup_path, pdf_backup_path = self._generate_backup_filenames(
                excel_path, pdf_path
            )

            self.gui.log_status("")
            self.gui.log_status("📋 Backup files to create:")
            self.gui.log_status(f"  📊 Excel: {os.path.basename(excel_backup_path)}")
            self.gui.log_status(f"  📄 PDF:   {os.path.basename(pdf_backup_path)}")
            self.gui.log_status("")

            # Step 2: Create backup files with validation
            self.gui.log_status("Creating Excel backup...")
            self._create_single_backup(excel_path, excel_backup_path, "Excel")

            self.gui.log_status("Creating PDF backup...")
            self._create_single_backup(pdf_path, pdf_backup_path, "PDF")

            # Step 3: Final validation of created backups
            self._validate_created_backups(
                excel_path, pdf_path, excel_backup_path, pdf_backup_path
            )

            self.gui.log_status("")
            self.gui.log_status("✅ Backup files created and validated successfully!")
            self.gui.log_status("Your original files are now safely backed up.")
            self.gui.log_status("=" * 60)

            return excel_backup_path, pdf_backup_path

        except (PermissionError, OSError) as e:
            # Handle backup creation failures with comprehensive user guidance
            self._handle_backup_creation_failure(e, excel_path, pdf_path)
            raise PermissionError(f"Backup creation failed: {str(e)}")
        except Exception as e:
            # Handle unexpected backup creation failures
            self._handle_backup_creation_failure(e, excel_path, pdf_path)
            raise ValueError(f"Backup creation failed: {str(e)}")

    def _handle_backup_creation_failure(
        self, error: Exception, excel_path: str, pdf_path: str
    ) -> None:
        """Handle backup creation failures with comprehensive user guidance.

        Args:
            error (Exception): The error that occurred during backup creation
            excel_path (str): Path to Excel file
            pdf_path (str): Path to PDF file
        """
        try:
            # Log the failure
            self.gui.log_status("❌ BACKUP CREATION FAILED")
            self.gui.log_status("=" * 60)
            self.gui.log_status(f"Error: {str(error)}")

            # Determine error type and provide specific guidance
            error_type = type(error).__name__
            recovery_options = []

            if isinstance(error, PermissionError):
                self.gui.log_status("💡 PERMISSION ERROR - Backup creation blocked")
                recovery_options = [
                    "• Close Excel/PDF files if they are open",
                    "• Run application as administrator (if on Windows)",
                    "• Check folder permissions for the file directory",
                    "• Move files to a different folder with write permissions",
                    "• Disable backup creation using the checkbox",
                ]

            elif isinstance(error, FileNotFoundError):
                self.gui.log_status("💡 FILE NOT FOUND - Source files missing")
                recovery_options = [
                    "• Verify that the selected files still exist",
                    "• Re-select the Excel and PDF files",
                    "• Check if files were moved or deleted",
                ]

            elif isinstance(error, OSError):
                if "No space left" in str(error) or "Disk full" in str(error):
                    self.gui.log_status("💡 DISK SPACE ERROR - Insufficient storage")
                    recovery_options = [
                        "• Free up disk space on the target drive",
                        "• Move files to a drive with more space",
                        "• Delete unnecessary files or empty trash/recycle bin",
                        "• Disable backup creation if space is critical",
                    ]
                else:
                    self.gui.log_status("💡 FILE SYSTEM ERROR - System-level issue")
                    recovery_options = [
                        "• Check if the disk is write-protected",
                        "• Verify file system integrity",
                        "• Try moving files to a different location",
                        "• Restart the application and try again",
                    ]

            else:
                self.gui.log_status("💡 UNEXPECTED ERROR - Unknown issue")
                recovery_options = [
                    "• Try restarting the application",
                    "• Check available disk space",
                    "• Verify file permissions",
                    "• Disable backup creation as a workaround",
                ]

            # Display recovery options
            self.gui.log_status("")
            self.gui.log_status("🔧 SUGGESTED SOLUTIONS:")
            for option in recovery_options:
                self.gui.log_status(f"  {option}")

            self.gui.log_status("")
            self.gui.log_status("⚠️  ALTERNATIVE: Disable backup creation")
            self.gui.log_status("   You can uncheck 'Create backup files' to proceed")
            self.gui.log_status(
                "   without backups (original files will be modified directly)"
            )
            self.gui.log_status("=" * 60)

            # Show user-friendly error dialog with guidance
            self._show_backup_failure_dialog(error, recovery_options)

        except Exception as e:
            # Fallback error handling
            self.gui.log_status(f"Error handling backup failure: {str(e)}")

    def _show_backup_failure_dialog(
        self, error: Exception, recovery_options: List[str]
    ) -> None:
        """Show user-friendly dialog for backup creation failures.

        Args:
            error (Exception): The backup creation error
            recovery_options (List[str]): List of suggested recovery options
        """
        try:
            error_type = type(error).__name__

            # Create concise error message
            if isinstance(error, PermissionError):
                title = "Backup Creation - Permission Denied"
                message = (
                    "Cannot create backup files due to permission restrictions.\n\n"
                    "Common solutions:\n"
                    "• Close Excel/PDF files if open\n"
                    "• Check folder permissions\n"
                    "• Move files to a different location\n\n"
                    "Alternative: Disable backup creation and proceed without backups."
                )
            elif isinstance(error, FileNotFoundError):
                title = "Backup Creation - File Not Found"
                message = (
                    "Cannot create backup files because source files are missing.\n\n"
                    "Please verify that the selected files still exist and re-select them if needed."
                )
            elif "space" in str(error).lower() or "disk full" in str(error).lower():
                title = "Backup Creation - Insufficient Disk Space"
                message = (
                    "Cannot create backup files due to insufficient disk space.\n\n"
                    "Solutions:\n"
                    "• Free up disk space\n"
                    "• Move files to a drive with more space\n"
                    "• Disable backup creation to proceed without backups"
                )
            else:
                title = "Backup Creation Failed"
                message = (
                    f"Backup creation failed: {str(error)}\n\n"
                    "You can try:\n"
                    "• Restarting the application\n"
                    "• Moving files to a different location\n"
                    "• Disabling backup creation to proceed without backups"
                )

            messagebox.showerror(title, message)

        except Exception as e:
            # Fallback to simple error dialog
            messagebox.showerror(
                "Backup Creation Failed",
                f"Failed to create backup files: {str(error)}\n\nCheck the status log for details.",
            )

    def _validate_created_backups(
        self,
        excel_path: str,
        pdf_path: str,
        excel_backup_path: str,
        pdf_backup_path: str,
    ) -> None:
        """Validate that backup files were created correctly and completely.

        Args:
            excel_path (str): Original Excel file path
            pdf_path (str): Original PDF file path
            excel_backup_path (str): Created Excel backup path
            pdf_backup_path (str): Created PDF backup path

        Raises:
            ValueError: If backup validation fails
        """
        try:
            self.gui.log_status("🔍 Validating created backup files...")

            # Check Excel backup
            if not os.path.exists(excel_backup_path):
                raise ValueError(
                    f"Excel backup file was not created: {excel_backup_path}"
                )

            excel_original_size = os.path.getsize(excel_path)
            excel_backup_size = os.path.getsize(excel_backup_path)

            if excel_backup_size != excel_original_size:
                raise ValueError(
                    f"Excel backup size mismatch - original: {excel_original_size}, backup: {excel_backup_size}"
                )

            # Check PDF backup
            if not os.path.exists(pdf_backup_path):
                raise ValueError(f"PDF backup file was not created: {pdf_backup_path}")

            pdf_original_size = os.path.getsize(pdf_path)
            pdf_backup_size = os.path.getsize(pdf_backup_path)

            if pdf_backup_size != pdf_original_size:
                raise ValueError(
                    f"PDF backup size mismatch - original: {pdf_original_size}, backup: {pdf_backup_size}"
                )

            # Check file readability
            if not os.access(excel_backup_path, os.R_OK):
                raise ValueError(
                    f"Excel backup file is not readable: {excel_backup_path}"
                )

            if not os.access(pdf_backup_path, os.R_OK):
                raise ValueError(f"PDF backup file is not readable: {pdf_backup_path}")

            self.gui.log_status("✅ Backup file validation completed successfully")

        except Exception as e:
            # Clean up invalid backups
            for backup_path in [excel_backup_path, pdf_backup_path]:
                if os.path.exists(backup_path):
                    try:
                        os.remove(backup_path)
                        self.gui.log_status(
                            f"Cleaned up invalid backup: {os.path.basename(backup_path)}"
                        )
                    except:
                        pass  # Best effort cleanup
            raise e

    def _create_single_backup(
        self, source_path: str, backup_path: str, file_type: str
    ) -> None:
        """Create a single backup file by copying the source to backup location.

        Args:
            source_path (str): Path to source file
            backup_path (str): Path for backup file
            file_type (str): Type of file (for logging) - "Excel" or "PDF"

        Raises:
            FileNotFoundError: If source file doesn't exist
            PermissionError: If insufficient permissions
            OSError: If file operation fails
        """
        try:
            # Validate source file exists
            if not os.path.exists(source_path):
                raise FileNotFoundError(
                    f"{file_type} source file not found: {source_path}"
                )

            # Validate we can read the source file
            if not os.access(source_path, os.R_OK):
                raise PermissionError(
                    f"Cannot read {file_type} source file: {source_path}"
                )

            # Validate backup directory is writable
            backup_dir = Path(backup_path).parent
            if not os.access(backup_dir, os.W_OK):
                raise PermissionError(f"Cannot write to backup directory: {backup_dir}")

            # Validate backup file doesn't already exist (should be handled by unique naming)
            if os.path.exists(backup_path):
                raise ValueError(f"Backup file already exists: {backup_path}")

            # Show progress for larger files
            source_size = os.path.getsize(source_path)
            size_mb = source_size / (1024 * 1024)
            if size_mb > 5:  # Show size info for files larger than 5MB
                self.gui.log_status(
                    f"  📏 File size: {size_mb:.1f} MB - this may take a moment..."
                )

            # Copy file to backup location
            shutil.copy2(source_path, backup_path)

            # Verify backup was created successfully
            if not os.path.exists(backup_path):
                raise OSError(f"Backup file was not created: {backup_path}")

            # Verify backup file size matches original
            backup_size = os.path.getsize(backup_path)
            if source_size != backup_size:
                raise OSError(
                    f"Backup file size mismatch - original: {source_size}, backup: {backup_size}"
                )

            self.gui.log_status(
                f"  ✅ {file_type} backup created successfully: {os.path.basename(backup_path)}"
            )

        except (FileNotFoundError, PermissionError, OSError) as e:
            # Clean up partial backup if it was created
            if os.path.exists(backup_path):
                try:
                    os.remove(backup_path)
                except:
                    pass  # Best effort cleanup
            raise e

    def run(self) -> None:
        """Start the GUI application."""
        self.root.mainloop()


if __name__ == "__main__":
    app = AbstractRenumberTool()
    app.run()
