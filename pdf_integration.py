import subprocess
import sys

# Function to install modules
def install_module(module):
    try:
        __import__(module)
    except ImportError:
        print(f"Installing missing module: {module}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", module])

# List of required modules
required_modules = ["PyPDF2", "reportlab", "pillow", "pytesseract"]

# Install all required modules
for module in required_modules:
    install_module(module)

# Import the now-installed modules
import PyPDF2
from PyPDF2 import PdfWriter, PdfReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PIL import Image
import pytesseract
import os

# Configure Tesseract OCR (ensure Tesseract is installed on your system)
pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'  # Adjust this path based on your Tesseract installation

def create_pdf_with_data(input_data, output_pdf):
    """
    Create a PDF with user-entered data using ReportLab.
    """
    temp_pdf = "temp_data.pdf"
    c = canvas.Canvas(temp_pdf, pagesize=letter)
    c.drawString(100, 750, "Integrated Data:")
    
    y = 730  # Starting position for the text
    for key, value in input_data.items():
        c.drawString(100, y, f"{key}: {value}")
        y -= 20  # Move to the next line

    c.save()

    return temp_pdf

def merge_pdfs(template_pdf, data_pdf, output_pdf):
    """
    Merge the data PDF with a template PDF.
    """
    reader = PdfReader(template_pdf)
    writer = PdfWriter()

    # Append original template pages
    for page in reader.pages:
        writer.add_page(page)

    # Add the data page to the end
    data_reader = PdfReader(data_pdf)
    writer.pages.extend(data_reader.pages)

    # Write the output file
    with open(output_pdf, "wb") as f:
        writer.write(f)

def extract_text_with_ocr(pdf_file, output_folder):
    """
    Extract text from PDF using OCR and save extracted text to a file.
    """
    extracted_texts = []
    reader = PdfReader(pdf_file)

    for i, page in enumerate(reader.pages):
        # Extract image from each page
        page_content = page.get("/Contents")
        if page_content:
            page_image_path = os.path.join(output_folder, f"page_{i + 1}.jpg")
            page.extract_to_file(page_image_path)  # Save the page as an image

            # Perform OCR
            img = Image.open(page_image_path)
            text = pytesseract.image_to_string(img)
            extracted_texts.append(text)

            # Remove the temporary image file
            os.remove(page_image_path)

    return extracted_texts

def main():
    print("Welcome to the PDF Data Integration and OCR Script.")
    
    # Gather user-entered data
    print("Enter data to integrate into the PDF. Type 'done' when finished.")
    input_data = {}
    while True:
        key = input("Enter field name (e.g., Name, Date): ")
        if key.lower() == 'done':
            break
        value = input(f"Enter value for '{key}': ")
        input_data[key] = value

    # Specify template and output file paths
    template_pdf = "template.pdf"  # Replace with your template PDF path
    output_pdf = "output_with_data.pdf"

    # Create a PDF with integrated data
    print("Creating a PDF with your data...")
    data_pdf = create_pdf_with_data(input_data, output_pdf)

    # Merge the new data into the template PDF
    print("Merging the data PDF with the template PDF...")
    merge_pdfs(template_pdf, data_pdf, output_pdf)
    print(f"PDF with integrated data saved as '{output_pdf}'.")

    # Extract text from the final PDF using OCR
    output_folder = "ocr_output"
    os.makedirs(output_folder, exist_ok=True)
    print("Performing OCR on the output PDF...")
    extracted_texts = extract_text_with_ocr(output_pdf, output_folder)

    print("OCR Text Extraction Complete:")
    for page_num, text in enumerate(extracted_texts, start=1):
        print(f"Page {page_num} Text:")
        print(text)

    print("Process completed successfully.")

if __name__ == "__main__":
    main()
