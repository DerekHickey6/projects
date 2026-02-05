class TinyTransformer(nn.Module):
    def __init__(self, vocab_size, # Vocab size for input word ids range and output prediction must be size of vocab_size
                 embed_dim=32, 
                 n_heads=2, 
                 hidden_dim=64): 
        super().__init__()
        
        # initializes a lookup table that maps each word ID to a vector
        # each word has a 64-dimensional vector assigned to it, helps the model learn similar words
        self.embed = nn.Embedding(vocab_size, embed_dim)  ## Word embeddings
        
        # initializes positional embeddings: 1 vector per position in sequence
        self.pos_embed = nn.Embedding(200, embed_dim)
        
        # layer containing: 
        # self-attention - compares 1 word in sentence to every other word, learn word relationships
        # Multi-head attention (n_heads=2) - head 1 learns grammar, head 2 learns semantics 
        # feedforward network (hidden_dim=128) - mixes representations and extracts new feeatures
        self.transformer = nn.TransformerEncoder(
            nn.TransformerEncoderLayer(d_model=embed_dim, nhead=n_heads, dim_feedforward=hidden_dim, batch_first=True),
            num_layers=2  # layer 1 - learns word relationship, layer 2 - refines them
        )
        # maps each vector from the transformer into a prediction over the vocabulary
        self.fc = nn.Linear(embed_dim, vocab_size)
        
    def forward(self, x):
        # Transforms tensor x into (batch_size, seq_len, embed_size)
        emb = self.embed(x)
        
        # Create a tensor of positions for each token in sequence
        batch_size, seq_len = x.shape
        positions = torch.arange(seq_len, device=x.device).unsqueeze(0).expand(batch_size, seq_len)
        
        # look up positional embeddings for each position
        pos_embeddings = self.pos_embed(positions)
        
        # Add token embeddings + positional embeddings for final embedding
        # FINAL embedding includes the information about 'which word' + 'where does it go'
        emb = emb + pos_embeddings
        
        # compares each token to all other tokens, learns context & sentence structure - output = (1, seq_len, embed_dim)
        out = self.transformer(emb)
        # Predicts and returns next word
        logits = self.fc(out)
        return logits
    