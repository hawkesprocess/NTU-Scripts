import os
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from pathlib import Path
import threading

# Import the document chunker functionality
from document_chunker import chunk_document

class DocumentChunkerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Document Chunker")
        
        # Maximize window (works on Windows)
        self.root.state('zoomed')  # This works on Windows
        
        # Configure grid weights
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Configure styles and create UI
        self.setup_styles()
        self.create_widgets()
        
        # Processing state
        self.processing = False
        self.processing_thread = None
        
    def setup_styles(self):
        """Set up the styles for the UI."""
        self.style = ttk.Style()
        self.style.configure("TButton", padding=6)
        self.style.configure("TFrame", padding=10)
        self.style.configure("TLabel", padding=5)
        self.style.configure("Process.TButton", font=("Helvetica", 10, "bold"))
        self.style.configure("Status.TLabel", foreground="blue", font=("Helvetica", 9))
        self.style.configure("Title.TLabel", font=("Helvetica", 11, "bold"))
        self.style.configure("Section.TFrame", relief="groove", padding=10)
        
    def create_widgets(self):
        # Create main frame with proper weights
        self.main_frame = ttk.Frame(self.root, padding="15")
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(6, weight=1)  # Give weight to results section
        
        # Input section
        input_section = ttk.Frame(self.main_frame, style="Section.TFrame")
        input_section.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 15))
        input_section.grid_columnconfigure(1, weight=1)

        # Input title
        ttk.Label(
            input_section, 
            text="Document Selection", 
            style="Title.TLabel"
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))
        
        # Input file selection
        ttk.Label(input_section, text="Input File:").grid(row=1, column=0, sticky="w", pady=5)
        
        self.input_frame = ttk.Frame(input_section)
        self.input_frame.grid(row=1, column=1, sticky="ew", pady=5)
        self.input_frame.grid_columnconfigure(0, weight=1)
        
        self.input_path_var = tk.StringVar()
        self.input_entry = ttk.Entry(self.input_frame, textvariable=self.input_path_var)
        self.input_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        self.browse_btn = ttk.Button(self.input_frame, text="Browse", command=self.browse_input)
        self.browse_btn.grid(row=0, column=1)
        
        # File info label
        self.file_info_var = tk.StringVar()
        self.file_info_label = ttk.Label(input_section, textvariable=self.file_info_var, style="Status.TLabel")
        self.file_info_label.grid(row=2, column=0, columnspan=2, sticky="w", pady=(2, 5))
        
        # Output section
        output_section = ttk.Frame(self.main_frame, style="Section.TFrame")
        output_section.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 15))
        output_section.grid_columnconfigure(1, weight=1)
        
        # Output title
        ttk.Label(
            output_section, 
            text="Output Settings", 
            style="Title.TLabel"
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))
        
        # Output directory selection
        ttk.Label(output_section, text="Output Directory:").grid(row=1, column=0, sticky="w", pady=5)
        
        self.output_frame = ttk.Frame(output_section)
        self.output_frame.grid(row=1, column=1, sticky="ew", pady=5)
        self.output_frame.grid_columnconfigure(0, weight=1)
        
        self.output_dir_var = tk.StringVar(value="chunks")
        self.output_entry = ttk.Entry(self.output_frame, textvariable=self.output_dir_var)
        self.output_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        self.output_browse_btn = ttk.Button(self.output_frame, text="Browse", command=self.browse_output)
        self.output_browse_btn.grid(row=0, column=1)
        
        # Processing parameters section
        params_section = ttk.Frame(self.main_frame, style="Section.TFrame")
        params_section.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 15))
        params_section.grid_columnconfigure(1, weight=1)
        
        # Parameters title
        ttk.Label(
            params_section, 
            text="Processing Parameters", 
            style="Title.TLabel"
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))
        
        # Chunk size and threads frame
        self.params_frame = ttk.Frame(params_section)
        self.params_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=5)
        
        # Chunk size
        ttk.Label(self.params_frame, text="Items per Chunk:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        
        self.chunk_size_var = tk.IntVar(value=2)  # Default to 2 to match command line
        self.chunk_size_spinbox = ttk.Spinbox(
            self.params_frame, 
            from_=1, 
            to=1000, 
            textvariable=self.chunk_size_var, 
            width=5
        )
        self.chunk_size_spinbox.grid(row=0, column=1, padx=(0, 10))
        
        # Chunk size description label
        self.chunk_size_desc_var = tk.StringVar(value="(pages for PDF, paragraphs for Word)")
        self.chunk_size_desc = ttk.Label(
            self.params_frame, 
            textvariable=self.chunk_size_desc_var, 
            style="Status.TLabel"
        )
        self.chunk_size_desc.grid(row=0, column=2, sticky="w", padx=(0, 20))
        
        # Max workers
        ttk.Label(self.params_frame, text="Worker Threads:").grid(row=0, column=3, sticky="w", padx=(0, 10))
        
        self.max_workers_var = tk.IntVar(value=min(32, os.cpu_count() + 4) if os.cpu_count() else 8)
        self.max_workers_spinbox = ttk.Spinbox(
            self.params_frame,
            from_=1,
            to=64,
            textvariable=self.max_workers_var,
            width=5
        )
        self.max_workers_spinbox.grid(row=0, column=4)
        
        # Status and progress section
        status_section = ttk.Frame(self.main_frame, style="Section.TFrame")
        status_section.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 15))
        status_section.grid_columnconfigure(1, weight=1)

        # Status and progress title
        ttk.Label(
            status_section, 
            text="Status", 
            style="Title.TLabel"
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))

        # Progress bar
        ttk.Label(status_section, text="Progress:").grid(row=1, column=0, sticky="w", pady=5)
        
        self.progress_var = tk.DoubleVar(value=0.0)
        self.progress_bar = ttk.Progressbar(
            status_section, 
            orient="horizontal", 
            mode="indeterminate",
            variable=self.progress_var
        )
        self.progress_bar.grid(row=1, column=1, sticky="ew", pady=5, padx=(5, 0))

        # Status label
        ttk.Label(status_section, text="Status:").grid(row=2, column=0, sticky="w", pady=5)
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(
            status_section, 
            textvariable=self.status_var, 
            style="Status.TLabel"
        )
        self.status_label.grid(row=2, column=1, sticky="w", pady=5, padx=(5, 0))
        
        # Action buttons section
        action_frame = ttk.Frame(self.main_frame)
        action_frame.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(0, 15))
        action_frame.grid_columnconfigure(0, weight=1)
        action_frame.grid_columnconfigure(1, weight=1)
        
        # Process button
        self.process_btn = ttk.Button(
            action_frame,
            text="Process Document",
            command=self.process_document,
            style="Process.TButton"
        )
        self.process_btn.grid(row=0, column=0, padx=5, pady=5, sticky="e")
        
        # Cancel button (hidden initially)
        self.cancel_btn = ttk.Button(
            action_frame,
            text="Cancel",
            command=self.cancel_processing,
        )
        self.cancel_btn.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.cancel_btn.grid_remove()  # Hide initially
        
        # Results section
        results_section = ttk.Frame(self.main_frame, style="Section.TFrame")
        results_section.grid(row=5, column=0, columnspan=2, sticky="nsew")
        results_section.grid_columnconfigure(0, weight=1)
        results_section.grid_rowconfigure(1, weight=1)
        
        # Results title
        ttk.Label(
            results_section, 
            text="Results", 
            style="Title.TLabel"
        ).grid(row=0, column=0, sticky="w", pady=(0, 8))
        
        # Output log
        self.log_frame = ttk.Frame(results_section)
        self.log_frame.grid(row=1, column=0, sticky="nsew")
        self.log_frame.grid_columnconfigure(0, weight=1)
        self.log_frame.grid_rowconfigure(0, weight=1)
        
        self.output_text = tk.Text(self.log_frame, wrap="word", height=10)
        self.output_text.grid(row=0, column=0, sticky="nsew")
        
        self.scrollbar = ttk.Scrollbar(self.log_frame, orient="vertical", command=self.output_text.yview)
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.output_text.config(yscrollcommand=self.scrollbar.set)
    
    def browse_input(self):
        filepath = filedialog.askopenfilename(
            title="Select document file",
            filetypes=[
                ("Supported documents", "*.pdf *.docx"), 
                ("PDF files", "*.pdf"),
                ("Word documents", "*.docx"),
                ("All files", "*.*")
            ]
        )
        if filepath:
            self.input_path_var.set(filepath)
            self.update_file_info(filepath)
    
    def update_file_info(self, filepath):
        """Update the file info label with details about the selected file."""
        try:
            file_path = Path(filepath)
            file_size = os.path.getsize(filepath)
            file_ext = file_path.suffix.lower()
            
            # Format file size
            if file_size < 1024:
                size_str = f"{file_size} bytes"
            elif file_size < 1024 * 1024:
                size_str = f"{file_size / 1024:.2f} KB"
            else:
                size_str = f"{file_size / (1024 * 1024):.2f} MB"
            
            # Set appropriate file type and chunk description
            if file_ext == ".pdf":
                file_type = "PDF document"
                self.chunk_size_desc_var.set("(pages per chunk)")
            elif file_ext == ".docx":
                file_type = "Word document"
                self.chunk_size_desc_var.set("(paragraphs per chunk)")
            else:
                file_type = "Unknown file type"
                self.chunk_size_desc_var.set("(items per chunk)")
            
            self.file_info_var.set(f"{file_path.name} ({size_str}) - {file_type}")
        except Exception:
            self.file_info_var.set("")
    
    def browse_output(self):
        dirpath = filedialog.askdirectory(title="Select Output Directory")
        if dirpath:
            self.output_dir_var.set(dirpath)
    
    def process_document(self):
        if self.processing:
            return
        
        # Get and validate inputs
        input_path = self.input_path_var.get().strip()
        output_dir = self.output_dir_var.get().strip()
        chunk_size = self.chunk_size_var.get()
        max_workers = self.max_workers_var.get()
        
        if not input_path or not output_dir or chunk_size < 1 or max_workers < 1:
            messagebox.showerror("Error", "Please provide valid input file, output directory, chunk size, and max workers.")
            return
        
        file_ext = Path(input_path).suffix.lower()
        if file_ext not in ['.pdf', '.docx']:
            messagebox.showerror("Error", "Unsupported file type. Please select a PDF or Word document (.docx) file.")
            return
        
        # Update UI for processing state
        self.output_text.delete(1.0, tk.END)
        self.processing = True
        self.process_btn.grid_remove()
        self.cancel_btn.grid()
        self.status_var.set("Processing document... Please wait.")
        self.progress_bar.start(10)
        self.output_text.insert(tk.END, "Starting document processing...\n")
        self.set_inputs_state("disabled")
        
        # Start processing thread
        self.processing_thread = threading.Thread(
            target=self._process_document_thread, 
            args=(input_path, output_dir, chunk_size, max_workers)
        )
        self.processing_thread.daemon = True
        self.processing_thread.start()
    
    def cancel_processing(self):
        if not self.processing:
            return
        self.cancel_btn.config(state="disabled")
        self.status_var.set("Cancelling...")
        self.output_text.insert(tk.END, "\nCancelling processing...\n")
        self.processing = False
    
    def set_inputs_state(self, state):
        """Enable or disable input controls."""
        for widget in (self.input_entry, self.browse_btn, self.output_entry, 
                      self.output_browse_btn, self.chunk_size_spinbox, 
                      self.max_workers_spinbox):
            widget.config(state=state)
    
    def _process_document_thread(self, input_path, output_dir, chunk_size, max_workers):
        """Thread function to process the document."""
        try:
            if not self.processing:
                return
            success, message = chunk_document(input_path, output_dir, chunk_size, max_workers)
            self.root.after(0, self._update_ui_after_processing, success, message)
        except Exception as e:
            self.root.after(0, self._update_ui_after_processing, False, f"Error: {str(e)}")
    
    def _update_ui_after_processing(self, success, message):
        """Update the UI after processing is complete."""
        # Reset UI state
        self.progress_bar.stop()
        self.processing = False
        self.processing_thread = None
        self.cancel_btn.grid_remove()
        self.process_btn.grid()
        self.set_inputs_state("normal")
        
        # Show results
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, message)
        
        if success:
            self.status_var.set("Document successfully chunked!")
        else:
            self.status_var.set("Error occurred during processing")
            messagebox.showerror("Error", "Some errors occurred during processing. See the results for details.")


def main():
    root = tk.Tk()
    app = DocumentChunkerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main() 