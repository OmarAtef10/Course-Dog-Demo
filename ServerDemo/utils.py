from datetime import datetime
import PyPDF2
import inspect

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
    

class Logger:
    def __init__(self, file_path) -> None:
        self.file = open(file_path, '+a')
        self.file.write('---------------------------------------------------\n')

    def info(self, msg):
        dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.file.write(f"INFO @ {inspect.stack()[1][3]} - {dt_string}: {msg}\n")

    def warn(self, msg):
        dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.file.write(f"WARN @ {inspect.stack()[1][3]} - {dt_string}: {msg}\n")

    def fatal(self, msg):
        dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.file.write(f"FATAL @ {inspect.stack()[1][3]} - {dt_string}: {msg}\n")

    def close(self):
        self.file.close()
