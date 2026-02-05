import os

def load_dailydialog(folder):
    conversations = []
    
    # iterates through files in the 'folder' directory
    for filename in os.listdir(folder):
        if filename.lower().endswith(".txt"):
            path = os.path.join(folder, filename)
            print(f"Loading DailyDialog: {filename}")
            
            # Reads the file contents
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                
            for line in lines:
                
                parts = line.split("\t")
                dialogue_text = parts[0]
                
                raw_parts = dialogue_text.split("__eou__")
                
                utterances = []
                for part in raw_parts:
                    cleaned = part.strip()
                    
                    # Skip empty segments
                    if not cleaned:
                        continue
                    
                    # Skip segments that are PURELY numbers and spaces
                    if not any(c.isalpha() for c in cleaned):
                        continue
                    
                    # Otherwise its real text
                    utterances.append(cleaned)
                
                
                conv_lines = []
                turn = 0
                
                # convert to 'User/Bot' conversation
                for utt in utterances:
                    if turn % 2 == 0:
                        conv_lines.append(f"User: {utt}")
                    else:
                        conv_lines.append(f"Bot: {utt}")
                    turn += 1    
                
                if len(conv_lines) >= 2:
                    # append all conversations to 1 location
                    conversations.append("\n".join(conv_lines))
            
    return conversations
                
def load_cornell(folder):
    lines_path = os.path.join(folder, "movie_lines.txt")
    conv_path = os.path.join(folder, "movie_conversations.txt")
    
    # --- Extract line data ---
    print("Loading Cornell movie lines...")
    
    id2line = {}  # dictionary with line ID mapped to actually movie line
    
    with open(lines_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            # Extracts useful parts
            parts = line.split(" +++$+++ ")
            if len(parts) == 5:
                line_id = parts[0].strip()      # extract line id
                text = parts[4].strip()         # extracts text
                id2line[line_id] = text         # assigns text to line id
    
    # --- extract Conversation data ---
    print("Loading Cornell conversations...")
    
    conversations = []
    with open(conv_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            parts = line.split(" +++$+++ ")
            if len(parts) == 4:
                utterance_ids = eval(parts[3].strip())    # converts string line to python list
            
                conv_lines = []
                # Numbers the Id's into a dictionary
                for i, uid in enumerate(utterance_ids):
                    # Gets text-line from id2line of line-id
                    text = id2line.get(uid.strip(), "")
                    # Sorts every other line to be User/Bot
                    if i % 2 == 0:
                        conv_lines.append(f"User: {text}")
                    else:
                        conv_lines.append(f"Bot: {text}")
                    
                conversations.append("\n".join(conv_lines))
    
    return conversations

def save_merged(conversations, output_file):
    merged = "\n\n".join(conversations)
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(merged)
        
    print(f"Merged conversations dataset saved -> {output_file}")
    
if __name__ == "__main__":
    dailydialog_folder = "data/raw_conversational/dailydialog"
    cornell_folder = "data/raw_conversational/cornell"
    output_file = "data/processed/conversation_data.txt"
    
    # Load datasets
    dd_convs = load_dailydialog(dailydialog_folder)
    cornell_convs = load_cornell(cornell_folder)
    
    # Merge them
    all_conv = dd_convs + cornell_convs
    
    # Save all
    save_merged(all_conv, output_file)