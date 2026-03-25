import tkinter as tk
import cv2
import numpy as np
import pyautogui


class TutorialPointer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.config(bg='grey')
        self.root.attributes("-transparentcolor", "grey")

        # The "Game Arrow"
        self.label = tk.Label(self.root, text="👇 CLICK HERE",
                              fg="white", bg="#ff1744",
                              font=("Arial", 12, "bold"), padx=10, pady=5)
        self.label.pack()

        # Step 1: Look for the Insert button
        self.current_step = 1
        self.target_image = 'target_button.png'

        self.run_scanner()
        self.root.mainloop()

    def run_scanner(self):
        try:
            # 1. Take a screenshot of your screen
            screen = pyautogui.screenshot()
            screen_np = cv2.cvtColor(np.array(screen), cv2.COLOR_RGB2GRAY)

            # 2. Load the button image you saved
            template = cv2.imread(self.target_image, 0)

            if template is not None:
                # 3. Use OpenCV to find the pixels that match the button
                res = cv2.matchTemplate(screen_np, template, cv2.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

                # 4. If the match is strong (>80%), snap the pointer to it
                if max_val > 0.8:
                    w, h = template.shape[::-1]
                    center_x, center_y = max_loc[0] + w // 2, max_loc[1] + h // 2
                    self.root.geometry(f"+{center_x}+{center_y}")
                    self.label.config(text="🎯 CLICK INSERT", bg="#00c853")
                else:
                    # Otherwise, follow the mouse while searching
                    mx, my = pyautogui.position()
                    self.root.geometry(f"+{mx + 25}+{my + 25}")
                    self.label.config(text="🔍 Searching for 'Insert'...", bg="#ff1744")

        except Exception as e:
            print(f"Error: {e}")

        # Repeat every 200ms for smooth tracking
        self.root.after(200, self.run_scanner)


if __name__ == "__main__":
    app = TutorialPointer()