# PRD: Alphanumeric Index# Support

## Introduction/Overview

The Abstract Renumber Tool currently supports only numeric values in the Index# column (1, 2, 3, etc.). However, users need to process Excel files where the Index# column contains alphanumeric values like "A1", "B5", "AGH42", etc. The tool should handle these alphanumeric values as unique identifiers for PDF bookmark mapping while still renumbering the Index# column to sequential numbers (1, 2, 3, etc.) after sorting.

**Problem it solves:** Currently, the tool fails with an error when encountering alphanumeric values in the Index# column, preventing users from processing files with mixed or alphanumeric index formats.

**Goal:** Enable the tool to process Excel files with any Index# format (numeric, alphanumeric, or mixed) while maintaining the existing sorting and renumbering functionality.

## Goals

1. **Universal Index# Support**: Handle any Index# format (numeric, alphanumeric, or mixed) without errors
2. **Backward Compatibility**: Maintain full compatibility with existing numeric-only Index# columns
3. **Consistent Renumbering**: Always renumber Index# column to sequential numbers (1, 2, 3, etc.) after sorting
4. **Proper Bookmark Mapping**: Correctly map PDF bookmarks using original Index# values regardless of format
5. **Mixed Format Handling**: Support files containing both numeric and alphanumeric Index# values

## User Stories

1. **As an abstract processor**, I want to process Excel files with alphanumeric Index# values like "A1", "B5", "AGH42" so that I can work with files that have non-numeric identifiers.

2. **As an abstract processor**, I want the tool to handle mixed Index# formats (like A1, B5, 8, 13, AGH42) in the same file so that I don't need to standardize my data before processing.

3. **As an abstract processor**, I want the Index# column to be renumbered to sequential numbers (1, 2, 3, etc.) after sorting regardless of the original format so that the output follows the standard numbering convention.

4. **As an abstract processor**, I want PDF bookmarks to be correctly updated using the original Index# values as identifiers so that the bookmark mapping works regardless of the original Index# format.

5. **As an existing user**, I want the tool to continue working exactly as before with numeric-only Index# columns so that my current workflow is not disrupted.

## Functional Requirements

1. **Index# Column Processing**
   - The system must accept Index# values in any format: numeric (1, 2, 3), alphanumeric (A1, B5, AGH42), or mixed
   - The system must treat Index# as string type throughout the processing pipeline
   - The system must preserve original Index# values in the Original_Index column for PDF bookmark mapping
   - The system must not attempt to convert Index# values to numeric during data type processing

2. **Sorting and Renumbering**
   - The system must sort Excel data by the existing priority order (Legal Description, Grantee, Grantor, Document Type, Document Date, Received Date)
   - The system must renumber the Index# column starting from 1 and incrementing by 1 after sorting
   - The system must not preserve alphanumeric formats in the final Index# column
   - The system must maintain the Original_Index column with original values for bookmark mapping

3. **PDF Bookmark Mapping**
   - The system must use original Index# values (as strings) to identify and map PDF bookmarks
   - The system must generate new bookmark titles using the new sequential Index# numbers
   - The system must handle bookmark extraction and matching using string comparison
   - The system must preserve bookmarks that don't match the expected format

4. **Backward Compatibility**
   - The system must maintain full compatibility with existing numeric-only Index# columns
   - The system must not change the behavior for files with only numeric Index# values
   - The system must maintain the same output format and file structure

5. **Error Handling**
   - The system must not fail when encountering alphanumeric Index# values
   - The system must provide clear error messages for other processing issues
   - The system must handle edge cases like empty Index# values or special characters

## Non-Goals (Out of Scope)

1. **Index# Format Preservation**: Will not preserve alphanumeric formats in the final Index# column
2. **Custom Numbering Schemes**: Will not support custom renumbering patterns or formats
3. **Index# Validation**: Will not validate or restrict the format of Index# values beyond basic string handling
4. **Sorting by Index#**: Will not use Index# values for sorting (only as identifiers)
5. **Format Conversion**: Will not attempt to convert between different Index# formats

## Design Considerations

- **String-Based Processing**: Index# column should be treated as string type throughout the pipeline
- **Mapping Strategy**: Use string-based mapping between original and new Index# values
- **PDF Integration**: Update PDF processor to handle string-based index extraction and mapping
- **Data Type Handling**: Remove numeric conversion attempts for Index# column

## Technical Considerations

- **Data Type Changes**: Modify `_process_data_types()` method to keep Index# as string
- **Mapping Interface**: Update `get_original_index_mapping()` to return `Dict[str, int]`
- **PDF Processor Updates**: Modify PDF processor methods to handle string-based index mapping
- **Type Safety**: Ensure all related methods are updated to handle string-based Index# values

## Success Metrics

1. **Functionality**: Tool successfully processes files with alphanumeric Index# values without errors
2. **Backward Compatibility**: Existing files with numeric-only Index# values continue to work unchanged
3. **Mixed Format Support**: Files with mixed Index# formats (A1, B5, 8, 13, AGH42) process correctly
4. **Output Consistency**: Final Index# column always contains sequential numbers (1, 2, 3, etc.)
5. **Bookmark Accuracy**: PDF bookmarks are correctly mapped and updated using original Index# values

## Open Questions

1. Should the tool provide any validation or warnings for unusual Index# formats?
2. How should the tool handle Index# values that contain special characters or spaces?
3. Should there be any logging or feedback about the Index# format conversion process?
4. Are there any performance considerations for very large files with complex Index# formats? 