"""
Google Gemini AI Integration Module
This module provides integration with Google's Gemini AI API for natural language processing,
content generation, and multi-modal analysis.
"""

import os
from typing import Optional, List, Dict, Any
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("google-generativeai package not installed. Install with: pip install google-generativeai")


class GeminiAI:
    """
    Google Gemini AI client wrapper for seamless integration.
    Supports text generation, multi-turn conversations, and content analysis.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-pro"):
        """
        Initialize the Gemini AI client.
        
        Args:
            api_key (str, optional): Google Gemini API key. If not provided, 
                                    reads from GOOGLE_GEMINI_API_KEY environment variable.
            model (str): Model name to use. Defaults to "gemini-pro".
        
        Raises:
            ValueError: If API key is not provided and not in environment variables.
            ImportError: If google-generativeai is not installed.
        """
        if not GEMINI_AVAILABLE:
            raise ImportError("google-generativeai is not installed. Install with: pip install google-generativeai")
        
        self.api_key = api_key or os.getenv("GOOGLE_GEMINI_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "API key not provided. Set GOOGLE_GEMINI_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        genai.configure(api_key=self.api_key)
        self.model_name = model
        self.model = genai.GenerativeModel(model)
        self.conversation_history: List[Dict[str, str]] = []
        
        logger.info(f"Gemini AI initialized with model: {model}")
    
    def generate_text(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        top_p: float = 0.9,
        top_k: int = 40
    ) -> str:
        """
        Generate text based on a prompt.
        
        Args:
            prompt (str): The input prompt for text generation.
            temperature (float): Controls randomness (0.0 to 2.0). Higher = more creative.
            max_tokens (int): Maximum length of generated response.
            top_p (float): Nucleus sampling parameter.
            top_k (int): Top-k sampling parameter.
        
        Returns:
            str: Generated text response.
        
        Raises:
            Exception: If API call fails.
        """
        try:
            generation_config = genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
                top_p=top_p,
                top_k=top_k
            )
            
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            logger.info("Text generation completed successfully")
            return response.text
        
        except Exception as e:
            logger.error(f"Error generating text: {str(e)}")
            raise
    
    def start_conversation(self) -> None:
        """Initialize a new multi-turn conversation."""
        self.conversation_history = []
        logger.info("New conversation started")
    
    def chat(self, user_message: str) -> str:
        """
        Send a message in the conversation and get a response.
        
        Args:
            user_message (str): User's message in the conversation.
        
        Returns:
            str: Assistant's response.
        
        Raises:
            Exception: If API call fails.
        """
        try:
            # Add user message to history
            self.conversation_history.append({
                "role": "user",
                "content": user_message
            })
            
            # Build conversation context
            conversation_text = ""
            for msg in self.conversation_history:
                role = "User" if msg["role"] == "user" else "Assistant"
                conversation_text += f"{role}: {msg['content']}\n"
            
            # Generate response
            response = self.model.generate_content(conversation_text)
            assistant_response = response.text
            
            # Add assistant response to history
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_response
            })
            
            logger.info("Chat message processed successfully")
            return assistant_response
        
        except Exception as e:
            logger.error(f"Error in chat: {str(e)}")
            raise
    
    def analyze_content(self, content: str, analysis_type: str = "general") -> Dict[str, Any]:
        """
        Analyze content using Gemini AI.
        
        Args:
            content (str): Content to analyze.
            analysis_type (str): Type of analysis (general, sentiment, summary, etc.).
        
        Returns:
            Dict[str, Any]: Analysis results.
        """
        prompts = {
            "sentiment": f"Analyze the sentiment of the following text:\n{content}",
            "summary": f"Provide a concise summary of the following text:\n{content}",
            "keywords": f"Extract key themes and keywords from the following text:\n{content}",
            "general": f"Analyze the following content:\n{content}"
        }
        
        prompt = prompts.get(analysis_type, prompts["general"])
        
        try:
            response = self.generate_text(prompt)
            logger.info(f"Content analysis ({analysis_type}) completed")
            
            return {
                "analysis_type": analysis_type,
                "content": content[:100] + "..." if len(content) > 100 else content,
                "result": response
            }
        
        except Exception as e:
            logger.error(f"Error analyzing content: {str(e)}")
            raise
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """
        Get the current conversation history.
        
        Returns:
            List[Dict[str, str]]: List of conversation messages.
        """
        return self.conversation_history
    
    def clear_conversation(self) -> None:
        """Clear the conversation history."""
        self.conversation_history = []
        logger.info("Conversation history cleared")


def main():
    """Example usage of GeminiAI."""
    try:
        # Initialize Gemini AI
        gemini = GeminiAI()
        
        # Example 1: Simple text generation
        print("=" * 50)
        print("Example 1: Text Generation")
        print("=" * 50)
        prompt = "Explain quantum computing in simple terms"
        response = gemini.generate_text(prompt)
        print(f"Prompt: {prompt}")
        print(f"Response: {response}\n")
        
        # Example 2: Multi-turn conversation
        print("=" * 50)
        print("Example 2: Multi-turn Conversation")
        print("=" * 50)
        gemini.start_conversation()
        
        messages = [
            "What are the benefits of renewable energy?",
            "Can you explain solar energy in detail?",
            "What about wind energy?"
        ]
        
        for msg in messages:
            print(f"User: {msg}")
            response = gemini.chat(msg)
            print(f"Assistant: {response}\n")
        
        # Example 3: Content analysis
        print("=" * 50)
        print("Example 3: Content Analysis")
        print("=" * 50)
        content = "I absolutely love this product! It works perfectly and exceeded my expectations."
        analysis = gemini.analyze_content(content, analysis_type="sentiment")
        print(f"Analysis Type: {analysis['analysis_type']}")
        print(f"Result: {analysis['result']}\n")
    
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
