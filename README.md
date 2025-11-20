# Abstract Renumber Tool

A modern Python application that automates the process of sorting Excel data and renumbering corresponding PDF bookmarks while maintaining synchronized document relationships. Built with a clean architecture using dependency injection and pipeline processing.

## 🚀 Features

### Core Processing
- **Multi-Criteria Sorting**: Sort Excel data by Legal Description, Grantee, Grantor, Document Type, Document Date, and Received Date
- **Automatic Renumbering**: Renumber Index# column starting from 1 after sorting
- **PDF Bookmark Synchronization**: Update PDF bookmarks to match new Excel order
- **Document Unit Architecture**: Maintains immutable Excel row ↔ PDF page range relationships to prevent data corruption

### User Interface
- **Tkinter Desktop App**: Local desktop GUI for interactive processing
- **Dual Processing Modes**: Single file processing or multi-file merge operations

> **Note**: Streamlit web interface was removed as of 2025-11-19. The application now uses Tkinter exclusively for local desktop operation.

### Advanced Features
- **Multi-File Merge**: Combine multiple Excel/PDF pairs into consolidated documents
  - **Column Preservation**: Automatically preserves all columns from all merged files
  - **Smart Column Matching**: Case-insensitive, whitespace-tolerant column matching
  - **Logical Column Order**: Template columns first, followed by new columns
- **Data Filtering**: Filter Excel data by column values before processing
- **PDF Page Reordering**: Optionally reorder PDF pages to match bookmark order
- **Document Image Checking**: Add/update Document_Found column in Excel output
- **Safe Backup System**: Automatic timestamped backups with rollback on failure
- **Template Preservation**: Maintains Excel formatting, styles, and layouts

## 🏗️ Architecture

The application follows clean architecture principles with clear separation of concerns:

```
├── core/                    # Business logic and domain models
│   ├── models.py           # Data classes (Options, Result, DocumentUnit)
│   ├── interfaces.py       # Protocol definitions for dependency injection
│   ├── app_controller.py   # Main application orchestrator
│   ├── services/           # Business services
│   │   └── renumber.py     # Main renumbering service
│   ├── pipeline/           # Processing pipeline
│   │   ├── pipeline.py     # Pipeline orchestrator
│   │   ├── context.py      # Pipeline execution context
│   │   └── steps/          # Individual processing steps
│   └── transform/          # Data transformation utilities
├── adapters/               # External interface adapters
│   ├── excel_repo.py       # Excel file operations
│   ├── pdf_repo.py         # PDF file operations
│   └── ui_tkinter.py       # Tkinter UI adapter
└── app/                    # Application entry points
    └── tk_app.py           # Tkinter application
```

### Pipeline Processing

The application uses a 7-step pipeline with conditional execution:

1. **ValidateStep**: Comprehensive input validation
2. **LoadStep**: File loading and DocumentUnit creation
3. **FilterDfStep**: Optional data filtering
4. **SortDfStep**: Multi-criteria sorting
5. **RebuildPdfStep**: PDF reconstruction with updated bookmarks
6. **SaveStep**: File output operations
7. **FormatExcelStep**: Excel formatting and finalization

## 📋 Requirements

### System Requirements
- Python 3.7 or higher
- Linux/Windows/macOS support
- For GUI: tkinter (usually included, on Linux: `sudo apt-get install python3-tk`)

### Required Excel Columns
Your Excel file must contain these columns (case-insensitive):
- **Index#**: Sequential number for each record
- **Document Type**: Type of document (Release, Decision, etc.)
- **Legal Description**: Property legal description
- **Grantee**: Party receiving rights
- **Grantor**: Party granting rights
- **Document Date**: Date of the document
- **Received Date**: Date document was received

### File Format Support
- **Excel**: .xlsx, .xls (max 400MB for web interface)
- **PDF**: .pdf with bookmarks (max 400MB for web interface)

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd aa-abstract-renumber
   ```

2. **Create virtual environment** (recommended):
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   python3 -m pip install -r requirements.txt
   ```

## 🚀 Usage

### Desktop Interface (Tkinter)

1. **Run the application**:
   ```bash
   python3 main.py
   ```

2. **Use the GUI to**:
   - Select Excel and PDF files
   - Configure processing options
   - Process files with automatic backup

## ⚙️ Configuration

### Environment Variables
```bash
export PDF_BACKEND=pypdf  # PDF processing backend (currently only pypdf supported)
```

### Processing Options
- **Backup Creation**: Create timestamped backups before processing
- **Sort Bookmarks**: Sort PDF bookmarks naturally
- **Reorder Pages**: Reorder PDF pages to match bookmark order
- **Data Filtering**: Filter by column values
- **Document Image Check**: Add Document_Found column

## 🔢 Version Management

### Version Display

The application displays its version in multiple locations for easy identification:
- **Window Title**: "Abstract Renumber Tool v1.0.0" (visible in title bar)
- **Footer**: "Version 1.0.0" (bottom-right of main window in gray text)
- **Executable Name**: `AbstractRenumberTool-v1.0.0.exe` (when built for distribution)

### Single Source of Truth

All version information comes from a single file: **`_version.py`** at the project root.

This ensures consistency across all displays without manual updates in multiple places.

### Semantic Versioning Rules

Version numbers follow the **MAJOR.MINOR.PATCH** format (e.g., `1.0.0`):

