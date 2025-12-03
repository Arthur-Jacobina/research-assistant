from __future__ import annotations

import logging
import os

import click
import uvicorn
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from utils.agent_executor import DspyAgentExecutor


logger = logging.getLogger(__name__)
logging.basicConfig()

@click.command()
@click.option('--host', 'host', default='localhost')
@click.option('--port', 'port', default=10020)
def main(host: str, port: int):
    """A2A DSPy Sample Server with Bearer Token Authentication."""
    skill = AgentSkill(
        id='dspy_agent',
        name='Research Agent',
        description='A research agent that can answer questions related to any scientific paper.',
        tags=['Research', 'Memory', 'Paper'],
        examples=[
            'What is the main idea of the paper?',
            'What is the main contribution of the paper?',
            'What is the main result of the paper?',
            'What is the main conclusion of the paper?',
            'What is the main future work of the paper?',
            'What is the main related work of the paper?',
            'What is the main related work of the paper?',
        ],
    )

    agent_executor = DspyAgentExecutor()
    agent_card = AgentCard(
        name='Research Agent',
        description='A research agent that can answer questions related to any scientific paper.',
        url=f'http://{host}:{port}/',
        version='1.0.0',
        default_input_modes=['text'],
        default_output_modes=['text'],
        capabilities=AgentCapabilities(streaming=True),
        skills=[skill],
    )
    request_handler = DefaultRequestHandler(
        agent_executor=agent_executor, task_store=InMemoryTaskStore()
    )

    server = A2AStarletteApplication(agent_card, request_handler)
    starlette_app = server.build()
    
    starlette_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    uvicorn.run(starlette_app, host=host, port=port)


if __name__ == '__main__':
    main()
