import PyPDF2


class PdfReader:
    @staticmethod
    def read(path):
        data = ''
        pdfFile = open(path, 'rb') 
        pdfReader = PyPDF2.PdfReader(pdfFile)
        pages = len(pdfReader.pages)

        for page in range(pages):
            pageOBJ = pdfReader.pages[page]
            data += pageOBJ.extract_text()
        pdfFile.close()
        return data