# ml_model.py - IMPROVED ML PERFORMANCE ANALYSIS

import pandas as pd
import numpy as np
from collections import defaultdict
from datetime import datetime, timedelta

class CareerLensMLModel:
    """
    Enhanced ML model for student performance analysis
    """
    
    def __init__(self):
        self.topic_weights = {
            'C': 1.2,
            'Java': 1.2,
            'Python': 1.2,
            'DBMS': 1.1,
            'OS': 1.1,
            'Data Structures': 1.3,
            'Quantitative Aptitude': 1.0,
            'Logical Reasoning': 1.0,
            'Grammar': 0.8,
        }
    
    def analyze_performance_trends(self, user_attempts):
        """
        Analyze performance trends over time
        Returns: dict with trend analysis
        """
        if len(user_attempts) < 2:
            return {'trend': 'insufficient_data', 'direction': 'stable'}
        
        # Sort by timestamp
        df = pd.DataFrame(user_attempts)
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp')
        
        # Calculate rolling averages
        df['percentage'] = (df['score'] / df['total_questions'] * 100)
        df['rolling_avg'] = df['percentage'].rolling(window=5, min_periods=1).mean()
        
        # Determine trend
        recent_avg = df['rolling_avg'].iloc[-3:].mean()
        older_avg = df['rolling_avg'].iloc[:max(len(df)-3, 1)].mean()
        
        if recent_avg > older_avg + 10:
            trend = 'improving'
        elif recent_avg < older_avg - 10:
            trend = 'declining'
        else:
            trend = 'stable'
        
        return {
            'trend': trend,
            'recent_performance': round(recent_avg, 1),
            'overall_performance': round(df['percentage'].mean(), 1),
            'improvement': round(recent_avg - older_avg, 1)
        }
    
    def identify_weak_topics(self, user_attempts):
        """
        Identify weak topics with detailed analysis
        Returns: List of dicts with recommendations
        """
        if not user_attempts:
            return []
        
        df = pd.DataFrame(user_attempts)
        
        # Group by topic and subtopic
        topic_stats = df.groupby(['topic', 'subtopic']).agg({
            'score': 'sum',
            'total_questions': 'sum',
        }).reset_index()
        
        topic_stats['attempts'] = df.groupby(['topic', 'subtopic']).size().values
        topic_stats['percentage'] = (topic_stats['score'] / topic_stats['total_questions'] * 100).round(1)
        
        # Calculate priority with weights
        topic_stats['weighted_score'] = topic_stats.apply(
            lambda row: row['percentage'] * self.topic_weights.get(row['topic'], 1.0),
            axis=1
        )
        
        # Determine priority
        topic_stats['priority'] = topic_stats['weighted_score'].apply(
            lambda x: 3 if x < 50 else (2 if x < 70 else 1)
        )
        
        # Generate recommendations
        weaknesses = []
        for _, row in topic_stats.iterrows():
            topic_name = f"{row['topic']}"
            if row['subtopic']:
                topic_name += f" - {row['subtopic']}"
            
            weakness = {
                'topic': row['topic'],
                'subtopic': row['subtopic'],
                'display_name': topic_name,
                'percentage': float(row['percentage']),
                'attempts': int(row['attempts']),
                'priority': int(row['priority']),
                'level': 'Weak' if row['priority'] == 3 else ('Moderate' if row['priority'] == 2 else 'Strong')
            }
            
            # Personalized recommendations
            if row['priority'] == 3:
                weakness['recommendation'] = f"Focus heavily on {topic_name}. Your score is {row['percentage']:.1f}%. Practice more questions daily and review fundamental concepts."
                weakness['action'] = 'High Priority - Practice Daily'
                weakness['next_steps'] = [
                    f"Take at least 2 quizzes on {topic_name} this week",
                    "Review incorrect answers carefully",
                    "Focus on understanding core concepts",
                    "Consider watching tutorial videos"
                ]
            elif row['priority'] == 2:
                weakness['recommendation'] = f"Good progress in {topic_name} with {row['percentage']:.1f}%. Keep practicing regularly to strengthen understanding."
                weakness['action'] = 'Medium Priority - Regular Practice'
                weakness['next_steps'] = [
                    f"Take 1 quiz on {topic_name} this week",
                    "Review challenging questions",
                    "Try solving problems independently"
                ]
            else:
                weakness['recommendation'] = f"Excellent work in {topic_name}! You scored {row['percentage']:.1f}%. Maintain this level with periodic review."
                weakness['action'] = 'Low Priority - Periodic Review'
                weakness['next_steps'] = [
                    f"Take 1 quiz monthly to maintain proficiency",
                    "Help others or teach concepts to reinforce learning"
                ]
            
            weaknesses.append(weakness)
        
        # Sort by priority (highest first)
        weaknesses.sort(key=lambda x: (-x['priority'], x['percentage']))
        
        return weaknesses
    
    def calculate_readiness_score(self, user_attempts):
        """
        Calculate overall placement readiness with detailed breakdown
        """
        if not user_attempts:
            return {
                'score': 0,
                'status': 'Not Assessed',
                'message': 'Take quizzes to assess your readiness',
                'confidence': 0,
                'total_attempts': 0,
                'breakdown': {}
            }
        
        df = pd.DataFrame(user_attempts)
        
        # Calculate basic metrics
        total_score = sum(a['score'] for a in user_attempts)
        total_questions = sum(a['total_questions'] for a in user_attempts)
        overall_percentage = (total_score / total_questions * 100) if total_questions > 0 else 0
        
        # Calculate topic-wise performance
        topic_performance = {}
        for topic in df['topic'].unique():
            topic_data = df[df['topic'] == topic]
            topic_score = topic_data['score'].sum()
            topic_total = topic_data['total_questions'].sum()
            topic_pct = (topic_score / topic_total * 100) if topic_total > 0 else 0
            topic_performance[topic] = round(topic_pct, 1)
        
        # Calculate weighted score
        weighted_sum = 0
        weight_total = 0
        for topic, percentage in topic_performance.items():
            weight = self.topic_weights.get(topic, 1.0)
            weighted_sum += percentage * weight
            weight_total += weight
        
        final_score = (weighted_sum / weight_total) if weight_total > 0 else overall_percentage
        
        # Determine status and message
        if final_score >= 80:
            status = 'Excellent - Ready for Placements'
            message = '🎉 You are well-prepared! Focus on mock interviews and company-specific preparation.'
            color = 'success'
        elif final_score >= 70:
            status = 'Good - Almost Ready'
            message = '👍 You are on the right track. Focus on weak areas and take more practice tests.'
            color = 'info'
        elif final_score >= 60:
            status = 'Average - Needs Work'
            message = '📚 Keep practicing consistently. Focus on fundamentals and weak topics.'
            color = 'warning'
        elif final_score >= 40:
            status = 'Below Average - Significant Improvement Needed'
            message = '⚡ You need more practice. Start with basics and build gradually.'
            color = 'warning'
        else:
            status = 'Needs Substantial Improvement'
            message = '💪 Focus on building strong fundamentals. Practice daily and review concepts regularly.'
            color = 'danger'
        
        # Calculate confidence (based on number of attempts)
        confidence = min(len(user_attempts) / 20, 1.0) * 100
        
        # Identify strengths and weaknesses
        strengths = [t for t, p in topic_performance.items() if p >= 75]
        weaknesses = [t for t, p in topic_performance.items() if p < 50]
        
        return {
            'score': round(final_score, 1),
            'status': status,
            'message': message,
            'confidence': round(confidence, 1),
            'total_attempts': len(user_attempts),
            'breakdown': topic_performance,
            'strengths': strengths,
            'weaknesses': weaknesses,
            'color': color,
            'recommendations': self._get_readiness_recommendations(final_score, weaknesses)
        }
    
    def _get_readiness_recommendations(self, score, weak_topics):
        """Generate recommendations based on readiness score"""
        recommendations = []
        
        if score >= 80:
            recommendations = [
                "Start applying to companies",
                "Practice mock interviews",
                "Prepare company-specific questions",
                "Build confidence with more tests"
            ]
        elif score >= 70:
            recommendations = [
                "Focus on weak topics: " + ", ".join(weak_topics[:3]) if weak_topics else "Continue regular practice",
                "Take more comprehensive tests",
                "Practice coding problems daily",
                "Aim for 80%+ in weak areas"
            ]
        elif score >= 60:
            recommendations = [
                "Create a structured study plan",
                "Dedicate 2-3 hours daily to weak topics",
                "Take quizzes regularly to track progress",
                "Focus on fundamentals first"
            ]
        else:
            recommendations = [
                "Start with basic concepts",
                "Set daily learning goals",
                "Practice 1-2 topics thoroughly each week",
                "Don't rush - focus on understanding"
            ]
        
        return recommendations


