import pyautogui
import base64
from io import BytesIO
from PIL import ImageEnhance

def capture_screen_base64():
    try: # <--- This was missing!
        # 1. Take the screenshot
        screenshot = pyautogui.screenshot()

        # 2. Boost Contrast (Helps the Big Brain see through Dark Mode)
        enhancer = ImageEnhance.Contrast(screenshot)
        screenshot = enhancer.enhance(2.0)

        # 3. Convert to Base64 for Ollama
        buffered = BytesIO()
        screenshot.save(buffered, format="JPEG", quality=90)
        img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
        return img_str

    except Exception as e:
        print(f"Vision Capture Error: {e}")
        return None