"""
The module provides a series of text preprocessing supporting utils.

Last modified:
    2024-02-05
"""

import re
import spacy
from typing import List, Dict, Union
import pandas as pd
from gensim.utils import simple_preprocess
import json
from pathlib import Path


def is_in_word_list(row: str, terms: list) -> bool:
    """
    Check if any of the given terms are present in the input row.

    Args:
        row (str): The input row to search for terms in.
        terms (list): A list of terms to search for in the row.

    Returns:
        bool: True if any of the terms are found in the row, False otherwise.
    """
    pattern = r"\b(" + "|".join(re.escape(term) for term in terms) + r")\b"
    return bool(re.search(pattern, str(row), re.IGNORECASE))


def sent_to_words(sentences: List[str]):
    """
    Converts sentences into a list of words, performing simple preprocessing.

    Args:
        sentences: A list of sentences to be converted.

    Yields:
        A generator yielding lists of words extracted from each sentence after preprocessing.
    """
    for sentence in sentences:
        sentence = re.sub(r"\s", " ", sentence).strip()
        yield (simple_preprocess(str(sentence), deacc=True))


def lemmatize_sent(sent, nlp, allowed_postags=["NOUN", "ADJ", "VERB", "ADV"]):
    """
    Lemmatizes words in a sentence based on allowed part-of-speech tags.

    Args:
        sent: The sentence represented as a list of words.
        nlp: An instance of spacy's language model.
        allowed_postags: List of part-of-speech tags allowed for lemmatization.

    Returns:
        A list of lemmatized words filtered by allowed part-of-speech tags.
    """
    doc = nlp(" ".join(sent))
    return [token.lemma_ for token in doc if token.pos_ in allowed_postags]


def make_phrases(texts: List[str], phrases_model):
    """
    Apply phrase models to texts to detect and join multi-word expressions.

    Args:
        texts: List of tokenized texts.
        phrases_model: A Phraser model that detects phrases.

    Returns:
        A list of texts with phrases detected and joined.
    """
    return [phrases_model[doc] for doc in texts]


def preprocess_text(
    texts: List[str],
    stopwords: List[str],
    bigram_mod,
    trigram_mod,
    nlp: spacy.language.Language,
):
    """
    Preprocesses texts by removing stopwords, applying bigram and trigram models, and lemmatizing.

    Args:
        texts: List of texts to preprocess.
        stopwords: List of stopwords to remove.
        bigram_mod: Bigram Phraser model.
        trigram_mod: Trigram Phraser model.
        nlp: An instance of spacy's language model for lemmatization.

    Returns:
        A list of preprocessed and lemmatized texts.
    """
    texts_no_stopwords = [
        [word for word in simple_preprocess(str(doc)) if word not in stopwords]
        for doc in texts
    ]
    print("Stopwords has been done.")
    texts_bigrams = make_phrases(texts_no_stopwords, bigram_mod)
    texts_trigrams = make_phrases(texts_bigrams, trigram_mod)
    texts_lemmatized = [lemmatize_sent(doc, nlp) for doc in texts_trigrams]

    return texts_lemmatized


def generate_continous_df(
    checked_df: pd.DataFrame, min_date: str, max_date: str, freq="MS"
):
    """
    Generates a continuous date range dataframe and merges it with an existing dataframe.

    Args:
        checked_df: The dataframe to merge with the continuous date range.
        min_date: The start date for the continuous date range.
        max_date: The end date for the continuous date range.
        freq: The frequency of the dates to generate, defaults to 'MS' (month start).

    Returns:
        A dataframe with a continuous date range merged with the existing dataframe.

    Raises:
        ValueError: If 'date' column is not found in the checked dataframe.
    """
    dates_range = pd.date_range(start=min_date, end=max_date, freq=freq)
    dates_df = pd.DataFrame(dates_range, columns=["date"])
    if "date" in checked_df.columns:
        checked_df["date"] = pd.to_datetime(checked_df["date"], format="mixed")
        checked_df = dates_df.merge(checked_df, how="left", on="date").fillna(0)
        return checked_df
    else:
        raise ValueError("cannot find `date` column in dataframe being checked.")


