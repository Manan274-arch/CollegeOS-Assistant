from pathlib import Path
from PIL import Image
import pytesseract


TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


def extract_text_from_image(image_path):
    image_path = Path(image_path)

    if not image_path.exists():
        return f"Error: Image file not found at {image_path}"

    try:
        image = Image.open(image_path)

        extracted_text = pytesseract.image_to_string(image)

        extracted_text = extracted_text.strip()

        if extracted_text == "":
            return "No text could be extracted from the image."

        return extracted_text

    except Exception as error:
        return f"Error while extracting text from image: {error}"


if __name__ == "__main__":
    test_image_path = "data/uploads/sample_timetable.jpeg"

    result = extract_text_from_image(test_image_path)

    print("\n--- OCR RESULT ---")
    print(result)