import dspy
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import requests
import re
from typing import List, Optional, Dict

from arxiv_parser import ArxivParser
from memory.raw import retrieve_context, save_interaction

load_dotenv()

lm = dspy.LM(model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"))
dspy.configure(lm=lm)

def get_paper_text(url: str) -> str:
    """Get the text of a paper from a url."""
    parser = ArxivParser(url)
    return parser.parse_url_to_markdown(url)

class PaperAnalyzerSignature(dspy.Signature):
    """Analyze a paper and return a summary of the paper."""
    user_input: str = dspy.InputField(description="The user query about the paper.")
    context: List[Dict] = dspy.InputField(description="The context of the conversation.")
    response: str = dspy.OutputField(description="The response to the user query.")

ag = dspy.ReAct(PaperAnalyzerSignature, tools=[get_paper_text])

def chat_turn(user_input: str, user_id: str) -> str:
    # Retrieve context
    context = retrieve_context(user_input, user_id)
    
    # Generate response
    response = ag(user_input=user_input, context=context)
    
    # Save interaction
    save_interaction(user_id, user_input, response.response)
    
    return response.response

if __name__ == "__main__":
    print("Welcome to your personal Research Agent! How can I assist you with your research today?")
    user_id = "alice"
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("Research Agent: Thank you for using our research service. Have a great research!")
            break
        
        response = chat_turn(user_input, user_id)
        print(f"Research Agent: {response}")