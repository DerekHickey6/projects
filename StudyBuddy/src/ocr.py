import mss
import pytesseract
from PIL import Image
import re
from collections import Counter

# fucntion to grab text from all monitors
def grab_text():
    """Takes a screenshot and extract text using OCR"""
    all_text = ""
    # using mss - screenshotting capture
    with mss.mss() as sct:
        for i, monitor in enumerate(sct.monitors[1:], start=1):
            # print(f"Capturing monitor: {i}...")
            # Takes screenshot of monitors and saves as shot 
            shot = sct.grab(monitor)
            # Copies the screenshot and saves as PIL.image
            img = Image.frombytes("RGB", (shot.width, shot.height), shot.rgb)
            # Converts image to a string for further processing
            text = pytesseract.image_to_string(img)
            all_text += f"\n\n ===== Monitor {i} =====\n {text}"
            
        return all_text

# Exctracts words from text parameter and returns the top 'K' words in the text
def extract_keywords(text: str, top_k: int =10):
    # performs a regex substitution, "substitute anything thats not a letter or space (aka numbers, punctuation) and replace with a single space"
    cleaned = re.sub(r'[^A-Za-z ]+', ' ', text).lower()
    # Splits on whitespace and creates list from words in text
    words = cleaned.split()
    # initializes a set of unimportant common words 
    stop_words = {
        "the","and","for","that","this","with","from","are","was","were","will",
        "your","you","they","them","his","her","she","he","its","have","has",
        "had","been","being","to","of","in","on","at","by","as","is","it","a","an"
    }
    # List comp. of eliminates stop_words and short words
    words = [w for w in words if len(w) > 3 and w not in stop_words]
    # counts frequency of each word and stores as dictionary
    freq = Counter(words)
    # isolates the 'top_k' amount of most common words
    common = freq.most_common(top_k)
    out = []
    for word, count in common:
        # Appends each word from the common dict
        out.append(word)
    
    return out
    
    