# ============================================================================
# HELPER FUNCTIONS FOR APP.PY
# ============================================================================

def analyze_user_performance(scores_data):
    """
    Main function to analyze user performance
    Compatible with app.py
    """
    if not scores_data:
        return []
    
    model = CareerLensMLModel()
    weaknesses = model.identify_weak_topics(scores_data)
    
    return weaknesses


def get_overall_readiness(scores_data):
    """
    Get placement readiness analysis
    Compatible with app.py
    """
    if not scores_data:
        return {
            'score': 0,
            'status': 'Not Assessed',
            'message': 'Take quizzes to assess your readiness',
            'confidence': 0,
            'total_attempts': 0,
            'breakdown': {},
            'strengths': [],
            'weaknesses': [],
            'recommendations': []
        }
    
    model = CareerLensMLModel()
    readiness = model.calculate_readiness_score(scores_data)
    
    return readiness


def determine_difficulty_level(user_scores, topic, subtopic):
    """
    Determine adaptive difficulty level
    Compatible with app.py and ai_question_generator.py
    """
    if not user_scores:
        return "intermediate"
    
    # Filter relevant attempts
    relevant = [
        s for s in user_scores 
        if s['topic'] == topic and (not subtopic or s.get('subtopic') == subtopic)
    ]
    
    if not relevant:
        return "intermediate"
    
    # Calculate average percentage
    total_score = sum(s['score'] for s in relevant)
    total_q = sum(s['total_questions'] for s in relevant)
    percent = (total_score / total_q * 100) if total_q > 0 else 0
    
    # Adaptive thresholds based on number of attempts
    attempts = len(relevant)
    
    if attempts >= 5:
        # More aggressive progression after 5+ attempts
        if percent < 50:
            return "beginner"
        elif percent >= 80:
            return "advanced"
        else:
            return "intermediate"
    else:
        # Conservative progression for first few attempts
        if percent < 40:
            return "beginner"
        elif percent >= 75:
            return "advanced"
        else:
            return "intermediate"