| Component | When to Increment | Examples |
|-----------|-------------------|----------|
| **MAJOR** | Breaking changes that affect user workflows | UI redesign, removed features, incompatible changes |
| **MINOR** | New features that are backward compatible | New buttons, additional options, enhanced functionality |
| **PATCH** | Bug fixes and minor improvements | Fixed errors, typo corrections, performance tweaks |

**Increment Rules**:
- When incrementing a component, reset lower components to 0
- Examples:
  - `1.2.5` → `1.3.0` (added feature, reset PATCH)
  - `1.3.7` → `2.0.0` (breaking change, reset MINOR and PATCH)

### Version Update Workflow

To release a new version:

1. **Update version** in `_version.py`:
   ```bash
   # Edit the file
   vim _version.py
   # Change: __version__ = "1.0.0" to "1.0.1" (or appropriate version)
   ```

2. **Update CHANGELOG.md**:
   ```bash
   # Add new version section with changes
   vim CHANGELOG.md
   # Add: ## [1.0.1] - 2025-11-20
   #      ### Fixed
   #      - Description of changes
   ```

3. **Commit the changes**:
   ```bash
   git add _version.py CHANGELOG.md
   git commit -m "chore: bump version to 1.0.1"
   ```

4. **Create git tag**:
   ```bash
   git tag -a v1.0.1 -m "Version 1.0.1: Brief description of changes"
   git push origin main v1.0.1
   ```

5. **Build the executable**:
   ```bash
   cd build
   python3 build.py
   ```

6. **Verify the update**:
   - Check executable name: `ls dist/AbstractRenumberTool-v1.0.1.exe`
   - Launch the app and verify window title shows "v1.0.1"
   - Check footer shows "Version 1.0.1"
   - Verify git tag: `git tag -l`

### Version Increment Examples

**Bug Fix (PATCH)**: `1.0.0` → `1.0.1`
```bash
# Example: Fixed Windows file locking warning
echo '__version__ = "1.0.1"' > _version.py
```

**New Feature (MINOR)**: `1.0.1` → `1.1.0`
```bash
# Example: Added export to CSV button
echo '__version__ = "1.1.0"' > _version.py
```

**Breaking Change (MAJOR)**: `1.1.0` → `2.0.0`
```bash
# Example: Redesigned GUI workflow
echo '__version__ = "2.0.0"' > _version.py
```

### Detailed Version Management Guide

For comprehensive version management instructions, workflow examples, and troubleshooting, see:
- **CHANGELOG**: `CHANGELOG.md` - Version history and release notes
- **Quickstart Guide**: `specs/005-version-display-system/quickstart.md`
- **Technical Specification**: `specs/005-version-display-system/spec.md`

## 📊 Data Processing

### Sorting Priority
Data is sorted in this order:
1. Legal Description (alphabetical)
2. Grantee (alphabetical)
3. Grantor (alphabetical)
4. Document Type (alphabetical)
5. Document Date (chronological)
6. Received Date (chronological)

### Bookmark Format
PDF bookmarks are updated to: `Index#-Document Type-Received Date`

Example: `1-Release-2/20/1961`

### Output Files
- **Single File Mode**: Files saved with `_processed` suffix
- **Desktop Mode**: Original filenames with timestamped backups
- **Multi-File Mode**: Consolidated files with merged data

## 🧪 Testing

Run the test suite:
```bash
python3 -m pytest
```

Run specific test categories:
```bash
python3 -m pytest tests/core/          # Core logic tests
python3 -m pytest tests/adapters/      # Adapter tests
python3 -m pytest tests/integration/   # Integration tests
```

## 🔧 Development

### Project Structure
- **Clean Architecture**: Clear separation between business logic and external concerns
- **Dependency Injection**: Protocol-based interfaces for testability
- **Pipeline Pattern**: Modular, testable processing steps
- **Repository Pattern**: Abstracted file operations

### Adding New Features
1. Define interfaces in `core/interfaces.py`
2. Implement business logic in `core/services/`
3. Add pipeline steps in `core/pipeline/steps/`
4. Create adapters in `adapters/`
5. Add UI components in `pages/components/`

## 🐛 Troubleshooting

### Common Issues

**Missing Required Columns**
- Ensure all required columns exist in Excel file
- Column names are case-insensitive
- Check for typos in column headers

**Date Formatting**
- Ensure dates are formatted as dates, not text in Excel
- Use consistent date formats throughout the file

**PDF Issues**
- Ensure PDF is not password-protected
- Verify PDF contains bookmarks
- Check file permissions for modification

**File Size Limits**
- Web interface: 400MB per file
- Desktop interface: No hard limits (system dependent)

**Memory Issues**
- Large files may require more system memory
- Consider processing files in smaller batches

### Error Messages
The application provides detailed error messages with context. Check the logs for specific failure points in the pipeline.

## 📄 License

See LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Follow PEP 8 style guidelines
4. Add tests for new functionality
5. Submit a pull request

## 📚 Dependencies

- **pandas**: Data manipulation and analysis
- **openpyxl**: Excel file operations
- **pypdf**: PDF processing and bookmark manipulation
- **tkinter**: Desktop GUI framework (system package)
- **natsort**: Natural sorting algorithms
- **python-dateutil**: Date parsing utilities

## Todo
> Note: Streamlit-related TODOs removed as Streamlit interface was deprecated 2025-11-19
