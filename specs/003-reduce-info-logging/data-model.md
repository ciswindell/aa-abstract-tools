# Data Model: Reduce Excessive Info Logging

**Feature**: 003-reduce-info-logging  
**Date**: 2025-11-19  
**Approach**: Simple - categorize messages as KEEP or DELETE

## Message Categories

### KEEP (~10 messages)

**Operation Boundaries**:
- `"Starting processing..."` - User knows operation began
- `"Processing complete: {count} documents, {pages} pages"` - User sees results

**Phase Transitions** (7 pipeline steps):
- `"Step 1 of 7: Validating files..."`
- `"Step 2 of 7: Loading data..."`
- `"Step 3 of 7: Sorting data..."`
- `"Step 4 of 7: Rebuilding PDF..."`
- `"Step 5 of 7: Saving outputs..."`
- `"Step 6 of 7: Formatting Excel..."`
- (Step 7 is FilterDfStep, often skipped)

**Critical Messages** (always keep):
- All ERROR messages (red, user-friendly)
- All WARNING messages (orange)
- All SUCCESS messages (green)

---

### DELETE (~70 messages)

**Category 1: Redundant Step Execution**
```python
# DELETE - redundant with "Step X of Y" message
"Executing step 1/7: ValidateStep"
"Executing step 2/7: LoadStep"
"Executing step 4/7: SortDfStep"
# ... etc
```

**Category 2: Internal Phases**
```python
# DELETE - internal implementation phases
"Phase A: Filtering DocumentUnits based on _include flag"
"Phase A complete: 67/67 DocumentUnits included"
"Phase B: Reordering DocumentUnits by DataFrame sort order"
"Phase B complete: 67 DocumentUnits reordered"
"Phase C: Creating fresh PDF with PyPDF bookmarks"
"Phase C complete: 126 pages added, 67 bookmarks created"
```

**Category 3: Sub-Step Operations**
```python
# DELETE - too granular, implementation details
"Validating input files before loading"
"Validating file existence and accessibility"
"Validating Excel sheet names"
"Validating Excel data integrity"
"Validating PDF bookmark structure"
"Validating PDF bookmark to Excel row cross-references"
```

**Category 4: Verbose Metrics**
```python
# DELETE - too much detail
"Sheet 'Worksheet' found in /path/to/file.xlsx"
"Excel file 1 data integrity passed: 91 rows, 91 unique Index# values"
"PDF file 1 bookmark validation passed: 67/67 bookmarks have valid Index# format"
"Cross-reference validation passed for pair 1: 67/67 PDF bookmarks"
"Loaded 91 rows from /path/to/file.xlsx"
"Loaded PDF with 126 pages, 67 bookmarks from /path/to/file.pdf"
"Created 67 DocumentUnits from file1.xlsx:file1.pdf"
"Document linking: 67/91 Excel rows have corresponding PDF documents"
"Applied date formatting to 4 columns, 4000 cells"
```

**Category 5: Intermediate State**
```python
# DELETE - internal state updates
"Starting file loading and merging"
"Found 1 file pairs to process"
"Processing pair 1/1: file1.xlsx, file1.pdf"
"Created intermediate PDF: /tmp/intermediate_merged_xyz.pdf"
"Loading complete: 67 DocumentUnits, 126 total pages"
"Cleaned up intermediate PDF: /tmp/intermediate_merged_xyz.pdf"
"Starting PyPDF-optimized three-phase PDF reconstruction"
"Loaded intermediate PDF with 126 pages"
```

**Category 6: Item-Level Processing**
```python
# DELETE - too granular
"Sorting 67 bookmarks naturally"
"Added 67 bookmarks sorted naturally"
"Saving 91 rows from NMNM 091308"
"Saving 91/91 rows to Excel"
```

---

## Step Counter Model

**Context Attributes**:
```python
class PipelineContext:
    # ... existing attributes ...
    step_number: int = 0      # Current step (1-indexed)
    total_steps: int = 0      # Total non-skipped steps
```

