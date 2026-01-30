"""
COMPREHENSIVE ML ANALYSIS MODULE
=================================
Replaces old ml_model.py
- Includes ALL branch topics (CSE, ECE, MECH, CIVIL, etc.)
- ML-based performance analysis
- ML-based readiness calculation
- ML-based recommendations
"""

import pandas as pd
import numpy as np
import joblib
from datetime import datetime
from collections import defaultdict

# ============================================================================
# ALL BRANCH TOPICS (Complete Coverage)
# ============================================================================

ALL_TOPICS = {
    # CSE/IT Topics
    'C': {'weight': 1.2, 'branch': ['CSE', 'IT', 'ECE', 'EEE', 'MECH', 'CIVIL', 'CHEM']},
    'Java': {'weight': 1.2, 'branch': ['CSE', 'IT']},
    'Python': {'weight': 1.2, 'branch': ['CSE', 'IT', 'ECE', 'EEE', 'MECH', 'CIVIL', 'CHEM', 'AI/ML']},
    'DBMS': {'weight': 1.1, 'branch': ['CSE', 'IT']},
    'OS': {'weight': 1.1, 'branch': ['CSE', 'IT']},
    'Data Structures': {'weight': 1.3, 'branch': ['CSE', 'IT', 'AI/ML']},
    'Algorithms': {'weight': 1.3, 'branch': ['CSE', 'IT', 'AI/ML']},
    'Computer Networks': {'weight': 1.1, 'branch': ['CSE', 'IT']},
    'OOP': {'weight': 1.2, 'branch': ['CSE', 'IT']},
    'Web Development': {'weight': 1.0, 'branch': ['CSE', 'IT']},
    'Cloud Computing': {'weight': 1.1, 'branch': ['CSE', 'IT']},
    
    # ECE Topics
    'Digital Electronics': {'weight': 1.2, 'branch': ['ECE']},
    'Signal Processing': {'weight': 1.3, 'branch': ['ECE']},
    'Embedded Systems': {'weight': 1.2, 'branch': ['ECE']},
    'VLSI': {'weight': 1.3, 'branch': ['ECE']},
    'Microprocessors': {'weight': 1.2, 'branch': ['ECE']},
    'Communication Systems': {'weight': 1.2, 'branch': ['ECE']},
    'Antenna Theory': {'weight': 1.1, 'branch': ['ECE']},
    'Control Systems': {'weight': 1.2, 'branch': ['ECE', 'EEE']},
    
    # EEE Topics
    'Circuit Theory': {'weight': 1.2, 'branch': ['EEE']},
    'Power Systems': {'weight': 1.3, 'branch': ['EEE']},
    'Electrical Machines': {'weight': 1.3, 'branch': ['EEE']},
    'Power Electronics': {'weight': 1.2, 'branch': ['EEE']},
    'Renewable Energy': {'weight': 1.1, 'branch': ['EEE']},
    'Electrical Drives': {'weight': 1.2, 'branch': ['EEE']},
    'Switchgear': {'weight': 1.1, 'branch': ['EEE']},
    
    # MECH Topics
    'Thermodynamics': {'weight': 1.3, 'branch': ['MECH']},
    'Mechanics': {'weight': 1.2, 'branch': ['MECH']},
    'Manufacturing': {'weight': 1.2, 'branch': ['MECH']},
    'CAD/CAM': {'weight': 1.2, 'branch': ['MECH']},
    'Fluid Mechanics': {'weight': 1.2, 'branch': ['MECH', 'CHEM']},
    'Heat Transfer': {'weight': 1.2, 'branch': ['MECH', 'CHEM']},
    'Machine Design': {'weight': 1.3, 'branch': ['MECH']},
    'Automobile Engineering': {'weight': 1.1, 'branch': ['MECH']},
    
    # CIVIL Topics
    'AutoCAD': {'weight': 1.2, 'branch': ['CIVIL']},
    'Structural Analysis': {'weight': 1.3, 'branch': ['CIVIL']},
    'Surveying': {'weight': 1.2, 'branch': ['CIVIL']},
    'Construction Management': {'weight': 1.1, 'branch': ['CIVIL']},
    'Geotechnical Engineering': {'weight': 1.2, 'branch': ['CIVIL']},
    'Transportation Engineering': {'weight': 1.1, 'branch': ['CIVIL']},
    'Environmental Engineering': {'weight': 1.1, 'branch': ['CIVIL']},
    'Concrete Technology': {'weight': 1.2, 'branch': ['CIVIL']},
    'Estimation & Costing': {'weight': 1.1, 'branch': ['CIVIL']},
    
    # CHEM Topics
    'Chemical Thermodynamics': {'weight': 1.3, 'branch': ['CHEM']},
    'Process Control': {'weight': 1.2, 'branch': ['CHEM']},
    'Reaction Engineering': {'weight': 1.3, 'branch': ['CHEM']},
    'Mass Transfer': {'weight': 1.2, 'branch': ['CHEM']},
    'Process Equipment Design': {'weight': 1.2, 'branch': ['CHEM']},
    'Chemical Plant Design': {'weight': 1.2, 'branch': ['CHEM']},
    
    # AI/ML Topics
    'Machine Learning': {'weight': 1.3, 'branch': ['AI/ML']},
    'Deep Learning': {'weight': 1.3, 'branch': ['AI/ML']},
    'Statistics': {'weight': 1.2, 'branch': ['AI/ML']},
    'Neural Networks': {'weight': 1.3, 'branch': ['AI/ML']},
    'NLP': {'weight': 1.2, 'branch': ['AI/ML']},
    'Computer Vision': {'weight': 1.2, 'branch': ['AI/ML']},
    'Data Science': {'weight': 1.2, 'branch': ['AI/ML']},
    'TensorFlow': {'weight': 1.1, 'branch': ['AI/ML']},
    
    # Common/Aptitude Topics
    'Quantitative Aptitude': {'weight': 1.0, 'branch': ['ALL']},
    'Logical Reasoning': {'weight': 1.0, 'branch': ['ALL']},
    'Verbal Ability': {'weight': 0.9, 'branch': ['ALL']},
    'Grammar': {'weight': 0.8, 'branch': ['ALL']},
}


