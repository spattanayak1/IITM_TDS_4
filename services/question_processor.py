import base64
import json
from io import BytesIO
import re
from typing import Optional, List, Dict, Any


class QuestionProcessor:
    def __init__(self):
        self.common_tds_keywords = [
            'gpt', 'openai', 'ai-proxy', 'docker', 'podman', 'ga4', 'ga5', 
            'graded assignment', 'dashboard', 'bonus', 'end-term', 'exam',
            'discourse', 'tds', 'tools in data science', 'anand', 'professor'
        ]
    
    def process_question(self, question: str, image_b64: Optional[str] = None) -> Dict[str, Any]:
        """
        Process the incoming question and extract relevant information
        """
        processed = {
            'original_question': question,
            'cleaned_question': self.clean_question(question),
            'keywords': self.extract_keywords(question),
            'question_type': self.classify_question(question),
            'has_image': image_b64 is not None,
            'image_info': None
        }
        
        if image_b64:
            processed['image_info'] = self.process_image(image_b64)
        
        return processed
    
    def clean_question(self, question: str) -> str:
        """
        Clean and normalize the question text
        """
        # Remove extra whitespace
        cleaned = re.sub(r'\s+', ' ', question.strip())
        
        # Normalize common terms
        cleaned = re.sub(r'gpt-?3\.?5-?turbo-?0125', 'gpt-3.5-turbo-0125', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'gpt-?4o-?mini', 'gpt-4o-mini', cleaned, flags=re.IGNORECASE)
        
        return cleaned
    
    def extract_keywords(self, question: str) -> List[str]:
        """
        Extract relevant keywords from the question
        """
        keywords = []
        question_lower = question.lower()
        
        for keyword in self.common_tds_keywords:
            if keyword.lower() in question_lower:
                keywords.append(keyword)
        
        # Extract model names
        model_patterns = [
            r'gpt-?3\.?5-?turbo-?0125',
            r'gpt-?4o-?mini',
            r'gpt-?4',
            r'gpt-?3\.?5'
        ]
        
        for pattern in model_patterns:
            matches = re.findall(pattern, question, flags=re.IGNORECASE)
            keywords.extend(matches)
        
        # Extract assignment references
        assignment_matches = re.findall(r'ga\d+', question, flags=re.IGNORECASE)
        keywords.extend(assignment_matches)
        
        return list(set(keywords))  # Remove duplicates
    
    def classify_question(self, question: str) -> str:
        """
        Classify the type of question being asked
        """
        question_lower = question.lower()
        
        # Course information questions
        if any(phrase in question_lower for phrase in ['what is tds', 'tds full form', 'stands for', 'about tds', 'tools in data science']):
            return 'course_info'
        # Grading and deadline questions
        elif any(word in question_lower for word in ['grade', 'grading', 'deadline', 'due date', 'project 01', 'project 1', 's grade']):
            return 'grading_system'
        # Model usage questions
        elif any(word in question_lower for word in ['gpt', 'model', 'ai-proxy', 'openai']):
            return 'model_usage'
        elif any(word in question_lower for word in ['docker', 'podman', 'container']):
            return 'environment_setup'
        elif any(word in question_lower for word in ['ga4', 'ga5', 'graded assignment', 'assignment']):
            return 'assignment_help'
        elif any(word in question_lower for word in ['dashboard', 'score', 'marks', 'bonus']):
            return 'grading_system'
        elif any(word in question_lower for word in ['exam', 'end-term', 'when is']):
            return 'schedule_inquiry'
        else:
            return 'general'
    
    def process_image(self, image_b64: str) -> Optional[Dict[str, Any]]:
        """
        Process base64 encoded image and extract basic information
        """
        try:
            # Decode base64 image to get basic info
            image_data = base64.b64decode(image_b64)
            
            return {
                'size_bytes': len(image_data),
                'format': 'base64_decoded',
                'note': 'Image received but detailed processing not available'
            }
        except Exception as e:
            print(f"Error processing image: {e}")
            return None