PROJECT_FOLDER_PATH = "/Users/czhang/Desktop/pacific-observatory/"
SCRAPE_ALL = False

# URL-related Information
# MATANGI TONGA
MATANGI_PAGE_URLS = [f"https://matangitonga.to/topic/all?page={num}"
                     for num in range(1, 937)]
MATANGI_PAGE_URLS_ELEMENTS = ["views-field views-field-title",  # Title + embedded URL
                              # Category (e.g. Editorials/Politics/Travel/Business...)
                              "views-field views-field-term-node-tid",
                              "views-field views-field-field-first-publication",  # Date
                              "views-field views-field-field-location"  # News Location
                              ]

# ABC AUSTRILIA
ABC_AU_TOPIC_DICT = {
    26514: "fiji",
    26790: "solomon_islands",
    26730: "papua_new_guinea",
    26874: "vanuatu",
    26720: "pacific",
    26664: "marshall_islands",
    26832: "tonga"
}

# PINA
PINA_URLS = [f"https://pina.com.fj/category/news/page/{num}"
             for num in range(1, 475)]

# Fiji
# Fiji Sun
FIJI_SUN_URLS = ["https://fijisun.com.fj/category/fiji-news/page/" + str(i)
                 for i in range(1, 1547)]
FIJI_SUN_URLS.extend(["https://fijisun.com.fj/category/news/nation/page/" + str(i)
                      for i in range(1, 888)])


# RNZ New Zealand


# Samoa
##
SAMOA_OBSERVER_URLS = [f"https://www.samoaobserver.ws/stories/page/{num}.json?&category=samoa&api=true"
                       for num in range(0, 2079)]

# Solomon Islands
## Solomon Star
SOLOMON_STAR_URLS = [f"https://www.solomonstarnews.com/category/news/news-national/page/{page}"
                     for page in range(1, 1450)]



## Solomon Times
SOLOMON_TIMES_URLS = [f"https://www.solomontimes.com/news/latest/{year}/{month}" 
                      for year in range(2007, 2024) for month in range(1, 13)]


# Pupua New Guinea
# Post Courier
POST_COURIER_PAGE_URLS = [f"https://www.postcourier.com.pg/national-news/page/{num}"
                          for num in range(1, 1797)]
POST_COURIER_PAGE_ELEMENTS = ["entry-title", "posted-on"]
POST_COURIER_NEWS_ELEMENTS = ["entry-content", "tags-links"]

# PNG Business

#
