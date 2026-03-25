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
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        # 0.8 is 80% visible, 20% see-through
        self.root.attributes("-alpha", 0.8)
        self.root.config(bg='grey')
        self.root.attributes("-transparentcolor", "grey")

        # UI Styling - Cyberpunk Purple
        self.frame = tk.Frame(self.root, bg="#6200ee", padx=15, pady=15, highlightthickness=2,
                              highlightbackground="#bb86fc")
        self.frame.pack()

        self.label = tk.Label(self.frame, text="✨ Flowt HUD: Online", fg="#03dac6",
                              bg="#6200ee", font=("Consolas", 10, "bold"), wraplength=220)
        self.label.pack()

        self.entry = tk.Entry(self.frame, width=28, bg="#3700b3", fg="white", insertbackground="white")
        self.entry.bind("<Return>", self.start_voyage)

        self.mode = "FLOAT"
        self.target_x, self.target_y = 0, 0

        # Hotkeys
        keyboard.add_hotkey('ctrl+shift+h', self.open_input)
        keyboard.add_hotkey('ctrl+shift+s', self.reset_flowt)

        self.animation_loop()
        self.root.mainloop()

    def _show_stars(self, x, y):
        """Creates a temporary star burst at the target location."""
        star_window = tk.Toplevel()
        star_window.overrideredirect(True)
        star_window.attributes("-topmost", True)
        star_window.attributes("-transparentcolor", "black")
        star_window.config(bg="black")
        # Center the star burst area
        star_window.geometry(f"200x200+{x - 100}+{y - 100}")

        canvas = tk.Canvas(star_window, width=200, height=200, bg="black", highlightthickness=0)
        canvas.pack()

        # Generate 15 random stars
        for _ in range(15):
            sx, sy = random.randint(50, 150), random.randint(50, 150)
            canvas.create_text(sx, sy, text="★", fill="gold", font=("Arial", random.randint(10, 20)))

        # Self-destruct after 2 seconds
        star_window.after(2000, star_window.destroy)

    def open_input(self):
        self.root.after(0, self._ui_show_input)

    def _ui_show_input(self):
        self.mode = "INPUT"
        self.entry.pack(pady=5)
        self.entry.focus_set()
        self.label.config(text="🛰️ SCANNING FOR TARGET...", fg="#03dac6")

    def reset_flowt(self):
        self.root.after(0, self._ui_reset)

    def _ui_reset(self):
        self.mode = "FLOAT"
        self.entry.pack_forget()
        self.entry.delete(0, tk.END)
        self.label.config(text="⛵ Flowt: Ready", fg="#03dac6")

    def start_voyage(self, event):
        query = self.entry.get()
        if not query: return
        self.label.config(text="🌊 NAVIGATING...", fg="#bb86fc")
        self.entry.pack_forget()
        threading.Thread(target=self.think_and_see, args=(query,), daemon=True).start()

    def think_and_see(self, query):
        img_64 = vision.capture_screen_base64()

        # Moondream likes "Point-and-detect" style prompts
        prompt = f"Find the center coordinates of the '{query}' in this image. Return only [x, y]."

        try:
            response = ollama.chat(
                model='moondream',  # Use the lightweight model
                messages=[{'role': 'user', 'content': prompt, 'images': [img_64]}]
            )

            output = response['message']['content']
            print(f"Moondream Result: {output}")

            # The same flexible Regex we built earlier will work here
            match = re.search(r'\[\s*(\d+)\s*,\s*(\d+)\s*\]', output)

            if match:
                # IMPORTANT: Moondream often returns coordinates in percentages (0-1000)
                # If the numbers are small (like 150, 45), it's likely percentage-based.
                raw_x, raw_y = int(match.group(1)), int(match.group(2))

                # Logic to check if we need to scale the coordinates
                width, height = pyautogui.size()
                if raw_x <= 1000 and raw_y <= 1000:
                    self.target_x = int((raw_x / 1000) * width)
                    self.target_y = int((raw_y / 1000) * height)
                else:
                    self.target_x, self.target_y = raw_x, raw_y

                self.mode = "SAILING"
                self.root.after(0, lambda: self.label.config(text="🎯 Landfall!", bg="#00c853"))
                self.root.after(0, lambda: self._show_stars(self.target_x, self.target_y))
        except Exception as e:
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


if __name__ == "__main__":
    app = FlowtAgent()