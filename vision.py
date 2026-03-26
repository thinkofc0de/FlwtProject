import pyautogui
import base64
import io
from PIL import ImageEnhance


def capture_targeted_region(region_type):
    try:
        width, height = pyautogui.size()

        # 1. Define the Sector
        if region_type == "RIBBON":
            y_start, y_end = 0, int(height * 0.20)
        elif region_type == "BOTTOM":
            y_start, y_end = int(height * 0.90), height
        else:
            y_start, y_end = int(height * 0.20), int(height * 0.90)

        # 2. Capture and IMMEDIATELY Resize
        screenshot = pyautogui.screenshot(region=(0, y_start, width, y_end - y_start))

        # WE OPTIMIZE HERE:
        # Resize to a max width of 720px while keeping aspect ratio.
        # This makes the Base64 string much shorter!
        screenshot.thumbnail((720, 720))

        # 3. Enhance Contrast but keep it simple
        enhancer = ImageEnhance.Contrast(screenshot)
        screenshot = enhancer.enhance(1.5)

        # 4. Save with Low Quality / High Compression
        buffered = io.BytesIO()
        screenshot.save(buffered, format="JPEG", quality=40, optimize=True)
        img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')

        return img_str, y_start

    except Exception as e:
        print(f"Vision Speed Error: {e}")
        return None, 0
