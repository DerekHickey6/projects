import os
from PyPDF2 import PdfReader

def extract_text_from_pdfs(input_folder, output_file):
    """Extract text from all PDF files in a folder and save to a single .txt file"""
    all_text = []
    
    # Loop through all files in the folder
    for filename in os.listdir(input_folder):
        # Only process files that end with .pdf
        if filename.lower().endswith(".pdf"):
            # Concatenates path names
            pdf_path = os.path.join(input_folder, filename)
            print(f"Reading: {filename}")
            
            # initialize a reader to read the current files contents
            reader = PdfReader(pdf_path)
            
            # Loop through each page and extract all text
            for page in reader.pages:
                # Extract text; if none, use empty string
                text = page.extract_text() or ""
                all_text.append(text)
    
    # Merge all into one string
    merged_text = "\n\n".join(all_text)
    
    # Write the merged text out to a .txt file
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(merged_text)
    
    print(f"Extraction complete -> savied to {output_file}")
    
    
if __name__ == "__main__":
    # When run directly, extracts data from raw_pdfs and into data/processed/notes_from_pdf.txt
    extract_text_from_pdfs(
        input_folder="data/raw_pdfs",
        output_file="data/processed/notes_from_pdf.txt"
    )
            