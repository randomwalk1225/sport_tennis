"""
Tennis Match Prediction Model
Predicts match outcomes using machine learning
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler
import joblib
from pathlib import Path


class MatchPredictor:
    """Tennis match outcome predictor"""

    def __init__(self, model_type='random_forest'):
        """
        Initialize predictor

        Args:
            model_type: 'random_forest', 'gradient_boosting', or 'logistic'
        """
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = None
        self.is_trained = False

        # Initialize model
        if model_type == 'random_forest':
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                min_samples_split=10,
                random_state=42
            )
        elif model_type == 'gradient_boosting':
            self.model = GradientBoostingClassifier(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                random_state=42
            )
        elif model_type == 'logistic':
            self.model = LogisticRegression(
                max_iter=1000,
                random_state=42
            )
        else:
            raise ValueError(f"Unknown model type: {model_type}")

    def train(self, X, y, test_size=0.2):
        """
        Train the model

        Args:
            X: feature DataFrame
            y: target Series
            test_size: proportion of data for testing

        Returns:
            dict with training metrics
        """
        print(f"Training {self.model_type} model...")

        # Store feature names
        self.feature_names = X.columns.tolist()

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )

        print(f"Training samples: {len(X_train)}")
        print(f"Testing samples: {len(X_test)}")

        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # Train model
        self.model.fit(X_train_scaled, y_train)
        self.is_trained = True

        # Evaluate
        train_pred = self.model.predict(X_train_scaled)
        test_pred = self.model.predict(X_test_scaled)

        metrics = {
            'train_accuracy': accuracy_score(y_train, train_pred),
            'test_accuracy': accuracy_score(y_test, test_pred),
            'train_size': len(X_train),
            'test_size': len(X_test)
        }

        print(f"\n[+] Training Accuracy: {metrics['train_accuracy']:.4f}")
        print(f"[+] Testing Accuracy: {metrics['test_accuracy']:.4f}")

        # Cross-validation
        cv_scores = cross_val_score(self.model, X_train_scaled, y_train, cv=5)
        metrics['cv_mean'] = cv_scores.mean()
        metrics['cv_std'] = cv_scores.std()

        print(f"[+] Cross-Validation: {metrics['cv_mean']:.4f} (+/- {metrics['cv_std']:.4f})")

        # Feature importance (if available)
        if hasattr(self.model, 'feature_importances_'):
            importances = pd.DataFrame({
                'feature': self.feature_names,
                'importance': self.model.feature_importances_
            }).sort_values('importance', ascending=False)

            metrics['feature_importance'] = importances
            print(f"\n[+] Top 10 Features:")
            print(importances.head(10).to_string(index=False))

        return metrics

    def predict(self, X):
        """
        Predict match outcomes

        Args:
            X: feature DataFrame

        Returns:
            predictions (0 or 1)
        """
        if not self.is_trained:
            raise ValueError("Model not trained yet. Call train() first.")

        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)

    def predict_proba(self, X):
        """
        Predict match outcome probabilities

        Args:
            X: feature DataFrame

        Returns:
            probabilities for each class
        """
        if not self.is_trained:
            raise ValueError("Model not trained yet. Call train() first.")

        X_scaled = self.scaler.transform(X)
        return self.model.predict_proba(X_scaled)

    def save(self, filepath):
        """Save trained model"""
        if not self.is_trained:
            raise ValueError("Model not trained yet. Call train() first.")

        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'model_type': self.model_type
        }

        joblib.dump(model_data, filepath)
        print(f"[+] Model saved to {filepath}")

    def load(self, filepath):
        """Load trained model"""
        model_data = joblib.load(filepath)

        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.feature_names = model_data['feature_names']
        self.model_type = model_data['model_type']
        self.is_trained = True

        print(f"[+] Model loaded from {filepath}")


def demo():
    """Demo match prediction"""
    from data_manager import TennisDataManager
    from data_preprocessor import TennisDataPreprocessor

    print("="*60)
    print("Tennis Match Prediction Demo")
    print("="*60)

    # Load and prepare data
    manager = TennisDataManager()
    preprocessor = TennisDataPreprocessor()

    print("\nStep 1: Loading data...")
    df = manager.load_matches('atp', years=[2022, 2023, 2024])

    if df is None:
        print("Failed to load data")
        return

    print(f"Loaded {len(df)} matches")

    # Prepare for ML
    print("\nStep 2: Preprocessing...")
    X, y = preprocessor.prepare_for_ml(df)

    # Train multiple models
    print("\n" + "="*60)
    print("Step 3: Training Models")
    print("="*60)

    models = {}
    for model_type in ['random_forest', 'gradient_boosting', 'logistic']:
        print(f"\n--- {model_type.upper().replace('_', ' ')} ---")
        predictor = MatchPredictor(model_type=model_type)
        metrics = predictor.train(X, y, test_size=0.2)
        models[model_type] = {
            'predictor': predictor,
            'metrics': metrics
        }

    # Compare models
    print("\n" + "="*60)
    print("Model Comparison")
    print("="*60)

    comparison = pd.DataFrame({
        model: {
            'Train Acc': info['metrics']['train_accuracy'],
            'Test Acc': info['metrics']['test_accuracy'],
            'CV Mean': info['metrics']['cv_mean'],
            'CV Std': info['metrics']['cv_std']
        }
        for model, info in models.items()
    }).T

    print(comparison.to_string())

    # Save best model
    best_model_name = comparison['Test Acc'].idxmax()
    best_model = models[best_model_name]['predictor']

    model_path = 'models/tennis_predictor_best.pkl'
    Path('models').mkdir(exist_ok=True)
    best_model.save(model_path)

    print(f"\n[+] Best model ({best_model_name}) saved!")

    # Example prediction
    print("\n" + "="*60)
    print("Example Prediction")
    print("="*60)

    # Get a sample match
    sample = X.iloc[[0]]
    prob = best_model.predict_proba(sample)

    print(f"Sample features:")
    print(sample.T.to_string())
    print(f"\nPredicted win probability: {prob[0][1]:.2%}")


if __name__ == '__main__':
    demo()
