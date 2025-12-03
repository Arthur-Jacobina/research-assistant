from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import (
    InternalError,
    InvalidParamsError,
    Task,
    TextPart,
    UnsupportedOperationError,
)
from a2a.utils.errors import ServerError
from braintrust import current_span, traced

from llm.agent import workflow
from core.logger import logger
# from memory.mem0 import Mem0Memory
from memory.raw import RawMemory


class DspyAgentExecutor(AgentExecutor):
    """Memory-aware DSPy AgentExecutor with per-user context."""

    def __init__(self) -> None:
        self.memory = RawMemory()

    @traced
    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        """Execute the task."""
        with logger.start_span():
            error = self._validate_request(context)
            if error:
                raise ServerError(error=InvalidParamsError())

            updater = TaskUpdater(
                event_queue, context.task_id, context.context_id
            )
            if not context.current_task:
                await updater.submit()

            await updater.start_work()

            query = context.get_user_input()
            try:
                ctx = await self.memory.retrieve(
                    query=query, user_id=context.context_id
                )
                # Get the appropriate ReAct agent based on user intent
                agent = workflow(user_input=str(query))
                # Execute with the signature's expected fields
                result = agent(user_input=str(query), context=ctx)
                current_span().log(input=query, output=result.response)
                await self.memory.save(
                    user_id=context.context_id,
                    user_input=query,
                    assistant_response=result.response,
                )
            except Exception as e:
                current_span().log(error=e)
                raise ServerError(error=InternalError()) from e
            
            # Task is complete when we have a response
            await updater.add_artifact(
                [TextPart(text=result.response)],
                name='answer',
            )
            await updater.complete()

    async def cancel(
        self, request: RequestContext, event_queue: EventQueue
    ) -> Task | None:
        """Cancel the task."""
        raise ServerError(error=UnsupportedOperationError())

    def _validate_request(self, context: RequestContext) -> bool:
        return False