# ===================================================================================== #
#    Train Model - contians:                                                            #
#       Dataset Loader -- Training Save Point -- Vocab/Prediction -- Training Loop      #
#                                                                                       #
# ===================================================================================== #

import os
import re
import sys
import time
import shutil
from tqdm import tqdm
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import torch
from torch import nn
from torch.utils.data import Dataset, DataLoader

from ai_engine import SentencePieceTokenizer, TinyGPT

# =========================== #
#       Load the dataset      #
# =========================== #
def load_corpus(path):
    """Load the full training text from final_dataset.txt"""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

# =============================== #
#       Training Save Point       #
# =============================== #
def save_checkpoint(model, optimizer, epoch, global_step, folder="models"):
    # 7. Save Model + tokenizer
    os.makedirs(folder, exist_ok=True)
    ckpt_path = f"{folder}/tinyGPT_checkpoint.pt"

    # saves model
    torch.save({
        "model": model.state_dict(),
        "optimizer": optimizer.state_dict(),
        "epoch": epoch,
        "global_step": global_step
    }, ckpt_path)

    sp_model_path = "studybuddy_sp.model"
    if os.path.exists(sp_model_path):
        shutil.copy(sp_model_path, f"{folder}/studybuddy_sp.model")

    print(f"✔ Checkpoint saved → {ckpt_path}")

# =============================== #
#       Training Load Point       #
# =============================== #
def load_checkpoint(model, optimizer, folder="models"):
    # Build checkpoint path
    ckpt_path = f"{folder}/tinyGPT_checkpoint.pt"

    # Check if file exists
    if not os.path.exists(ckpt_path):
        print("No checkpoint found - starting from scratch.")
        return model, optimizer, 0, 0   # epoch, global_step
    else: print(f"Loading checkpoint from {ckpt_path}")

    # Load model from checkpoint path
    data = torch.load(ckpt_path, map_location="cpu")

    # Restore model and optimizer state
    model.load_state_dict(data["model"])
    optimizer.load_state_dict(data["optimizer"])

    # Pull out training progress info
    epoch = data.get("epoch", 0)
    global_step = data.get("global_step", 0)

    print(f"Loaded checkpoint at epoch {epoch}, step {global_step}")

    return model, optimizer, epoch, global_step



# ======================================================= #
#       Builds Vocab and Trains to Predict Next Char      #
# ======================================================= #
class TextDataset(Dataset):
    def __init__(self, tokenizer, text, seq_len=200, max_samples = 500_000):

        self.seq_len = seq_len
        self.tokenizer = tokenizer

        # Encode entire text once into subwords
        ids = tokenizer.sp.encode(text, out_type=int)

        max_i = min(len(ids) - seq_len - 1, max_samples)

        # Converr to a numpy array
        ids_np = np.array(ids, dtype=np.int32)

        # Preallocate arrays for input + targets
        self.inputs = np.lib.stride_tricks.sliding_window_view(
            ids_np, window_shape=seq_len
        )[:max_i]

        self.targets = np.lib.stride_tricks.sliding_window_view(
            ids_np[1:], window_shape=seq_len
        )[:max_i]

    def __len__(self):
        return len(self.inputs)


    def __getitem__(self, idx):
        x = torch.from_numpy(self.inputs[idx]).long()
        y = torch.from_numpy(self.targets[idx]).long()
        return x, y


