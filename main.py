import tkinter as tk
import pyautogui
import keyboard
import ollama
import threading
import re
import vision
import random


class FlowtAgent:
    def __init__(self):
        self.root = tk.Tk()
        # Initialize Memory First to avoid AttributeError
        self.coord_cache = {}

        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.8)
        self.root.config(bg='grey')
        self.root.attributes("-transparentcolor", "grey")

        # UI Styling
        self.frame = tk.Frame(self.root, bg="#6200ee", padx=15, pady=15, highlightthickness=2,
                              highlightbackground="#bb86fc")
        self.frame.pack()

        self.label = tk.Label(self.frame, text="✨ Flowt HUD: Online", fg="#03dac6", bg="#6200ee",
                              font=("Consolas", 10, "bold"), wraplength=220)
        self.label.pack()

        self.entry = tk.Entry(self.frame, width=28, bg="#3700b3", fg="white", insertbackground="white")
        self.entry.bind("<Return>", self.start_voyage)

        self.mode = "FLOAT"
        self.target_x, self.target_y = 0, 0

        keyboard.add_hotkey('ctrl+shift+h', self.open_input)
        keyboard.add_hotkey('ctrl+shift+s', self.reset_flowt)

        self.animation_loop()
        self.root.mainloop()

    def classify_intent(self, query):
        q = query.lower()
        ribbon_keys = ['file', 'insert', 'references', 'view', 'layout', 'home', 'tab', 'menu', 'design', 'help']
        bottom_keys = ['taskbar', 'start', 'clock', 'battery', 'wifi', 'volume', 'date']

        if any(key in q for key in ribbon_keys):
            return "RIBBON"
        elif any(key in q for key in bottom_keys):
            return "BOTTOM"
        else:
            return "WORKING_AREA"

    def start_voyage(self, event):
        query = self.entry.get()
        if not query: return
        self.label.config(text="🌊 NAVIGATING...", fg="#bb86fc")
        self.entry.pack_forget()
        threading.Thread(target=self.think_and_see, args=(query,), daemon=True).start()

    def think_and_see(self, query):
        query_key = query.lower().strip()

        # Step 5 (Cache Check): Instant return if already found
        if query_key in self.coord_cache:
            self.target_x, self.target_y = self.coord_cache[query_key]
            self.mode = "SAILING"
            self.root.after(0, lambda: self.label.config(text=f"⚡ CACHE HIT: {query_key}", bg="#00c853"))
            return

        # Step 1 & 2: Process text and decide region
        region = self.classify_intent(query)
        self.label.config(text=f"🔍 SCANNING {region}...", fg="#bb86fc")

        try:
            # Step 3: Targeted Screenshot
            img_64, offset_y = vision.capture_targeted_region(region)

            # Step 4: Search with optimized prompt
            prompt = f"Find center of '{query}'. Return only [x, y]."
            response = ollama.chat(model='moondream',
                                   messages=[{'role': 'user', 'content': prompt, 'images': [img_64]}])

            output = response['message']['content']
            match = re.search(r'\[\s*(\d+)\s*,\s*(\d+)\s*\]', output)

            if match:
                raw_x, raw_y = int(match.group(1)), int(match.group(2))
                width, height = pyautogui.size()

                # Determine slice height for correct scaling
                if region == "RIBBON":
                    slice_h = int(height * 0.20)
                elif region == "BOTTOM":
                    slice_h = int(height * 0.10)
                else:
                    slice_h = int(height * 0.70)

                # Step 5: Global Coordinate Remapping
                self.target_x = int((raw_x / 1000) * width)
                self.target_y = offset_y + int((raw_y / 1000) * slice_h)

                # Save to Memory
                self.coord_cache[query_key] = (self.target_x, self.target_y)

                self.mode = "SAILING"
                self.root.after(0, lambda: self.label.config(text="🎯 Landfall!", bg="#00c853"))
                self.root.after(0, lambda: self._show_stars(self.target_x, self.target_y))
        except Exception as e:
            print(f"Error: {e}")
            self.root.after(0, lambda: self.label.config(text="⚠️ ERROR", bg="orange"))

    def animation_loop(self):
        try:
            curr_x, curr_y = self.root.winfo_x(), self.root.winfo_y()
            if self.mode == "FLOAT":
                mx, my = pyautogui.position()
                new_x = curr_x + ((mx + 25) - curr_x) * 0.1
                new_y = curr_y + ((my + 25) - curr_y) * 0.1
                self.root.geometry(f"+{int(new_x)}+{int(new_y)}")
            elif self.mode == "SAILING":
                new_x = curr_x + (self.target_x - curr_x) * 0.05
                new_y = curr_y + (self.target_y - curr_y) * 0.05
                self.root.geometry(f"+{int(new_x)}+{int(new_y)}")
                if abs(new_x - self.target_x) < 5 and abs(new_y - self.target_y) < 5:
                    self.mode = "LANDED"
            self.root.after(10, self.animation_loop)
        except:
            pass

    def open_input(self):
        self.mode = "INPUT"
        self.entry.pack(pady=5)
        self.entry.focus_set()
        self.label.config(text="🛰️ SCANNING...", fg="#03dac6")

    def reset_flowt(self):
        self.mode = "FLOAT"
        self.coord_cache = {}  # Clear memory
        self.entry.pack_forget()
        self.label.config(text="⛵ Flowt: Ready", fg="#03dac6")

    def _show_stars(self, x, y):
        star_window = tk.Toplevel()
        star_window.overrideredirect(True)
        star_window.attributes("-topmost", True, "-transparentcolor", "black")
        star_window.geometry(f"200x200+{x - 100}+{y - 100}")
        canvas = tk.Canvas(star_window, width=200, height=200, bg="black", highlightthickness=0)
        canvas.pack()
        for _ in range(15):
            sx, sy = random.randint(50, 150), random.randint(50, 150)
            canvas.create_text(sx, sy, text="★", fill="gold", font=("Arial", random.randint(10, 20)))
        star_window.after(2000, star_window.destroy)


if __name__ == "__main__":
    app = FlowtAgent()