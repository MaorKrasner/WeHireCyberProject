from fpdf import FPDF
from io import StringIO
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.pdfpage import PDFPage


# function that converts text file to pdf file
def convert_from_text_to_pdf(text_file_path, pdf_file_path):
    # Read the content of the text file as a list of lines
    with open(text_file_path, 'r', encoding="utf8") as f:
        text = f.readlines()

    pdf = FPDF()  # Create a PDF object
    pdf.add_page()  # Add a page
    pdf.set_font('Arial', size=12)  # Set the font and font size

    # write each line of the text to the pdf file
    for i in range(len(text)):
        pdf.cell(200, 10, txt=text[i], ln=1)

    # Save the PDF file
    pdf.output(pdf_file_path)


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
        return text


if __name__ == '__main__':
    convert_from_text_to_pdf("C:\\Users\\Student\\Desktop\\maor123.txt", "C:\\Users\\Student\\Desktop\\pdfmaor123.pdf")
