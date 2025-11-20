"""
Tennis Data Preprocessor
Cleans and prepares tennis match data for machine learning
"""

import pandas as pd
import numpy as np
from datetime import datetime


class TennisDataPreprocessor:
    """Preprocess tennis match data for analysis and ML"""

    def __init__(self):
        self.feature_columns = []

    def clean_matches(self, df):
        """Clean and standardize match data"""
        print(f"Cleaning {len(df)} matches...")

        # Create a copy
        df = df.copy()

        # Convert date to datetime
        if 'tourney_date' in df.columns:
            df['tourney_date'] = pd.to_datetime(df['tourney_date'], format='%Y%m%d', errors='coerce')
            df['year'] = df['tourney_date'].dt.year
            df['month'] = df['tourney_date'].dt.month

        # Clean surface
        if 'surface' in df.columns:
            df['surface'] = df['surface'].fillna('Unknown').str.strip()

        # Fill missing ranks with high number
        for col in ['winner_rank', 'loser_rank']:
            if col in df.columns:
                df[col] = df[col].fillna(9999).astype(int)

        # Fill missing heights
        for col in ['winner_ht', 'loser_ht']:
            if col in df.columns:
                median_ht = df[col].median()
                df[col] = df[col].fillna(median_ht)

        # Fill missing ages
        for col in ['winner_age', 'loser_age']:
            if col in df.columns:
                median_age = df[col].median()
                df[col] = df[col].fillna(median_age)

        # Clean hand (R/L/U)
        for col in ['winner_hand', 'loser_hand']:
            if col in df.columns:
                df[col] = df[col].fillna('U').str.strip()

        print(f"[+] Cleaned data shape: {df.shape}")
        return df

    def create_player_features(self, df):
        """Create player-specific features"""
        print("Creating player features...")

        df = df.copy()

        # Rank difference
        if 'winner_rank' in df.columns and 'loser_rank' in df.columns:
            df['rank_diff'] = df['winner_rank'] - df['loser_rank']

        # Age difference
        if 'winner_age' in df.columns and 'loser_age' in df.columns:
            df['age_diff'] = df['winner_age'] - df['loser_age']

        # Height difference (cm)
        if 'winner_ht' in df.columns and 'loser_ht' in df.columns:
            df['height_diff'] = df['winner_ht'] - df['loser_ht']

        # Hand matchup (same hand = 1, different = 0)
        if 'winner_hand' in df.columns and 'loser_hand' in df.columns:
            df['same_hand'] = (df['winner_hand'] == df['loser_hand']).astype(int)

        print(f"[+] Added player features")
        return df

    def create_match_features(self, df):
        """Create match-context features"""
        print("Creating match features...")

        df = df.copy()

        # Surface encoding
        if 'surface' in df.columns:
            df['is_hard'] = (df['surface'] == 'Hard').astype(int)
            df['is_clay'] = (df['surface'] == 'Clay').astype(int)
            df['is_grass'] = (df['surface'] == 'Grass').astype(int)
            df['is_carpet'] = (df['surface'] == 'Carpet').astype(int)

        # Tournament level encoding
        if 'tourney_level' in df.columns:
            df['is_grand_slam'] = (df['tourney_level'] == 'G').astype(int)
            df['is_masters'] = (df['tourney_level'] == 'M').astype(int)
            df['is_atp500'] = (df['tourney_level'] == 'A').astype(int)

        # Round encoding (higher number = later round)
        if 'round' in df.columns:
            round_mapping = {
                'F': 7, 'SF': 6, 'QF': 5, 'R16': 4,
                'R32': 3, 'R64': 2, 'R128': 1, 'RR': 3
            }
            df['round_num'] = df['round'].map(round_mapping).fillna(0).astype(int)

        print(f"[+] Added match features")
        return df

    def create_serve_features(self, df):
        """Create serving statistics features"""
        print("Creating serve features...")

        df = df.copy()

        # Winner serve statistics
        if 'w_1stIn' in df.columns and 'w_svpt' in df.columns:
            df['w_1st_serve_pct'] = (df['w_1stIn'] / df['w_svpt'].replace(0, np.nan)) * 100
            df['w_1st_serve_pct'] = df['w_1st_serve_pct'].fillna(0)

        if 'w_1stWon' in df.columns and 'w_1stIn' in df.columns:
            df['w_1st_win_pct'] = (df['w_1stWon'] / df['w_1stIn'].replace(0, np.nan)) * 100
            df['w_1st_win_pct'] = df['w_1st_win_pct'].fillna(0)

        if 'w_2ndWon' in df.columns and 'w_svpt' in df.columns and 'w_1stIn' in df.columns:
            df['w_2nd_win_pct'] = (df['w_2ndWon'] / (df['w_svpt'] - df['w_1stIn']).replace(0, np.nan)) * 100
            df['w_2nd_win_pct'] = df['w_2nd_win_pct'].fillna(0)

        # Loser serve statistics
        if 'l_1stIn' in df.columns and 'l_svpt' in df.columns:
            df['l_1st_serve_pct'] = (df['l_1stIn'] / df['l_svpt'].replace(0, np.nan)) * 100
            df['l_1st_serve_pct'] = df['l_1st_serve_pct'].fillna(0)

        if 'l_1stWon' in df.columns and 'l_1stIn' in df.columns:
            df['l_1st_win_pct'] = (df['l_1stWon'] / df['l_1stIn'].replace(0, np.nan)) * 100
            df['l_1st_win_pct'] = df['l_1st_win_pct'].fillna(0)

        # Ace and DF rates
        if 'w_ace' in df.columns and 'w_svpt' in df.columns:
            df['w_ace_rate'] = (df['w_ace'] / df['w_svpt'].replace(0, np.nan)) * 100
            df['w_ace_rate'] = df['w_ace_rate'].fillna(0)

        if 'w_df' in df.columns and 'w_svpt' in df.columns:
            df['w_df_rate'] = (df['w_df'] / df['w_svpt'].replace(0, np.nan)) * 100
            df['w_df_rate'] = df['w_df_rate'].fillna(0)

        print(f"[+] Added serve features")
        return df

    def prepare_for_ml(self, df, target='winner'):
        """
        Prepare data for machine learning
        Creates balanced dataset by duplicating matches with swapped players

        Args:
            df: DataFrame with match data
            target: 'winner' creates binary classification (1=player1 wins)

        Returns:
            X: features DataFrame
            y: target Series
        """
        print("Preparing data for machine learning...")

        # Apply all preprocessing
        df = self.clean_matches(df)
        df = self.create_player_features(df)
        df = self.create_match_features(df)
        df = self.create_serve_features(df)

        # Create two samples per match (player1 wins, player1 loses)
        # Use vectorized operations instead of slow iterrows()

        # Sample 1: player1 = winner (label = 1)
        X1 = pd.DataFrame({
            'p1_rank': df['winner_rank'].fillna(9999),
            'p2_rank': df['loser_rank'].fillna(9999),
            'rank_diff': df['rank_diff'].fillna(0),
            'p1_age': df['winner_age'].fillna(25),
            'p2_age': df['loser_age'].fillna(25),
            'age_diff': df['age_diff'].fillna(0),
            'p1_ht': df['winner_ht'].fillna(180),
            'p2_ht': df['loser_ht'].fillna(180),
            'height_diff': df['height_diff'].fillna(0),
            'is_hard': df['is_hard'].fillna(0),
            'is_clay': df['is_clay'].fillna(0),
            'is_grass': df['is_grass'].fillna(0),
            'is_grand_slam': df['is_grand_slam'].fillna(0),
            'is_masters': df['is_masters'].fillna(0),
        })
        y1 = pd.Series([1] * len(df), name='target')

        # Sample 2: player1 = loser (label = 0)
        X2 = pd.DataFrame({
            'p1_rank': df['loser_rank'].fillna(9999),
            'p2_rank': df['winner_rank'].fillna(9999),
            'rank_diff': -df['rank_diff'].fillna(0),
            'p1_age': df['loser_age'].fillna(25),
            'p2_age': df['winner_age'].fillna(25),
            'age_diff': -df['age_diff'].fillna(0),
            'p1_ht': df['loser_ht'].fillna(180),
            'p2_ht': df['winner_ht'].fillna(180),
            'height_diff': -df['height_diff'].fillna(0),
            'is_hard': df['is_hard'].fillna(0),
            'is_clay': df['is_clay'].fillna(0),
            'is_grass': df['is_grass'].fillna(0),
            'is_grand_slam': df['is_grand_slam'].fillna(0),
            'is_masters': df['is_masters'].fillna(0),
        })
        y2 = pd.Series([0] * len(df), name='target')

        # Combine both samples
        X = pd.concat([X1, X2], ignore_index=True)
        y = pd.concat([y1, y2], ignore_index=True)

        # Fill NaN
        X = X.fillna(X.median())

        self.feature_columns = list(X.columns)

        print(f"[+] Features: {len(self.feature_columns)}")
        print(f"[+] Samples: {len(X)} (from {len(df)} matches)")
        print(f"[+] Class distribution: {y.value_counts().to_dict()}")
        print(f"[+] Feature list: {self.feature_columns}")

        return X, y

    def get_player_stats(self, df, player_name, recent_n=10):
        """Get recent statistics for a specific player"""
        player_matches = df[
            (df['winner_name'].str.contains(player_name, case=False, na=False)) |
            (df['loser_name'].str.contains(player_name, case=False, na=False))
        ].sort_values('tourney_date', ascending=False).head(recent_n)

        if len(player_matches) == 0:
            return None

        # Calculate win rate
        wins = (player_matches['winner_name'].str.contains(player_name, case=False, na=False)).sum()
        win_rate = wins / len(player_matches) * 100

        stats = {
            'matches': len(player_matches),
            'wins': wins,
            'losses': len(player_matches) - wins,
            'win_rate': win_rate,
            'surfaces': player_matches['surface'].value_counts().to_dict(),
            'recent_tournaments': player_matches['tourney_name'].head(5).tolist()
        }

        return stats


def demo():
    """Demo preprocessing"""
    from data_manager import TennisDataManager

    manager = TennisDataManager()
    preprocessor = TennisDataPreprocessor()

    # Load recent ATP data
    print("Loading ATP 2023-2024 data...")
    df = manager.load_matches('atp', years=[2023, 2024])

    if df is not None:
        # Prepare for ML
        X, y = preprocessor.prepare_for_ml(df)

        print(f"\n{'='*50}")
        print("Prepared ML Dataset")
        print(f"{'='*50}")
        print(f"\nFeatures shape: {X.shape}")
        print(f"Target shape: {y.shape}")

        print(f"\nSample features:")
        print(X.head())

        # Get Djokovic stats
        print(f"\n{'='*50}")
        print("Player Stats Example: Djokovic")
        print(f"{'='*50}")
        stats = preprocessor.get_player_stats(df, 'Djokovic', recent_n=20)
        if stats:
            for key, value in stats.items():
                if key != 'recent_tournaments':
                    print(f"{key}: {value}")


if __name__ == '__main__':
    demo()
