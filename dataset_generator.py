"""
Custom Dataset Generator for CareerLens ML Models
Generates synthetic training data aligned with your quiz system
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Define topics and subtopics from your system
TOPICS = {
    'C': ['Arrays', 'Pointers', 'Loops', 'Functions'],
    'Java': ['OOPs', 'Inheritance', 'Exceptions'],
    'Python': ['Lists', 'Dictionaries', 'File Handling'],
    'DBMS': ['SQL', 'Normalization', 'Transactions'],
    'OS': ['Processes', 'Threads', 'Memory Management'],
    'Data Structures': ['Linked List', 'Stacks', 'Queues', 'Trees']
}

DIFFICULTY_LEVELS = ['beginner', 'intermediate', 'advanced']

def generate_user_learning_path(num_attempts=20):
    """
    Simulate realistic user learning progression
    - Users improve over time
    - Some topics are harder than others
    - Users have strengths/weaknesses
    """
    
    # User characteristics
    overall_ability = random.uniform(0.3, 0.9)  # 0-1 scale
    learning_rate = random.uniform(0.02, 0.08)  # How fast they improve
    
    # Topic-specific strengths
    topic_strengths = {
        topic: random.uniform(0.7, 1.3) 
        for topic in TOPICS.keys()
    }
    
    attempts = []
    current_date = datetime.now() - timedelta(days=num_attempts * 3)
    
    for attempt in range(num_attempts):
        # Select random topic and subtopic
        topic = random.choice(list(TOPICS.keys()))
        subtopic = random.choice(TOPICS[topic])
        
        # Calculate difficulty based on performance
        if attempt < 5:
            difficulty = 'beginner'
        elif attempt < 12:
            difficulty = 'intermediate'
        else:
            difficulty = 'advanced'
        
        # Calculate score based on ability, topic strength, and learning progress
        base_score = overall_ability + (learning_rate * attempt)
        topic_modifier = topic_strengths[topic]
        difficulty_penalty = {'beginner': 0, 'intermediate': -0.1, 'advanced': -0.2}[difficulty]
        
        # Add randomness
        noise = random.uniform(-0.15, 0.15)
        
        final_score = (base_score * topic_modifier + difficulty_penalty + noise)
        final_score = max(0, min(1, final_score))  # Clamp to 0-1
        
        # Convert to actual quiz scores
        total_questions = 5
        correct_answers = int(final_score * total_questions)
        
        # Time taken (better students are faster)
        time_taken = int(900 * (1 - final_score * 0.3) + random.randint(-120, 120))
        time_taken = max(300, min(900, time_taken))
        
        attempts.append({
            'topic': topic,
            'subtopic': subtopic,
            'difficulty': difficulty,
            'score': correct_answers,
            'total_questions': total_questions,
            'percentage': round(final_score * 100, 1),
            'time_taken': time_taken,
            'attempt_number': attempt + 1,
            'timestamp': current_date
        })
        
        current_date += timedelta(days=random.randint(1, 5))
    
    return attempts

def generate_dataset(num_users=500, min_attempts=10, max_attempts=30):
    """
    Generate complete dataset for training ML models
    """
    all_data = []
    
    for user_id in range(num_users):
        num_attempts = random.randint(min_attempts, max_attempts)
        user_attempts = generate_user_learning_path(num_attempts)
        
        for attempt in user_attempts:
            attempt['user_id'] = f'user_{user_id:04d}'
            all_data.append(attempt)
    
    df = pd.DataFrame(all_data)
    
    # Add derived features useful for ML
    df['score_ratio'] = df['score'] / df['total_questions']
    df['is_improving'] = df.groupby('user_id')['percentage'].diff() > 0
    df['avg_previous_score'] = df.groupby(['user_id', 'topic'])['percentage'].transform(
        lambda x: x.shift().expanding().mean()
    )
    
    return df

def generate_placement_readiness_labels(df):
    """
    Add placement readiness labels based on overall performance
    This can be used for classification models
    """
    user_stats = df.groupby('user_id').agg({
        'percentage': 'mean',
        'attempt_number': 'max'
    }).reset_index()
    
    user_stats['readiness'] = pd.cut(
        user_stats['percentage'],
        bins=[0, 50, 65, 80, 100],
        labels=['Needs Improvement', 'Average', 'Good', 'Excellent']
    )
    
    df = df.merge(user_stats[['user_id', 'readiness']], on='user_id')
    return df

def save_datasets():
    """Generate and save datasets"""
    
    # Generate main dataset
    print("Generating quiz performance dataset...")
    df = generate_dataset(num_users=500, min_attempts=15, max_attempts=35)
    
    # Add readiness labels
    df = generate_placement_readiness_labels(df)
    
    # Save complete dataset
    df.to_csv('data/careerlens_quiz_data.csv', index=False)
    print(f"✓ Saved complete dataset: {len(df)} records")
    
    # Create train/test split
    from sklearn.model_selection import train_test_split
    
    train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)
    train_df.to_csv('data/train_quiz_data.csv', index=False)
    test_df.to_csv('data/test_quiz_data.csv', index=False)
    print(f"✓ Train set: {len(train_df)} | Test set: {len(test_df)}")
    
    # Generate summary statistics
    print("\n" + "="*60)
    print("DATASET SUMMARY")
    print("="*60)
    print(f"Total Users: {df['user_id'].nunique()}")
    print(f"Total Quiz Attempts: {len(df)}")
    print(f"Average Score: {df['percentage'].mean():.1f}%")
    print(f"\nReadiness Distribution:")
    print(df.groupby('readiness')['user_id'].nunique())
    print(f"\nTopic Distribution:")
    print(df['topic'].value_counts())
    
    return df

if __name__ == "__main__":
    # Generate datasets
    dataset = save_datasets()
    
    # Display sample
    print("\n" + "="*60)
    print("SAMPLE DATA (first 10 rows)")
    print("="*60)
    print(dataset.head(10).to_string())
    
    print("\n✅ Dataset generation complete!")
    print("Files saved:")
    print("  - data/careerlens_quiz_data.csv (complete dataset)")
    print("  - data/train_quiz_data.csv (training set)")
    print("  - data/test_quiz_data.csv (test set)")