import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from src.text.epu import EPU

parent_dirs = "data/text/"
country_dirs = [
    parent_dirs + country
    for country in os.listdir(parent_dirs)
    and "marshall_islands" not in country
    and "tonga" not in country
]
output_dir = "testing_outputs/text/"

print(country_dirs)
