import google.generativeai as genai
from typing import List, Dict, Any
import re

class GeminiChat:
    """Handles Gemini API integration for document analysis and general chat"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name="gemini-2.5-flash")

        self.chat_session = None
        self.document_context = ""

        # 🟦 UNIVERSAL GENERATE FUNCTION (REQUIRED)
    def generate(self, prompt: str):
        """Generate response using the latest Gemini API format"""
        try:
            response = self.model.generate_content(
                contents=[{"role": "user", "parts": [{"text": prompt}]}]
            )
            return response
        except Exception as e:
            # Return string so your caller can print it safely
            class FakeResponse:
                text = f"❌ Varsha Error: {str(e)}"
            return FakeResponse()
    
    def set_document_context(self, content: str):
        """Set the document context for conversations"""
        self.document_context = content
    
    def general_chat(self, user_query: str) -> str:
        """Chat with Gemini for general queries (no document context)"""
        try:
            # Create general conversational prompt
            prompt = f"""
You are Varsha, a friendly and intelligent AI assistant. You are helpful, knowledgeable, and conversational.

You can help with:
- General conversation and greetings
- General knowledge and facts  
- Science and technology questions
- History and current events
- Math and problem-solving
- Creative writing and brainstorming
- Programming and technical help
- Learning and education
- Lifestyle advice and recommendations

USER QUERY: {user_query}

Instructions:
1. Be warm, friendly, and conversational in your responses
2. For greetings (hi, hello, etc.), respond naturally and ask how you can help
3. Provide helpful, accurate, and engaging responses
4. If you're not sure about something, say so honestly
5. Keep responses concise but informative
6. Show enthusiasm and personality in your responses

Please provide a helpful and friendly response:
"""
            
            # Generate response
            response = self.generate(prompt)
            return response.text
        
        except Exception as e:
            return f"I encountered an error while processing your request: {str(e)}. Please try rephrasing your question."
    
    def chat_with_documents(self, user_query: str, document_content: str) -> str:
        """Chat with Gemini about document content"""
        try:
            # Create context-aware prompt
            prompt = self._create_document_prompt(user_query, document_content)
            
            # Generate response
            response = self.generate(prompt)
            return response.text
        
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def intelligent_chat(self, user_query: str, document_content: str = "") -> str:
        """
        Intelligent chat that determines whether to use document context or general knowledge
        """
        try:
            if document_content.strip():
                # Check if query is document-related
                doc_keywords = ["document", "text", "file", "uploaded", "this", "above", "content", "paper", "pdf", "summarize", "analyze"]
                query_lower = user_query.lower()
                
                is_doc_related = any(keyword in query_lower for keyword in doc_keywords)
                
                if is_doc_related or len(user_query.split()) > 10:  # Longer queries often relate to documents
                    return self.chat_with_documents(user_query, document_content)
                else:
                    # Offer both options
                    general_response = self.general_chat(user_query)
                    return f"{general_response}\n\n💡 **Note**: If you want me to answer this question based on your uploaded documents, please rephrase your question to reference the documents specifically."
            else:
                return self.general_chat(user_query)
                
        except Exception as e:
            return f"I encountered an error: {str(e)}. Please try again."
    
    def _create_document_prompt(self, user_query: str, document_content: str) -> str:
        """Create a structured prompt for document-based queries"""
        
        # Truncate document if too long (Gemini has token limits)
        max_content_length = 15000  # Adjust based on needs
        if len(document_content) > max_content_length:
            document_content = document_content[:max_content_length] + "\n\n[Content truncated...]"
        
        prompt = f"""
You are Varsha, an AI document assistant. You have been provided with document content and need to answer user queries based on this content.

DOCUMENT CONTENT:
{document_content}

USER QUERY: {user_query}

Instructions:
1. Answer the user's question based primarily on the provided document content
2. If the answer isn't in the documents, clearly state that
3. Provide specific quotes or references when possible
4. Be conversational and helpful
5. If asked for analysis (sentiment, summary, etc.), provide detailed insights

Please provide a comprehensive and helpful response:
"""
        return prompt
    
    def summarize_document(self, document_content: str, summary_type: str = "general") -> str:
        """Generate document summary using Gemini"""
        
        summary_prompts = {
            "general": "Provide a comprehensive summary of this document, highlighting the key points, main themes, and important information.",
            "executive": "Create an executive summary focusing on key findings, recommendations, and business-critical information.",
            "bullet": "Summarize this document in bullet points, organizing information by main topics or sections.",
            "abstract": "Create an academic-style abstract summarizing the purpose, methodology, findings, and conclusions."
        }
        
        prompt = f"""
{summary_prompts.get(summary_type, summary_prompts["general"])}

DOCUMENT CONTENT:
{document_content[:12000]}

