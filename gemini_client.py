# gemini_client.py
import os
import time
import google.generativeai as genai

GEMINI_MODEL = "gemini-2.5-flash"  # Updated to match api.py
MAX_RETRIES = 3

class GeminiClient:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("Missing GEMINI_API_KEY environment variable")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(GEMINI_MODEL)

    def summarize_log(self, log_text: str) -> str:
        """
        Summarize logs into plain English with retries & token safety.
        """
        prompt = f"""
        You are SmartGuard AI. Summarize the following application log
        in plain English. Include:
        - Root cause (if visible)
        - Severity (warning/critical/info)
        - Timestamp context if present
        - Suggested fix if possible

        Log:
        {log_text[:2000]}  # truncate to avoid token overflow
        """

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = self.model.generate_content(prompt)
                return response.text.strip()
            except Exception as e:
                print(f"[Gemini] Attempt {attempt} failed: {e}")
                time.sleep(2 * attempt)  # backoff
        return "AI summarization failed after retries."
    
    def analyze_logs(self, logs_data: str) -> str:
        """
        Analyze multiple logs and provide insights.
        """
        prompt = f"""
        You are SmartGuard AI. Analyze these logs and provide insights:
        {logs_data[:3000]}
        
        Provide:
        - Key issues identified
        - Severity assessment
        - Root cause analysis
        - Recommended actions
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"[Gemini] Analysis failed: {e}")
            return "AI analysis failed."
    
    def chat_response(self, user_message: str, context_data: str = "") -> str:
        """
        Generate conversational response with system context.
        """
        prompt = f"""
        You are SmartGuard AI Assistant. Answer this question: "{user_message}"
        
        System context:
        {context_data}
        
        Provide a helpful, concise answer about the system status, any issues, or suggestions.
        If there are errors or warnings, explain what might be causing them and suggest fixes.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"[Gemini] Chat failed: {e}")
            return "Sorry, I couldn't process your request. Please try again."
