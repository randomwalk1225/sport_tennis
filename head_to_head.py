"""
Head-to-Head Match Prediction with Explanation
"""

import pandas as pd
import numpy as np
from data_manager import TennisDataManager
from match_predictor import MatchPredictor


class HeadToHeadPredictor:
    """Predict matches between real players with explanations"""

    def __init__(self):
        self.manager = TennisDataManager()
        self.predictor = MatchPredictor()
        self.predictor.load('models/tennis_predictor_best.pkl')

        # Load recent player data
        self.player_data = None
        self.load_player_database()

    def load_player_database_from_json(self):
        """Load player database from JSON file (for deployment)"""
        import json
        import os

        json_path = 'players_database.json'
        print(f"Checking for {json_path}...")
        print(f"Current directory: {os.getcwd()}")
        print(f"Files in directory: {os.listdir('.')[:10]}")  # Show first 10 files

        if os.path.exists(json_path):
            print(f"Loading player database from {json_path}...")
            try:
                with open(json_path, 'r') as f:
                    self.player_data = json.load(f)
                print(f"[+] Loaded {len(self.player_data)} players from JSON")
                return True
            except Exception as e:
                print(f"[-] Error loading JSON: {e}")
                return False
        else:
            print(f"[-] {json_path} not found")
            return False

    def load_player_database(self):
        """Load recent player data to get stats"""
        # Try loading from JSON first (for deployment)
        if self.load_player_database_from_json():
            return

        print("Loading player database from ATP data...")
        df = self.manager.load_matches('atp', years=[2024])

        if df is None:
            print("Failed to load data")
            print("HINT: For deployment, make sure players_database.json exists")
            return

        # Create player database with latest stats
        players = {}

        # Process winners
        for _, row in df.iterrows():
            player_name = row['winner_name']
            if pd.notna(player_name) and player_name not in players:
                players[player_name] = {
                    'name': player_name,
                    'rank': row.get('winner_rank', 999),
                    'age': row.get('winner_age', 25),
                    'height': row.get('winner_ht', 185),
                    'hand': row.get('winner_hand', 'R'),
                }

        # Process losers (to get more players)
        for _, row in df.iterrows():
            player_name = row['loser_name']
            if pd.notna(player_name) and player_name not in players:
                players[player_name] = {
                    'name': player_name,
                    'rank': row.get('loser_rank', 999),
                    'age': row.get('loser_age', 25),
                    'height': row.get('loser_ht', 185),
                    'hand': row.get('loser_hand', 'R'),
                }

        self.player_data = players
        print(f"[+] Loaded {len(players)} players")

    def get_player_info(self, player_name):
        """Get player information"""
        # Try exact match
        if player_name in self.player_data:
            return self.player_data[player_name]

        # Try partial match
        matches = [p for p in self.player_data.keys()
                   if player_name.lower() in p.lower()]

        if matches:
            return self.player_data[matches[0]]

        return None

    def predict_match(self, player1_name, player2_name,
                     surface='hard', is_grand_slam=False, is_masters=False):
        """
        Predict match between two players

        Returns:
            dict with prediction and explanation
        """
        # Get player info
        p1_info = self.get_player_info(player1_name)
        p2_info = self.get_player_info(player2_name)

        if p1_info is None:
            return f"Player '{player1_name}' not found in database"
        if p2_info is None:
            return f"Player '{player2_name}' not found in database"

        # Prepare features
        features = pd.DataFrame([{
            'p1_rank': p1_info['rank'],
            'p2_rank': p2_info['rank'],
            'rank_diff': p1_info['rank'] - p2_info['rank'],
            'p1_age': p1_info['age'],
            'p2_age': p2_info['age'],
            'age_diff': p1_info['age'] - p2_info['age'],
            'p1_ht': p1_info['height'],
            'p2_ht': p2_info['height'],
            'height_diff': p1_info['height'] - p2_info['height'],
            'is_hard': 1 if surface.lower() == 'hard' else 0,
            'is_clay': 1 if surface.lower() == 'clay' else 0,
            'is_grass': 1 if surface.lower() == 'grass' else 0,
            'is_grand_slam': 1 if is_grand_slam else 0,
            'is_masters': 1 if is_masters else 0,
        }])

        # Predict
        probabilities = self.predictor.predict_proba(features)[0]
        p1_win_prob = probabilities[1] * 100
        p2_win_prob = probabilities[0] * 100

        # Create explanation
        explanation = self._create_explanation(
            p1_info, p2_info, features.iloc[0], p1_win_prob, surface
        )

        return {
            'player1': p1_info,
            'player2': p2_info,
            'p1_win_prob': p1_win_prob,
            'p2_win_prob': p2_win_prob,
            'predicted_winner': p1_info['name'] if p1_win_prob > 50 else p2_info['name'],
            'surface': surface,
            'tournament_type': 'Grand Slam' if is_grand_slam else ('Masters 1000' if is_masters else 'Regular'),
            'explanation': explanation
        }

    def _create_explanation(self, p1, p2, features, p1_win_prob, surface):
        """Create detailed explanation of prediction"""
        explanation = []

        # Calculate p2 win probability
        p2_win_prob = 100 - p1_win_prob

        # Ranking analysis (most important feature - 76.7%)
        rank_diff = p1['rank'] - p2['rank']
        if rank_diff < -10:
            explanation.append(
                f"[+] Ranking Advantage: {p1['name']}이 {p2['name']}보다 {abs(rank_diff)}계단 높습니다 "
                f"(#{p1['rank']} vs #{p2['rank']}). 랭킹은 가장 중요한 요소입니다 (중요도 76.7%)."
            )
        elif rank_diff > 10:
            explanation.append(
                f"[-] Ranking Disadvantage: {p2['name']}이 {p1['name']}보다 {abs(rank_diff)}계단 높습니다 "
                f"(#{p2['rank']} vs #{p1['rank']}). 랭킹은 가장 중요한 요소입니다 (중요도 76.7%)."
            )
        else:
            explanation.append(
                f"[=] Similar Ranking: 두 선수의 랭킹 차이가 작습니다 "
                f"(#{p1['rank']} vs #{p2['rank']}). 접전이 예상됩니다."
            )

        # Age analysis (important feature - 4.1%)
        age_diff = p1['age'] - p2['age']
        if abs(age_diff) > 5:
            if age_diff > 0:
                explanation.append(
                    f"[AGE] Age Difference: {p1['name']}이 {abs(age_diff):.1f}살 더 많습니다 "
                    f"({p1['age']:.1f}세 vs {p2['age']:.1f}세). 젊은 선수가 유리할 수 있습니다."
                )
            else:
                explanation.append(
                    f"[AGE] Age Difference: {p2['name']}이 {abs(age_diff):.1f}살 더 많습니다 "
                    f"({p2['age']:.1f}세 vs {p1['age']:.1f}세). 젊은 선수가 유리할 수 있습니다."
                )

        # Height analysis (small impact - 0.8%)
        height_diff = p1['height'] - p2['height']
        if abs(height_diff) > 5:
            taller = p1['name'] if height_diff > 0 else p2['name']
            explanation.append(
                f"[HT] Height Difference: {taller}가 {abs(height_diff):.0f}cm 더 큽니다 "
                f"({p1['height']:.0f}cm vs {p2['height']:.0f}cm). 키가 큰 선수는 서브에서 유리합니다."
            )

        # Surface
        explanation.append(
            f"[COURT] Surface: {surface.upper()} 코트 (서피스는 작은 영향 ~1%)"
        )

        # Win probability interpretation
        if abs(p1_win_prob - 50) < 5:
            explanation.append(
                f"[*] CONCLUSION: 거의 호각입니다! 두 선수 모두 승리 가능성이 높습니다."
            )
        elif p1_win_prob > 70:
            explanation.append(
                f"[*] CONCLUSION: {p1['name']}의 압도적인 우세가 예상됩니다."
            )
        elif p2_win_prob > 70:
            explanation.append(
                f"[*] CONCLUSION: {p2['name']}의 압도적인 우세가 예상됩니다."
            )
        else:
            winner = p1['name'] if p1_win_prob > 50 else p2['name']
            explanation.append(
                f"[*] CONCLUSION: {winner}가 근소하게 우세하지만, 상대도 충분히 승산이 있습니다."
            )

        return explanation

    def print_prediction(self, result):
        """Pretty print prediction results"""
        if isinstance(result, str):
            print(result)
            return

        print("\n" + "="*70)
        print(f"      {result['player1']['name']} vs {result['player2']['name']}")
        print("="*70)

        print(f"\n[MATCH INFO]")
        print(f"  Court: {result['surface'].upper()}")
        print(f"  Tournament: {result['tournament_type']}")

        print(f"\n[PLAYER 1] {result['player1']['name']}")
        print(f"  Ranking: #{result['player1']['rank']}")
        print(f"  Age: {result['player1']['age']:.1f}")
        print(f"  Height: {result['player1']['height']:.0f}cm")
        print(f"  Hand: {result['player1']['hand']}")

        print(f"\n[PLAYER 2] {result['player2']['name']}")
        print(f"  Ranking: #{result['player2']['rank']}")
        print(f"  Age: {result['player2']['age']:.1f}")
        print(f"  Height: {result['player2']['height']:.0f}cm")
        print(f"  Hand: {result['player2']['hand']}")

        print(f"\n[WIN PROBABILITY]")
        print(f"  {result['player1']['name']}: {result['p1_win_prob']:.2f}%")
        print(f"  {result['player2']['name']}: {result['p2_win_prob']:.2f}%")

        print(f"\n[PREDICTED WINNER] {result['predicted_winner']}")

        print(f"\n[ANALYSIS]")
        for i, exp in enumerate(result['explanation'], 1):
            print(f"  {i}. {exp}")

        print("\n" + "="*70)


def main():
    """Demo predictions"""
    predictor = HeadToHeadPredictor()

    # Example 1: Djokovic vs Alcaraz
    print("\n" + "="*70)
    result = predictor.predict_match(
        'Djokovic', 'Alcaraz',
        surface='hard',
        is_grand_slam=True
    )
    predictor.print_prediction(result)

    # Example 2: Sinner vs Medvedev
    print("\n" + "="*70)
    result = predictor.predict_match(
        'Sinner', 'Medvedev',
        surface='hard',
        is_masters=True
    )
    predictor.print_prediction(result)

    # Example 3: Djokovic vs Sinner on clay
    print("\n" + "="*70)
    result = predictor.predict_match(
        'Djokovic', 'Sinner',
        surface='clay',
        is_grand_slam=True
    )
    predictor.print_prediction(result)


if __name__ == '__main__':
    main()
