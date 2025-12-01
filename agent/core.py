import os

import dspy

from dotenv import load_dotenv

from .tools import get_paper_text


load_dotenv()

lm = dspy.LM(model='gpt-4o-mini', api_key=os.getenv('OPENAI_API_KEY'))
dspy.configure(lm=lm)

class PaperAnalyzerSignature(dspy.Signature):
    """Analyze a paper and return a summary of the paper. When there's a clear query use it in the get_paper_text tool. Always give a comprehensive response."""
    user_input: str = dspy.InputField(description='The user query about the paper.')
    context: list[dict] = dspy.InputField(description='The context of the conversation.')
    response: str = dspy.OutputField(description='The response to the user query.')

ag = dspy.ReAct(PaperAnalyzerSignature, tools=[get_paper_text])
