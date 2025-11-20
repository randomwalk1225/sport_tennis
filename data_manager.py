"""
Tennis Data Manager
Automatically downloads and updates tennis data from Jeff Sackmann's repositories
"""

import os
import subprocess
import pandas as pd
from pathlib import Path
from datetime import datetime


class TennisDataManager:
    """Manage tennis data from multiple sources"""

    def __init__(self, base_dir="C:/Users/rando/repos/sportstat"):
        self.base_dir = Path(base_dir)
        self.repos = {
            'atp': {
                'url': 'https://github.com/JeffSackmann/tennis_atp.git',
                'dir': self.base_dir / 'tennis_atp',
                'pattern': 'atp_matches_*.csv'
            },
            'wta': {
                'url': 'https://github.com/JeffSackmann/tennis_wta.git',
                'dir': self.base_dir / 'tennis_wta',
                'pattern': 'wta_matches_*.csv'
            },
            'charting': {
                'url': 'https://github.com/JeffSackmann/tennis_MatchChartingProject.git',
                'dir': self.base_dir / 'tennis_MatchChartingProject',
                'pattern': 'charting-*.csv'
            }
        }

    def clone_or_update(self, repo_name):
        """Clone repository if not exists, otherwise pull latest"""
        repo_info = self.repos[repo_name]
        repo_dir = repo_info['dir']

        if repo_dir.exists():
            print(f"Updating {repo_name} repository...")
            try:
                result = subprocess.run(
                    ['git', 'pull'],
                    cwd=repo_dir,
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                if result.returncode == 0:
                    print(f"[+] {repo_name} updated successfully")
                    return True
                else:
                    print(f"[-] Error updating {repo_name}: {result.stderr}")
                    return False
            except Exception as e:
                print(f"[-] Error: {e}")
                return False
        else:
            print(f"Cloning {repo_name} repository...")
            try:
                result = subprocess.run(
                    ['git', 'clone', repo_info['url'], str(repo_dir)],
                    capture_output=True,
                    text=True,
                    timeout=180
                )
                if result.returncode == 0:
                    print(f"[+] {repo_name} cloned successfully")
                    return True
                else:
                    print(f"[-] Error cloning {repo_name}: {result.stderr}")
                    return False
            except Exception as e:
                print(f"[-] Error: {e}")
                return False

    def update_all(self):
        """Update all repositories"""
        print("=== Updating All Tennis Data ===\n")
        results = {}
        for repo_name in self.repos.keys():
            results[repo_name] = self.clone_or_update(repo_name)
            print()
        return results

    def list_data_files(self, repo_name, year=None):
        """List available data files"""
        repo_info = self.repos[repo_name]
        repo_dir = repo_info['dir']

        if not repo_dir.exists():
            print(f"Repository {repo_name} not found. Run update_all() first.")
            return []

        pattern = repo_info['pattern']
        files = sorted(repo_dir.glob(pattern))

        if year:
            files = [f for f in files if str(year) in f.name]

        return files

    def load_matches(self, repo_name, years=None):
        """
        Load match data for specified years

        Args:
            repo_name: 'atp' or 'wta'
            years: list of years or None for all years

        Returns:
            pandas DataFrame with all matches
        """
        files = self.list_data_files(repo_name)

        if years:
            files = [f for f in files if any(str(y) in f.name for y in years)]

        if not files:
            print(f"No files found for {repo_name}")
            return None

        print(f"Loading {len(files)} files from {repo_name}...")

        dfs = []
        for file in files:
            try:
                df = pd.read_csv(file, encoding='utf-8', low_memory=False)
                df['source_file'] = file.name
                dfs.append(df)
            except Exception as e:
                print(f"Error loading {file.name}: {e}")

        if dfs:
            combined = pd.concat(dfs, ignore_index=True)
            print(f"[+] Loaded {len(combined)} matches")
            return combined
        else:
            return None

    def get_player_matches(self, player_name, repo_name='atp', years=None):
        """Get all matches for a specific player"""
        df = self.load_matches(repo_name, years)

        if df is None:
            return None

        # Filter for player in either winner or loser column
        player_matches = df[
            (df['winner_name'].str.contains(player_name, case=False, na=False)) |
            (df['loser_name'].str.contains(player_name, case=False, na=False))
        ]

        print(f"[+] Found {len(player_matches)} matches for {player_name}")
        return player_matches

    def get_data_summary(self):
        """Get summary of available data"""
        summary = {}

        for repo_name in ['atp', 'wta']:
            files = self.list_data_files(repo_name)
            if files:
                years = sorted([int(f.stem.split('_')[-1]) for f in files if f.stem.split('_')[-1].isdigit()])
                summary[repo_name] = {
                    'files': len(files),
                    'years': f"{min(years)}-{max(years)}" if years else "N/A",
                    'total_years': len(years)
                }

        # Charting data
        charting_files = self.list_data_files('charting')
        summary['charting'] = {
            'files': len(charting_files),
            'types': len(set(f.stem.split('-')[1] for f in charting_files if '-' in f.stem))
        }

        return summary


def main():
    """Demo usage"""
    manager = TennisDataManager()

    # Update all repositories
    print("Step 1: Updating repositories...")
    results = manager.update_all()

    # Show summary
    print("\n" + "="*50)
    print("Step 2: Data Summary")
    print("="*50)
    summary = manager.get_data_summary()

    for repo, info in summary.items():
        print(f"\n{repo.upper()}:")
        for key, value in info.items():
            print(f"  {key}: {value}")

    # Example: Load recent ATP matches
    print("\n" + "="*50)
    print("Step 3: Sample - Loading ATP 2023-2024 matches")
    print("="*50)
    recent_matches = manager.load_matches('atp', years=[2023, 2024])

    if recent_matches is not None:
        print(f"\nColumns: {list(recent_matches.columns)[:10]}...")
        print(f"\nSample match:")
        print(recent_matches.iloc[0][['tourney_name', 'winner_name', 'loser_name', 'score']].to_dict())

    # Example: Get Djokovic's matches
    print("\n" + "="*50)
    print("Step 4: Sample - Djokovic's 2024 matches")
    print("="*50)
    djokovic_matches = manager.get_player_matches('Djokovic', 'atp', years=[2024])

    if djokovic_matches is not None:
        print(f"\nTournaments played:")
        print(djokovic_matches['tourney_name'].unique()[:10])


if __name__ == '__main__':
    main()