# ============================================================================
# ML-POWERED ANALYSIS ENGINE
# ============================================================================

class MLAnalysisEngine:
    """
    Complete ML-based analysis engine
    Uses trained model for all predictions
    """
    
    def __init__(self, model_dir='ml'):
        """Load trained ML model"""
        try:
            self.model = joblib.load(f'{model_dir}/careerlens_ml.pkl')
            self.label_encoder = joblib.load(f'{model_dir}/label_encoder.pkl')
            self.scaler = joblib.load(f'{model_dir}/scaler.pkl')
            self.loaded = True
        except FileNotFoundError:
            self.loaded = False
            self.model = None
    
    def extract_features(self, user_scores):
        """Extract 10 ML features from user quiz history"""
        if not user_scores:
            return None
        
        df = pd.DataFrame(user_scores)
        
        # Calculate percentage if not present
        if 'percentage' not in df.columns:
            df['percentage'] = (df['score'] / df['total_questions'] * 100)
        
        # Sort by timestamp if available
        if 'timestamp' in df.columns:
            df = df.sort_values('timestamp')
        
        # 10 Features
        features = {
            'avg_score': df['percentage'].mean(),
            'std_score': df['percentage'].std() if len(df) > 1 else 0,
            'total_attempts': len(df),
            'topics_covered': df['topic'].nunique(),
            'improvement': 0,
            'score_variance': df['percentage'].var() if len(df) > 1 else 0,
            'avg_time': df['time_taken'].mean() if 'time_taken' in df.columns else 600,
            'avg_difficulty': 2.0,
            'best_topic_score': 0,
            'worst_topic_score': 0
        }
        
        # Improvement calculation
        if len(df) >= 5:
            recent = df.tail(5)['percentage'].mean()
            old = df.head(5)['percentage'].mean()
            features['improvement'] = recent - old
        
        # Difficulty mapping
        if 'difficulty' in df.columns:
            diff_map = {'beginner': 1, 'intermediate': 2, 'advanced': 3}
            features['avg_difficulty'] = df['difficulty'].map(diff_map).mean()
        
        # Best/worst topics
        topic_perf = df.groupby('topic')['percentage'].mean()
        if len(topic_perf) > 0:
            features['best_topic_score'] = topic_perf.max()
            features['worst_topic_score'] = topic_perf.min()
        
        return features
    
    def ml_predict_readiness(self, user_scores):
        """ML-based readiness prediction"""
        if not self.loaded:
            # Fallback to rule-based
            return self._fallback_readiness(user_scores)
        
        features = self.extract_features(user_scores)
        if not features:
            return {
                'score': 0,
                'status': 'Insufficient Data',
                'confidence': 0,
                'ml_powered': False
            }
        
        # Prepare feature vector
        X = np.array([[
            features['avg_score'], features['std_score'],
            features['total_attempts'], features['topics_covered'],
            features['improvement'], features['score_variance'],
            features['avg_time'], features['avg_difficulty'],
            features['best_topic_score'], features['worst_topic_score']
        ]])
        
        # Scale and predict
        X_scaled = self.scaler.transform(X)
        prediction = self.model.predict(X_scaled)[0]
        prediction_proba = self.model.predict_proba(X_scaled)[0]
        
        # Decode
        status = self.label_encoder.inverse_transform([prediction])[0]
        confidence = float(prediction_proba[prediction])
        
        # Map to score
        score_map = {
            'Ready': 85,
            'Almost Ready': 70,
            'Needs Improvement': 45,
            'Insufficient Data': 20
        }
        score = score_map.get(status, 50)
        
        return {
            'score': score,
            'status': status,
            'confidence': round(confidence * 100, 1),
            'ml_powered': True,
            'total_attempts': features['total_attempts'],
            'topics_covered': features['topics_covered'],
            'avg_score': round(features['avg_score'], 1),
            'improvement': round(features['improvement'], 1),
            'probabilities': {
                self.label_encoder.inverse_transform([i])[0]: round(float(prob) * 100, 1)
                for i, prob in enumerate(prediction_proba)
            }
        }
    
    def _fallback_readiness(self, user_scores):
        """Fallback if model not loaded"""
        features = self.extract_features(user_scores)
        if not features:
            return {'score': 0, 'status': 'Insufficient Data', 'confidence': 0, 'ml_powered': False}
        
        avg = features['avg_score']
        topics = features['topics_covered']
        attempts = features['total_attempts']
        
        if avg >= 75 and topics >= 5 and attempts >= 10:
            status = 'Ready'
            score = 85
        elif avg >= 60 and topics >= 3:
            status = 'Almost Ready'
            score = 70
        elif topics < 2 or attempts < 5:
            status = 'Insufficient Data'
            score = 20
        else:
            status = 'Needs Improvement'
            score = 45
        
        return {
            'score': score,
            'status': status,
            'confidence': 75,
            'ml_powered': False,
            'total_attempts': attempts,
            'topics_covered': topics,
            'avg_score': round(avg, 1)
        }
    
    def ml_analyze_weak_topics(self, user_scores):
        """ML-based weak topic identification"""
        if not user_scores:
            return []
        
        df = pd.DataFrame(user_scores)
        
        # Calculate percentage
        if 'percentage' not in df.columns:
            df['percentage'] = (df['score'] / df['total_questions'] * 100)
        
        # Get latest attempt per topic-subtopic
        if 'timestamp' in df.columns:
            df = df.sort_values('timestamp', ascending=False)
        df_latest = df.drop_duplicates(subset=['topic', 'subtopic'], keep='first')
        
        # Group by topic
        topic_analysis = []
        for topic, group in df_latest.groupby('topic'):
            avg_perf = group['percentage'].mean()
            attempts = len(group)
            
            # Get topic weight
            topic_weight = ALL_TOPICS.get(topic, {}).get('weight', 1.0)
            weighted_score = avg_perf * topic_weight
            
            # Determine priority
            if weighted_score < 50:
                priority = 3  # High
                level = 'Weak'
                color = 'danger'
            elif weighted_score < 70:
                priority = 2  # Medium
                level = 'Moderate'
                color = 'warning'
            else:
                priority = 1  # Low
                level = 'Strong'
                color = 'success'
            
            # Generate recommendation
            if priority == 3:
                action = 'High Priority - Practice Daily'
                recommendation = f"Focus heavily on {topic}. Your score is {avg_perf:.1f}%. Practice fundamental concepts and take more quizzes."
            elif priority == 2:
                action = 'Medium Priority - Regular Practice'
                recommendation = f"Good progress in {topic} ({avg_perf:.1f}%). Keep practicing to strengthen understanding."
            else:
                action = 'Low Priority - Maintain Proficiency'
                recommendation = f"Excellent work in {topic}! Maintain this level with periodic review."
            
            topic_analysis.append({
                'topic': topic,
                'display_name': topic,
                'percentage': round(avg_perf, 1),
                'attempts': attempts,
                'priority': priority,
                'level': level,
                'color': color,
                'action': action,
                'recommendation': recommendation,
                'weighted_score': round(weighted_score, 1)
            })
        
        # Sort by priority (high to low), then by percentage (low to high)
        topic_analysis.sort(key=lambda x: (-x['priority'], x['percentage']))
        
        return topic_analysis
    
    def ml_get_recommendations(self, user_scores):
        """ML-based personalized recommendations"""
        readiness = self.ml_predict_readiness(user_scores)
        features = self.extract_features(user_scores) if user_scores else {}
        
        recommendations = []
        
        # Based on ML prediction
        status = readiness['status']
        
        if status == 'Insufficient Data':
            recommendations.append({
                'icon': '📊',
                'title': 'Start Your Learning Journey',
                'message': f"Take more quizzes to unlock ML-powered insights. Current: {readiness.get('total_attempts', 0)} quizzes",
                'priority': 'high',
                'action': 'Take at least 10 quizzes across different topics'
            })
        
        elif status == 'Needs Improvement':
            recommendations.append({
                'icon': '💪',
                'title': 'Focus on Fundamentals',
                'message': f"ML Analysis: Your average score is {readiness.get('avg_score', 0):.1f}%. Strengthen your foundation.",
                'priority': 'high',
                'action': 'Practice basics daily, review weak concepts'
            })
        
        elif status == 'Almost Ready':
            recommendations.append({
                'icon': '🎯',
                'title': 'Almost There!',
                'message': f"ML Confidence: {readiness['confidence']}%. Cover more topics to boost readiness.",
                'priority': 'medium',
                'action': f"Cover {6 - readiness.get('topics_covered', 0)} more topics"
            })
        
        else:  # Ready
            recommendations.append({
                'icon': '🎉',
                'title': 'Placement Ready!',
                'message': f"ML Analysis shows {readiness['confidence']}% confidence. Focus on interview prep.",
                'priority': 'low',
                'action': 'Practice mock interviews and coding rounds'
            })
        
        # Improvement trend
        improvement = features.get('improvement', 0)
        if improvement < -10:
            recommendations.append({
                'icon': '📉',
                'title': 'Performance Declining',
                'message': f"ML detected {abs(improvement):.1f}% drop in recent performance.",
                'priority': 'high',
                'action': 'Take a break, review fundamentals'
            })
        elif improvement > 15:
            recommendations.append({
                'icon': '📈',
                'title': 'Great Improvement!',
                'message': f"ML detected {improvement:.1f}% improvement. Keep it up!",
                'priority': 'low',
                'action': 'Maintain consistent practice'
            })
        
        # Consistency check
        if features.get('std_score', 0) > 25:
            recommendations.append({
                'icon': '🎯',
                'title': 'Improve Consistency',
                'message': 'ML found high variance in scores. Aim for stable performance.',
                'priority': 'medium',
                'action': 'Regular practice, review before quizzes'
            })
        
        # Topic coverage
        topics_covered = readiness.get('topics_covered', 0)
        if topics_covered < 5:
            recommendations.append({
                'icon': '📚',
                'title': 'Expand Topic Coverage',
                'message': f"ML recommends covering {6 - topics_covered} more topics.",
                'priority': 'medium',
                'action': 'Explore new topics this week'
            })
        
        return recommendations