def load_topics_words(
    additional_name: Union[str, None] = None,
) -> Dict[str, Union[List[str], Dict[str, List[str]]]]:
    """
    Load topic words from the topics_words.json configuration file.

    Args:
        additional_name (Union[str, None]): Optional name of additional topic category
            (e.g., 'job', 'inflation'). If provided, returns only that category's terms.

    Returns:
        Dict containing:
        - If additional_name is None: All topics with keys 'economic', 'policy', 'uncertainty', 'additional_terms'
        - If additional_name is provided: Only the specified additional_terms category

    Raises:
        FileNotFoundError: If topics_words.json is not found.
        KeyError: If additional_name is provided but not found in additional_terms.
    """
    config_path = Path(__file__).parent / "topics_words.json"

    if not config_path.exists():
        raise FileNotFoundError(f"topics_words.json not found at {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        topics_data = json.load(f)

    if additional_name is None:
        return topics_data
    else:
        if additional_name not in topics_data.get("additional_terms", {}):
            raise KeyError(
                f"additional_name '{additional_name}' not found in topics_words.json. "
                f"Available options: {list(topics_data.get('additional_terms', {}).keys())}"
            )
        return topics_data["additional_terms"][additional_name]


def generate_news_statistics_table(country_folder: Path) -> str:
    """
    Generate a markdown table with news statistics by country and newspaper/media source.

    Reads news.csv files from the country folder structure and generates a formatted
    markdown table showing:
    - Country name
    - Newspaper/Media source
    - Number of articles (formatted with thousands separator)
    - Earliest article date (YYYY-MM-DD format, or "N/A" if no data)

    Args:
        country_folder (Path): Path to the folder containing country subdirectories,
            each with newspaper subdirectories containing news.csv files.

    Returns:
        str: A formatted markdown table with news statistics.

    Example:
        >>> from pathlib import Path
        >>> country_folder = Path("data/news")
        >>> table = generate_news_statistics_table(country_folder)
        >>> print(table)
    """
    # Dictionary to store data: {country: {newspaper: {count, min_date}}}
    data_by_country = {}
    total_articles = 0

    # Loop through country folders
    for country_folder_path in country_folder.iterdir():
        if not country_folder_path.is_dir():
            continue

        country = country_folder_path.name

        # Find all newspaper folders with news.csv files
        for newspaper_folder in country_folder_path.iterdir():
            if not newspaper_folder.is_dir():
                continue

            newspaper = newspaper_folder.name
            news_file = newspaper_folder / "news.csv"

            if not news_file.exists():
                continue

            try:
                # Read the CSV file
                df = pd.read_csv(news_file, encoding="utf-8")

                if df.empty:
                    continue

                # Get count and earliest date
                article_count = len(df)
                total_articles += article_count

                # Parse date column and find minimum (earliest) date
                if "date" in df.columns:
                    df["date"] = pd.to_datetime(df["date"], errors="coerce")
                    min_date = df["date"].min()
                    min_date_str = (
                        min_date.strftime("%Y-%m-%d") if pd.notna(min_date) else "N/A"
                    )
                else:
                    min_date_str = "N/A"

                # Determine if this is ABC AU or RNZ based on newspaper folder name
                is_abc_au = newspaper.startswith("abc_au_")
                is_rnz = newspaper.startswith("rnz_")

                # If ABC AU or RNZ, add to "pacific" country instead of original country
                target_country = "pacific" if (is_abc_au or is_rnz) else country

                # Store data
                if target_country not in data_by_country:
                    data_by_country[target_country] = {}

                data_by_country[target_country][newspaper] = {
                    "count": article_count,
                    "min_date": min_date_str,
                }

            except Exception as e:
                print(f"Warning: Could not process {news_file}: {e}")
                continue

    # Mapping for specific newspaper display names
    newspaper_display_names = {
        "people_s_daily_online": "People's Daily Online",
        "matangi_tonga": "Matangi Tonga Online",
        "mi_journal": "MI Journal",
        "pina": "PINA",
        "png_business_news": "PNG Business News",
        "sibc": "SIBC",
        "today": "Today Online",
        "ub_post": "UB Post",
        "vbr": "Vanuatu Business Review (VBR)",
    }

    # Sort countries and newspapers
    sorted_countries = sorted(data_by_country.keys())

    # Build markdown table
    lines = []
    lines.append("| Country | Newspaper/Media Source | Number of Articles | From |")
    lines.append("|---------|------------------------|--------------------|----|")

    for country in sorted_countries:
        newspapers = sorted(data_by_country[country].keys())

        # Create a list of display items (name, count, min_date)
        display_items = []
        abc_au_total = 0
        abc_au_min_date = None
        rnz_total = 0
        rnz_min_date = None

        for newspaper in newspapers:
            info = data_by_country[country][newspaper]

            # Group ABC AU newspapers
            if newspaper.startswith("abc_au_"):
                abc_au_total += info["count"]
                if abc_au_min_date is None or info["min_date"] < abc_au_min_date:
                    abc_au_min_date = info["min_date"]
            # Group RNZ newspapers
            elif newspaper.startswith("rnz_"):
                rnz_total += info["count"]
                if rnz_min_date is None or info["min_date"] < rnz_min_date:
                    rnz_min_date = info["min_date"]
            # Other newspapers
            else:
                display_items.append((newspaper, info["count"], info["min_date"]))

        # Add grouped ABC AU and RNZ to display items
        if abc_au_total > 0:
            display_items.append(
                (
                    "Australian Broadcasting Corporation (ABC AU)",
                    abc_au_total,
                    abc_au_min_date,
                )
            )
        if rnz_total > 0:
            display_items.append(("Radio New Zealand (RNZ)", rnz_total, rnz_min_date))

        # Sort all display items alphabetically
        display_items.sort(key=lambda x: x[0].lower())

        # Display all items for this country
        is_first_row = True
        # Format country name: replace underscores with spaces and capitalize
        formatted_country = country.replace("_", " ").title()

        for newspaper, count, min_date in display_items:
            count_str = f"{count:,}"
            date_str = min_date if min_date else "N/A"

            # Format newspaper name
            # Check if it's a display name (ABC AU or RNZ)
            if newspaper.startswith(
                "Australian Broadcasting Corporation"
            ) or newspaper.startswith("Radio New Zealand"):
                formatted_newspaper = newspaper
            # Check if it has a specific mapping
            elif newspaper in newspaper_display_names:
                formatted_newspaper = newspaper_display_names[newspaper]
            # Otherwise, replace underscores with spaces and capitalize
            else:
                formatted_newspaper = newspaper.replace("_", " ").title()

            if is_first_row:
                lines.append(
                    f"| {formatted_country} | {formatted_newspaper} | {count_str} | {date_str} |"
                )
                is_first_row = False
            else:
                lines.append(f"| | {formatted_newspaper} | {count_str} | {date_str} |")

    # Add total row
    total_str = f"{total_articles:,}"
    lines.append(f"| **Total** | | **{total_str}** | |")

    return "\n".join(lines)


if __name__ == "__main__":
    from pathlib import Path

    country_folder = Path(
        "data/text"
    )  # Path to country folders with newspaper subdirectories
    table = generate_news_statistics_table(country_folder)
    print(table)
