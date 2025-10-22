import numpy as np
from sklearn.ensemble import RandomForestClassifier
import pickle
import os

class SuggestionModel:
    """
    ML Model to analyze quiz scores and provide intelligent suggestions
    """

    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.is_trained = False
        self.model_path = 'models/suggestion_model.pkl'

    def prepare_features(self, scores_data):
        """
        Convert score data into features for ML model
        scores_data: list of dicts with keys: topic, subtopic, score, total_questions
        Returns: feature matrix and labels
        """
        features = []
        labels = []

        for score in scores_data:
            percent = (score['score'] / score['total_questions']) * 100

            # Features: [percentage, total_questions]
            features.append([percent, score['total_questions']])

            # Labels: 0=Need Practice, 1=Good, 2=Excellent
            if percent < 50:
                labels.append(0)
            elif percent < 75:
                labels.append(1)
            else:
                labels.append(2)

        return np.array(features), np.array(labels)

    def train(self, scores_data):
        """
        Train the model with user scores
        """
        if len(scores_data) < 5:
            # Not enough data to train
            return False

        X, y = self.prepare_features(scores_data)
        self.model.fit(X, y)
        self.is_trained = True
        return True

    def predict_weakness(self, score, total_questions):
        """
        Predict if a topic is weak, moderate, or strong
        Returns: 0=Weak, 1=Moderate, 2=Strong
        """
        if not self.is_trained:
            # Fallback to rule-based if model not trained
            percent = (score / total_questions) * 100
            if percent < 50:
                return 0
            elif percent < 75:
                return 1
            else:
                return 2

        percent = (score / total_questions) * 100
        features = np.array([[percent, total_questions]])
        return self.model.predict(features)[0]

    def get_confidence_score(self, score, total_questions):
        """
        Get confidence probability for prediction
        """
        if not self.is_trained:
            return None

        percent = (score / total_questions) * 100
        features = np.array([[percent, total_questions]])
        probabilities = self.model.predict_proba(features)[0]
        return max(probabilities)


def analyze_user_performance(scores_data):
    """
    Analyze user performance using ML and provide intelligent suggestions
    """
    if not scores_data:
        return []

    # Group scores by topic
    topic_scores = {}
    for score in scores_data:
        key = score['topic'] if not score['subtopic'] else f"{score['topic']} - {score['subtopic']}"

        if key not in topic_scores:
            topic_scores[key] = {
                'total_score': 0,
                'total_questions': 0,
                'attempts': 0,
                'topic': score['topic'],
                'subtopic': score['subtopic']
            }

        topic_scores[key]['total_score'] += score['score']
        topic_scores[key]['total_questions'] += score['total_questions']
        topic_scores[key]['attempts'] += 1

    # Create ML model
    model = SuggestionModel()

    # Train if enough data
    if len(scores_data) >= 5:
        model.train(scores_data)

    # Analyze each topic
    suggestions = []
    for key, data in topic_scores.items():
        avg_score = data['total_score'] / data['total_questions']
        percent = avg_score * 100

        # Get ML prediction
        prediction = model.predict_weakness(data['total_score'], data['total_questions'])

        # Generate suggestion based on ML prediction and performance
        suggestion = {
            'topic': key,
            'percentage': round(percent, 1),
            'attempts': data['attempts'],
            'level': ['Weak', 'Moderate', 'Strong'][prediction],
            'priority': 3 - prediction,  # Higher priority for weaker topics
        }

        # Generate recommendation text
        if prediction == 0:  # Weak
            suggestion['recommendation'] = f"Focus heavily on {key}. Your score is {percent:.1f}%. Practice more questions and review concepts."
            suggestion['action'] = 'High Priority - Practice Daily'
        elif prediction == 1:  # Moderate
            suggestion['recommendation'] = f"Good progress in {key} with {percent:.1f}%. Keep practicing to strengthen your understanding."
            suggestion['action'] = 'Medium Priority - Regular Practice'
        else:  # Strong
            suggestion['recommendation'] = f"Excellent work in {key}! You scored {percent:.1f}%. Maintain this level with occasional review."
            suggestion['action'] = 'Low Priority - Periodic Review'

        suggestions.append(suggestion)

    # Sort by priority (highest first)
    suggestions.sort(key=lambda x: x['priority'], reverse=True)

    return suggestions


def get_overall_readiness(scores_data):
    """
    Calculate overall placement readiness score
    """
    if not scores_data:
        return {
            'score': 0,
            'status': 'Not Assessed',
            'message': 'Take more quizzes to assess your readiness'
        }

    total_score = sum(s['score'] for s in scores_data)
    total_questions = sum(s['total_questions'] for s in scores_data)

    if total_questions == 0:
        return {
            'score': 0,
            'status': 'Not Assessed',
            'message': 'No quiz data available'
        }

    overall_percent = (total_score / total_questions) * 100

    if overall_percent >= 80:
        status = 'Excellent - Ready'
        message = 'You are well-prepared for placements!'
    elif overall_percent >= 65:
        status = 'Good - Almost Ready'
        message = 'You are on the right track. Focus on weak areas.'
    elif overall_percent >= 50:
        status = 'Average - Needs Work'
        message = 'Keep practicing. Focus on fundamentals.'
    else:
        status = 'Needs Improvement'
        message = 'Significant practice required. Start with basics.'

    return {
        'score': round(overall_percent, 1),
        'status': status,
        'message': message,
        'total_quizzes': len(scores_data)
    }
