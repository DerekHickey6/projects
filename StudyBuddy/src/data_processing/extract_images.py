import os               # for listing image files
from PIL import Image   # for opening images
import pytesseract      # for OCR (Optical Character recognition)

def extract_text_from_images(input_folder, output_file):
    """Extract text from PNG/JPG images in a folder and save to single .txt file"""
    all_text = []
    
    # Loop through images
    for filename in os.listdir(input_folder):
        if filename.lower().endswith((".png", ".jpeg", ".jpg")):
            # Look for images
            img_path = os.path.join(input_folder, filename)
            print(f"OCR on {filename}")
            
            # Extracts text
            try:
                img = Image.open(img_path)              # Opens image for OCR
                text = pytesseract.image_to_string(img) # Extracts text from image
                all_text.append(text)                   # appends extracted test to 'all_text'
            except Exception as e:
                print(f"Skipping unreadable image: {filename}")
                print("Reason", e)
                continue

    merged_text = "\n\n".join(all_text)
    
    # Write all text to a file
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(merged_text)
        
    print(f"OCR extraction complete -> saved to {output_file}")


if __name__ == "__main__":
    extract_text_from_images(
        input_folder="data/raw_images",
        output_file="data/processed/notes_from_images.txt"
    )