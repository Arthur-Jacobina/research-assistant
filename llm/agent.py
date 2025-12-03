import os

import dspy

from dotenv import load_dotenv

from .tools import get_paper, get_sections, get_section, get_subsections

from braintrust.wrappers.dspy import BraintrustDSpyCallback

load_dotenv()

lm = dspy.LM(model='gpt-4o-mini', api_key=os.getenv('OPENAI_API_KEY'))
dspy.configure(lm=lm, callbacks=[BraintrustDSpyCallback()])

class PaperAnalyzerSignature(dspy.Signature):
    """Analyze a paper and return a summary of the paper. When there's a clear query use it in the get_paper_text tool. Always give a comprehensive response."""
    user_input: str = dspy.InputField(description='The user query about the paper.')
    context: list[dict] = dspy.InputField(description='The context of the conversation.')
    response: str = dspy.OutputField(description='The response to the user query.')

class IntentAnalyzerSignature(dspy.Signature):
    """Analyze if the user want to learn more generic info about the paper, math related info, section specific info or about the requirements for understanding the paper."""
    user_input: str = dspy.InputField(description='The user query about the paper.')
    intent: str = dspy.OutputField(description='The intent of the user query. Possible values are: "generic", "math", "section", "requirements".')

class GenericInfoSignature(dspy.Signature):
    """Provide generic information about the paper. You will use the abstract, introduction and last section of the paper to answer the user query."""
    user_input: str = dspy.InputField(description='The user query about the paper.')
    context: list[dict] = dspy.InputField(description='The context of the conversation.')
    response: str = dspy.OutputField(description='The response to the user query. Always give a comprehensive response.')

class MathInfoSignature(dspy.Signature):
    """Provide math related information about the paper. You will use the formulas and equations in the paper to answer the user query."""
    user_input: str = dspy.InputField(description='The user query about the paper.')
    context: list[dict] = dspy.InputField(description='The context of the conversation.')
    response: str = dspy.OutputField(description='The response to the user query. Always give a comprehensive response.')

class SectionInfoSignature(dspy.Signature):
    """Provide information about a specific section of the paper. You will use the section content and the abstract to answer the user query."""
    user_input: str = dspy.InputField(description='The user query about the paper.')
    context: list[dict] = dspy.InputField(description='The context of the conversation.')
    response: str = dspy.OutputField(description='The response to the user query. Always give a comprehensive response.')

class RequirementsInfoSignature(dspy.Signature):
    """Provide information about the requirements for understanding the paper. You will use the abstract and the introduction to answer the user query."""
    user_input: str = dspy.InputField(description='The user query about the paper.')
    context: list[dict] = dspy.InputField(description='The context of the conversation.')
    response: str = dspy.OutputField(description='The response to the user query. Always give a comprehensive response.')

intent_analyzer = dspy.Predict(IntentAnalyzerSignature)

def workflow(user_input: str) -> dspy.ReAct:
    """Analyze the user query and determine the intent."""
    intent = intent_analyzer(user_input=user_input)
    if intent.intent == "generic":
        return dspy.ReAct(GenericInfoSignature, tools=[get_paper, get_sections, get_section])
    elif intent.intent == "math":
        return dspy.ReAct(MathInfoSignature, tools=[get_paper, get_sections, get_section, get_subsections])
    elif intent.intent == "section":
        return dspy.ReAct(SectionInfoSignature, tools=[get_paper, get_sections, get_section, get_subsections])
    elif intent.intent == "requirements":
        return dspy.ReAct(RequirementsInfoSignature, tools=[get_paper, get_sections, get_section, get_subsections])
    else:
        return dspy.ReAct(PaperAnalyzerSignature, tools=[get_paper, get_sections, get_section, get_subsections])