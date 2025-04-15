# Document Chunker

I was cramming for an exam and needed to study a PDF that was several hundred pages long. I usually upload PDFs into ChatGPT to help me learn, but it struggles with large files. So, while eating Mala, I built a quick POC that splits PDF and Word (DOCX) documents into smaller chunks. From there, I used ChatGPT to refactor the code and make it more performant.

## Features

- Support for both PDF and Word (DOCX) files
- Memory-mapped file handling for processing large files efficiently
- Multi-threaded processing with configurable thread count
- Optimized for minimal memory usage with large documents
- Detailed progress and result reporting
- Command-line and GUI interfaces with cancel capability
- Error handling with detailed feedback
- Performance metrics and timing information

## Installation

Install the required dependencies:

```
pip install -r requirements.txt
```

## Usage

### Command-line Version

Basic usage:

```
python document_chunker.py input_file.pdf
python document_chunker.py input_file.docx
```

This will break the document into chunks of X pages/paragraphs each and save them in a directory called "chunks".

#### Options

- `--output-dir`: Specify a custom output directory (default: "chunks")
- `--chunk-size`: Specify the number of pages/paragraphs per chunk (default: 2)
- `--max-workers`: Specify the maximum number of worker threads (default: CPU count + 4)

Example with options:

```
python document_chunker.py input_file.pdf --output-dir my_chunks --chunk-size 5 --max-workers 8
```

### Graphical User Interface (GUI)

For a more user-friendly experience, use the GUI version:

```
python document_chunker_ui.py
```

The GUI provides the following features:
- File browser to select the input document (PDF or DOCX)
- File information display showing file type and size
- Directory browser to choose where to save chunks
- Configuration for pages/paragraphs per chunk and worker threads
- Progress indicator with cancel capability
- Result log showing the details of created chunks and timing information

## Requirements

- Python 3.6+
- PyPDF2 (for PDF processing)
- python-docx (for Word document processing)
- tkinter (for the GUI, included with most Python installations) 