# ============================================================================
# GLOBAL INSTANCE & HELPER FUNCTIONS (For app.py)
# ============================================================================

_ml_engine = None

def get_ml_engine():
    """Singleton: Load ML engine once"""
    global _ml_engine
    if _ml_engine is None:
        _ml_engine = MLAnalysisEngine()
    return _ml_engine


def analyze_user_performance(scores_data):
    """
    MAIN FUNCTION: Analyze user performance with ML
    Replace old ml_model.analyze_user_performance()
    """
    engine = get_ml_engine()
    return engine.ml_analyze_weak_topics(scores_data)


def get_overall_readiness(scores_data):
    """
    MAIN FUNCTION: Get ML-based readiness
    Replace old ml_model.get_overall_readiness()
    """
    engine = get_ml_engine()
    readiness = engine.ml_predict_readiness(scores_data)
    
    # Add recommendations
    readiness['recommendations'] = engine.ml_get_recommendations(scores_data)
    
    # Add breakdown
    topic_analysis = engine.ml_analyze_weak_topics(scores_data)
    readiness['breakdown'] = {
        t['topic']: t['percentage'] 
        for t in topic_analysis
    }
    
    return readiness


def get_ml_insights(scores_data):
    """
    NEW FUNCTION: Get complete ML insights
    For special ML section in UI
    """
    engine = get_ml_engine()
    
    return {
        'readiness': engine.ml_predict_readiness(scores_data),
        'weak_topics': engine.ml_analyze_weak_topics(scores_data),
        'recommendations': engine.ml_get_recommendations(scores_data),
        'features': engine.extract_features(scores_data) if scores_data else {},
        'ml_powered': engine.loaded
    }


# For backward compatibility during transition
def determine_difficulty_level(user_scores, topic, subtopic):
    """Adaptive difficulty (keep existing logic)"""
    if not user_scores:
        return "intermediate"
    
    relevant = [s for s in user_scores if s['topic'] == topic]
    if not relevant:
        return "intermediate"
    
    total_score = sum(s['score'] for s in relevant)
    total_q = sum(s['total_questions'] for s in relevant)
    percent = (total_score / total_q * 100) if total_q > 0 else 0
    
    attempts = len(relevant)
    
    if attempts >= 5:
        if percent < 50:
            return "beginner"
        elif percent >= 80:
            return "advanced"
        else:
            return "intermediate"
    else:
        if percent < 40:
            return "beginner"
        elif percent >= 75:
            return "advanced"
        else:
            return "intermediate"