import os
import re
from abc import ABC, abstractmethod
import pandas as pd
import tabula
import PyPDF2
import pytesseract
from PIL import Image
from pdf2image import convert_from_path

class BaseExtractor(ABC):
    """
    Base class for PDF table extractors.
    Implements table location and defines extractor interface.
    """

    def __init__(self, filepath: str):
        """
        Constructor to initialize filepath.

        Args:
            filepath (str): Path of PDF file
        """
        self.filepath = filepath

    @staticmethod
    def locate_table(filepath: str,
                     search_string: str,
                     ignore_case: bool = True) -> dict:
        """
        Locates pages containing given search string in text.

        Args:
            filepath (str): Path of PDF file.
            search_string (str): String to search pages for.
            ignore_case (bool): Default set to be insensitive to casing.

        Returns: 
            A dict of matched string page numbers
        """
        search_lst = []
        reader = PyPDF2.PdfReader(filepath)

        for page_num, page in enumerate(reader.pages):
            try:
                page_text = page.extract_text()
                hits = None
                if not ignore_case:
                    hits = re.search(search_string, page_text.lower())
                else:
                    hits = re.search(
                        search_string, page_text.lower(), re.IGNORECASE)

                if hits:
                    search_lst.append(page_num)
            except Exception as e:
                print(f"Error in page {page_num}: {e}")
        return {"table_loc": search_lst}

    @abstractmethod
    def extract(self):
        """
        Abstract method to extract table from page.
        """
        return


class TesseractExtractor(BaseExtractor):
    """
    A Tesseract-based pdf extractor
    """
    def __init__(self, filepath: str):
        super().__init__(filepath)
        self.table_loc = None

    def extract(self, search_string: str, config: str, **kwargs) -> str:
        """
        Extracts table text from located page using OCR with Tesseract.
        Args:
            search_string (str): the string of interests passed to locate_table() for
                getting the specific table's page number.

            config (str): the config string to pass to pytesseract.image_to_string()
        Return:
            text (str): the raw 

        """
        self.table_loc = self.locate_table(
            self.filepath, search_string, ignore_case=True)["table_loc"]
        if len(self.table_loc) >= 1:
            page_num = self.table_loc[-1]
            images = self._convert_to_images(**kwargs)
            self.img = images[page_num]
            text = pytesseract.image_to_string(self.img, lang='eng',
                                               config=config)
            return text

    def _convert_to_images(self, **kwargs):
        """
        Converts PDFs to Images by calling pdf2image.convert_from_path() methods.

        Return:

        """
        return convert_from_path(self.filepath, **kwargs)


class TabulaExtractor(BaseExtractor):

    def extract(self,
                search_string: str,
                table_page: int,
                table_seq: int = 0) -> pd.DataFrame:
        """
        Extracts table from located page as DataFrame using Tabula.
        Args:
            search_string (str):
            table_page (int):
            table_seq ()
        Return:
            
        """

        self.table_loc = self.locate_table(self.filepath, search_string,
                                           ignore_case=True)["table_loc"]
        if len(self.table_loc) != 0:
            table_page = self.table_loc[-1]
            dfs = tabula.read_pdf(self.filepath, pages=table_page, stream=True)
            if len(dfs) > 1:
                print(f"The page has {len(dfs)} tables.")
                df = dfs[table_seq]

            else:
                df = dfs[0]
                df.columns = df.iloc[0, :].to_list()
        else:
            dfs = tabula.read_pdf(self.filepath, pages="all", stream=True)
            df = dfs[table_page]
            df.columns = df.iloc[0, :].to_list()

        df = df.iloc[1:].reset_index().drop("index", axis=1)

        return df
