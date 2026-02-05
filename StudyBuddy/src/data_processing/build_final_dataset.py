import os

def merge_processed_texts(input_folder, output_file):
    
    all_text = []
    
    # Loop through all files in directory
    for filename in os.listdir(input_folder):
        # use only .txt files
        if not filename.lower().endswith(".txt"):
            continue
        
        # Avoid merging final_dataset.txt into itself if re-run
        if filename == os.path.basename(output_file):
            continue
        
        file_path = os.path.join(input_folder, filename)
        print(f"Adding: {filename}")
        
        # Read text from file
        with open(file_path, "r",encoding="utf-8") as f:
            text = f.read().strip()
            
        # Skips empty files
        if not text:
            continue
        
        all_text.append(text)
        
    # Join every file's content with newlines for separation
    merged_text = "\n\n".join(all_text)
    
    # Save the merged dataset
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(merged_text)
        
    print(f"\n  Final dataset daved to -> {output_file}")
    
if __name__ == "__main__":
    merge_processed_texts(
        input_folder="data/processed",
        output_file="data/processed/final_dataset.txt"
    )
    