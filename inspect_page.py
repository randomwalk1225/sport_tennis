"""
Quick script to inspect the actual DOM structure of the page
"""

from playwright.sync_api import sync_playwright
import time

url = "https://www.atptour.com/en/players/novak-djokovic/d643/player-activity"

with sync_playwright() as p:
    print("Launching browser...")
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    print(f"Navigating to {url}")
    page.goto(url, wait_until="load", timeout=60000)

    print("Waiting for page to stabilize...")
    time.sleep(15)

    print("\nInspecting page structure...")

    # Use JavaScript to inspect the page
    result = page.evaluate("""() => {
        // Find all divs with class containing 'activity' or 'match' or 'tournament'
        const allDivs = document.querySelectorAll('div');
        const activityDivs = [];

        allDivs.forEach(div => {
            if (div.className && (
                div.className.includes('activity') ||
                div.className.includes('match') ||
                div.className.includes('tournament') ||
                div.className.includes('result')
            )) {
                activityDivs.push({
                    className: div.className,
                    id: div.id,
                    textPreview: div.innerText.substring(0, 100)
                });
            }
        });

        return {
            activityDivsCount: activityDivs.length,
            activityDivs: activityDivs.slice(0, 10),  // First 10
            allTablesCount: document.querySelectorAll('table').length,
            bodyText: document.body.innerText.substring(0, 500)
        };
    }""")

    print(f"\nResults:")
    print(f"- Activity/Match/Tournament divs found: {result['activityDivsCount']}")
    print(f"- Tables found: {result['allTablesCount']}")
    print(f"\nFirst 10 relevant divs:")
    for i, div in enumerate(result['activityDivs'], 1):
        print(f"\n{i}. Class: {div['className']}")
        print(f"   ID: {div['id']}")
        print(f"   Text preview: {div['textPreview'][:50]}...")

    print(f"\nBody text preview:")
    print(result['bodyText'])

    print("\n\nPress Enter to close browser...")
    input()

    browser.close()
