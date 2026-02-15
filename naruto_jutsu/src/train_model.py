"""
Phase 2: Training script for gesture classifier.
Trains a Random Forest classifier on collected gesture data and evaluates performance.
Target: ≥ 90% accuracy in good lighting.
"""

import pandas as pd
import numpy as np
import pickle
from pathlib import Path
from datetime import datetime
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import json


class GestureTrainer:
    """
    Train and evaluate gesture recognition classifier.
    """
    
    def __init__(self, data_path: Path):
        """
        Initialize trainer with path to training data CSV.
        
        Args:
            data_path: Path to CSV file with gesture samples
        """
        self.data_path = data_path
        self.data = None
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.model = None
        self.label_encoder = LabelEncoder()
        
        print("=== Naruto Jutsu Gesture Trainer ===")
        print(f"Loading data from: {data_path}")
    
    def load_data(self):
        """Load and prepare training data."""
        try:
            self.data = pd.read_csv(self.data_path)
            print(f"✓ Loaded {len(self.data)} samples")
            
            # Show samples per gesture
            print("\nSamples per gesture:")
            gesture_counts = self.data['gesture_label'].value_counts()
            for gesture, count in gesture_counts.items():
                status = "✓" if count >= 200 else "⚠"
                print(f"  {status} {gesture}: {count}")
            
            # Check for minimum samples and filter if needed
            min_samples = gesture_counts.min()
            
            # Remove gestures with only 1 sample (can't be split)
            gestures_to_remove = gesture_counts[gesture_counts < 2].index.tolist()
            if gestures_to_remove:
                print(f"\n⚠ Removing gestures with < 2 samples (can't split for train/test):")
                for gesture in gestures_to_remove:
                    print(f"    - {gesture}: {gesture_counts[gesture]} sample(s)")
                    self.data = self.data[self.data['gesture_label'] != gesture]
                print(f"\n✓ Remaining samples: {len(self.data)}")
            
            # Warn about low sample counts
            gesture_counts = self.data['gesture_label'].value_counts()
            min_samples = gesture_counts.min()
            if min_samples < 50:
                print(f"\n⚠ Warning: Some gestures have < 50 samples (minimum: {min_samples}).")
                print(f"   Recommendation: collect more data for better accuracy.")
                print(f"   For stratified split, each gesture needs at least 5-10 samples.")
            
            # Check if we have enough data to train
            if len(self.data) < 10:
                print("\n✗ Error: Not enough training data. Need at least 10 samples total.")
                return False
            
            if len(gesture_counts) < 2:
                print("\n✗ Error: Need at least 2 different gestures to train a classifier.")
                return False
            
            return True
        
        except Exception as e:
            print(f"✗ Error loading data: {e}")
            return False
    
    def prepare_data(self, test_size: float = 0.2, random_state: int = 42):
        """
        Split data into training and validation sets.
        
        Args:
            test_size: Fraction of data to use for testing (e.g., 0.2 = 20%)
            random_state: Random seed for reproducibility
        """
        # Separate features and labels
        feature_cols = [col for col in self.data.columns if col.startswith('feature_')]
        X = self.data[feature_cols].values
        y = self.data['gesture_label'].values
        
        # Encode labels (convert gesture names to integers)
        y_encoded = self.label_encoder.fit_transform(y)
        
        # Check sample distribution
        unique, counts = np.unique(y_encoded, return_counts=True)
        min_count = counts.min()
        
        # Adjust test_size if needed for small datasets
        if min_count < 5:
            print(f"\n⚠ Warning: Smallest class has only {min_count} samples.")
            print(f"   Using stratify=None to avoid split errors.")
            stratify_param = None
        else:
            stratify_param = y_encoded
        
        # Adjust test_size to ensure at least 1 sample in test for each class
        min_test_size = 1 / min_count
        if test_size < min_test_size:
            test_size = min(0.3, min_test_size * 1.5)
            print(f"   Adjusted test_size to {test_size:.2f} for small dataset")
        
        # Split into train/test
        try:
            self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
                X, y_encoded, test_size=test_size, random_state=random_state, stratify=stratify_param
            )
        except ValueError as e:
            # If stratified split fails, fall back to non-stratified
            print(f"\n⚠ Stratified split failed, using random split instead.")
            self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
                X, y_encoded, test_size=test_size, random_state=random_state, stratify=None
            )
        
        print(f"\n✓ Data split: {len(self.X_train)} training, {len(self.X_test)} testing")
        print(f"  Feature dimensions: {self.X_train.shape[1]}")
    
    def train_model(self, n_estimators: int = 100, max_depth: int = 20):
        """
        Train Random Forest classifier.
        
        Args:
            n_estimators: Number of trees in the forest
            max_depth: Maximum depth of each tree
        """
        print(f"\nTraining Random Forest (n_estimators={n_estimators}, max_depth={max_depth})...")
        
        self.model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=42,
            n_jobs=-1  # Use all CPU cores
        )
        
        self.model.fit(self.X_train, self.y_train)
        print("✓ Training complete")
    
    def evaluate_model(self):
        """Evaluate model performance on test set."""
        print("\n=== Model Evaluation ===")
        
        # Predictions on test set
        y_pred = self.model.predict(self.X_test)
        
        # Overall accuracy
        accuracy = accuracy_score(self.y_test, y_pred)
        print(f"\nTest Accuracy: {accuracy * 100:.2f}%")
        
        # Check if meets target
        target_accuracy = 0.90
        if accuracy >= target_accuracy:
            print(f"✓ Meets target accuracy (≥ {target_accuracy * 100}%)")
        else:
            print(f"⚠ Below target accuracy (≥ {target_accuracy * 100}%). "
                  f"Consider collecting more data or tuning hyperparameters.")
        
        # Cross-validation score (only if we have enough samples)
        unique_train_classes = len(np.unique(self.y_train))
        if len(self.y_train) >= 10 and unique_train_classes >= 2:
            try:
                # Determine number of folds based on smallest class size
                min_class_size = min(np.bincount(self.y_train))
                n_folds = min(5, min_class_size)
                
                if n_folds >= 2:
                    print(f"\nPerforming {n_folds}-fold cross-validation...")
                    cv_scores = cross_val_score(self.model, self.X_train, self.y_train, cv=n_folds)
                    print(f"Cross-validation accuracy: {cv_scores.mean() * 100:.2f}% (+/- {cv_scores.std() * 100:.2f}%)")
                else:
                    print("\n⚠ Skipping cross-validation (not enough samples per class)")
            except Exception as e:
                print(f"\n⚠ Cross-validation skipped: {e}")
        else:
            print("\n⚠ Skipping cross-validation (insufficient training data)")
        
        # Detailed classification report
        print("\nClassification Report:")
        gesture_names = self.label_encoder.classes_
        print(classification_report(
            self.y_test, y_pred, 
            target_names=gesture_names,
            digits=3,
            zero_division=0
        ))
        
        # Confusion matrix
        print("Confusion Matrix:")
        cm = confusion_matrix(self.y_test, y_pred)
        print("\n         ", end="")
        for name in gesture_names:
            print(f"{name[:6]:>7}", end="")
        print()
        for i, row in enumerate(cm):
            print(f"{gesture_names[i][:6]:>9}", end="")
            for val in row:
                print(f"{val:>7}", end="")
            print()
        
        # Feature importance
        feature_importance = self.model.feature_importances_
        top_features = np.argsort(feature_importance)[-10:][::-1]
        print(f"\nTop 10 most important features:")
        for i, idx in enumerate(top_features, 1):
            print(f"  {i}. Feature {idx}: {feature_importance[idx]:.4f}")
        
        return accuracy
    
    def save_model(self, output_dir: Path = None):
        """Save trained model to disk."""
        if output_dir is None:
            output_dir = Path(__file__).resolve().parent.parent / "models"
        
        output_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_file = output_dir / f"gesture_classifier_{timestamp}.pkl"
        
        # Package model with metadata
        model_data = {
            'model': self.model,
            'label_encoder': self.label_encoder,
            'gesture_names': list(self.label_encoder.classes_),
            'feature_count': self.X_train.shape[1],
            'training_samples': len(self.X_train),
            'test_accuracy': accuracy_score(self.y_test, self.model.predict(self.X_test)),
            'timestamp': timestamp
        }
        
        with open(model_file, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"\n✓ Model saved to: {model_file}")
        
        # Also save training metadata as JSON
        metadata_file = output_dir / f"training_metadata_{timestamp}.json"
        metadata = {
            'timestamp': timestamp,
            'data_file': str(self.data_path),
            'total_samples': len(self.data),
            'training_samples': len(self.X_train),
            'test_samples': len(self.X_test),
            'gestures': list(self.label_encoder.classes_),
            'test_accuracy': float(model_data['test_accuracy']),
            'model_params': {
                'n_estimators': self.model.n_estimators,
                'max_depth': self.model.max_depth
            }
        }
        
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"✓ Metadata saved to: {metadata_file}")
        
        return model_file


