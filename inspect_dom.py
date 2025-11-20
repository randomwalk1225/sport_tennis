"""
Inspect the actual DOM structure in detail
"""

from playwright.sync_api import sync_playwright
import time
import json

url = "https://www.atptour.com/en/players/novak-djokovic/d643/player-activity"

with sync_playwright() as p:
    print("Launching browser...")
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    print(f"Navigating to {url}")
    page.goto(url, wait_until="load", timeout=60000)

    print("Waiting...")
    time.sleep(15)

    print("\nInspecting DOM structure...")

    # Get detailed structure
    result = page.evaluate("""() => {
        const tournaments = [];
        const tournamentDivs = document.querySelectorAll('div[class*="tournament"]');

        tournamentDivs.forEach((div, index) => {
            if (index < 2) {  // Only first 2 for inspection
                const info = {
                    index: index,
                    className: div.className,
                    id: div.id,
                    children: []
                };

                // Get first level children
                Array.from(div.children).forEach(child => {
                    info.children.push({
                        tagName: child.tagName,
                        className: child.className,
                        textContent: child.textContent.substring(0, 100)
                    });
                });

                tournaments.push(info);
            }
        });

        return {
            tournamentsFound: tournamentDivs.length,
            firstTwoTournaments: tournaments
        };
    }""")

    print(f"\nTournaments found: {result['tournamentsFound']}")
    print(f"\nDetailed structure of first 2 tournaments:")
    print(json.dumps(result['firstTwoTournaments'], indent=2))

    print("\n\nPress Enter to close...")
    input()

    browser.close()
