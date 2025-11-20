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
from database.qdrant import insert_paper, get_paper

load_dotenv()

mlflow.dspy.autolog()
lm = dspy.LM(model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"))
dspy.configure(lm=lm)
Memory = RawMemory()

def get_paper_text(url: str, query: Optional[str] = None) -> str:
    """Get the text of a paper from a url."""
    paper = get_paper(url, query)
    if paper is not None:
        return paper["markdown"]
    else:
        parser = ArxivParser(url)
        markdown = parser.parse_url_to_markdown(url)
        insert_paper(url, markdown)
        return markdown

class PaperAnalyzerSignature(dspy.Signature):
    """Analyze a paper and return a summary of the paper. When there's a clear query use it in the get_paper_text tool."""
    user_input: str = dspy.InputField(description="The user query about the paper.")
    context: List[Dict] = dspy.InputField(description="The context of the conversation.")
    response: str = dspy.OutputField(description="The response to the user query.")

ag = dspy.ReAct(PaperAnalyzerSignature, tools=[get_paper_text])

@mlflow.trace
def chat_turn(user_input: str, user_id: str, session_id: str) -> str:
    mlflow.update_current_trace(
        metadata={
            "mlflow.trace.user": user_id,  
            "mlflow.trace.session": session_id,
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
    session_id = "123"

    while True:
        user_input = input("You: ")
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("Research Agent: Thank you for using our research service. Have a great research!")
            break
        
        response = chat_turn(user_input, user_id, session_id)
        print(f"Research Agent: {response}")