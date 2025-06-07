#!/usr/bin/env python3
"""
Abstract Renumber Tool
A class-based application for sorting Excel data and renumbering PDF bookmarks.
"""

import os
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
        main_frame.grid_rowconfigure(5, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)

        # Title
        title_label = ttk.Label(
            main_frame, text="Abstract Renumber Tool", font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # File selection
        self._create_file_selection(main_frame)

        # Process button
        self.process_button = ttk.Button(
            main_frame,
            text="Process Files",
            command=self.controller.process_files,
            state="disabled",
        )
        self.process_button.grid(row=4, column=0, columnspan=2, pady=20)

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

    def _create_status_area(self, parent: ttk.Frame) -> None:
        """Create status text area with scrollbar."""
        status_frame = ttk.LabelFrame(parent, text="Status", padding="10")
        status_frame.grid(
            row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(20, 0)
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
            messagebox.showerror("Error", f"Processing failed: {str(e)}")

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
        try:
            self.gui.log_status("Starting data processing...")

            # Sort the data according to PRD requirements
            self.gui.log_status(
                "Sorting data by: Legal Description, Grantee, Grantor, Document Type, Document Date, Received Date"
            )
            self.excel_processor.sort_data()
            self.gui.log_status("✓ Data sorted successfully")

            # Generate output filenames
            excel_file, pdf_file = self.gui.get_selected_files()
            excel_output_path, pdf_output_path = self._generate_output_filenames(
                excel_file, pdf_file
            )
            self.gui.log_status(
                f"Output files will be: {os.path.basename(excel_output_path)}, {os.path.basename(pdf_output_path)}"
            )

            # Check if output files exist and get user confirmation if needed
            if not self._check_output_files_exist(excel_output_path, pdf_output_path):
                self.gui.log_status("Processing cancelled by user")
                return False

            # Validate file access permissions
            self.gui.log_status("Validating file permissions...")
            if not self._validate_file_access(
                excel_output_path, "write"
            ) or not self._validate_file_access(pdf_output_path, "write"):
                self.gui.log_status("Processing stopped due to file access issues")
                return False

            # Save processed Excel file
            if not self._save_processed_excel_file(excel_output_path):
                self.gui.log_status("Processing stopped due to Excel file save failure")
                return False

            # Save updated PDF file
            if not self._save_updated_pdf_file(pdf_output_path):
                self.gui.log_status("Processing stopped due to PDF file save failure")
                return False

            # Provide success feedback with output filenames
            self._show_completion_success(excel_output_path, pdf_output_path)

            return True

        except Exception as e:
            self.gui.log_status(f"Processing failed: {str(e)}")
            messagebox.showerror(
                "Processing Error",
                f"An unexpected error occurred during processing:\n\n{str(e)}\n\nPlease check the status log for details.",
            )
            raise ValueError(f"Processing failed: {str(e)}")

    def _show_completion_success(
        self, excel_output_path: str, pdf_output_path: str
    ) -> None:
        """Show completion success message with output file paths.

        Args:
            excel_output_path (str): Path to the saved Excel file
            pdf_output_path (str): Path to the saved PDF file
        """
        # Log status messages
        self.gui.log_status("=" * 50)
        self.gui.log_status("🎉 PROCESSING COMPLETED SUCCESSFULLY! 🎉")
        self.gui.log_status("=" * 50)
        self.gui.log_status("Files created:")
        self.gui.log_status(f"  📊 Excel: {os.path.basename(excel_output_path)}")
        self.gui.log_status(f"  📄 PDF:   {os.path.basename(pdf_output_path)}")
        self.gui.log_status(f"Location: {os.path.dirname(excel_output_path)}")
        self.gui.log_status("=" * 50)

        # Get bookmark processing summary if available
        bookmark_details = ""
        if hasattr(self, "pdf_processor") and self.pdf_processor.bookmarks:
            # Create a dummy summary to show what happened with bookmarks
            try:
                excel_data = self.excel_processor.get_dataframe().to_dict("records")
                index_mapping = self.excel_processor.get_original_index_mapping()
                new_titles = self.pdf_processor.generate_new_bookmark_titles(
                    excel_data, index_mapping
                )
                summary = self.pdf_processor.get_bookmark_update_summary(new_titles)

                bookmark_details = (
                    f"✓ Updated {summary['total_bookmarks_updated']} bookmarks from Excel data\n"
                    f"✓ Preserved {summary['total_bookmarks_preserved']} existing bookmarks\n"
                )
            except:
                bookmark_details = "✓ PDF bookmarks processed\n"

        # Show success dialog with detailed information
        message = (
            "🎉 Processing completed successfully!\n\n"
            "✓ Excel data sorted and renumbered\n"
            f"{bookmark_details}"
            "✓ All formatting and formulas preserved\n\n"
            f"📊 Excel file: {os.path.basename(excel_output_path)}\n"
            f"📄 PDF file: {os.path.basename(pdf_output_path)}\n\n"
            f"📁 Location: {os.path.dirname(excel_output_path)}\n\n"
            "Your files are ready to use!"
        )

        messagebox.showinfo("Processing Complete", message)

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

    def _generate_output_filenames(
        self, excel_path: str, pdf_path: str
    ) -> Tuple[str, str]:
        """Generate output filenames with '_renumbered' suffix before file extension.

        Args:
            excel_path (str): Path to source Excel file
            pdf_path (str): Path to source PDF file

        Returns:
            tuple[str, str]: Tuple of (excel_output_path, pdf_output_path)

        Raises:
            ValueError: If filename generation fails
        """
        try:
            # Process Excel filename
            excel_file = Path(excel_path)
            excel_stem = excel_file.stem  # filename without extension
            excel_suffix = excel_file.suffix  # file extension
            excel_dir = excel_file.parent
            excel_output = excel_dir / f"{excel_stem}_renumbered{excel_suffix}"

            # Process PDF filename
            pdf_file = Path(pdf_path)
            pdf_stem = pdf_file.stem  # filename without extension
            pdf_suffix = pdf_file.suffix  # file extension
            pdf_dir = pdf_file.parent
            pdf_output = pdf_dir / f"{pdf_stem}_renumbered{pdf_suffix}"

            return str(excel_output), str(pdf_output)

        except Exception as e:
            raise ValueError(f"Failed to generate output filenames: {str(e)}")

    def _check_output_files_exist(self, excel_output: str, pdf_output: str) -> bool:
        """Check if output files already exist and get user confirmation to overwrite.

        Args:
            excel_output (str): Path to Excel output file
            pdf_output (str): Path to PDF output file

        Returns:
            bool: True if user confirms overwrite or files don't exist, False otherwise
        """
        existing_files = []

        if os.path.exists(excel_output):
            existing_files.append(os.path.basename(excel_output))
        if os.path.exists(pdf_output):
            existing_files.append(os.path.basename(pdf_output))

        if existing_files:
            file_list = "\n".join(f"• {file}" for file in existing_files)
            result = messagebox.askyesno(
                "Overwrite Files?",
                f"The following output files already exist:\n\n{file_list}\n\n"
                "Do you want to overwrite them?",
                icon="warning",
            )
            return result

        return True  # No existing files, safe to proceed

    def run(self) -> None:
        """Start the GUI application."""
        self.root.mainloop()


if __name__ == "__main__":
    app = AbstractRenumberTool()
    app.run()
