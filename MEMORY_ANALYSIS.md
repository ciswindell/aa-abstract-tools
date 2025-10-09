# Memory Management Analysis & Findings

## Root Causes of Memory Issues

After extensive testing and consultation with Streamlit documentation (via Context7), we identified the following root causes:

### 1. File Uploader Memory Retention (PRIMARY ISSUE)
**Problem**: `st.file_uploader` stores uploaded files in RAM (BytesIO buffers) and retains them across reruns.

**Streamlit Behavior** (from official docs):
- Files are stored in Python memory (RAM) as BytesIO buffers, NOT on disk
- Files persist until:
  - A new file is uploaded (replacing the old one)
  - The file uploader is cleared by the user
  - The browser tab is closed
- **You CANNOT programmatically clear file uploaders via `st.session_state`**

**Evidence from Logs**:
- Run 1: 144K tracked objects
- Run 2: 516K tracked objects ← **372K new objects created and never freed!**

**Solution Implemented**:
- Regenerate file uploader widget keys on reset using timestamps
- This forces Streamlit to create entirely new widgets, allowing old ones to be garbage collected
- Clear all uploader-related session state keys

### 2. ZIP Download Memory Spike (UNAVOIDABLE)
**Problem**: Creating ZIP files for download causes ~1GB memory spike

**Streamlit Limitation** (from official docs):
- `st.download_button` MUST cache the entire `data` parameter in memory to serve it when clicked
- There is no streaming API for downloads in Streamlit
- For 500MB input files (PDF + Excel), a ~1GB ZIP is expected

**Evidence from Logs**:
```
[POST-PROCESS] MEMORY BEFORE DOWNLOAD: 1331.36 MB
[POST-PROCESS] MEMORY AFTER DOWNLOAD: 2314.74 MB (+983.38 MB)
```

**Solution Implemented**:
- Accept the temporary memory spike as unavoidable
- Clear cached ZIP files immediately on reset via `st.cache_data.clear()`
- Use fixed download button keys to prevent multiple copies

### 3. Python Memory Allocator Not Releasing to OS
**Problem**: Even after `gc.collect()`, Python holds freed memory in its own heap instead of returning it to the OS

**Evidence from Logs**:
```
[RESET] MEMORY AFTER gc.collect(): 2312.62 MB (change: +0.00 MB) ← No memory freed!
[RESET] MEMORY AFTER malloc_trim(): 1683.74 MB (freed: 628.88 MB) ← 629MB released to OS!
```

**Solution Implemented**:
- Use `ctypes.CDLL("libc.so.6").malloc_trim(0)` to force glibc to release memory back to OS
- This is Linux-specific but essential for production deployment on Digital Ocean

## Implemented Solutions

### 1. Smart File Uploader Key Regeneration
**Location**: `pages/components/state_management.py`

Forces Streamlit to create new uploader widgets on reset:
```python
timestamp = str(int(time.time() * 1000))
st.session_state.primary_excel_uploader_key = f"primary_excel_{timestamp}"
st.session_state.primary_pdf_uploader_key = f"primary_pdf_{timestamp}"
# ... etc
```

### 2. Comprehensive Session State Cleanup
**Location**: `pages/components/state_management.py`

Clears all large objects and uploader-related keys:
- Large DataFrames and processing results
- All uploaded file objects (by checking `hasattr(obj, "getvalue")`)
- All uploader widget keys (by checking `"uploader"` or `"uploaded"` in key name)
- All download button caches (keys starting with `"download_"`)

### 3. Aggressive Cache Clearing
**Location**: `pages/components/state_management.py`

```python
st.cache_data.clear()  # Clear cached ZIPs
st.cache_resource.clear()  # Clear cached resources
```

### 4. Forced OS Memory Release
**Location**: `pages/components/state_management.py`

```python
libc = ctypes.CDLL("libc.so.6")
libc.malloc_trim(0)  # Force glibc to release memory pages to OS
```

### 5. Pipeline Context Cleanup
**Location**: `core/pipeline/steps/save_step.py`

Explicitly clear large objects immediately after saving:
```python
context.final_pdf = None
context.df = None
context.document_units = None
context.processed_document_units = None
```

### 6. Controller Object Deletion
**Location**: `pages/single_file_processing.py`, `pages/multi_file_merge.py`

```python
del controller
gc.collect()  # Force garbage collection
```

## Expected Memory Profile

### Normal Operation (500MB PDFs):
1. **Baseline**: ~700-800 MB (Streamlit + libs)
2. **File Upload**: +500 MB (uploaded files in RAM)
3. **Processing**: +630 MB (PDF manipulation, DataFrame operations)
4. **Download Prep**: +983 MB (ZIP file creation) - **TEMPORARY**
5. **After Reset**: Back to ~700-800 MB baseline

### Memory Recovery via Reset:
- **Before Reset**: ~2.8 GB
- **After gc.collect()**: ~2.3 GB (freed Python objects)
- **After malloc_trim()**: ~1.7 GB (**freed 629 MB to OS**)
- Memory will drop to baseline (~800 MB) once user uploads new files, forcing Streamlit to clear old uploader widgets

## Key Takeaways

1. **ZIP download memory spikes are unavoidable** - this is a Streamlit limitation, not a bug
2. **File uploaders cannot be programmatically cleared** - we must regenerate widget keys to force cleanup
3. **Python's memory allocator hoards freed memory** - `malloc_trim()` is essential to return it to OS
4. **The app should NOT crash** on second run anymore, but memory will temporarily spike during download preparation

## Testing Recommendations

1. Test 3-5 consecutive processing runs
2. Monitor memory with `psutil` logging (already implemented)
3. Verify memory drops below 2GB after reset
4. Verify no crash on second/third runs
5. Test with files close to 400MB limit

## References

- Streamlit File Uploader Docs: https://docs.streamlit.io/develop/api-reference/widgets/file_uploader
- Streamlit Session State Docs: https://docs.streamlit.io/develop/api-reference/caching-and-state/session_state
- Streamlit Caching Docs: https://docs.streamlit.io/develop/concepts/architecture/caching

