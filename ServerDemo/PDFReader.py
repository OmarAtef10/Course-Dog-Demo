import PyPDF2


class PdfReader:
    @staticmethod
    def read(path):
        data = ''
        pdfFile = open(path, 'rb') 
        pdfReader = PyPDF2.PdfFileReader(pdfFile)
        pages = pdfReader.numPages

        for page in range(pages):
            pageOBJ = pdfReader.getPage(page)
            data += pageOBJ.extractText()
        pdfFile.close()
        return data