**Injected by Pipeline Executor**:
```python
def execute_pipeline(steps, context):
    # Count non-skipped steps
    non_skipped = [s for s in steps if not s.should_skip(context)]
    context.total_steps = len(non_skipped)
    
    # Assign step number as we execute
    context.step_number = 0
    for step in steps:
        if step.should_skip(context):
            continue
        context.step_number += 1
        step.execute(context)
```

**Used by Pipeline Steps**:
```python
def execute(self, context):
    # Access via context
    self.logger.info(
        f"Step {context.step_number} of {context.total_steps}: Validating files..."
    )
```

---

## Message Volume Comparison

### Before Implementation

**Total Messages**: 80-85 per operation

**Breakdown by Step**:
- ValidateStep: 12 messages
- LoadStep: 11 messages
- FilterDfStep: 5 messages (often skipped)
- SortDfStep: 8 messages
- RebuildPdfStep: 20 messages
- SaveStep: 15 messages
- FormatExcelStep: 10 messages

**User Experience**: Overwhelming, hard to follow progress

---

### After Implementation

**Total Messages**: 8-10 per operation

**Breakdown**:
- Operation start: 1 message
- Pipeline steps: 6-7 messages (one per non-skipped step)
- Operation complete: 1 message
- Plus any errors/warnings (as needed)

**User Experience**: Clear, easy to follow, shows progress

**Reduction**: 85% fewer messages (from 80-85 → 8-10)

---

## Message Format Standards

### Phase Transition Format
```
"Step {number} of {total}: {phase_name}..."
```

**Examples**:
- `"Step 1 of 7: Validating files..."`
- `"Step 3 of 7: Sorting data..."`
- `"Step 5 of 7: Saving outputs..."`

**Rules**:
- Always include ellipsis "..." to show ongoing operation
- Use present participle verbs (-ing form)
- Keep phase name short and clear
- No technical class names

### Completion Format
```
"Processing complete: {metric1}, {metric2}"
```

**Examples**:
- `"Processing complete: 67 documents processed, 126 pages"`
- `"Processing complete: 91 rows sorted"`

**Rules**:
- Include key metrics user cares about (counts, not technical details)
- Don't include file paths or timestamps
- Keep under 80 characters

---

## Implementation Checklist

**For Each Pipeline Step**:
- [ ] Find all `self.logger.info()` calls
- [ ] Delete all except one at the start
- [ ] Update keeper to use: `f"Step {context.step_number} of {context.total_steps}: [Phase]..."`
- [ ] Choose user-friendly phase name (not class name)
- [ ] Verify ERROR/WARNING/SUCCESS unchanged

**Phase Name Mapping**:
| Step Class | User-Friendly Name |
|------------|-------------------|
| ValidateStep | "Validating files..." |
| LoadStep | "Loading data..." |
| FilterDfStep | "Filtering data..." |
| SortDfStep | "Sorting data..." |
| RebuildPdfStep | "Rebuilding PDF..." |
| SaveStep | "Saving outputs..." |
| FormatExcelStep | "Formatting Excel..." |

---

## Testing Validation

**Manual Test**:
1. Run full pipeline with real files
2. Count messages in UI status area
3. Expected count: 8-10 messages
4. Verify all messages follow format standards

**What to Check**:
- [X] All messages show step counter ("Step X of Y")
- [X] Phase names are user-friendly (no class names)
- [X] No verbose technical details
- [X] ERROR/WARNING/SUCCESS unchanged
- [X] Total message count 5-15 (target 8-10)

---

## Notes

**Why This Model is Simple**:
- No new classes or abstractions
- Two simple categories: KEEP or DELETE
- Step counter uses existing context object
- No filtering logic, just delete lines

**Migration Strategy**:
- Just delete the lines (no gradual migration)
- Can add verbose logging back later if needed
- Git history preserves deleted messages

**Maintenance**:
- Future developers: Add only phase transition messages
- Avoid logging implementation details
- One message per major step, not per sub-operation
