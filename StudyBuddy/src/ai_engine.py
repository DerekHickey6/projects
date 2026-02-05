# ===================================================================================== #
#     Ai Engine - contians:                                                             #
#                Tokenizer -- Model Neural Network -- Chatbot Class                     #
#                                                                                       #
# ===================================================================================== #

import torch
from torch import nn
import torch.nn.functional as F     # functional versions of operations like: activations, loss functions, etc.
import re       # regular expression module - for splitting text into tokens like words
import sentencepiece as spm

# ================================== #
#       SentencePiece Tokenizer      #
# ================================== #
class SentencePieceTokenizer:
    def __init__(self, model_path="models/studybuddy_sp.model"):
        self.sp = spm.SentencePieceProcessor()
        self.sp.load(model_path)

    def encode(self, text, max_len=None):
        ids = self.sp.encode(text, out_type=int)

        if max_len:
            # Pad
            if len(ids) < max_len:
                ids = ids + [0] * (max_len - len(ids))
            else: # Truncate
                ids = ids[:max_len]

        return ids

    def decode(self, ids):
        # remove padding tokens
        ids = [i for i in ids if i != 0]
        return self.sp.decode(ids)

    @property
    def vocab_size(self):
        return self.sp.get_piece_size()


# ========================= #
#       Char Tokenizer      #
# ========================= #
class CharTokenizer:
    def __init__(self):
        self.char2idx = {"<PAD>": 0, "<UNK>": 1}    # Maps characters -> index
        self.idx2char = {0: "<PAD>", 1: "<UNK>"}    # Maps index -> characters

    def build_vocab(self, text):

        unique_chars = sorted(set(text))    # returns a list of unique characters

        for ch in unique_chars:
            if ch not in self.char2idx:     # checks if character is in character vocab
                idx = len(self.char2idx)    # if not, creates idx pointing to next spot in character vocab
                self.char2idx[ch] = idx     # updates char vocab dict using char as key
                self.idx2char[idx] = ch     # updates idx vocab dict using idx to add char to dicst

    # Converts raw text -> list of character indices
    def encode(self, text, max_len=200):

        # converts char in text to index, else sets it as UNK
        ids = [self.char2idx.get(ch, 1) for ch in text]

        # pad or truncate
        if len(ids) < max_len:
            ids = ids + [0] * (max_len - len(ids))  # if ids is short, pads with <PAD> * number of unused spaces in list
        else:
            ids = ids[:max_len]                     # if ids is long, truncates to ids [from beginning to the max len]

        return ids

    # Converts indices -> text string
    def decode(self, ids):
        chars = []
        for idx in ids:
            ch = self.idx2char.get(idx, "<UNK>")    # assign character of index [idx], else returns "<UNK>"
            if ch != "<PAD>":                       # if the character is not "<PAD>"
                chars.append(ch)                    # then add the character to chars list
        return "".join(chars)

# ========================= #
#       Word Tokenizer      #
# ========================= #
class SimpleTokenizer:
    def __init__(self):

        self.word2idx = {"<PAD>":0, "<UNK>":1}  # word to id mapping, <PAD> for sequencing to same length for batches
        self.idx2word = {0:"<PAD>", 1:"<UNK>"}  # id to work mapping, <UNK> for words that are unknown

    # counts how often each word appears
    # adds word that apear at least 'min_freq' times
    def build_vocab(self, text_list, min_freq=1):
        freq={}                                 # stored as key = word, value = count
        for text in text_list:
            # extracts "word-like" elements (no punctuation) and returns a list to iterate through
            for w in re.findall(r"\w+", text):
                # Counts how often a word gets repeated
                freq[w] = freq.get(w, 0) + 1

        # Create vocab IDs
        for word, count in freq.items():    # loop through word, count pair in freq dict
            if count >= min_freq:           # filter by frequency
                idx = len(self.word2idx)    # finds next available index
                self.word2idx[word] = idx   # add to word-to-index mapping
                self.idx2word[idx] = word   # add to index-to-word mapping

    # === Bridge between text + neural networks ===
    # returns a fixed-length list of integers
    def encode(self, text, max_len=100):
        # Tokenizes String to only word-chars (no - punctuation)
        tokens = re.findall(r"\w+", text.lower())
        # Converts words to id's
        ids = [self.word2idx.get(t, 1) for t in tokens]
        # Sequence padding = Truncates id's + pads with zeros if too shorts
        return ids[:max_len] + [0] * (max_len - len(ids))

    # Takes list of IDs, looks up corrisponding words and returns spaced out sentence
    def decode(self, ids):
        # returns a string of words (separated by a space)
        return " ".join(self.idx2word.get(i, "<UNK>") for i in ids)

