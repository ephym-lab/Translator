import os
import json
from abc import ABC, abstractmethod
from openai import OpenAI

class AIService(ABC):
    @abstractmethod
    def get_response(self, user_input, system_prompt):
        pass

class OpenAIService(AIService):
    def __init__(self, api_key):
        self.api_key = api_key
        try:
            self.client = OpenAI(api_key=api_key)
        except ImportError:
            raise Exception("OpenAI module not found. Please install the 'openai' package.")

    def get_response(self, user_input, system_prompt):
        try:
            completion = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                temperature=0
            )
            return completion.choices[0].message.content
        except Exception as e:
            return json.dumps({"content": f"Error calling OpenAI API: {str(e)}", "query": ""})

class GeminiService(AIService):
    def __init__(self, api_key):
        self.api_key = api_key
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
        except ImportError:
            raise Exception("Google Generative AI module not found. Please install 'google-generativeai'.")

    def get_response(self, user_input, system_prompt):
        try:
            import google.generativeai as genai
            
            # Combine system prompt with user input since system_instruction may not be supported
            combined_prompt = f"{system_prompt}\n\nUser Request: {user_input}"
            
            model = genai.GenerativeModel('gemini-2.5-flash')
            response = model.generate_content(combined_prompt)
            return response.text
        except Exception as e:
            return json.dumps({"content": f"Error calling Gemini API: {str(e)}", "query": ""})

class GrokService(AIService):
    def __init__(self, api_key):
        self.api_key = api_key

    def get_response(self, user_input, system_prompt):
        import http.client
        try:
            conn = http.client.HTTPSConnection("api.x.ai")
            payload = json.dumps({
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                "model": "grok-3-latest",
                "stream": False,
                "temperature": 0
            })
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            conn.request("POST", "/v1/chat/completions", payload, headers)
            res = conn.getresponse()
            data = res.read()
            response_json = json.loads(data.decode("utf-8"))
            return response_json['choices'][0]['message']['content']
        except Exception as e:
            return json.dumps({"content": f"Error calling Grok API: {str(e)}", "query": ""})

class MockService(AIService):
    def get_response(self, user_input, system_prompt):
       return "Hello, this is a mocked dataset entry."

from app.core.config import settings

class AIServiceFactory:
    @staticmethod
    def get_service():
        provider = os.getenv("AI_PROVIDER", "openai").lower()
        
        if provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY") or getattr(settings, "OPENAI_API_KEY", None)
            if api_key:
                return OpenAIService(api_key)
        
        elif provider == "gemini":
            api_key = os.getenv("GEMINI_API_KEY") or getattr(settings, "GEMINI_API_KEY", None)
            if api_key:
                return GeminiService(api_key)
                
        elif provider == "grok":
            api_key = os.getenv("GROK_API_KEY") or getattr(settings, "GROK_API_KEY", None)
            if api_key:
                return GrokService(api_key)
        
        # Default to Mock if no keys or provider not recognized
        print(f"Warning: defaulting to MockService. Provider: {provider}")
        return MockService()
