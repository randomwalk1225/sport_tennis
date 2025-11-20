"""
Example: Predict match outcome probabilities
"""

import pandas as pd
import numpy as np
from match_predictor import MatchPredictor


def predict_match(p1_rank, p2_rank, p1_age=25, p2_age=25,
                  p1_ht=185, p2_ht=185, surface='hard',
                  is_grand_slam=False, is_masters=False):
    """
    Predict match outcome

    Args:
        p1_rank: Player 1 ranking
        p2_rank: Player 2 ranking
        p1_age: Player 1 age
        p2_age: Player 2 age
        p1_ht: Player 1 height (cm)
        p2_ht: Player 2 height (cm)
        surface: 'hard', 'clay', or 'grass'
        is_grand_slam: Grand Slam tournament
        is_masters: Masters 1000 tournament

    Returns:
        dict with predictions
    """
    # Load trained model
    predictor = MatchPredictor()
    predictor.load('models/tennis_predictor_best.pkl')

    # Prepare features
    features = pd.DataFrame([{
        'p1_rank': p1_rank,
        'p2_rank': p2_rank,
        'rank_diff': p1_rank - p2_rank,
        'p1_age': p1_age,
        'p2_age': p2_age,
        'age_diff': p1_age - p2_age,
        'p1_ht': p1_ht,
        'p2_ht': p2_ht,
        'height_diff': p1_ht - p2_ht,
        'is_hard': 1 if surface.lower() == 'hard' else 0,
        'is_clay': 1 if surface.lower() == 'clay' else 0,
        'is_grass': 1 if surface.lower() == 'grass' else 0,
        'is_grand_slam': 1 if is_grand_slam else 0,
        'is_masters': 1 if is_masters else 0,
    }])

    # Predict
    prediction = predictor.predict(features)[0]
    probabilities = predictor.predict_proba(features)[0]

    result = {
        'player1_win_prob': probabilities[1] * 100,
        'player2_win_prob': probabilities[0] * 100,
        'predicted_winner': 'Player 1' if prediction == 1 else 'Player 2'
    }

    return result, features


def main():
    print("="*60)
    print("Tennis Match Win Probability Calculator")
    print("="*60)

    # Example 1: Top seed vs Lower seed
    print("\n" + "="*60)
    print("Example 1: Djokovic (Rank 1) vs Alcaraz (Rank 2)")
    print("Surface: Hard Court, Grand Slam")
    print("="*60)

    result, features = predict_match(
        p1_rank=1, p2_rank=2,
        p1_age=37, p2_age=21,
        p1_ht=188, p2_ht=183,
        surface='hard',
        is_grand_slam=True
    )

    print(f"\nPlayer 1 (Djokovic, Rank 1):")
    print(f"  Win Probability: {result['player1_win_prob']:.2f}%")
    print(f"\nPlayer 2 (Alcaraz, Rank 2):")
    print(f"  Win Probability: {result['player2_win_prob']:.2f}%")
    print(f"\nPredicted Winner: {result['predicted_winner']}")

    # Example 2: Big ranking difference
    print("\n" + "="*60)
    print("Example 2: Top 10 (Rank 5) vs Outsider (Rank 50)")
    print("Surface: Clay Court, Masters 1000")
    print("="*60)

    result, features = predict_match(
        p1_rank=5, p2_rank=50,
        p1_age=28, p2_age=26,
        p1_ht=185, p2_ht=180,
        surface='clay',
        is_masters=True
    )

    print(f"\nPlayer 1 (Rank 5):")
    print(f"  Win Probability: {result['player1_win_prob']:.2f}%")
    print(f"\nPlayer 2 (Rank 50):")
    print(f"  Win Probability: {result['player2_win_prob']:.2f}%")
    print(f"\nPredicted Winner: {result['predicted_winner']}")

    # Example 3: Close match
    print("\n" + "="*60)
    print("Example 3: Close Match (Rank 10 vs Rank 12)")
    print("Surface: Grass Court")
    print("="*60)

    result, features = predict_match(
        p1_rank=10, p2_rank=12,
        p1_age=25, p2_age=24,
        p1_ht=183, p2_ht=185,
        surface='grass'
    )

    print(f"\nPlayer 1 (Rank 10):")
    print(f"  Win Probability: {result['player1_win_prob']:.2f}%")
    print(f"\nPlayer 2 (Rank 12):")
    print(f"  Win Probability: {result['player2_win_prob']:.2f}%")
    print(f"\nPredicted Winner: {result['predicted_winner']}")

    # Example 4: Underdog scenario
    print("\n" + "="*60)
    print("Example 4: Huge Upset Potential (Rank 1 vs Rank 100)")
    print("Surface: Hard Court")
    print("="*60)

    result, features = predict_match(
        p1_rank=1, p2_rank=100,
        p1_age=30, p2_age=22,
        p1_ht=188, p2_ht=175,
        surface='hard'
    )

    print(f"\nPlayer 1 (Rank 1):")
    print(f"  Win Probability: {result['player1_win_prob']:.2f}%")
    print(f"\nPlayer 2 (Rank 100):")
    print(f"  Win Probability: {result['player2_win_prob']:.2f}%")
    print(f"\nPredicted Winner: {result['predicted_winner']}")

    # Example 5: Surface comparison
    print("\n" + "="*60)
    print("Example 5: Same Matchup, Different Surfaces")
    print("Rank 3 vs Rank 8")
    print("="*60)

    for surface in ['hard', 'clay', 'grass']:
        result, _ = predict_match(
            p1_rank=3, p2_rank=8,
            p1_age=27, p2_age=26,
            surface=surface
        )
        print(f"\n{surface.capitalize()} Court:")
        print(f"  Player 1 Win Prob: {result['player1_win_prob']:.2f}%")
        print(f"  Player 2 Win Prob: {result['player2_win_prob']:.2f}%")


if __name__ == '__main__':
    main()
