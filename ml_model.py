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
        }).reset_index()
        
        topic_stats['attempts'] = df.groupby('topic').size().values
        topic_stats['percentage'] = (topic_stats['score'] / topic_stats['total_questions'] * 100).round(1)
        
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
                weakness['recommendation'] = f"Focus heavily on {row['topic']}. Your score is {row['percentage']:.1f}%. Practice more questions and review fundamental concepts."
                weakness['action'] = 'High Priority - Practice Daily'
            elif row['priority'] == 2:
                weakness['recommendation'] = f"Good progress in {row['topic']} with {row['percentage']:.1f}%. Keep practicing to strengthen understanding."
                weakness['action'] = 'Medium Priority - Regular Practice'
            else:
                weakness['recommendation'] = f"Excellent work in {row['topic']}! You scored {row['percentage']:.1f}%. Maintain level with periodic review."
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
                'confidence': 0,
                'total_attempts': 0
            }
        
        # Calculate basic metrics
        total_score = sum(a['score'] for a in user_attempts)
        total_questions = sum(a['total_questions'] for a in user_attempts)
        percentage = (total_score / total_questions * 100) if total_questions > 0 else 0
        
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


# ============================================================================
# HELPER FUNCTIONS FOR APP.PY COMPATIBILITY
# ============================================================================

def analyze_user_performance(scores_data):
    """
    Analyze user performance and provide suggestions
    Compatible with app.py's expected format
    
    Args:
        scores_data: List of dicts with 'topic', 'subtopic', 'score', 'total_questions'
    
    Returns:
        List of suggestion dicts with topic analysis
    """
    if not scores_data:
        return []
    
    model = CareerLensMLModel()
    weaknesses = model.analyze_weaknesses(scores_data)
    
    return weaknesses


def get_overall_readiness(scores_data):
    """
    Get overall placement readiness score and status
    Compatible with app.py's expected format
    
    Args:
        scores_data: List of dicts with 'topic', 'subtopic', 'score', 'total_questions'
    
    Returns:
        Dict with 'score', 'status', 'message', 'confidence', 'total_attempts'
    """
    if not scores_data:
        return {
            'score': 0,
            'status': 'Not Assessed',
            'message': 'Take quizzes to assess your readiness',
            'confidence': 0,
            'total_attempts': 0
        }
    
    model = CareerLensMLModel()
    readiness = model.estimate_readiness(scores_data)
    
    return readiness
def determine_difficulty_level(user_scores, topic, subtopic):
    """Determine user's difficulty level for adaptive questions"""
    if not user_scores:
        return "intermediate"
    
    # Filter relevant attempts
    relevant = [s for s in user_scores 
                if s['topic'] == topic and (not subtopic or s.get('subtopic') == subtopic)]
    
    if not relevant:
        return "intermediate"
    
    # Calculate average percentage
    total_score = sum(s['score'] for s in relevant)
    total_q = sum(s['total_questions'] for s in relevant)
    percent = (total_score / total_q * 100) if total_q > 0 else 0
    
    # Determine level
    if percent < 40:
        return "beginner"
    elif percent >= 75:
        return "advanced"
    else:
        return "intermediate"

# Example usage
if __name__ == "__main__":
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
    
    # Analyze weaknesses
    weaknesses = analyze_user_performance(sample_attempts)
    print(f"\nWeak Topics:")
    for w in weaknesses:
        print(f"  - {w['topic']}: {w['percentage']}% ({w['level']})")
    
    # Estimate readiness
    readiness = get_overall_readiness(sample_attempts)
    print(f"\nPlacement Readiness: {readiness['score']}% - {readiness['status']}")
    print(f"Confidence: {readiness['confidence']}%")