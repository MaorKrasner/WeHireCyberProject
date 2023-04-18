from io import StringIO

import PyPDF4
import pdfquery
import pdfplumber
from fpdf import FPDF
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.pdfpage import PDFPage

import io
import os
from pathlib import Path
from reportlab.pdfgen import canvas
from PyPDF4 import PdfFileWriter, PdfFileReader


# function that converts text file to pdf file
def convert_from_text_to_pdf(text_file_path, pdf_file_path):
    # Read the content of the text file as a list of lines
    with open(text_file_path, 'r', errors='ignore') as f:
        text = f.readlines()

    pdf = FPDF()  # Create a PDF object
    pdf.add_page()  # Add a page
    pdf.set_font('Arial', size=12)  # Set the font and font size

    # write each line of the text to the pdf file
    for i in range(len(text)):
        pdf.cell(200, 10, txt=text[i], ln=1)

    # Save the PDF file
    pdf.output(pdf_file_path)


def convert_from_text_to_pdf_pypdf4(text_file_path, pdf_file_path):
    with open(text_file_path, 'r') as f:
        text = f.read()

    pdf_writer = PdfFileWriter()
    pdf_canvas = canvas.Canvas(io.BytesIO())
    pdf_canvas.drawString(72, 720, text)
    pdf_canvas.save()
    pdf_page = PdfFileReader(io.BytesIO(pdf_canvas.getpdfdata())).getPage(0)

    pdf_writer.addPage(pdf_page)

    with open(pdf_file_path, 'wb') as out_file:
        pdf_writer.write(out_file)

def extract_text_from_pdf(pdf_path):
    """
    Extracts text from a PDF file using PyPDF4.

    Args:
        pdf_path (str): The path to the PDF file.

    Returns:
        str: The extracted text.
    """
    try:
        with open(pdf_path, 'rb') as f:
            pdf_reader = PyPDF4.PdfFileReader(f)
            text = ""

            # Iterate over each page of the PDF
            for i in range(pdf_reader.getNumPages()):
                page = pdf_reader.getPage(i)
                text += page.extractText()

            return text
    except Exception as e:
        print(f"Error extracting text from PDF file: {e}")
        return ""

def convert_from_pdf_to_text(pdf_file_path):
    with open(pdf_file_path, 'rb') as file:
        resource_manager = PDFResourceManager()
        fake_file_handle = StringIO()
        la_params = LAParams()
        converter = TextConverter(resource_manager, fake_file_handle, laparams=la_params)
        page_interpreter = PDFPageInterpreter(resource_manager, converter)

        for page in PDFPage.get_pages(file, check_extractable=True):
            page_interpreter.process_page(page)

        text = fake_file_handle.getvalue()

    converter.close()
    fake_file_handle.close()

    if text:
        text = text.replace("(cid:10)", "")
        text = text.replace("\n", "")
        text = text.replace(" ", "")
        return text[:-1]


def extract_from_pdf(pdf_file_path):
    pdf = pdfquery.PDFQuery(pdf_file_path)
    pdf.load()

    # Select all the text elements on the first page of the PDF
    #text_elements = pdf.pq('LTTextLineHorizontal:in_bbox("0,0,612,792"):not(:empty)')
    text_elements = pdf.pq('LTTextLineHorizontal:in_bbox("0,0,612,792"):not(:empty):not(:contains("(cid:10)"))')
    #text_elements = pdf.pq('LTTextLineHorizontal:in_bbox("0,0,612,792")')

    # Concatenate the text from each elements
    print(text_elements)
    for elem in text_elements:
        print(elem)
    text = ''.join([elem.text.strip() for elem in text_elements])
    #text = text.replace('(cid:10)', '')

    return text


if __name__ == '__main__':
    #convert_from_text_to_pdf("C:\\Users\\Student\\Desktop\\maor123.txt", "C:\\Users\\Student\\Desktop\\pdfmaor123.pdf")
    #list_of_pages = extract_from_pdf(r"C:\Users\maork\OneDrive\Desktop\WeHireCyberProject\UniversityStudentsDiplomasFolder\Maor Krasner 213225576.pdf")
    #text = convert_from_pdf_to_text(r"C:\Users\maork\OneDrive\Desktop\WeHireCyberProject\UniversityStudentsDiplomasFolder\Maor Krasner 213225576.pdf")
    #print(text)
    text = extract_from_pdf(r"C:\Users\maork\OneDrive\Desktop\WeHireCyberProject\UniversityStudentsDiplomasFolder\Maor Krasner 213225576.pdf")
    print(text)