Please provide a clear and well-structured summary:
"""
        
        try:
            response = self.generate(prompt)
            return response.text
        except Exception as e:
            return f"Error generating summary: {str(e)}"
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of text using Gemini"""
        
        # Detailed sentiment analysis with Gemini only
        prompt = f"""
Analyze the sentiment and emotional tone of the following text. Provide:
1. Overall sentiment (positive/negative/neutral) with confidence score (0-1)
2. Key emotional indicators
3. Tone analysis (formal/informal, optimistic/pessimistic, etc.)
4. Any notable emotional patterns
5. Provide a numerical sentiment score from -1 (very negative) to +1 (very positive)

TEXT TO ANALYZE:
{text[:8000]}

Please provide a detailed sentiment analysis in this format:
SENTIMENT: [positive/negative/neutral]
CONFIDENCE: [0-1]
SCORE: [-1 to +1]
ANALYSIS: [detailed analysis]
"""
        
        try:
            response = self.generate(prompt)
            
            # Simple parsing to extract score if possible
            response_text = response.text
            score = 0.0  # Default neutral
            
            # Try to extract score from response
            score_match = re.search(r'SCORE:\s*([-+]?\d*\.?\d+)', response_text)
            if score_match:
                try:
                    score = float(score_match.group(1))
                    score = max(-1.0, min(1.0, score))  # Clamp between -1 and 1
                except:
                    score = 0.0
            
            return {
                'detailed_analysis': response_text,
                'sentiment_score': score,
                'sentiment_category': 'positive' if score > 0.1 else 'negative' if score < -0.1 else 'neutral'
            }
        
        except Exception as e:
            return {
                'detailed_analysis': f"Error in sentiment analysis: {str(e)}",
                'sentiment_score': 0.0,
                'sentiment_category': 'neutral'
            }
    
    def extract_key_information(self, document_content: str, info_type: str = "general") -> str:
        """Extract specific types of information from documents"""
        
        extraction_prompts = {
            "entities": "Extract and list all important entities (people, organizations, locations, dates, etc.) mentioned in this document.",
            "keywords": "Identify and list the most important keywords and key phrases from this document.",
            "topics": "Identify the main topics and themes discussed in this document.",
            "facts": "Extract the key facts, statistics, and specific information from this document.",
            "conclusions": "Identify the main conclusions, findings, or outcomes presented in this document."
        }
        
        prompt = f"""
{extraction_prompts.get(info_type, extraction_prompts["keywords"])}

DOCUMENT CONTENT:
{document_content[:12000]}

Please provide a well-organized extraction:
"""
        
        try:
            response = self.generate(prompt)
            return response.text
        except Exception as e:
            return f"Error extracting information: {str(e)}"
    
    def answer_question(self, question: str, document_content: str) -> str:
        """Answer specific questions about document content"""
        
        prompt = f"""
You are answering a specific question about document content. Please:
1. Provide a direct answer if the information is available
2. Quote relevant sections from the document
3. If the answer isn't in the document, clearly state that
4. Provide context and explanation when helpful

DOCUMENT CONTENT:
{document_content[:12000]}

QUESTION: {question}

Answer:
"""
        
        try:
            response = self.generate(prompt)
            return response.text
        except Exception as e:
            return f"Error answering question: {str(e)}"
    
    def search_in_documents(self, search_query: str, document_content: str) -> str:
        """Search for specific information in documents"""
        
        # Simple keyword search first
        keywords = search_query.lower().split()
        relevant_sections = []
        
        # Split document into paragraphs and find relevant ones
        paragraphs = document_content.split('\n\n')
        for i, paragraph in enumerate(paragraphs):
            if any(keyword in paragraph.lower() for keyword in keywords):
                relevant_sections.append(f"Section {i+1}: {paragraph}")
        
        if relevant_sections:
            context = "\n\n".join(relevant_sections[:5])  # Limit to 5 most relevant sections
            
            prompt = f"""
Based on the search query "{search_query}", here are the most relevant sections from the document:

{context}

Please provide a comprehensive response that:
1. Addresses the search query
2. Synthesizes information from the relevant sections
3. Provides specific references and quotes
4. Explains the context and significance

Response:
"""
            
            try:
                response = self.generate(prompt)
                return response.text
            except Exception as e:
                return f"Error processing search: {str(e)}"
        
        else:
            return f"No relevant information found for '{search_query}' in the uploaded documents."
    
    def get_conversation_suggestions(self, has_documents: bool = False) -> List[str]:
        """Generate conversation starter suggestions"""
        if has_documents:
            return [
                "📄 Summarize the main points from my documents",
                "🔍 What are the key findings in this research?", 
                "📊 Analyze the sentiment of the uploaded content",
                "💡 What insights can you extract from these documents?",
                "❓ Ask me any general knowledge question too!"
            ]
        else:
            return [
                "🤔 What's the latest in AI and technology?",
                "📚 Help me learn about a specific topic",
                "💭 Let's brainstorm some creative ideas",
                "🧮 Help me solve a math or logic problem",
                "📝 Assist with writing or content creation",
                "🌍 Tell me about current events or history"
            ]