"""
Train model with extended data (2000-2024)
"""

from data_manager import TennisDataManager
from data_preprocessor import TennisDataPreprocessor
from match_predictor import MatchPredictor
import pandas as pd
from pathlib import Path


def main():
    print("="*70)
    print("Extended Tennis Match Prediction Training (2000-2024)")
    print("="*70)

    # Load and prepare data
    manager = TennisDataManager()
    preprocessor = TennisDataPreprocessor()

    print("\nStep 1: Loading extended data (2000-2024)...")
    years = list(range(2000, 2025))  # 2000-2024
    df = manager.load_matches('atp', years=years)

    if df is None:
        print("Failed to load data")
        return

    print(f"[+] Loaded {len(df)} matches from {len(years)} years")

    # Prepare for ML
    print("\nStep 2: Preprocessing...")
    X, y = preprocessor.prepare_for_ml(df)

    print(f"\n[+] Training samples: {len(X)}")
    print(f"[+] Original matches: {len(df)}")
    print(f"[+] Expansion ratio: {len(X) / len(df):.1f}x")

    # Train Gradient Boosting (best from previous test)
    print("\n" + "="*70)
    print("Step 3: Training Gradient Boosting Model")
    print("="*70)

    predictor = MatchPredictor(model_type='gradient_boosting')
    metrics = predictor.train(X, y, test_size=0.2)

    # Save model
    model_path = 'models/tennis_predictor_2000_2024.pkl'
    Path('models').mkdir(exist_ok=True)
    predictor.save(model_path)

    print("\n" + "="*70)
    print("Training Summary")
    print("="*70)
    print(f"Data period: 2000-2024 (25 years)")
    print(f"Total matches: {len(df):,}")
    print(f"Training samples: {len(X):,}")
    print(f"Train accuracy: {metrics['train_accuracy']:.4f}")
    print(f"Test accuracy: {metrics['test_accuracy']:.4f}")
    print(f"CV mean: {metrics['cv_mean']:.4f} (+/- {metrics['cv_std']:.4f})")
    print(f"\nModel saved: {model_path}")

    # Compare with old model
    print("\n" + "="*70)
    print("Comparison with Previous Model")
    print("="*70)
    print("Old model (2022-2024):")
    print("  - Matches: ~93,203")
    print("  - Test accuracy: 66.55%")
    print(f"\nNew model (2000-2024):")
    print(f"  - Matches: {len(df):,}")
    print(f"  - Test accuracy: {metrics['test_accuracy']*100:.2f}%")

    improvement = (metrics['test_accuracy'] - 0.6655) * 100
    if improvement > 0:
        print(f"  - Improvement: +{improvement:.2f}%")
    else:
        print(f"  - Change: {improvement:.2f}%")


if __name__ == '__main__':
    main()
