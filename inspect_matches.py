"""
Inspect match structure in detail
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

    print("\nInspecting match structure...")

    # Get detailed match structure
    result = page.evaluate("""() => {
        const tournamentDivs = document.querySelectorAll('div.tournament.tournament--expanded');
        const firstTournament = tournamentDivs[0];

        if (!firstTournament) return null;

        const header = firstTournament.querySelector('.header');
        const content = firstTournament.querySelector('.content');

        const result = {
            headerText: header ? header.textContent : 'No header',
            contentChildren: []
        };

        if (content) {
            Array.from(content.children).forEach((child, index) => {
                const childInfo = {
                    index: index,
                    tagName: child.tagName,
                    className: child.className,
                    textContent: child.textContent.substring(0, 200),
                    childrenCount: child.children.length,
                    children: []
                };

                // Get grandchildren
                Array.from(child.children).forEach((grandchild, gIndex) => {
                    childInfo.children.push({
                        index: gIndex,
                        tagName: grandchild.tagName,
                        className: grandchild.className,
                        textContent: grandchild.textContent.substring(0, 100)
                    });
                });

                result.contentChildren.push(childInfo);
            });
        }

        return result;
    }""")

    print("\nFirst tournament structure:")
    print(json.dumps(result, indent=2, ensure_ascii=False))

    print("\n\nPress Enter to close...")
    input()

    browser.close()
