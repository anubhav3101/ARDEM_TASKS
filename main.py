import pytesseract
from PIL import Image
import pandas as pd
import re
import os

# Ensure the path to tesseract executable is correct
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text_from_image(image_path):
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img)
    return text

def extract_summary_details(text):
    data = {
        "Total": None,
        "Date": None,
        "PO #": None,
        "Invoice #": None,
        "Tax ID": "No data found",
        "Tax": None,
        "Subtotal": None,
        "Shipping": None
    }

    # Regular expressions to extract specific fields
    total_amount = re.search(r'Total\s*[:\-]?\s*\$?(\d+[\.,]?\d*)', text, re.IGNORECASE)
    date = re.search(r'Date\s*[:\-]?\s*(\d{1,2}/\d{1,2}/\d{4})', text, re.IGNORECASE)
    po_number = re.search(r'PO #\s*[:\-]?\s*(\S+)', text, re.IGNORECASE)
    invoice_number = re.search(r'Invoice #\s*[:\-]?\s*(\S+)', text, re.IGNORECASE)
    tax = re.search(r'Tax\s*[:\-]?\s*\$?(\d+[\.,]?\d*)', text, re.IGNORECASE)
    subtotal = re.search(r'Subtotal\s*[:\-]?\s*\$?(\d+[\.,]?\d*)', text, re.IGNORECASE)
    shipping = re.search(r'Shipping\s*[:\-]?\s*\$?(\d+[\.,]?\d*)', text, re.IGNORECASE)

    # Fill in the extracted data
    if total_amount:
        data["Total"] = total_amount.group(1)
    if date:
        data["Date"] = date.group(1)
    if po_number:
        data["PO #"] = po_number.group(1)
    if invoice_number:
        data["Invoice #"] = invoice_number.group(1)
    if tax:
        data["Tax"] = tax.group(1)
    if subtotal:
        data["Subtotal"] = subtotal.group(1)
    if shipping:
        data["Shipping"] = shipping.group(1)

    return data

def extract_line_items(text):
    # Regular expressions to extract line item details
    lines = text.split('\n')
    line_items = []
    for line in lines:
        description_match = re.search(r'Description\s*[:\-]?\s*(.*)', line, re.IGNORECASE)
        unit_price_match = re.search(r'Unit Price\s*[:\-]?\s*\$?(\d+[\.,]?\d*)', line, re.IGNORECASE)
        quantity_match = re.search(r'Quantity\s*[:\-]?\s*(\d+)', line, re.IGNORECASE)
        amount_match = re.search(r'Total\s*[:\-]?\s*\$?(\d+[\.,]?\d*)', line, re.IGNORECASE)
        discount_match = re.search(r'Discount\s*[:\-]?\s*\$?(\d+[\.,]?\d*)', line, re.IGNORECASE)

        if description_match and unit_price_match and quantity_match and amount_match:
            line_items.append({
                "Description": description_match.group(1),
                "Unit Price": unit_price_match.group(1),
                "Quantity": quantity_match.group(1),
                "Total": amount_match.group(1),
                "Discount": discount_match.group(1) if discount_match else None
            })

    return line_items

def get_confidence_level():
    # Placeholder for confidence level (for simplicity, fixed confidence is used)
    return "95.00%"

# Directory containing images
image_directory = r"C:\Users\shukl\Downloads\anubhav work lko"
summary_output_directory = "summary_csv"
line_items_output_directory = "line_items_csv"

os.makedirs(summary_output_directory, exist_ok=True)
os.makedirs(line_items_output_directory, exist_ok=True)

for image_file in os.listdir(image_directory):
    if image_file.endswith(('.png', '.jpg', '.jpeg', '.tiff')):
        image_path = os.path.join(image_directory, image_file)
        text = extract_text_from_image(image_path)
        
        # Extract summary details
        summary_data = extract_summary_details(text)
        summary_extracted_data = []
        for field, value in summary_data.items():
            summary_extracted_data.append({
                "Field": field,
                "Data": value,
                "Confidence": get_confidence_level()
            })

        # Convert to DataFrame and save to CSV
        summary_df = pd.DataFrame(summary_extracted_data)
        summary_csv_path = os.path.join(summary_output_directory, f"{os.path.splitext(image_file)[0]}_summary.csv")
        summary_df.to_csv(summary_csv_path, index=False)

        # Extract line items
        line_items_data = extract_line_items(text)
        line_items_df = pd.DataFrame(line_items_data)
        line_items_csv_path = os.path.join(line_items_output_directory, f"{os.path.splitext(image_file)[0]}_line_items.csv")
        line_items_df.to_csv(line_items_csv_path, index=False)

print("Data extracted and saved to CSV files")
