# CSV Merge Wizard

A web application that merges multiple CSV files into a single Excel file with intelligent header matching and Vietnamese character support.

## Features

- **Smart CSV Merging**: Automatically handles different header structures
- **Multi-encoding Support**: Handles UTF-8, UTF-16, and other encodings
- **Vietnamese Character Support**: Properly processes Vietnamese text
- **Web Interface**: User-friendly drag-and-drop interface
- **API Endpoints**: RESTful API for programmatic access

## Local Development

### Prerequisites

- Python 3.11 or higher
- pip or uv package manager

### Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd CsvMergeWizard
```

2. Install dependencies:
```bash
# Using pip
pip install -r requirements.txt

# Or using uv
uv sync
```

3. Run the application:
```bash
python main.py
```

The application will be available at `http://localhost:5000`

## Deployment to Vercel

### Prerequisites

- Vercel account
- Vercel CLI (optional but recommended)

### Deployment Steps

1. **Install Vercel CLI** (optional):
```bash
npm install -g vercel
```

2. **Deploy using Vercel Dashboard**:
   - Go to [vercel.com](https://vercel.com)
   - Click "New Project"
   - Import your GitHub repository
   - Vercel will automatically detect the Python project and use the configuration in `vercel.json`

3. **Deploy using Vercel CLI**:
```bash
vercel
```

### Configuration Files

The following files are configured for Vercel deployment:

- `vercel.json`: Vercel configuration
- `requirements.txt`: Python dependencies
- `main.py`: FastAPI application (modified for serverless deployment)

### Important Notes for Vercel Deployment

1. **File Storage**: The application uses in-memory storage with base64 encoding for temporary files, as Vercel's serverless functions are stateless.

2. **Function Timeout**: The maximum execution time is set to 30 seconds in `vercel.json`. For large files, you may need to increase this limit.

3. **Memory Limits**: Vercel has memory limits for serverless functions. Very large CSV files may exceed these limits.

4. **CORS**: The application is configured to allow all origins for development. For production, you should restrict this to your domain.

## API Endpoints

- `GET /`: Main web interface
- `POST /api/upload`: Upload ZIP file containing CSV files
- `GET /api/download/{file_id}`: Download processed Excel file
- `DELETE /api/cleanup/{file_id}`: Clean up temporary files
- `GET /api/health`: Health check endpoint

## Usage

1. **Prepare your CSV files**: Organize your CSV files in a folder
2. **Create a ZIP file**: Compress the folder containing your CSV files
3. **Upload**: Use the web interface to upload the ZIP file
4. **Download**: Download the merged Excel file

## Limitations

- **File Size**: Limited by Vercel's serverless function limits
- **Processing Time**: Limited to 30 seconds per request
- **Memory**: Limited by Vercel's memory allocation
- **Temporary Storage**: Files are stored in memory and will be lost when the function completes

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally
5. Submit a pull request

## License

This project is open source and available under the [MIT License](LICENSE). 