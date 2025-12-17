# This file will contain utilities to deal with IMF CPI data
# https://data.imf.org/en/datasets/IMF.STA:CPI
import sdmx
import pandas as pd
from typing import Union, List, Dict
import sys
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


DATA_ROOT = PROJECT_ROOT / "data" / "cpi"
IMF_ROOT = DATA_ROOT / "imf"
OUTPUT_ROOT = PROJECT_ROOT / "outputs" / "cpi" / "imf"

os.makedirs(DATA_ROOT, exist_ok=True)
os.makedirs(IMF_ROOT, exist_ok=True)
os.makedirs(OUTPUT_ROOT, exist_ok=True)


def _get_country_cpi_data(
    country: str,
    frequency: str = "M",  # One of "M", "Q", "Y"
    start_period: int = 2012,
    component: str = "_T",
) -> pd.DataFrame:
    IMF_DATA = sdmx.Client("IMF_DATA")
    try:
        data_msg = IMF_DATA.data(
            "CPI",
            key=f"{country}.CPI.{component}.IX.{frequency}",
            params={"startPeriod": start_period},
        )
        output = sdmx.to_pandas(data_msg).dropna().reset_index()
        output.to_csv(IMF_ROOT / f"{country}.cpi.{frequency}.csv", index=False)
        return output
    except Exception as e:
        print(f"Error for {country}: {e}")
        return None


def get_cpi_data(
    country: Union[List, str],
    frequency: str = "M",  # One of "M", "Q", "Y"
    start_period: int = 2012,
    component: str = "_T",
) -> pd.DataFrame:
    output = []
    if isinstance(country, list):
        for c in country:
            csv_path = IMF_ROOT / f"{c}.cpi.{frequency}.csv"
            if os.path.exists(csv_path):
                data = pd.read_csv(csv_path)
                output.append(data)
            else:
                data = _get_country_cpi_data(c, frequency, start_period, component)
                output.append(data)
    else:
        csv_path = IMF_ROOT / f"{country}.cpi.{frequency}.csv"
        if os.path.exists(csv_path):
            data = pd.read_csv(csv_path)
            output.append(data)
        else:
            data = _get_country_cpi_data(country, frequency, start_period, component)
            output.append(data)
    return pd.concat(output).reset_index(drop=True)


def analyze_cpi_by_frequency(countries: List[str]) -> Dict:
    """
    Analyze CPI data availability by frequency for multiple countries.

    Returns:
        Dict with:
        - country_data: {country_iso3: {'frequency': 'Monthly'/'Quarterly'/'No Data', 'latest_period': '2025-M10'}}
    """
    country_data = {}

    for country in countries:
        has_monthly = False
        has_quarterly = False
        latest_monthly = None
        latest_quarterly = None

        # Try to get monthly data
        try:
            monthly_df = get_cpi_data(country, frequency="M")
            if monthly_df is not None and not monthly_df.empty:
                has_monthly = True
                latest_monthly = monthly_df.reset_index()["TIME_PERIOD"].max()
        except Exception:
            pass

        # Try to get quarterly data
        try:
            quarterly_df = get_cpi_data(country, frequency="Q")
            if quarterly_df is not None and not quarterly_df.empty:
                has_quarterly = True
                latest_quarterly = quarterly_df.reset_index()["TIME_PERIOD"].max()
        except Exception:
            pass

        # Determine highest frequency and store data
        if has_monthly:
            country_data[country] = {
                "frequency": "Monthly",
                "latest_period": latest_monthly,
            }
        elif has_quarterly:
            country_data[country] = {
                "frequency": "Quarterly",
                "latest_period": latest_quarterly,
            }
        else:
            country_data[country] = {"frequency": "No Data", "latest_period": None}

    return {"country_data": country_data}


def save_cpi_analysis_report(analysis: Dict, countries_df: pd.DataFrame):
    """
    Print CPI data analysis report as markdown table.

    Args:
        analysis: Dict from analyze_cpi_by_frequency with country_data
        countries_df: DataFrame with 'iso3' and 'name' columns
    """
    # Create a mapping of ISO3 to country name
    iso3_to_name = dict(zip(countries_df["iso3"], countries_df["name"]))

    # Build report data
    report_data = []
    country_data = analysis["country_data"]
    sorted_countries = sorted(country_data.keys(), key=lambda x: iso3_to_name.get(x, x))

    for iso3 in sorted_countries:
        country_name = iso3_to_name.get(iso3, iso3)
        data = country_data[iso3]
        frequency = data["frequency"]
        latest_period = (
            data["latest_period"] if data["latest_period"] is not None else "No Data"
        )

        report_data.append(
            {
                "Country Name": country_name,
                "ISO3": iso3,
                "Frequency": frequency,
                "Last Reported": latest_period,
            }
        )

    # Create DataFrame and print as markdown
    df = pd.DataFrame(report_data)
    print(df.to_markdown(index=False))


if __name__ == "__main__":
    countries = pd.read_csv(DATA_ROOT / "_countries.csv")
    countries_list = countries["iso3"].tolist()

    analysis = analyze_cpi_by_frequency(countries_list)
    save_cpi_analysis_report(analysis, countries)
