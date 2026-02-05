import os

def merge_text_files(input_folder, output_file):
    """Merge all .txt files in a folder into 1 big dataset"""
    all_text = []
    
    # List all .txt files and append their content
    for filename in os.listdir(input_folder):
        if filename.lower().endswith(".txt"):
            txt_path = os.path.join(input_folder, filename)
            print(f"Adding: {filename}")
            
            # appends the contents of .txt file to all_text
            with open(txt_path, "r", encoding="utf-8") as f:
                all_text.append(f.read())
                
    merged = "\n\n".join(all_text)
    
    # Save final merged file
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(merged)
        
    print(f"Merged dataset saved -> {output_file}")
    
    if __name__ == "__main__":
        merge_text_files(
            input_folder="data/processed",
            output_file="data/processed/final_dataset.txt"
        )
        