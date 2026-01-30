"""
PRODUCTION PREDICTION MODULE
============================
Use trained ML model in Flask app for real-time predictions
"""

import joblib
import numpy as np
import pandas as pd
from datetime import datetime

class ProductionMLModel:
    """
    Production-ready ML prediction system
    Integrates with CareerLens Flask app
    """
    
    def __init__(self, model_dir='ml'):
        """Load trained model and artifacts"""
        try:
            self.model = joblib.load(f'{model_dir}/careerlens_ml.pkl')
            self.label_encoder = joblib.load(f'{model_dir}/label_encoder.pkl')
            self.scaler = joblib.load(f'{model_dir}/scaler.pkl')
            self.loaded = True
            print("✅ ML Model loaded successfully")
        except FileNotFoundError:
            print("⚠️  Model not found. Train model first: python advanced_ml_pipeline.py")
            self.loaded = False
    
    def extract_features(self, user_scores):
        """
        Extract features from user quiz history
        Input: List of dicts with {topic, subtopic, score, total_questions, timestamp}
        Output: Feature vector for prediction
        """
        if not user_scores:
            return None
        
        df = pd.DataFrame(user_scores)
        
        # Sort by timestamp if available
        if 'timestamp' in df.columns:
            df = df.sort_values('timestamp')
        
        # Calculate percentage if not present
        if 'percentage' not in df.columns:
            df['percentage'] = (df['score'] / df['total_questions'] * 100)
        
        # Feature 1: Average score
        avg_score = df['percentage'].mean()
        
        # Feature 2: Standard deviation
        std_score = df['percentage'].std() if len(df) > 1 else 0
        
        # Feature 3: Total attempts
        total_attempts = len(df)
        
        # Feature 4: Topics covered
        topics_covered = df['topic'].nunique()
        
        # Feature 5: Improvement (recent vs old)
        if len(df) >= 5:
            recent_scores = df.tail(5)['percentage'].mean()
            old_scores = df.head(5)['percentage'].mean()
            improvement = recent_scores - old_scores
        else:
            improvement = 0
        
        # Feature 6: Score variance
        score_variance = df['percentage'].var() if len(df) > 1 else 0
        
        # Feature 7: Average time (if available)
        if 'time_taken' in df.columns:
            avg_time = df['time_taken'].mean()
        else:
            avg_time = 600  # default
        
        # Feature 8: Average difficulty
        if 'difficulty' in df.columns:
            difficulty_map = {'beginner': 1, 'intermediate': 2, 'advanced': 3}
            avg_difficulty = df['difficulty'].map(difficulty_map).mean()
        else:
            avg_difficulty = 2.0  # default intermediate
        
        # Feature 9 & 10: Best and worst topic scores
        topic_performance = df.groupby('topic')['percentage'].mean()
        best_topic_score = topic_performance.max() if len(topic_performance) > 0 else 0
        worst_topic_score = topic_performance.min() if len(topic_performance) > 0 else 0
        
        # Create feature vector
        features = np.array([[
            avg_score,
            std_score,
            total_attempts,
            topics_covered,
            improvement,
            score_variance,
            avg_time,
            avg_difficulty,
            best_topic_score,
            worst_topic_score
        ]])
        
        return features
    
    def predict_readiness(self, user_scores):
        """
        Predict placement readiness for a user
        
        Returns:
        {
            'readiness': 'Ready' | 'Almost Ready' | 'Needs Improvement' | 'Insufficient Data',
            'confidence': 0.95,
            'scores': {'Ready': 0.95, 'Almost Ready': 0.03, ...},
            'features': {...}
        }
        """
        if not self.loaded:
            return {
                'readiness': 'Model Not Loaded',
                'confidence': 0.0,
                'error': 'ML model not trained yet'
            }
        
        if not user_scores:
            return {
                'readiness': 'Insufficient Data',
                'confidence': 0.0,
                'message': 'Take more quizzes to get predictions'
            }
        
        # Extract features
        features = self.extract_features(user_scores)
        
        if features is None:
            return {
                'readiness': 'Insufficient Data',
                'confidence': 0.0
            }
        
        # Scale features
        features_scaled = self.scaler.transform(features)
        
        # Predict
        prediction = self.model.predict(features_scaled)[0]
        prediction_proba = self.model.predict_proba(features_scaled)[0]
        
        # Decode label
        readiness_label = self.label_encoder.inverse_transform([prediction])[0]
        
        # Get confidence (probability of predicted class)
        confidence = prediction_proba[prediction]
        
        # Get all class probabilities
        class_probas = {
            self.label_encoder.inverse_transform([i])[0]: float(prob)
            for i, prob in enumerate(prediction_proba)
        }
        
        # Feature breakdown
        feature_values = {
            'avg_score': float(features[0][0]),
            'std_score': float(features[0][1]),
            'total_attempts': int(features[0][2]),
            'topics_covered': int(features[0][3]),
            'improvement': float(features[0][4]),
            'score_variance': float(features[0][5]),
            'avg_time': float(features[0][6]),
            'avg_difficulty': float(features[0][7]),
            'best_topic_score': float(features[0][8]),
            'worst_topic_score': float(features[0][9])
        }
        
        return {
            'readiness': readiness_label,
            'confidence': float(confidence),
            'probabilities': class_probas,
            'features': feature_values,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_recommendations(self, user_scores):
        """
        Get personalized recommendations based on prediction
        """
        prediction_result = self.predict_readiness(user_scores)
        readiness = prediction_result['readiness']
        features = prediction_result.get('features', {})
        
        recommendations = []
        
        # Based on readiness level
        if readiness == 'Insufficient Data':
            recommendations.append({
                'priority': 'high',
                'title': 'Take More Quizzes',
                'message': f"You've taken {features.get('total_attempts', 0)} quizzes. Take at least 10 to get accurate assessment.",
                'action': 'Start taking quizzes in different topics'
            })
        
        elif readiness == 'Needs Improvement':
            recommendations.append({
                'priority': 'high',
                'title': 'Focus on Fundamentals',
                'message': f"Your average score is {features.get('avg_score', 0):.1f}%. Focus on core concepts.",
                'action': 'Review weak topics and practice daily'
            })
        
        elif readiness == 'Almost Ready':
            recommendations.append({
                'priority': 'medium',
                'title': 'You\'re Close!',
                'message': f"Cover {6 - features.get('topics_covered', 0)} more topics to be placement-ready.",
                'action': 'Take quizzes in uncovered topics'
            })
        
        else:  # Ready
            recommendations.append({
                'priority': 'low',
                'title': 'Well Prepared!',
                'message': f"You're scoring {features.get('avg_score', 0):.1f}% on average. Focus on interview prep.",
                'action': 'Practice mock interviews and coding problems'
            })
        
        # Topic coverage recommendation
        if features.get('topics_covered', 0) < 6:
            recommendations.append({
                'priority': 'medium',
                'title': 'Expand Topic Coverage',
                'message': f"You've covered {features.get('topics_covered', 0)}/6 core topics.",
                'action': 'Take quizzes in: DBMS, OS, Data Structures'
            })
        
        # Consistency recommendation
        if features.get('std_score', 0) > 20:
            recommendations.append({
                'priority': 'medium',
                'title': 'Improve Consistency',
                'message': 'Your scores vary significantly. Focus on consistent practice.',
                'action': 'Review concepts regularly and take practice tests'
            })
        
        # Improvement recommendation
        if features.get('improvement', 0) < -10:
            recommendations.append({
                'priority': 'high',
                'title': 'Performance Declining',
                'message': 'Your recent scores are lower than earlier attempts.',
                'action': 'Take a break and review fundamentals'
            })
        
        return recommendations


# ============================================================================
# FLASK INTEGRATION HELPER FUNCTIONS
# ============================================================================

# Global model instance (loaded once when app starts)
_ml_model = None

def get_ml_model():
    """Singleton pattern: Load model only once"""
    global _ml_model
    if _ml_model is None:
        _ml_model = ProductionMLModel()
    return _ml_model


def predict_user_readiness(user_scores):
    """
    Main function to use in Flask app
    
    Usage in app.py:
    
    from ml_predict import predict_user_readiness
    
    @app.route('/suggestions')
    def suggestions():
        scores = get_user_scores(session['user_email'])
        prediction = predict_user_readiness(scores)
        return render_template('suggestions.html', prediction=prediction)
    """
    model = get_ml_model()
    return model.predict_readiness(user_scores)


def get_user_recommendations(user_scores):
    """Get recommendations for Flask app"""
    model = get_ml_model()
    return model.get_recommendations(user_scores)


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    # Test with sample data
    sample_scores = [
        {'topic': 'C', 'subtopic': 'Arrays', 'score': 3, 'total_questions': 5},
        {'topic': 'C', 'subtopic': 'Pointers', 'score': 2, 'total_questions': 5},
        {'topic': 'Java', 'subtopic': 'OOPs', 'score': 4, 'total_questions': 5},
        {'topic': 'Python', 'subtopic': 'Lists', 'score': 5, 'total_questions': 5},
        {'topic': 'DBMS', 'subtopic': 'SQL', 'score': 4, 'total_questions': 5},
        {'topic': 'OS', 'subtopic': 'Processes', 'score': 3, 'total_questions': 5},
    ]
    
    print("🧪 Testing ML Prediction System\n")
    print("="*60)
    
    # Test prediction
    result = predict_user_readiness(sample_scores)
    
    print(f"\n📊 Prediction Results:")
    print(f"   Readiness: {result['readiness']}")
    print(f"   Confidence: {result['confidence']*100:.1f}%")
    print(f"\n   Probabilities:")
    for label, prob in result.get('probabilities', {}).items():
        print(f"      {label:20s}: {prob*100:.1f}%")
    
    print(f"\n   Features Used:")
    for feature, value in result.get('features', {}).items():
        print(f"      {feature:20s}: {value:.2f}")
    
    # Test recommendations
    recommendations = get_user_recommendations(sample_scores)
    print(f"\n💡 Recommendations:")
    for rec in recommendations:
        print(f"\n   [{rec['priority'].upper()}] {rec['title']}")
        print(f"   {rec['message']}")
        print(f"   → {rec['action']}")
    
    print("\n" + "="*60)
    print("✅ Testing complete!")