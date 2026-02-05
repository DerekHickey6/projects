import os
import sentencepiece as spm

# 1. Path to training corpus
CORPUS_PATH = "data/processed/final_dataset.txt"

# 2. where to save the tokenizer files
MODEL_PREFIX = "studybuddy_sp"          # will create studybuddy_sp.model / .vocab
VOCAB_SIZE = 10000

def main():
    if not os.path.exists(CORPUS_PATH):
        raise FileNotFoundError(f"Corpus not found at: {CORPUS_PATH}")

    print("Corpus found. Training SentencePiece tokenizer...")

    # 3. Train SentencePiece tokenizer
    spm.SentencePieceTrainer.train(
        input=CORPUS_PATH,
        model_prefix=MODEL_PREFIX,
        vocab_size=VOCAB_SIZE,
        character_coverage=1.0,     # includes all unicode for math symbols
        model_type="unigram"        # works best for math/STEM fields
    )

    # 4. Show whats done
    model_file = MODEL_PREFIX + ".model"
    vocab_file = MODEL_PREFIX + ".vocab"

    if os.path.exists(model_file) and os.path.exists(vocab_file):
        print(f"Done Training -- {model_file} -- {vocab_file}")
    else:
        print("Training finished but error occured, tokenizer files not found")

if __name__ == "__main__":
    main()