import os
import pandas as pd
from src.text.scrapers import NewspaperScraper
name = os.path.basename(__file__).split(".")[0]
region= os.path.basename(os.path.dirname(__file__))
SIBC_PAGE_URLS = [
    f"https://www.sibconline.com.sb/?s&post_type=post&paged={num}"
    for num in range(1, 1335)
    # for num in range(1, 40) # For testing
]

class SIBCScraper(NewspaperScraper):
    """
    SIBC (Solomon Islands Broadcasting Corporation) newspaper scraper
    using the NewspaperScraper base class.
    """
    
    def __init__(self):
        super().__init__(
            name=name,
            # domain="sibconline.com.sb",
            domain=None,
            region=region,
            parser="html.parser"
        )
        self.page_urls = SIBC_PAGE_URLS

        
        # Ensure target directory exists
        os.makedirs(self.target_dir, exist_ok=True)
    
    def get_page_enum(self):
        """Get the list of page URLs to scrape for article listings."""
        return self.page_urls
    
    def get_news_urls(self):
        """Scrape article URLs and metadata from listing pages."""
        print("Scraping article URLs from SIBC listing pages...")
        
        pages_raw = self.scrape_urls(
            self.page_urls,
            "item-bot-content",
            speed_up=True
        )
        
        # Parse the scraped pages
        urls_info = []
        for page in pages_raw:
                items = page[1]
                for item in items:
                    title_entry = item.find(class_="item-title").find("a")
                    date_entry = item.find(class_="item-date-time")
                    
                    if title_entry and date_entry:
                        date = date_entry.text.replace("-", "").strip()
                    urls_info.append([
                        title_entry["href"], 
                        title_entry.text, 
                        date
                    ])
        
        # Create DataFrame
        self.urls_df = pd.DataFrame(urls_info, columns=["url", "title", "date"])
        self.urls_df["date"] = pd.to_datetime(self.urls_df["date"], format="mixed")
        self.urls_df = self.urls_df.sort_values(by="date").reset_index(drop=True)
        
        print(f"Found {len(self.urls_df)} articles")
        return self.urls_df
    
    def scrape_news(self):
        """Scrape full article content for new URLs."""
        
        urls_to_scrape = self.get_new_news()
        
        if not urls_to_scrape:
            print("No new articles to scrape")
            return pd.DataFrame()
        
        # Scrape article content
        news_raw = self.scrape_urls(
            urls_to_scrape,
            ["entry-body", "entry-taxonomies"],
            speed_up=True
        )
        
        # Parse article content
        news_info = []
        for news in news_raw:
            url = news[0]
            if len(news[1]) >= 2:
                for news_entry, tag_entry in zip(*news[1]):
                    text = " ".join(p.get_text(separator=" ", strip=True) for p in news_entry.find_all("p"))
                    tags = ", ".join(tag.text for tag in tag_entry.find_all("a"))
                    news_info.append([url, text, tags])
        
        # Create news DataFrame
        news_df = pd.DataFrame(news_info, columns=["url", "news", "tag"])
        news_df = news_df.merge(self.urls_df, how="left", on="url")[
            ["url", "title", "date", "news", "tag"]
        ]
        
        print(f"Successfully scraped {len(news_df)} articles")
        return news_df

    
    def run_full_scrape(self):
        """Execute the complete scraping workflow."""
        print("Starting SIBC scraping workflow...")
        
        # Step 1: Get article URLs
        self.get_news_urls()
        self.save_news_urls()
        
        # Step 2: Load previous data
        self.get_previous_news()
        
        # Step 3: Scrape article content
        news_df = self.scrape_news()
        
        # Step 4: Save results
        if len(news_df) > 0:
            self.save_scraped_news(news_df)
        
        print("SIBC scraping completed successfully!")


def main():
    """Main function to run the SIBC scraper."""
    scraper = SIBCScraper()
    scraper.run_full_scrape()


if __name__ == "__main__":
    main()
