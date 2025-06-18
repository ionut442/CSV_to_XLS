# CSV to Excel Converter

## Overview

This is a web-based CSV to Excel converter application that allows users to upload folders containing CSV files and convert them to Excel format. The application is built with a Python FastAPI backend and a React frontend, designed to handle Vietnamese character encoding properly and provide a smooth user experience for bulk CSV conversion.

## System Architecture

### Frontend Architecture
- **Framework**: React 18 (loaded via CDN)
- **Build System**: Babel (browser-based compilation)
- **Styling**: Tailwind CSS with custom CSS enhancements
- **Icons**: Feather Icons
- **HTTP Client**: Axios for API communication
- **Deployment**: Single HTML file with inline React components

### Backend Architecture
- **Framework**: FastAPI (Python)
- **Server**: Uvicorn ASGI server
- **File Processing**: Pandas for CSV manipulation, OpenPyXL for Excel output
- **File Handling**: Python's tempfile and zipfile modules for temporary storage
- **Encoding Support**: UTF-8 with BOM and fallback encoding detection for Vietnamese characters

## Key Components

### Backend Components
1. **File Upload Handler** (`/api/upload`)
   - Accepts ZIP files containing CSV files
   - Extracts and processes CSV files recursively
   - Converts CSV to Excel with proper Vietnamese encoding
   - Returns processed Excel files as ZIP archive

2. **File Download Handler** (`/api/download/{fileId}`)
   - Serves processed Excel files for download
   - Manages temporary file cleanup

3. **Cleanup Handler** (`/api/cleanup/{fileId}`)
   - Removes temporary files after download

### Frontend Components
1. **File Upload Zone**
   - Drag-and-drop interface for ZIP file uploads
   - Visual feedback for upload progress

2. **Processing Status**
   - Real-time status updates during file conversion
   - Progress indicators and error handling

3. **Download Interface**
   - Automatic download trigger for processed files
   - File cleanup management

## Data Flow

1. **Upload Phase**:
   - User uploads ZIP file containing CSV files
   - Backend extracts ZIP and identifies all CSV files recursively
   - Each CSV file is processed with Vietnamese encoding support

2. **Processing Phase**:
   - CSV files are read with UTF-8-sig encoding (BOM support)
   - Fallback to UTF-8 if BOM reading fails
   - Data is converted to Excel format using OpenPyXL
   - Processed files are packaged into a new ZIP archive

3. **Download Phase**:
   - Processed ZIP file is made available for download
   - Frontend automatically triggers download
   - Temporary files are cleaned up after successful download

## External Dependencies

### Python Dependencies
- **FastAPI**: Web framework for API endpoints
- **Uvicorn**: ASGI server for FastAPI
- **Pandas**: Data manipulation and CSV processing
- **OpenPyXL**: Excel file generation
- **Python-multipart**: File upload handling

### Frontend Dependencies (CDN)
- **React 18**: UI framework
- **Babel**: JSX compilation
- **Axios**: HTTP client
- **Tailwind CSS**: Utility-first CSS framework
- **Feather Icons**: Icon library

## Deployment Strategy

### Development Environment
- **Platform**: Replit with Python 3.11 runtime
- **Package Manager**: UV for Python dependency management
- **Port**: Application runs on port 8000
- **Auto-install**: Dependencies are installed automatically on startup

### Production Considerations
- Static file serving through FastAPI
- CORS middleware configured for cross-origin requests
- Temporary file management with automatic cleanup
- Error handling and logging for production debugging

## Changelog

- June 18, 2025. Initial setup

## User Preferences

Preferred communication style: Simple, everyday language.