# Intermediate Files

`vu_monthly_error.csv` contains the calculation error from the Vanuatu's census data:
  - `Total` is parsed from the scraped pdf files, as stored in
  - `cal_row_sums` is the constructed variable that manually calculates the sum of the row through `check_quality` function defined in `/scripts/python/PdfParse.py`
  - `error` is the difference between `Total` and `cal_row_sums` and either +1 or -1.

`vu_monthly_visitor.csv` is the corrected version of the Vanuatu's monthly visitors from 2004 to 2022. 
