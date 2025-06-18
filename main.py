import os
import tempfile
import zipfile
import shutil
from pathlib import Path
from typing import List
import pandas as pd
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="CSV to Excel Converter", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5000", "http://127.0.0.1:5000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global storage for processed files
processed_files = {}

def find_csv_files(directory: Path) -> List[Path]:
    """Recursively find all CSV files in directory and subdirectories."""
    csv_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.csv'):
                csv_files.append(Path(root) / file)
    return csv_files

def read_csv_with_vietnamese_support(file_path: Path) -> pd.DataFrame:
    """Read CSV file with proper Vietnamese character support."""
    # Check for BOM to detect UTF-16 encoding
    with open(file_path, 'rb') as f:
        first_bytes = f.read(4)
    
    # Detect UTF-16 BOM patterns
    if first_bytes.startswith(b'\xff\xfe'):
        # UTF-16 LE BOM
        primary_encodings = ['utf-16-le', 'utf-16']
    elif first_bytes.startswith(b'\xfe\xff'):
        # UTF-16 BE BOM  
        primary_encodings = ['utf-16-be', 'utf-16']
    elif first_bytes.startswith(b'\xef\xbb\xbf'):
        # UTF-8 BOM
        primary_encodings = ['utf-8-sig', 'utf-8']
    else:
        # No BOM detected, try common encodings
        primary_encodings = ['utf-8-sig', 'utf-8', 'cp1252', 'latin1']
    
    # Try all encodings including fallbacks
    all_encodings = primary_encodings + ['utf-16', 'utf-16-le', 'utf-16-be', 'utf-8-sig', 'utf-8', 'cp1252', 'latin1']
    # Remove duplicates while preserving order
    encodings = list(dict.fromkeys(all_encodings))
    
    for encoding in encodings:
        try:
            # Read with error handling for inconsistent field counts
            df = pd.read_csv(
                file_path, 
                encoding=encoding,
                on_bad_lines='skip',  # Skip malformed lines
                engine='python',     # Use Python engine for better error handling
                sep=None,            # Auto-detect separator (important for UTF-16)
                quotechar='"',       # Handle quoted fields
                skipinitialspace=True # Skip spaces after delimiter
            )
            
            # Check if we got any data
            if not df.empty:
                # Clean column names to remove any remaining BOM or control characters
                df.columns = df.columns.str.replace('\ufeff', '').str.replace('\x00', '').str.strip()
                logger.info(f"Successfully read {file_path} with encoding {encoding}, shape: {df.shape}")
                return df
            
        except (UnicodeDecodeError, pd.errors.EmptyDataError, pd.errors.ParserError) as e:
            logger.warning(f"Failed to read {file_path} with encoding {encoding}: {str(e)}")
            continue
    
    # Return empty DataFrame if all attempts fail
    logger.error(f"Could not read {file_path} with any method")
    return pd.DataFrame()

