# Query Validation System

## Overview

The Query Validation System prevents users from overusing the API by blocking queries that are not relevant to the provided article. This helps reduce API costs, prevent system abuse, and improve user experience by providing helpful feedback.

## How It Works

### Two-Stage Validation Process

#### Stage 1: Fast Pre-filtering (< 10ms)
- **Pattern Matching**: Detects obviously irrelevant queries using regex patterns
- **Keyword Analysis**: Checks for common off-topic patterns (weather, cooking, greetings, etc.)
- **Length Validation**: Blocks extremely short or vague queries
- **Title Overlap**: Allows queries that have meaningful overlap with article title

#### Stage 2: Semantic Similarity Check (< 100ms)
- **Embedding Generation**: Creates embeddings for both query and article content
- **Cosine Similarity**: Calculates semantic similarity between query and article
- **Threshold-Based Decision**: Uses 0.65 similarity threshold (moderate strictness)
- **Caching**: Article embeddings are cached to avoid repeated API calls

## Features

### 1. Speed-Optimized
- Most validation happens in ~100ms total
- Cached embeddings reduce repeated API calls
- Fast pattern matching eliminates obviously irrelevant queries

### 2. Smart Suggestions
- Provides helpful query suggestions when blocking irrelevant questions
- Suggestions are based on article title and content
- Guides users toward relevant questions

### 3. Override Mechanism
- Users can bypass validation with "force:" prefix
- Useful for edge cases where validation might be too strict
- Logged for monitoring purposes

### 4. Enhanced Error Messages
- Clear explanation of why query was blocked
- Specific suggestions for better queries
- Instructions for override mechanism

## API Response Format

### Successful Query (HTTP 200)
```json
{
  "result": "Answer to the user's question..."
}
```

### Blocked Query (HTTP 422)
```json
{
  "error": "Your question doesn't appear to be related to this article.",
  "reason": "Query seems unrelated to article content (similarity: 0.23)",
  "suggestions": [
    "What are the main points about [Article Topic]?",
    "Can you explain the key concepts in [Article Topic]?",
    "What should I know about [Article Topic]?"
  ],
  "override_available": true,
  "override_hint": "Add 'force:' at the beginning of your question to override this check."
}
```

## Configuration

### Validation Patterns
The system blocks queries matching these patterns:
- Weather queries: `weather`, `temperature`, `rain`, `snow`, etc.
- Cooking/recipes: `recipe`, `cook`, `bake`, `ingredient`, etc.
- Personal questions: `my`, `personal`, `yourself`, `who are you`, etc.
- Math calculations: `calculate`, `math`, `equation`, `solve` + numbers
- Generic greetings: `hello`, `hi`, `hey`, `how are you`, etc.
- Current events: `today`, `yesterday`, `current`, `latest news`, etc.
- Technical help: `how to`, `tutorial`, `step by step`, `install`, etc.

### Similarity Threshold
- **Current**: 0.65 (moderate strictness)
- **Adjustable**: Can be tuned between 0.5 (loose) and 0.8 (strict)
- **Recommendation**: 0.65 provides good balance between blocking irrelevant queries and allowing related questions

## Performance Metrics

### Validation Speed
- **Pre-filter**: < 10ms (pattern matching)
- **Semantic check**: < 100ms (with caching)
- **Total overhead**: ~100ms per query

### API Cost Impact
- **Embedding calls**: Only once per article (cached)
- **Model used**: `text-embedding-3-small` (cost-effective)
- **Estimated cost**: ~$0.0001 per article validation

## Usage Examples

### Valid Queries (Will Pass)
```
"What are the main findings in this research?"
"How does the author explain [topic from article]?"
"What evidence is provided for [claim in article]?"
"Can you summarize the key points?"
```

### Invalid Queries (Will Be Blocked)
```
"What's the weather today?" → Weather query
"How do I cook pasta?" → Cooking query
"Hello, how are you?" → Greeting
"What is 2+2?" → Unrelated math
"Hi" → Too short/vague
```

### Override Examples
```
"force: What's the weather today?" → Will bypass validation
"force: How do I cook pasta?" → Will bypass validation
```

## Testing

Run the validation test suite:
```bash
python test_query_validation.py
```

This tests:
- ✅ Valid queries are accepted
- ❌ Invalid queries are blocked
- 📝 Helpful suggestions are provided
- 🔄 Force override mechanism works
- ⚡ Performance is acceptable

## Monitoring

### Logs
The system logs validation decisions:
```
INFO: Query rejected: Query seems unrelated to article content (confidence: 0.85)
INFO: Query validation overridden by user
```

### Metrics to Track
- Validation success/failure rates
- Common blocked query patterns
- Override usage frequency
- Performance metrics (response time)

## Troubleshooting

### Common Issues

1. **Legitimate queries being blocked**
   - Lower similarity threshold (e.g., 0.6 instead of 0.65)
   - Check if query is too vague or short
   - Use force override for testing

2. **Irrelevant queries passing through**
   - Add new patterns to `irrelevant_patterns`
   - Increase similarity threshold (e.g., 0.7 instead of 0.65)
   - Check embedding quality

3. **Slow performance**
   - Verify embedding cache is working
   - Check OpenAI API response times
   - Consider using smaller embedding model

### Configuration Adjustments

Edit `utils/validation/queryValidator.py`:

```python
# Adjust similarity threshold
threshold = 0.65  # Change this value

# Add new irrelevant patterns
self.irrelevant_patterns.append(r'\b(new_pattern)\b')

# Modify cache behavior
self.embedding_cache = {}  # Clear cache if needed
```

## Future Enhancements

1. **Machine Learning Improvements**
   - Train custom classifier on article-query pairs
   - Use fine-tuned embeddings for domain-specific content
   - Implement active learning from user feedback

2. **Advanced Features**
   - Query intent classification
   - Multi-language support
   - Context-aware validation

3. **Analytics Dashboard**
   - Real-time validation metrics
   - Query pattern analysis
   - User behavior insights

## Implementation Details

### Files Added/Modified
- `utils/validation/queryValidator.py` - Main validation logic
- `utils/validation/__init__.py` - Package initialization
- `app.py` - Integration with query endpoint
- `requirements.txt` - Added scikit-learn dependency
- `test_query_validation.py` - Test suite

### Dependencies Added
- `scikit-learn==1.5.1` - For cosine similarity calculation

### API Changes
- `/query` endpoint now includes validation step
- New response format for blocked queries (HTTP 422)
- Support for "force:" override prefix
