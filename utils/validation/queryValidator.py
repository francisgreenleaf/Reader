"""
Query validation utilities to prevent irrelevant queries from consuming API resources
"""
import re
import os
import logging
from typing import Tuple, Dict, List, Optional
from dataclasses import dataclass
import numpy as np
from openai import OpenAI

logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    is_valid: bool
    confidence: float
    reason: str
    suggestions: List[str] = None

class QueryValidator:
    def __init__(self, openai_client: OpenAI):
        self.client = openai_client
        self.irrelevant_patterns = [
            # Weather queries
            r'\b(weather|temperature|rain|snow|sunny|cloudy|forecast)\b',
            # Cooking/recipes
            r'\b(recipe|cook|bake|ingredient|kitchen|food preparation)\b',
            # Personal questions
            r'\b(my|personal|yourself|who are you|tell me about you)\b',
            # Math calculations unrelated to content
            r'\b(calculate|math|equation|solve)\s+[\d\+\-\*\/\=\(\)]+',
            # Generic greetings/chat
            r'\b(hello|hi|hey|how are you|good morning|good evening)\b',
            # Current events unrelated to article
            r'\b(today|yesterday|current|latest news|breaking)\b',
            # Technical help unrelated to article
            r'\b(how to|tutorial|step by step|install|download)\b'
        ]
        
        # Cache for article embeddings to avoid repeated API calls
        self.embedding_cache = {}
    
    def validate_query(self, query: str, article_content: str, article_title: str = "") -> ValidationResult:
        """
        Validate if a query is relevant to the article content
        
        Args:
            query: User's query
            article_content: The article content
            article_title: Article title (optional, for additional context)
            
        Returns:
            ValidationResult with validation decision and suggestions
        """
        # Stage 1: Fast pre-filter
        pre_filter_result = self._fast_pre_filter(query, article_title)
        if not pre_filter_result.is_valid:
            return pre_filter_result
        
        # Stage 2: Semantic similarity check
        try:
            similarity_result = self._semantic_similarity_check(query, article_content, article_title)
            return similarity_result
        except Exception as e:
            logger.error(f"Error in semantic similarity check: {e}")
            # Fallback to allowing the query if validation fails
            return ValidationResult(
                is_valid=True,
                confidence=0.5,
                reason="Validation system unavailable, allowing query"
            )
    
    def _fast_pre_filter(self, query: str, article_title: str = "") -> ValidationResult:
        """
        Fast pattern-based filtering for obviously irrelevant queries
        """
        query_lower = query.lower()
        
        # Check for completely irrelevant patterns
        for pattern in self.irrelevant_patterns:
            if re.search(pattern, query_lower, re.IGNORECASE):
                # Check if it might still be relevant to the article title
                if article_title and self._has_title_overlap(query_lower, article_title.lower()):
                    continue
                
                return ValidationResult(
                    is_valid=False,
                    confidence=0.9,
                    reason="Query appears unrelated to article content",
                    suggestions=self._generate_suggestions_from_title(article_title)
                )
        
        # Check for extremely short or vague queries
        if len(query.strip()) < 10:
            return ValidationResult(
                is_valid=False,
                confidence=0.7,
                reason="Query too short or vague",
                suggestions=[
                    "Try asking a more specific question about the article",
                    "Ask about main topics or themes discussed",
                    "Request clarification on specific points mentioned"
                ]
            )
        
        return ValidationResult(is_valid=True, confidence=0.8, reason="Passed pre-filter")
    
    def _has_title_overlap(self, query: str, title: str) -> bool:
        """Check if query has meaningful overlap with article title"""
        query_words = set(re.findall(r'\b\w{4,}\b', query))  # Words with 4+ chars
        title_words = set(re.findall(r'\b\w{4,}\b', title))
        
        overlap = len(query_words.intersection(title_words))
        return overlap >= 2  # At least 2 meaningful words in common
    
    def _semantic_similarity_check(self, query: str, article_content: str, article_title: str = "") -> ValidationResult:
        """
        Use embeddings to check semantic similarity between query and article
        """
        # Create cache key for article
        article_key = hash(article_content[:1000])  # Use first 1000 chars for cache key
        
        # Get article embedding (with caching)
        if article_key not in self.embedding_cache:
            # Create a representative text from title + content snippet
            article_text = f"{article_title}\n\n{article_content[:2000]}"  # First 2000 chars
            article_embedding = self._get_embedding(article_text)
            self.embedding_cache[article_key] = article_embedding
        else:
            article_embedding = self.embedding_cache[article_key]
        
        # Get query embedding
        query_embedding = self._get_embedding(query)
        
        # Calculate similarity
        similarity = np.dot(query_embedding, article_embedding) / (np.linalg.norm(query_embedding) * np.linalg.norm(article_embedding))
        
        # Set threshold (0.55 is more permissive - allows related questions but blocks irrelevant ones)
        threshold = 0.55
        
        if similarity >= threshold:
            return ValidationResult(
                is_valid=True,
                confidence=float(similarity),
                reason=f"Query is relevant to article content (similarity: {similarity:.2f})"
            )
        else:
            return ValidationResult(
                is_valid=False,
                confidence=float(1 - similarity),
                reason=f"Query seems unrelated to article content (similarity: {similarity:.2f})",
                suggestions=self._generate_content_based_suggestions(article_content, article_title)
            )
    
    def _get_embedding(self, text: str) -> np.ndarray:
        """Get embedding for text using OpenAI's embedding API"""
        try:
            response = self.client.embeddings.create(
                model="text-embedding-3-small",  # Fast and cost-effective
                input=text[:8000]  # Limit text length
            )
            return np.array(response.data[0].embedding)
        except Exception as e:
            logger.error(f"Error getting embedding: {e}")
            raise
    
    def _generate_suggestions_from_title(self, title: str) -> List[str]:
        """Generate query suggestions based on article title"""
        if not title:
            return [
                "Try asking about the main topic of the article",
                "Ask for a summary or explanation of key points"
            ]
        
        return [
            f"What are the main points about {title}?",
            f"Can you explain the key concepts in {title}?",
            f"What should I know about {title}?",
        ]
    
    def _generate_content_based_suggestions(self, content: str, title: str = "") -> List[str]:
        """Generate more sophisticated suggestions based on article content"""
        suggestions = []
        
        # Extract key topics from first few paragraphs
        content_start = content[:1000]
        
        # Look for common question starters that might work
        base_suggestions = [
            "What is the main argument presented in this article?",
            "Can you summarize the key findings discussed?",
            "What are the implications mentioned in this piece?",
        ]
        
        if title:
            base_suggestions.extend([
                f"How does this article explain {title}?",
                f"What evidence does the author provide about {title}?"
            ])
        
        return base_suggestions[:3]  # Return top 3 suggestions
    
    def clear_cache(self):
        """Clear the embedding cache"""
        self.embedding_cache.clear()
