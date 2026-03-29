import pyautogui
import base64
import io
from PIL import Image, ImageEnhance


def capture_targeted_region(region_type):
    try:
        width, height = pyautogui.size()

        # 1. Define Boundaries
        if region_type == "RIBBON":
            y_start, h = 0, int(height * 0.20)
        elif region_type == "BOTTOM":
            y_start, h = int(height * 0.90), int(height * 0.10)
        else:
            y_start, h = int(height * 0.20), int(height * 0.70)

        # 2. Capture Screenshot
        screenshot = pyautogui.screenshot(region=(0, y_start, width, h))

        # 3. AGGRESSIVE RESIZE (Speed fix for local LLM)
        # Forces the width to 448px to match Moondream's native eye
        new_size = (448, int(448 * (h / width)))
        screenshot = screenshot.resize(new_size, Image.Resampling.LANCZOS)

        # Convert to Grayscale (reduces data load by 66%)
        screenshot = screenshot.convert('L')

        # Enhance Contrast
        enhancer = ImageEnhance.Contrast(screenshot)
        screenshot = enhancer.enhance(1.5)

        # 4. Save to Base64 (Low Quality = High Speed)
        buffered = io.BytesIO()
        screenshot.save(buffered, format="JPEG", quality=40, optimize=True)
        img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')

        return img_str, y_start

    except Exception as e:
        print(f"Vision Speed Error: {e}")
        return None, 0