# Example usage
if __name__ == "__main__":
    # Test with sample data
    sample_attempts = [
        {'topic': 'C', 'subtopic': 'Arrays', 'score': 3, 'total_questions': 5, 'timestamp': '2024-01-01'},
        {'topic': 'C', 'subtopic': 'Pointers', 'score': 2, 'total_questions': 5, 'timestamp': '2024-01-02'},
        {'topic': 'Java', 'subtopic': 'OOPs', 'score': 4, 'total_questions': 5, 'timestamp': '2024-01-03'},
        {'topic': 'Python', 'subtopic': 'Lists', 'score': 5, 'total_questions': 5, 'timestamp': '2024-01-04'},
    ]
    
    print("\n" + "="*80)
    print("ML MODEL TEST")
    print("="*80)
    
    # Test performance analysis
    weaknesses = analyze_user_performance(sample_attempts)
    print(f"\n📊 Found {len(weaknesses)} topics:")
    for w in weaknesses:
        print(f"  - {w['display_name']}: {w['percentage']}% ({w['level']})")
        print(f"    Action: {w['action']}")
    
    # Test readiness calculation
    readiness = get_overall_readiness(sample_attempts)
    print(f"\n🎯 Placement Readiness: {readiness['score']}%")
    print(f"   Status: {readiness['status']}")
    print(f"   Confidence: {readiness['confidence']}%")
    print(f"\n   Recommendations:")
    for rec in readiness.get('recommendations', []):
        print(f"   - {rec}")