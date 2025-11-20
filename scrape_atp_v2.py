"""
ATP Tour Player Activity Scraper v2
Uses JavaScript to extract data directly from the DOM
"""

from playwright.sync_api import sync_playwright
import json
import time


def scrape_player_activity(player_id: str, player_name: str):
    """
    Scrape player activity data from ATP Tour website using JavaScript

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
        time.sleep(15)

        # Scroll to load lazy content
        print("Scrolling to load all content...")
        for i in range(5):
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(2)

        # Extract data using JavaScript
        print("Extracting data...")
        data = page.evaluate("""() => {
            const tournaments = [];
            const tournamentDivs = document.querySelectorAll('div.tournament');

            tournamentDivs.forEach(tournamentDiv => {
                // Skip tournament-footer divs
                if (tournamentDiv.classList.contains('tournament-footer')) {
                    return;
                }

                // Get tournament header
                const header = tournamentDiv.querySelector('.tournament-header');
                if (!header) return;

                const tournamentName = header.querySelector('.tournament-title')?.textContent?.trim() || 'Unknown';
                const tournamentLocation = header.querySelector('.tournament-location')?.textContent?.trim() || '';
                const tournamentDate = header.querySelector('.tournament-date')?.textContent?.trim() || '';

                // Get matches
                const matches = [];
                const matchRows = tournamentDiv.querySelectorAll('.match-row, .accordion-item-content .match, [class*="match"]');

                matchRows.forEach(matchRow => {
                    const matchData = {
                        round: matchRow.querySelector('[class*="round"]')?.textContent?.trim() || '',
                        opponent: matchRow.querySelector('[class*="opponent"], [class*="player"]')?.textContent?.trim() || '',
                        rank: matchRow.querySelector('[class*="rank"]')?.textContent?.trim() || '',
                        score: matchRow.querySelector('[class*="score"]')?.textContent?.trim() || '',
                        result: matchRow.querySelector('[class*="result"]')?.textContent?.trim() || ''
                    };

                    // Only add if we have some data
                    if (matchData.opponent || matchData.score) {
                        matches.push(matchData);
                    }
                });

                tournaments.push({
                    name: tournamentName,
                    location: tournamentLocation,
                    date: tournamentDate,
                    matches: matches
                });
            });

            return tournaments;
        }""")

        print(f"Found {len(data)} tournaments")

        # Take screenshot
        page.screenshot(path="player_activity_v2.png", full_page=True)
        print("Screenshot saved")

        browser.close()

    return {
        'player_id': player_id,
        'player_name': player_name,
        'tournaments': data
    }


def main():
    # Scrape Novak Djokovic's data
    player_id = 'd643'
    player_name = 'novak-djokovic'

    print("Starting ATP Tour scraper v2...\n")

    try:
        data = scrape_player_activity(player_id, player_name)

        # Save to JSON
        output_file = f'{player_name}_activity_v2.json'
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
            print(f"  Name: {first_tournament.get('name', 'N/A')}")
            print(f"  Location: {first_tournament.get('location', 'N/A')}")
            print(f"  Date: {first_tournament.get('date', 'N/A')}")
            print(f"  Matches: {len(first_tournament.get('matches', []))}")

            if first_tournament.get('matches'):
                print(f"\n  First match:")
                first_match = first_tournament['matches'][0]
                for key, value in first_match.items():
                    if value:
                        print(f"    {key}: {value}")

    except Exception as e:
        print(f"[-] Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