def merge_csv_files(csv_files: List[Path]) -> pd.DataFrame:
    """Merge multiple CSV files with same headers into one DataFrame."""
    if not csv_files:
        raise ValueError("No CSV files found")
    
    dataframes = []
    header_reference = None
    successful_files = 0
    
    for csv_file in csv_files:
        try:
            logger.info(f"Processing file: {csv_file}")
            df = read_csv_with_vietnamese_support(csv_file)
            
            if df.empty:
                logger.warning(f"Empty or unreadable CSV file: {csv_file}")
                continue
            
            # Clean column names (remove extra spaces, BOM, null chars, etc.)
            df.columns = df.columns.str.replace('\ufeff', '').str.replace('\x00', '').str.strip()
            
            # Check if headers match (for first file, set as reference)
            if header_reference is None:
                header_reference = list(df.columns)
                logger.info(f"Reference headers ({len(header_reference)} columns): {header_reference}")
                dataframes.append(df)
                successful_files += 1
            else:
                current_headers = list(df.columns)
                
                # Try to match headers with some flexibility
                if len(current_headers) == len(header_reference):
                    # Same number of columns, assume they match
                    df.columns = header_reference  # Align column names
                    dataframes.append(df)
                    successful_files += 1
                    logger.info(f"Added file {csv_file} with aligned headers")
                elif set(current_headers).issubset(set(header_reference)):
                    # Current file has subset of reference headers
                    df_aligned = df.reindex(columns=header_reference, fill_value='')
                    dataframes.append(df_aligned)
                    successful_files += 1
                    logger.info(f"Added file {csv_file} with subset headers, filled missing columns")
                elif set(header_reference).issubset(set(current_headers)):
                    # Current file has superset of reference headers
                    df_subset = df[header_reference]
                    dataframes.append(df_subset)
                    successful_files += 1
                    logger.info(f"Added file {csv_file} with superset headers, selected matching columns")
                else:
                    # Try to find common columns
                    common_columns = list(set(header_reference) & set(current_headers))
                    if len(common_columns) >= len(header_reference) * 0.7:  # At least 70% match
                        # Update reference to common columns for all dataframes
                        header_reference = common_columns
                        # Reprocess existing dataframes
                        dataframes = [existing_df[common_columns] for existing_df in dataframes]
                        df_common = df[common_columns]
                        dataframes.append(df_common)
                        successful_files += 1
                        logger.info(f"Updated reference headers to common columns ({len(common_columns)}): {common_columns}")
                    else:
                        logger.warning(f"Header mismatch in {csv_file}. Expected: {header_reference}, Got: {current_headers}. Skipping file.")
                        continue
            
        except Exception as e:
            logger.error(f"Error processing {csv_file}: {str(e)}")
            continue
    
    if not dataframes:
        raise ValueError("No valid CSV files could be processed. Check that files have consistent structure and valid encoding.")
    
    # Concatenate all dataframes
    merged_df = pd.concat(dataframes, ignore_index=True)
    logger.info(f"Successfully merged {successful_files} out of {len(csv_files)} CSV files into {len(merged_df)} rows with {len(merged_df.columns)} columns")
    
    return merged_df

@app.post("/api/upload")
async def upload_folder(file: UploadFile = File(...)):
    """Upload and process folder containing CSV files."""
    filename = file.filename or "upload.zip"
    if not filename.endswith('.zip'):
        raise HTTPException(status_code=400, detail="Please upload a ZIP file containing your folder structure")
    
    # Create temporary directory for processing
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, filename)
    extract_dir = os.path.join(temp_dir, "extracted")
    
    try:
        # Save uploaded zip file
        with open(zip_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Extract zip file
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        # Find all CSV files recursively
        csv_files = find_csv_files(Path(extract_dir))
        
        if not csv_files:
            raise HTTPException(status_code=400, detail="No CSV files found in the uploaded folder")
        
        logger.info(f"Found {len(csv_files)} CSV files")
        
        # Merge CSV files
        merged_df = merge_csv_files(csv_files)
        
        # Create Excel file
        excel_filename = "merged_data.xlsx"
        excel_path = os.path.join(temp_dir, excel_filename)
        
        # Save to Excel with proper encoding
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            merged_df.to_excel(writer, index=False, sheet_name='Merged Data')
        
        # Store file info for download
        file_id = f"temp_{len(processed_files)}"
        processed_files[file_id] = {
            'path': excel_path,
            'filename': excel_filename,
            'temp_dir': temp_dir
        }
        
        return {
            'success': True, 
            'message': f'Successfully processed {len(csv_files)} CSV files into Excel format',
            'file_id': file_id,
            'row_count': len(merged_df),
            'csv_count': len(csv_files)
        }
        
    except Exception as e:
        # Clean up temp directory on error
        shutil.rmtree(temp_dir, ignore_errors=True)
        logger.error(f"Error processing upload: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing files: {str(e)}")

@app.get("/api/download/{file_id}")
async def download_excel(file_id: str):
    """Download the processed Excel file."""
    if file_id not in processed_files:
        raise HTTPException(status_code=404, detail="File not found or expired")
    
    file_info = processed_files[file_id]
    
    if not os.path.exists(file_info['path']):
        raise HTTPException(status_code=404, detail="File no longer available")
    
    return FileResponse(
        path=file_info['path'],
        filename=file_info['filename'],
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

@app.delete("/api/cleanup/{file_id}")
async def cleanup_file(file_id: str):
    """Clean up temporary files after download."""
    if file_id in processed_files:
        file_info = processed_files[file_id]
        shutil.rmtree(file_info['temp_dir'], ignore_errors=True)
        del processed_files[file_id]
        return {'success': True, 'message': 'File cleaned up successfully'}
    
    return {'success': False, 'message': 'File not found'}

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "message": "CSV to Excel Converter API is running"}

# Serve React frontend
app.mount("/", StaticFiles(directory=".", html=True), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
