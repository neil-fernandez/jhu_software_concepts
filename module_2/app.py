from scrape import scrape_data, save_data

if __name__ == "__main__":
    url = "https://www.thegradcafe.com/survey/"
    parsed_data = scrape_data(url, max_pages=3)
    save_data("applicant_data.json", parsed_data)