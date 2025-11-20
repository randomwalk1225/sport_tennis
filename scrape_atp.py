"""
ATP Tour Player Activity Scraper
Scrapes match data from ATP Tour website for a given player
"""

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json
import time


def scrape_player_activity(player_id: str, player_name: str):
    """
    Scrape player activity data from ATP Tour website

    Args:
        player_id: ATP player ID (e.g., 'd643' for Djokovic)
        player_name: Player name for the URL slug (e.g., 'novak-djokovic')

    Returns:
        Dictionary containing tournament and match data
    """
    url = f"https://www.atptour.com/en/players/{player_name}/{player_id}/player-activity"

    with sync_playwright() as p:
        print(f"Launching browser...")
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        print(f"Navigating to {url}")
        page.goto(url, wait_until="load", timeout=60000)

        # Wait for tournaments to load
        print("Waiting for tournament data to load...")
        time.sleep(15)  # Give JavaScript time to populate DOM

        # Scroll to load lazy content
        print("Scrolling to load all content...")
        for i in range(5):
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(2)

        # Get page content
        html = page.content()

        # Save HTML for debugging
        with open("page_source.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("HTML saved to page_source.html")

        # Take a screenshot for debugging
        page.screenshot(path="player_activity.png", full_page=True)
        print("Screenshot saved as player_activity.png")

        browser.close()

    # Parse HTML with BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')

    # Extract data
    tournaments = []

    # Find all tournament sections (divs with class 'tournament')
    tournament_divs = soup.find_all('div', class_=lambda x: x and 'tournament' in x and 'tournament-footer' not in x)

    print(f"\nFound {len(tournament_divs)} tournament sections")

    for tournament_div in tournament_divs:
        # Extract tournament name and info from the div text
        tournament_text = tournament_div.get_text(strip=False)
        lines = [line.strip() for line in tournament_text.split('\n') if line.strip()]

        # First line is usually the tournament name
        tournament_name = lines[0] if lines else "Unknown"

        # Second line usually contains location and dates
        tournament_info = lines[1] if len(lines) > 1 else "Unknown"

        # Extract matches - look for match rows within the tournament
        matches = []

        # Find all rows in this tournament (divs or other elements containing match data)
        # We'll look for elements that contain "R", "QF", "SF", "F" (round indicators)
        match_elements = tournament_div.find_all(['div', 'li', 'tr'])

        for elem in match_elements:
            elem_text = elem.get_text(strip=True)

            # Skip if too short or is the header
            if len(elem_text) < 5 or elem_text == tournament_name:
                continue

            # Try to parse match data
            # Pattern: Round | Opponent | Result | Score
            parts = [p.strip() for p in elem_text.split('\n') if p.strip()]

            if len(parts) >= 3:
                # This might be a match row
                match_data = {
                    'round': parts[0] if len(parts) > 0 else '',
                    'opponent': parts[1] if len(parts) > 1 else '',
                    'result': parts[2] if len(parts) > 2 else '',
                    'score': parts[3] if len(parts) > 3 else ''
                }

                # Only add if it looks like a valid match
                if match_data['round'] and match_data['opponent']:
                    matches.append(match_data)

        tournament_data = {
            'name': tournament_name,
            'info': tournament_info,
            'matches': matches
        }

        tournaments.append(tournament_data)

    return {
        'player_id': player_id,
        'player_name': player_name,
        'tournaments': tournaments
    }


def main():
    # Scrape Novak Djokovic's data
    player_id = 'd643'
    player_name = 'novak-djokovic'

    print("Starting ATP Tour scraper...\n")

    try:
        data = scrape_player_activity(player_id, player_name)

        # Save to JSON
        output_file = f'{player_name}_activity.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"\n[+] Data saved to {output_file}")
        print(f"[+] Found {len(data['tournaments'])} tournaments")

        # Print summary
        total_matches = sum(len(t['matches']) for t in data['tournaments'])
        print(f"[+] Total matches: {total_matches}")

        # Print first tournament as sample
        if data['tournaments']:
            print(f"\nSample - First tournament:")
            first_tournament = data['tournaments'][0]
            print(f"  Name: {first_tournament['name']}")
            print(f"  Location: {first_tournament['location']}")
            print(f"  Dates: {first_tournament['dates']}")
            print(f"  Matches: {len(first_tournament['matches'])}")

            if first_tournament['matches']:
                print(f"\n  First match:")
                first_match = first_tournament['matches'][0]
                for key, value in first_match.items():
                    print(f"    {key}: {value}")

    except Exception as e:
        print(f"[-] Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
