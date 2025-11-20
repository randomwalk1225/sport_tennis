"""
Scrape player activity by year
"""

from playwright.sync_api import sync_playwright
import json
import time
import sys


def scrape_player_activity_by_year(player_id: str, player_name: str, year: int):
    """
    Scrape player activity for a specific year
    """
    url = f"https://www.atptour.com/en/players/{player_name}/{player_id}/player-activity?matchType=Singles&year={year}&tournament=all"

    print(f"Scraping {player_name} for year {year}...")
    print(f"URL: {url}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        print(f"Loading page...")
        page.goto(url, wait_until="load", timeout=60000)

        print("Waiting for data to load...")
        time.sleep(15)

        # Scroll
        for i in range(5):
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(2)

        # Get HTML
        html = page.content()

        # Count tournaments
        tournament_count = page.evaluate("""() => {
            return document.querySelectorAll('.tournament.tournament--expanded').length;
        }""")

        print(f"Found {tournament_count} tournaments for year {year}")

        # Save HTML
        filename = f"{player_name}_activity_{year}.html"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"Saved HTML to {filename}")

        # Take screenshot
        screenshot_file = f"{player_name}_activity_{year}.png"
        page.screenshot(path=screenshot_file, full_page=True)
        print(f"Saved screenshot to {screenshot_file}")

        browser.close()

    return tournament_count


def main():
    player_id = 'd643'
    player_name = 'novak-djokovic'

    # Test different years
    years = [2025, 2024, 2023, 2022]

    results = {}

    for year in years:
        try:
            count = scrape_player_activity_by_year(player_id, player_name, year)
            results[year] = count
            print(f"[+] Year {year}: {count} tournaments\n")
        except Exception as e:
            print(f"[-] Year {year}: Error - {e}\n")
            results[year] = 0

    print("\n=== SUMMARY ===")
    for year, count in results.items():
        print(f"{year}: {count} tournaments")


if __name__ == '__main__':
    main()