# ================================ #
#       GPT Model Neural Net       #
# ================================ #
class TinyGPT(nn.Module):
    def __init__(self, vocab_size,
                 embed_dim=128,
                 n_heads=4,
                 hidden_dim=256,
                 max_seq_len=200):
        super().__init__()

        # Token + positional embeddings
        self.token_emb = nn.Embedding(vocab_size, embed_dim)    # Turns IDs into vectors
        self.pos_emb = nn.Embedding(max_seq_len, embed_dim)     # Turns word positions into vectors

        # One or more transformer blocks, with causal mask at forward
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=embed_dim,
            nhead=n_heads,
            dim_feedforward=hidden_dim,
            batch_first=True  # Keeps format (batch, seq, dim)
        )
        self.transformer = nn.TransformerEncoder(
            encoder_layer,
            num_layers=2      # can change later
        )

        # Final linear head -> logits over vocabulary
        # maps position's hidden vector to a distribution over vocab
        self.fc = nn.Linear(embed_dim, vocab_size)

        # Store max length for safety, safeguard to not exceed positional embeddings
        self.max_seq_len = max_seq_len

    def _causal_mask(self, seq_len, device):
        # Builds an upper-triangular mask to each position only cares about current/past tokens (not future)
        mask = torch.triu(torch.ones(seq_len, seq_len, device=device) * float("-inf"), diagonal=1)
        return mask

    def forward(self, x):
        """
        x: (batch, seq_len) of token IDs
        returns: logits (batch, seq_len, vocab_size)
        """

        batch_size, seq_len = x.shape

        # Clamp seq _len to max_seq_len to avoid indexing pos_emb out of range
        if seq_len > self.max_seq_len:
            x = x[:, -self.max_seq_len:]
            seq_len = self.max_seq_len

        # Token + Positional embeddings
        tok = self.token_emb(x)     # (batch, seq, emb_dim)

        positions = torch.arange(seq_len, device=x.device).unsqueeze(0)     # (1, seq)
        pos = self.pos_emb(positions)                                       # (1, seq, emb_dim)

        h = tok + pos

        # Causal mask so token i can only see token <= i
        mask = self._causal_mask(seq_len=seq_len, device=x.device)      # (seq, seq)

        h = self.transformer(h, mask=mask)  # (batch, seq, vocab_size)

        logits = self.fc(h)
        return logits

# ========================= #
#       ChatBot Class       #
# ========================= #
class LocalChatBot:
    def __init__(self):
        # Initializes char2idx & idx2char dictionarys, encode()/decode() functions
        self.tokenizer = SentencePieceTokenizer("models/studybuddy_sp.model")

        self.memory = []

        self.model = None

    # === Generates Response === #
    def generate(self, prompt, max_len=200, k=8, temperature=0.7):

        # Build full prompt
        history = " ".join(self.memory)                         # Create sentence of memory contents
        full_prompt = f"{history} User: {prompt} Bot:"          # Given to model to respond to

        # Converts input text to list of ints and wraps in a batch dimension
        encoded = torch.tensor([self.tokenizer.encode(full_prompt)], dtype=torch.long)   # outputs shape (1, seq_len)

        unk_id = self.tokenizer.sp.unk_id()
        pad_id = 0

        # at each step, predicts a new word and appends it
        for _ in range(max_len):
            # clamp sequence length
            if encoded.shape[1] > self.model.max_seq_len:
                encoded = encoded[:, -self.model.max_seq_len:]

            # Forward pass
            logits = self.model(encoded)

            # Extract last token's first
            last_logits = logits[0, -1].detach().clone()

            # Stops PAD/UNK token
            last_logits[pad_id] = -1e10
            last_logits[unk_id] = -1e10

            # repetition penalty
            last_token = encoded[0].tolist()[-20:]
            for prev_id in last_token:
                last_logits[prev_id] *= 0.7 # lower probability of repeating outputs

            # Temperature scaling for softer probability distribution
            scaled_logits = last_logits / temperature

            # Convert to probabilities for REAL probability distribution
            probs = F.softmax(scaled_logits, dim=0)

            # Top K filtering to restrict samples to best 'k' tokens
            topk_probs, topk_idx = torch.topk(probs, k)

            # Normalize top K probabilities
            topk_probs /= torch.sum(topk_probs)

            # Sample from top-k distribution, chooses a random token, weighted by probability
            next_id = torch.multinomial(topk_probs, 1).item()

            # Map back to original vocab index
            next_id = topk_idx[next_id].item()

            # STOP condition, if PAD/UNK
            if next_id in (pad_id, unk_id):
                continue

            # Appends next token + sequence grows by word each iteration
            encoded = torch.cat([encoded, torch.tensor([[next_id]])], dim=1)


        # Converts tensor -> Python list
        # Turns multiple token IDs -> human readable sentence
        ids = encoded[0].tolist()
        full_text = self.tokenizer.decode(ids)

        if "Bot:" in full_text:
            reply = full_text.split("Bot:")[-1].strip()
        else:
            reply = full_text

        # Save User message + Bot reply to memory,
        self.memory.append(f"User: {prompt}")
        self.memory.append(f"Bot: {reply}")
        self.memory = self.memory[-8:]   # saves only 10 most recent messages

        return reply

    # === Loads Model into ChatBot === #
    def load_model(self, model_path="models/tinyGPT_checkpoint.pt", sp_model="models/studybuddy_sp.model"):
        self.tokenizer = SentencePieceTokenizer(sp_model)

        vocab_size = self.tokenizer.vocab_size

        # recreate model with correct vocab size
        self.model = TinyGPT(vocab_size=vocab_size,
                             embed_dim=128,
                             n_heads=4,
                             hidden_dim=256,
                             max_seq_len=192)

        ckpt = torch.load(model_path, map_location="cpu")

        # Case 1: It's loading a checkpoint (contains 'model' key)
        if isinstance(ckpt, dict) and "model" in ckpt:
            print("Detected checkpoint file — loading state_dict from 'model' key.")
            self.model.load_state_dict(ckpt["model"])

        # Case 2: Loading final model .pt (pure state_dict)
        else:
            print("Detected raw model state_dict — loading directly.")
            self.model.load_state_dict(ckpt)

        self.model.eval()

        print("Model Successfully loaded and ready")

