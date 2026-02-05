import tkinter as tk
from pomodoro import Pomodoro
from ocr import grab_text, extract_keywords
from voice_mode import listen_to_voice, speak_text
import threading
from ai_engine import LocalChatBot

class App(tk.Tk):
    # Initializes the GUI with Tkinter
    def __init__(self):
        super().__init__()
        
        self.last_checked_keywords = []
        self.last_user_input = ""
        self.title("StudyBuddy - Hello")
        self.geometry("850x400")
        # Creates text object and pads vertically by 20 pixels
        tk.Label(self, text="StudyBuddy 1.2", font=("Segoe UI", 16)).pack(pady=20)
        
        # === Chatbot ===
        self.bot = LocalChatBot()
        self.bot.load_model("models/tinyGPT_checkpoint.pt", "models/studybuddy_sp.model")
        
        # ==== Layout ==== 
        main_frame = tk.Frame(self)
        main_frame.pack(fill="both", expand=True)
        
        # ==== pomodoro ====
        left_frame = tk.Frame(main_frame, padx=10, pady = 10)
        left_frame.pack(side="left", fill="both", expand=True)
        tk.Label(left_frame, text="Pomodoro")
        
        self.pomodoro = Pomodoro()
        self.running = False
        
        
        # Create labels
        self.phase_label = tk.Label(left_frame, text="Time to Focus", font=("Segoe UI", 14))
        self.phase_label.pack()
        
        self.timer_label = tk.Label(left_frame, text="30:00", font=("Segoe UI", 14))
        self.timer_label.pack(pady=10)
        
        self.session_count_label = tk.Label(left_frame, text=f"Pomodoro Count: {self.pomodoro.session_count}", font=("Segoe UI", 12))
        self.session_count_label.pack()
        
        # Create box for buttons and centers it
        btn_frame = tk.Frame(left_frame)
        btn_frame.pack(pady=20)
        
        # Create start/pause/reset buttons
        self.start_btn = tk.Button(btn_frame, text="Start", command=self.start_timer, width=8)
        self.start_btn.grid(row=0, column=0, padx=5)
        
        self.pause_btn = tk.Button(btn_frame, text="Pause", command=self.pause_timer, width=8)
        self.pause_btn.grid(row=0, column=1, padx=5)
        
        self.reset_btn = tk.Button(btn_frame, text="Reset", command=self.reset_timer, width=8)
        self.reset_btn.grid(row=0, column=2, padx=5)
        
        
        # ==== Chat Section ====
        right_frame = tk.Frame(main_frame, padx=10, pady=10)
        right_frame.pack(side="right", fill="both", expand=True)
        
        tk.Label(right_frame,  text="Chatbot", font=("Segoe UI", 16))
        
        # Contains the chat window and entry frame
        self.chat_display = tk.Text(right_frame, wrap="word", height=15, width=50, state="disabled", bg="#F6F6F6")
        self.chat_display.pack(pady=5, fill="both", expand=True)
        
        # Contains the components to type/send message, scan and voice options
        entry_frame = tk.Frame(right_frame)
        entry_frame.pack(fill="x")
        
        # Typing box
        self.chat_entry = tk.Entry(entry_frame, font=("Segoe UI", 16))
        self.chat_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.chat_entry.bind("<Return>", self.send_message)
        
        # Entry buttons (voice, scan, send)
        voice_btn = tk.Button(entry_frame, text="Voice", command=self.start_voice_thread)
        voice_btn.pack(side="right", padx=(5, 0))
        
        scan_btn = tk.Button(entry_frame, text="Scan", command=self.scan_screen)
        scan_btn.pack(side="right", padx=(5, 0), pady=8)
        
        send_btn = tk.Button(entry_frame, text="Send", command=self.send_message)
        send_btn.pack(side="right")
    
    # launches the voice interaction in a separate background thread
    # .voice_interaction() -> records voice, speech-to-text, showing text in chat
    # daemon=True -> makes thread stop automatically
    # .start() -> runs the new thread
    def start_voice_thread(self):
        threading.Thread(target=self.voice_interaction, daemon=True).start()

    # Listens to voice, speech-to-text and returns message that was recorded to display box
    def voice_interaction(self):
        """Record voice, display recognized text, and respond."""
        self.display_message("StudyBuddy", "Listening... Speak now!")
        self.update_idletasks()

        text = listen_to_voice(duration=8)  # Calls Vosk recognizer

        # handles if voice wasnt heard/recorded properly
        if not text:
            self.display_message("StudyBuddy", "I didn’t catch that — try again?")
            speak_text("I didn't catch that. Try again?")
            return

        # Display user's speech as chat
        self.display_message("You", text)

    # ==== Timer Control methods ====
    # Starts timer if pomodoro isn't already running
    def start_timer(self):
        if not self.running:
            self.running = True
            self.update_timer()
    
    # Pauses timer
    def pause_timer(self):
        self.running = False
    
    # Resets timer
    def reset_timer(self):
        self.running = False
        self.pomodoro = Pomodoro()
        self.update_display()
    
    # ==== Display and timer Loops ====
    # counts down timer and updates display every second
    def update_timer(self):
        if self.running:
            self.pomodoro.tick()
            self.update_display()
            self.after(1000, self.update_timer)
    
    # Updates display based on pomodoro phase
    def update_display(self):
        """Updates timer every second"""
        # Convert remaining seconding to minutes
        minutes, seconds = divmod(self.pomodoro.state.remaining_sec, 60)
        self.timer_label.config(text=f"{minutes:02d}:{seconds:02d}")
        
        phase_texts = {
            "focus": "Time to Focus!",
            "short_break": "Take a Short Break",
            "long_break": "Good job! you've earned a long break"
        }
        
        # updates phase tests and pomodoro count
        phase_display = phase_texts.get(self.pomodoro.state.phase, "Time to Focus!")
        self.phase_label.config(text=phase_display)
        
        self.session_count_label.config(text=f"Pomodoro Count: {self.pomodoro.session_count}")
        
    # ======================== #
    #       Chatbot Logic      # 
    # ======================== #
    
    # Sends message to chat box
    def send_message(self, event=None):
        # Gets text from chat box and converts to list
        last_user_input = self.chat_entry.get().strip()
        if not last_user_input:
            return None
        self.display_message("You", last_user_input)
        # Clears the text entry box
        self.chat_entry.delete(0, tk.END)
        
        # Generates and displays an AI response
        ai_reply = self.bot.generate(last_user_input)
        self.display_message("StudyBuddy", ai_reply)
    
    # Displays message to chat box
    def display_message(self, sender, message):
        self.chat_display.config(state="normal")
        self.chat_display.insert(tk.END, f"{sender}: {message}\n\n")
        self.chat_display.see(tk.END)
        self.chat_display.config(state="disabled")
        
    # Scans multiple monitors and returns s tring containing the most common words
    def scan_screen(self):
        self.display_message("StudyBuddy", "Please wait while I scan your monitor(s)")
        self.update_idletasks()
        
        text = grab_text()
        self.last_checked_keywords = extract_keywords(text)
        
        self.display_message("StudyBuddy", f"I found these study topics: \n{', '.join(self.last_checked_keywords)}")

if __name__ == "__main__":
    
    App().mainloop()
    