def main():
    """Main training pipeline."""
    # Find the most recent data file
    data_dir = Path(__file__).resolve().parent.parent / "data"
    
    if not data_dir.exists():
        print("✗ Data directory not found. Run capture_data.py first to collect training data.")
        return
    
    csv_files = list(data_dir.glob("gesture_data_*.csv"))
    if not csv_files:
        print("✗ No training data found. Run capture_data.py first to collect samples.")
        return
    
    # Use most recent data file
    data_file = sorted(csv_files)[-1]
    print(f"Using data file: {data_file}\n")
    
    # Train pipeline
    trainer = GestureTrainer(data_file)
    
    if not trainer.load_data():
        return
    
    trainer.prepare_data(test_size=0.2)
    trainer.train_model(n_estimators=100, max_depth=20)
    accuracy = trainer.evaluate_model()
    
    # Save model
    model_file = trainer.save_model()
    
    print("\n" + "=" * 60)
    print("Training complete!")
    print(f"Final test accuracy: {accuracy * 100:.2f}%")
    print(f"Model saved: {model_file}")
    print("\nNext steps:")
    print("  1. If accuracy < 90%, collect more training data")
    print("  2. Run main.py to test real-time gesture recognition")
    print("=" * 60)


if __name__ == "__main__":
    main()
