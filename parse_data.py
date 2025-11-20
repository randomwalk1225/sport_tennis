"""
Parse the scraped data to extract match information
"""

import json
import re

# Load the scraped data
with open('novak-djokovic_activity.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

parsed_tournaments = []

for tournament in data['tournaments']:
    name_text = tournament['name']

    # Extract tournament name (first meaningful part)
    # Pattern: looks for location after "Header 2"
    tournament_match = re.search(r'Header 2(.+?)(?:Athens|Shanghai|US Open|Wimbledon|Roland Garros|Geneva|Madrid|Monte-Carlo|Miami|Indian Wells|Doha|Australian Open|Brisbane|ATP\s)', name_text)

    # Extract different parts
    parts = name_text.split('Accordion')
    if len(parts) >= 2:
        header_part = parts[0]
        data_part = parts[1]

        # Extract tournament name and location
        # Remove "Header 2" prefix
        header_clean = header_part.replace('Header 2', '').strip()

        # Split by the long tournament name/location pattern
        location_match = re.search(r'([A-Z][a-z\s]+)([A-Z][a-z\s,|]+\|[^A]+)', header_clean)

        tournament_name = "Unknown"
        tournament_location = "Unknown"

        if location_match:
            tournament_name = location_match.group(1).strip()
            tournament_location = location_match.group(2).strip()
        else:
            # Try simpler split
            parts_simple = header_clean.split(',')
            if parts_simple:
                tournament_name = parts_simple[0]

        # Parse matches from data_part
        # Pattern: Round + Opponent (Rank) + Score + Bye
        # Example: "FL. Musetti  (9) 466375Bye"
        matches = []

        # Remove "RdOpponentScore" header
        match_text = data_part.replace('RdOpponentScore', '')

        # Pattern: Round (like F, SF, QF, R16, R32, etc) + Player Name (Rank) + Score + Bye
        pattern = r'(F|SF|QF|R\d+|R128|R64|R32|R16)\s*([A-Z][^(]+?)\s+\((\d+)\)\s+([\d\s]+?)(?:Bye|$)'

        for match in re.finditer(pattern, match_text):
            round_name = match.group(1).strip()
            opponent = match.group(2).strip()
            rank = match.group(3).strip()
            score = match.group(4).strip()

            matches.append({
                'round': round_name,
                'opponent': opponent,
                'rank': rank,
                'score': score
            })

        parsed_tournaments.append({
            'name': tournament_name,
            'location': tournament_location,
            'matches': matches
        })

# Save parsed data
output_data = {
    'player_id': data['player_id'],
    'player_name': data['player_name'],
    'tournaments': parsed_tournaments
}

with open('novak-djokovic_activity_parsed.json', 'w', encoding='utf-8') as f:
    json.dump(output_data, f, indent=2, ensure_ascii=False)

# Print summary
print(f"Parsed {len(parsed_tournaments)} tournaments")
total_matches = sum(len(t['matches']) for t in parsed_tournaments)
print(f"Total matches extracted: {total_matches}")

print("\nFirst tournament:")
if parsed_tournaments:
    first = parsed_tournaments[0]
    print(f"  Name: {first['name']}")
    print(f"  Location: {first['location']}")
    print(f"  Matches: {len(first['matches'])}")

    if first['matches']:
        print("\n  First 3 matches:")
        for i, match in enumerate(first['matches'][:3], 1):
            print(f"    {i}. {match['round']}: vs {match['opponent']} ({match['rank']}) - {match['score']}")

print("\nData saved to 'novak-djokovic_activity_parsed.json'")
