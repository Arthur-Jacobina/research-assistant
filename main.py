import dspy
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import requests
import re
from typing import List, Optional

from arxiv_parser import ArxivParser

load_dotenv()

lm = dspy.LM(model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"))
dspy.configure(lm=lm)

def get_paper_text(url: str) -> str:
    """Get the text of a paper from a url."""
    parser = ArxivParser(url)
    return parser.parse_url_to_markdown(url)

class PaperAnalyzerSignature(dspy.Signature):
    """Analyze a paper and return a summary of the paper."""
    url: str = dspy.InputField(description="The url of the paper to analyze.")
    requirements: str = dspy.OutputField(description="The requirements to understanding the paper. Include papers, topics and links")

ag = dspy.ReAct(PaperAnalyzerSignature, tools=[get_paper_text])

if __name__ == "__main__":
    # Example usage
    print (ag(url="https://arxiv.org/html/2511.09831v1"))