# ======================= #
#       Train Model       #
# ======================= #
def train_model(corpus_path= "data/processed/final_dataset.txt",
                seq_len=192,
                batch_size=32,
                epochs=2,
                lr=5e-4,
                max_samples=500_000,
                checkpoint_folder="models"):
    """Main training loop for TinyTransformer"""
    # 1. Load text
    print(f"Loading corpus from: {corpus_path}")
    text = load_corpus(corpus_path)
    tokenizer = SentencePieceTokenizer("models/studybuddy_sp.model")

    # Sanity-check tokenizer
    sample = text[:200]
    encoded = tokenizer.encode(sample)[:50]  # show first 50 tokens
    decoded = tokenizer.decode(encoded)


    print("\n--- Tokenizer Sanity Check ---")
    print("Sample text:", sample[:100].replace("\n"," "))
    print("Encoded IDs:", encoded)
    print("Decoded text:", decoded)
    print("-------------------------------\n")

    # 2. Build dataset from string to tensors

    dataset = TextDataset(tokenizer, text, seq_len=seq_len, max_samples=max_samples)
    vocab_size = tokenizer.vocab_size

    print(f"Vocab Size: {vocab_size}")
    print(f"Training samples: {len(dataset)}")

    # 3. initialize Dataloader
    loader = DataLoader(dataset,
                        batch_size=batch_size,
                        shuffle=True,
                        num_workers=4,      # uses multiple CPU threads
                        pin_memory=True,    # speeds host-to-device transfer
                        persistent_workers=True
                    )

    # Device (CPU or GPU)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device → {device}")

    # 4. Create a model and putting it on the target device
    model = TinyGPT(vocab_size=vocab_size,
                    embed_dim=128,
                    n_heads=4,
                    hidden_dim=256,
                    max_seq_len=seq_len)
    model.to(device)



    # 5. create optimizer
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)

    # Resume checkpoint training if checkpoint available
    model, optimizer, start_epoch, global_step = load_checkpoint(model, optimizer, folder=checkpoint_folder)

    # Create loss function
    loss_fn = nn.CrossEntropyLoss()

    save_every = 2000
    # 6. Training loop
    model.train()
    total_start_time = time.time()
    for epoch in range(start_epoch, epochs):
        epoch_start_time = time.time()
        total_loss = 0.0

        pbar = tqdm(loader, desc=f"Epoch {epoch+1}")

        for batch_idx, (x, y) in enumerate(pbar):
            # put data to target device
            x = x.to(device)
            y = y.to(device)

            # Zero previous gradients
            optimizer.zero_grad()

            # Forward pass
            logits = model(x)      # (batch, seq, vocab)

            # Flatten logits + target for loss calculation
            batch_size_now, seq_len_now, vocab_now = logits.shape
            logits_flat = logits.reshape(-1, vocab_now)    # (batch*seq, vocab)
            y_flat = y.reshape(-1)

            # Compute the loss
            loss = loss_fn(logits_flat, y_flat)
            # Backpropagation
            loss.backward()

            # Clips gradients
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)

            optimizer.step()

            total_loss += loss.item()
            avg = total_loss / (batch_idx + 1)

            pbar.set_postfix({"Loss": f"{avg:.4f}"})

            # Show progress every 100 batches
            if (batch_idx + 1) % 100 == 0:
                elapsed = time.time() - epoch_start_time
                elapsed_min = int(elapsed / 60)
                elapsed_sec = int(elapsed % 60)
                print(f"Epoch {epoch+1} | Step {batch_idx+1} | Avg Loss: {avg:.4f} | Elapsed Time: {elapsed_min:.0f} min, {elapsed_sec} sec")

            global_step += 1
            if global_step % save_every == 0:
                save_checkpoint(model, optimizer, epoch, global_step, folder=checkpoint_folder)

        epoch_loss = total_loss / max(1, (batch_idx+1))
        total_time = time.time() - total_start_time
        total_time_min = int(total_time / 60)
        total_time_sec = int(total_time % 60)
        print(f"Epoch {epoch+1} finished | Avg Loss: {epoch_loss:.4f} | Total Time: {total_time_min:.0f} min, {total_time_sec} sec")

    # 7. Final Save of Model + tokenizer
    os.makedirs("models", exist_ok=True)

    # saves model
    model_path = "models/tinyGPT.pt"
    torch.save(model.state_dict(), model_path)

    # saves vocabulary
    shutil.copy("models/studybuddy_sp.model", "models/studybuddy_sp.model")

    print(f"Saved model -> {model_path}")

if __name__ == "__main__":
    train_model()
