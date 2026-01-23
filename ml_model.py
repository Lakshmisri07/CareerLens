"""
Improved ML Model for CareerLens
Uses actual quiz performance data to provide intelligent suggestions
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.preprocessing import LabelEncoder
import joblib
import os

class CareerLensMLModel:
    """
    Enhanced ML model for:
    1. Predicting next question difficulty
    2. Identifying weak topics
    3. Estimating placement readiness
    4. Providing personalized learning paths
    """
    
    def __init__(self):
        self.difficulty_predictor = None
        self.readiness_predictor = None
        self.label_encoders = {}
        self.is_trained = False
    
    def prepare_features(self, user_attempts):
        """
        Extract features from user quiz history
        
        Args:
            user_attempts: List of dicts with quiz attempt data
        
        Returns:
            DataFrame with engineered features
        """
        df = pd.DataFrame(user_attempts)
        
        # Sort by timestamp
        df = df.sort_values('timestamp') if 'timestamp' in df.columns else df
        
        # Feature 1: Recent performance (last 5 attempts)
        df['recent_avg_score'] = df['score'].rolling(window=5, min_periods=1).mean()
        
        # Feature 2: Topic-specific average
        df['topic_avg_score'] = df.groupby('topic')['score'].transform('mean')
        
        # Feature 3: Improvement trend
        df['score_diff'] = df.groupby('topic')['score'].diff()
        df['is_improving'] = (df['score_diff'] > 0).astype(int)
        
        # Feature 4: Consistency (standard deviation)
        df['score_std'] = df.groupby('topic')['score'].transform('std').fillna(0)
        
        # Feature 5: Attempt count per topic
        df['topic_attempts'] = df.groupby('topic').cumcount() + 1
        
        # Feature 6: Overall attempt number
        df['overall_attempt'] = range(1, len(df) + 1)
        
        # Feature 7: Time-based features
        if 'time_taken' in df.columns:
            df['avg_time'] = df['time_taken'].expanding().mean()
            df['time_efficiency'] = df['score'] / (df['time_taken'] / 60)  # score per minute
        
        # Encode categorical variables
        for col in ['topic', 'subtopic', 'difficulty']:
            if col in df.columns:
                if col not in self.label_encoders:
                    self.label_encoders[col] = LabelEncoder()
                    df[f'{col}_encoded'] = self.label_encoders[col].fit_transform(df[col])
                else:
                    df[f'{col}_encoded'] = self.label_encoders[col].transform(df[col])
        
        return df
    
    def train(self, training_data_path='data/train_quiz_data.csv'):
        """
        Train ML models on historical quiz data
        """
        print("Loading training data...")
        df = pd.read_csv(training_data_path)
        
        # Prepare features
        print("Engineering features...")
        df_processed = self.prepare_features(df.to_dict('records'))
        
        # Define feature columns
        feature_cols = [
            'score', 'total_questions', 'recent_avg_score',
            'topic_avg_score', 'score_std', 'topic_attempts',
            'overall_attempt', 'topic_encoded', 'subtopic_encoded'
        ]
        
        if 'time_taken' in df.columns:
            feature_cols.extend(['avg_time', 'time_efficiency'])
        
        # Remove rows with NaN
        df_clean = df_processed[feature_cols + ['difficulty_encoded', 'readiness']].dropna()
        
        X = df_clean[feature_cols]
        
        # Model 1: Predict optimal difficulty level
        print("Training difficulty prediction model...")
        y_difficulty = df_clean['difficulty_encoded']
        self.difficulty_predictor = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.difficulty_predictor.fit(X, y_difficulty)
        
        # Model 2: Predict placement readiness
        print("Training readiness prediction model...")
        y_readiness = df_clean['readiness'].map({
            'Needs Improvement': 0,
            'Average': 1,
            'Good': 2,
            'Excellent': 3
        })
        self.readiness_predictor = GradientBoostingRegressor(
            n_estimators=100,
            max_depth=5,
            random_state=42
        )
        self.readiness_predictor.fit(X, y_readiness)
        
        self.is_trained = True
        print("✓ Models trained successfully!")
        
        # Calculate feature importance
        feature_importance = pd.DataFrame({
            'feature': feature_cols,
            'importance': self.difficulty_predictor.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print("\nTop 5 Most Important Features:")
        print(feature_importance.head().to_string())
        
        return feature_importance
    
    def predict_next_difficulty(self, user_attempts):
        """
        Predict optimal difficulty for next quiz
        
        Args:
            user_attempts: List of user's quiz attempts
        
        Returns:
            str: 'beginner', 'intermediate', or 'advanced'
        """
        if not self.is_trained:
            # Fallback to rule-based
            return self._rule_based_difficulty(user_attempts)
        
        # Prepare features
        df = self.prepare_features(user_attempts)
        
        # Get features for last attempt
        feature_cols = [
            'score', 'total_questions', 'recent_avg_score',
            'topic_avg_score', 'score_std', 'topic_attempts',
            'overall_attempt', 'topic_encoded', 'subtopic_encoded'
        ]
        
        X = df[feature_cols].iloc[-1:].fillna(0)
        
        # Predict
        difficulty_encoded = self.difficulty_predictor.predict(X)[0]
        difficulty = self.label_encoders['difficulty'].inverse_transform([int(difficulty_encoded)])[0]
        
        return difficulty
    
    def _rule_based_difficulty(self, user_attempts):
        """
        Fallback rule-based difficulty determination
        """
        if not user_attempts:
            return 'beginner'
        
        recent_scores = [a['score'] / a['total_questions'] for a in user_attempts[-5:]]
        avg_recent = sum(recent_scores) / len(recent_scores)
        
        if avg_recent < 0.5:
            return 'beginner'
        elif avg_recent < 0.75:
            return 'intermediate'
        else:
            return 'advanced'
    
    def analyze_weaknesses(self, user_attempts):
        """
        Identify user's weak topics with detailed analysis
        
        Returns:
            List of dicts with topic, score, priority, recommendation
        """
        df = pd.DataFrame(user_attempts)
        
        # Group by topic
        topic_stats = df.groupby('topic').agg({
            'score': 'sum',
            'total_questions': 'sum',
            'timestamp': 'count'  # number of attempts
        }).reset_index()
        
        topic_stats['percentage'] = (topic_stats['score'] / topic_stats['total_questions'] * 100).round(1)
        topic_stats['attempts'] = topic_stats['timestamp']
        
        # Calculate priority (lower score = higher priority)
        topic_stats['priority'] = topic_stats['percentage'].apply(lambda x: 
            3 if x < 50 else 2 if x < 70 else 1
        )
        
        # Generate recommendations
        weaknesses = []
        for _, row in topic_stats.iterrows():
            weakness = {
                'topic': row['topic'],
                'percentage': row['percentage'],
                'attempts': int(row['attempts']),
                'priority': int(row['priority']),
                'level': 'Weak' if row['priority'] == 3 else 'Moderate' if row['priority'] == 2 else 'Strong'
            }
            
            # Personalized recommendation
            if row['priority'] == 3:
                weakness['recommendation'] = f"Focus heavily on {row['topic']}. Practice more questions and review fundamental concepts."
                weakness['action'] = 'High Priority - Practice Daily'
            elif row['priority'] == 2:
                weakness['recommendation'] = f"Good progress in {row['topic']}. Keep practicing to strengthen understanding."
                weakness['action'] = 'Medium Priority - Regular Practice'
            else:
                weakness['recommendation'] = f"Excellent work in {row['topic']}! Maintain level with periodic review."
                weakness['action'] = 'Low Priority - Periodic Review'
            
            weaknesses.append(weakness)
        
        # Sort by priority
        weaknesses.sort(key=lambda x: x['priority'], reverse=True)
        
        return weaknesses
    
    def estimate_readiness(self, user_attempts):
        """
        Estimate overall placement readiness
        
        Returns:
            dict with score, status, message, confidence
        """
        if not user_attempts:
            return {
                'score': 0,
                'status': 'Not Assessed',
                'message': 'Take quizzes to assess readiness',
                'confidence': 0
            }
        
        # Calculate basic metrics
        total_score = sum(a['score'] for a in user_attempts)
        total_questions = sum(a['total_questions'] for a in user_attempts)
        percentage = (total_score / total_questions * 100) if total_questions > 0 else 0
        
        # If model is trained, use it for prediction
        if self.is_trained:
            df = self.prepare_features(user_attempts)
            feature_cols = [
                'score', 'total_questions', 'recent_avg_score',
                'topic_avg_score', 'score_std', 'topic_attempts',
                'overall_attempt', 'topic_encoded', 'subtopic_encoded'
            ]
            
            X = df[feature_cols].fillna(0)
            readiness_scores = self.readiness_predictor.predict(X)
            ml_readiness = readiness_scores[-1]  # Most recent prediction
            
            # Blend ML prediction with actual percentage
            final_score = (percentage * 0.6) + (ml_readiness * 25 * 0.4)
        else:
            final_score = percentage
        
        # Determine status
        if final_score >= 80:
            status = 'Excellent - Ready'
            message = 'You are well-prepared for placements!'
        elif final_score >= 65:
            status = 'Good - Almost Ready'
            message = 'You are on the right track. Focus on weak areas.'
        elif final_score >= 50:
            status = 'Average - Needs Work'
            message = 'Keep practicing. Focus on fundamentals.'
        else:
            status = 'Needs Improvement'
            message = 'Significant practice required. Start with basics.'
        
        # Calculate confidence based on number of attempts
        confidence = min(len(user_attempts) / 20, 1.0) * 100
        
        return {
            'score': round(final_score, 1),
            'status': status,
            'message': message,
            'confidence': round(confidence, 1),
            'total_attempts': len(user_attempts)
        }
    
    def save_model(self, path='models/careerlens_ml.pkl'):
        """Save trained models"""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump({
            'difficulty_predictor': self.difficulty_predictor,
            'readiness_predictor': self.readiness_predictor,
            'label_encoders': self.label_encoders,
            'is_trained': self.is_trained
        }, path)
        print(f"✓ Model saved to {path}")
    
    def load_model(self, path='models/careerlens_ml.pkl'):
        """Load trained models"""
        if os.path.exists(path):
            data = joblib.load(path)
            self.difficulty_predictor = data['difficulty_predictor']
            self.readiness_predictor = data['readiness_predictor']
            self.label_encoders = data['label_encoders']
            self.is_trained = data['is_trained']
            print(f"✓ Model loaded from {path}")
        else:
            print(f"⚠ Model file not found at {path}")


# Example usage
if __name__ == "__main__":
    # Initialize model
    model = CareerLensMLModel()
    
    # Train on generated data
    try:
        feature_importance = model.train('data/train_quiz_data.csv')
        model.save_model()
    except FileNotFoundError:
        print("⚠ Training data not found. Run dataset generator first!")
    
    # Example: Analyze a user
    sample_attempts = [
        {'topic': 'C', 'subtopic': 'Arrays', 'score': 3, 'total_questions': 5, 
         'difficulty': 'beginner', 'time_taken': 450, 'timestamp': '2024-01-01'},
        {'topic': 'C', 'subtopic': 'Pointers', 'score': 2, 'total_questions': 5,
         'difficulty': 'beginner', 'time_taken': 600, 'timestamp': '2024-01-02'},
        {'topic': 'Java', 'subtopic': 'OOPs', 'score': 4, 'total_questions': 5,
         'difficulty': 'intermediate', 'time_taken': 400, 'timestamp': '2024-01-03'},
    ]
    
    print("\n" + "="*60)
    print("ANALYSIS EXAMPLE")
    print("="*60)
    
    # Predict next difficulty
    next_diff = model._rule_based_difficulty(sample_attempts)
    print(f"\nRecommended Next Difficulty: {next_diff}")
    
    # Analyze weaknesses
    weaknesses = model.analyze_weaknesses(sample_attempts)
    print(f"\nWeak Topics:")
    for w in weaknesses:
        print(f"  - {w['topic']}: {w['percentage']}% ({w['level']})")
    
    # Estimate readiness
    readiness = model.estimate_readiness(sample_attempts)
    print(f"\nPlacement Readiness: {readiness['score']}% - {readiness['status']}")
    print(f"Confidence: {readiness['confidence']}%")