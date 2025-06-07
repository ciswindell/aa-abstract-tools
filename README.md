# Abstract Renumber Tool

A class-based Python application that automates the process of sorting Excel data and renumbering corresponding PDF bookmarks. The tool maintains synchronized numbering between Excel worksheets and PDF bookmark references when documents need to be reordered based on multiple sorting criteria.

## Features

- **Automated Sorting**: Sort Excel data by Legal Description, Grantee, Grantor, Document Type, Document Date, and Received Date
- **Index Renumbering**: Automatically renumber the Index# column starting from 1
- **Bookmark Synchronization**: Update PDF bookmarks to match the new Excel order
- **User-Friendly GUI**: Intuitive tkinter interface for file selection
- **Column Mapping**: Handle Excel files with different column names through mapping interface
- **Safe Output**: Creates new files with "_renumbered" suffix, preserving originals

## Requirements

- Python 3.7 or higher
- tkinter (usually included with Python, but on some Linux systems install with: `sudo apt-get install python3-tk`)
- Required packages (installed via requirements.txt):
  - pandas >= 1.5.0
  - PyPDF2 >= 3.0.0
  - openpyxl >= 3.0.0 (for Excel file reading)

## Installation

1. Clone or download this repository
2. Navigate to the project directory:
   ```bash
   cd aa-abstract-renumber
   ```
3. Create a virtual environment (recommended):
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
4. Install dependencies:
   ```bash
   python3 -m pip install -r requirements.txt
   ```

## Usage

1. Activate the virtual environment (if not already active):
   ```bash
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. Run the application:
   ```bash
   python3 abstract_renumber.py
   ```

3. The GUI will open with the following steps:
   - **Select Excel File**: Browse and select your Excel worksheet (.xlsx)
   - **Select PDF File**: Browse and select your corresponding PDF document
   - **Process Files**: Click "Process Files" to begin sorting and renumbering

4. The tool will:
   - Validate that your Excel file has the required columns
   - Show a column mapping dialog if columns need to be mapped
   - Sort the data according to the specified criteria
   - Renumber the Index# column starting from 1
   - Update PDF bookmarks to match the new order
   - Save new files with "_renumbered" suffix

## Required Excel Columns

Your Excel file must contain these columns (or you'll be prompted to map them):
- **Index#**: Sequential number for each record
- **Document Type**: Type of document (Release, Decision, etc.)
- **Legal Description**: Property legal description
- **Grantee**: Party receiving rights
- **Grantor**: Party granting rights  
- **Document Date**: Date of the document
- **Received Date**: Date document was received

## Sorting Priority

Data is sorted in the following order:
1. Legal Description (alphabetical)
2. Grantee (alphabetical)
3. Grantor (alphabetical)
4. Document Type (alphabetical)
5. Document Date (chronological)
6. Received Date (chronological)

## Output Files

The tool creates new files with "_renumbered" added to the filename:
- `Original_File.xlsx` → `Original_File_renumbered.xlsx`
- `Original_File.pdf` → `Original_File_renumbered.pdf`

## Bookmark Format

PDF bookmarks are updated to follow the format:
`Index#-Document Type-Received Date`

Example: `1-Release-2/20/1961`

## Troubleshooting

- **Missing Columns**: If your Excel file has different column names, use the mapping dialog to match them to required columns
- **Date Formatting**: Ensure dates in Excel are properly formatted as dates, not text
- **PDF Permissions**: Ensure the PDF is not password-protected or has restrictions that prevent modification
- **File Permissions**: Ensure you have write permissions in the directory where files are located

## Example Files

Sample files are available in the `example-reports/` directory for testing the application. 