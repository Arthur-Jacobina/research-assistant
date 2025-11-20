import dspy
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import requests
import re
from typing import List, Optional, Dict
import mlflow

from arxiv_parser import ArxivParser
from memory.raw import RawMemory
from database.main import insert_paper, get_paper

load_dotenv()

mlflow.dspy.autolog()
lm = dspy.LM(model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"))
dspy.configure(lm=lm)
Memory = RawMemory()

local_paper_cache: Dict[str, str] = {}

def get_paper_text(url: str) -> str:
    """Get the text of a paper from a url."""
    paper = get_paper(url)
    if paper is not None:
        return paper["markdown"]
    else:
        parser = ArxivParser(url)
        markdown = parser.parse_url_to_markdown(url)
        insert_paper(url, markdown)
        return markdown

class PaperAnalyzerSignature(dspy.Signature):
    """Analyze a paper and return a summary of the paper."""
    user_input: str = dspy.InputField(description="The user query about the paper.")
    context: List[Dict] = dspy.InputField(description="The context of the conversation.")
    response: str = dspy.OutputField(description="The response to the user query.")

ag = dspy.ReAct(PaperAnalyzerSignature, tools=[get_paper_text])

@mlflow.trace
def chat_turn(user_input: str, user_id: str) -> str:
    mlflow.update_current_trace(
        metadata={
            "mlflow.trace.user": user_id,  # Links trace to specific user
            "mlflow.trace.session": user_id,  # Groups trace with conversation
        }
    )
    # Retrieve context
    context = Memory.retrieve(user_input, user_id)
    
    # Generate response
    response = ag(user_input=user_input, context=context)
    
    # Save interaction
    Memory.save(user_id, user_input, response.response)
    
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