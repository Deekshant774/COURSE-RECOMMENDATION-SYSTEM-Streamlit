"""
Purpose: To scrape data from Coursera's Website
Links Used: 
    https://realpython.com/beautiful-soup-web-scraper-python/
    https://medium.com/analytics-vidhya/web-scraping-and-coursera-8db6af45d83f
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

# Explore the Website
# Link: https://www.coursera.org/courses
# Base URL: https://www.coursera.org/courses
# Query Parameters: ?page=1&index=prod_all_products_term_optimization
# Page Number Range: 1-100

class DataMaker:
    """
    Creates the data by scraping the website
    """

    site_url = None
    first_page = None
    last_page = None
    urls = []
    courses = []
    organizations = []
    learning_products = []
    ratings = []
    num_rated = []
    difficulty = []
    enrolled = []

    def __init__(self, site, first_page, last_page):
        """
        Initialises the page limit within
        which the data is to be scraped
        """
        self.site_url = site
        self.first_page = first_page
        self.last_page = last_page

    def scrape_features(self, page_url):
        """
        Scrapes 8 features from each page
        -----
        page_url:
            URL of the page
        """

        course_list_page = requests.get(page_url)
        course_list_soup = BeautifulSoup(course_list_page.content, 'html.parser')

        # --- course names ---
        cnames = [c.text for c in course_list_soup.select(".headline-1-text")]

        # --- partner names ---
        pnames = [p.text for p in course_list_soup.select(".horizontal-box > .partner-name")]

        # --- course URLs ---
        root = "https://www.coursera.org"
        links = [root + l.a["href"] for l in course_list_soup.select(
            ".ais-InfiniteHits > .ais-InfiniteHits-list > .ais-InfiniteHits-item"
        )]

        # --- learning product type ---
        learn_pdcts = [lp.text for lp in course_list_soup.find_all('div', '_jen3vs _1d8rgfy3')]

        # --- ratings ---
        cratings = course_list_soup.select(".ratings-text")
        ratings = []
        for r in cratings:
            try:
                ratings.append(float(r.text))
            except:
                ratings.append("Missing")

        # --- number of ratings ---
        cnumratings = course_list_soup.select(".ratings-count")
        num_ratings = []
        for nr in cnumratings:
            try:
                num_ratings.append(int(nr.text.replace(',', '').replace('(', '').replace(')', '')))
            except:
                num_ratings.append("Missing")

        # --- enrollment ---
        enrollers = [e.text if e else "Missing" for e in course_list_soup.select(".enrollment-number")]

        # --- difficulty ---
        difficulty = [d.text for d in course_list_soup.select(".difficulty")]

        # --- normalize lengths (so DataFrame won’t break) ---
        min_len = min(
            len(cnames), len(pnames), len(links),
            len(learn_pdcts), len(ratings),
            len(num_ratings), len(enrollers), len(difficulty)
        )

        self.courses.extend(cnames[:min_len])
        self.organizations.extend(pnames[:min_len])
        self.urls.extend(links[:min_len])
        self.learning_products.extend(learn_pdcts[:min_len])
        self.ratings.extend(ratings[:min_len])
        self.num_rated.extend(num_ratings[:min_len])
        self.enrolled.extend(enrollers[:min_len])
        self.difficulty.extend(difficulty[:min_len])

    def crawler(self):
        """
        Traverses between the first and last pages
        -----
        base_url:
            Base URL
        """
        for page in range(self.first_page, self.last_page+1):
            print("\nCrawling Page " + str(page))
            page_url = self.site_url + "?page=" + str(page) + \
                       "&index=prod_all_products_term_optimization"
            self.scrape_features(page_url)

    def make_dataset(self):
        """
        Make the dataset
        """
        # initiate crawler
        self.crawler()

        data_dict = {
            "Course URL": self.urls,
            "Course Name": self.courses,
            "Learning Product Type": self.learning_products,
            "Course Provided By": self.organizations,
            "Course Rating": self.ratings,
            "Course Rated By": self.num_rated,
            "Enrolled Student Count": self.enrolled,
            "Course Difficulty": self.difficulty
        }

        data = pd.DataFrame(data_dict)
        return data


def main():
    dm = DataMaker("https://coursera.org/courses", 1, 5)  # 🔹 use smaller range first for testing
    df = dm.make_dataset()
    os.makedirs("data", exist_ok=True)
    destination_path = os.path.join("data/coursera-courses-overview.csv")
    df.to_csv(destination_path, index=False)
    print(f"\n✅ Saved {len(df)} courses to {destination_path}")


if __name__ == "__main__":
    main()
