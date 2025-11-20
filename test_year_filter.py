"""
Test scraping different years
"""

from playwright.sync_api import sync_playwright
import time

player_id = 'd643'
player_name = 'novak-djokovic'

with sync_playwright() as p:
    print("Launching browser...")
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    # Try different URL patterns
    base_url = f"https://www.atptour.com/en/players/{player_name}/{player_id}/player-activity"

    print(f"\n1. Testing base URL...")
    page.goto(base_url, wait_until="load", timeout=60000)
    time.sleep(5)

    current_url = page.url
    print(f"Current URL: {current_url}")

    # Check for year filter options
    print("\n2. Looking for year filter options...")
    result = page.evaluate("""() => {
        // Find year selectors
        const yearElements = [];

        // Common patterns for year selectors
        const selectors = [
            'select[name*="year"]',
            'button[data-year]',
            'a[href*="year"]',
            '.year-filter',
            '[class*="year"]',
            'button:has-text("2024")',
            'button:has-text("2023")',
            'a:has-text("2024")',
            'a:has-text("2023")'
        ];

        for (const selector of selectors) {
            const elements = document.querySelectorAll(selector);
            if (elements.length > 0) {
                elements.forEach(el => {
                    yearElements.push({
                        selector: selector,
                        tagName: el.tagName,
                        text: el.textContent.substring(0, 50),
                        href: el.href || '',
                        className: el.className
                    });
                });
            }
        }

        return yearElements;
    }""")

    print(f"Found {len(result)} year-related elements:")
    for i, elem in enumerate(result[:10], 1):
        print(f"  {i}. {elem['tagName']} - {elem['text'][:30]} - {elem.get('href', '')[:50]}")

    # Try URL with year parameter
    print("\n3. Testing URL with year parameter...")
    test_urls = [
        f"{base_url}?year=2023",
        f"{base_url}?year=2022",
        f"{base_url}/2023",
        f"{base_url}/2022"
    ]

    for test_url in test_urls:
        print(f"\nTrying: {test_url}")
        page.goto(test_url, wait_until="load", timeout=60000)
        time.sleep(3)

        final_url = page.url
        print(f"Final URL: {final_url}")

        # Check if data loaded
        tournament_count = page.evaluate("""() => {
            return document.querySelectorAll('.tournament.tournament--expanded').length;
        }""")
        print(f"Tournaments found: {tournament_count}")

        if tournament_count > 0:
            print("✓ Success! This URL pattern works!")
            break

    print("\n\nPress Enter to close...")
    input()

    browser.close()
