import os
from datetime import datetime
import csv
import pandas as pd
from PyPDF2 import PdfReader


class FileMetaData:
    """
    Class to extract metadata for different file types
    """

    def __init__(self, file_path: str):
        """
        Initialize with a given filepath.
        """
        self.file_path = file_path

    def extract(self) -> dict:
        """
        Extracts and returns dict of metadata about file. The function is compatible with extracting 
        metadata information from .csv, .xlsx, and .pdf files.

        Returns:
            metadata (dict): Dictionary containing file metadata


        Example: 
         meta = FileMetaData("random.pdf")
         print(meta.extract())
         ----------
        {'filename': 'random.pdf',
        'created': datetime.datetime(2023, 11, 15, 14, 8, 21, 417070),
        'modified': datetime.datetime(2023, 11, 13, 13, 28, 11, 750389),
        'num_pages': 6}
        """
        metadata: dict = {
            "filename": os.path.basename(self.file_path),
            "created": datetime.fromtimestamp(os.path.getctime(self.file_path)),
            "modified": datetime.fromtimestamp(os.path.getmtime(self.file_path))
        }

        if self.file_path.endswith('.csv'):
            self._extract_csv_metadata(metadata)

        elif self.file_path.endswith('.xlsx'):
            self._extract_excel_metadata(metadata)

        elif self.file_path.endswith('.pdf'):
            self._extract_pdf_metadata(metadata)

        return metadata

    def _extract_csv_metadata(self, metadata: dict) -> None:
        """
        Helper method to extract CSV metadata
        """
        with open(self.file_path) as f:
            reader = csv.reader(f)
            metadata['num_rows'] = sum(1 for row in reader) - 1
            df = pd.read_csv(self.file_path)
            if "Unnamed: 0" in df.columns:
                df = df.drop("Unnamed: 0", axis=1)
            metadata['sample_data'] = df.sample(1).to_dict()

    def _extract_excel_metadata(self, metadata: dict) -> None:
        """
        Helper method to extract Excel metadata
        """
        wb = pd.ExcelFile(self.file_path)
        metadata['sheets'] = wb.sheet_names

    def _extract_pdf_metadata(self, metadata: dict) -> None:
        """
        Helper method to extract PDF metadata
        """
        with open(self.file_path, 'rb') as f:
            reader = PdfReader(f)
            metadata['num_pages'] = len(reader.pages)



