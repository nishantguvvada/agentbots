from dataclasses import dataclass

from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.gemini import GeminiModel
import os
from dotenv import load_dotenv

load_dotenv()

import logfire
# logfire.configure()
logfire.configure(send_to_logfire='if-token-present')

class DatabaseConn:
    """This is a fake database for example purposes.

    In reality, you'd be connecting to an external database
    (e.g. PostgreSQL) to get information about customers.
    """

    @classmethod
    async def customer_name(cls, *, id: int) -> str | None:
        if id == 123:
            return 'John'
        else:
            return 'Nishant'

    @classmethod
    async def customer_balance(cls, *, id: int, include_pending: bool) -> float:
        if id == 123:
            return 123.45
        else:
            return 9600000.31
            # raise ValueError('Customer not found')

@dataclass
class SupportDependencies:  # dataclass is used to pass data, connections, and logic into the model that will be needed when running system prompt and tool functions.
    customer_id: int
    db: DatabaseConn
# This Pydantic model is used to constrain the structured data returned by the agent. From this simple definition, Pydantic builds the JSON Schema that tells the LLM how to return the data, and performs validation to guarantee the data is correct at the end of the run.
class SupportResult(BaseModel):  
    support_advice: str = Field(description='Advice returned to the customer')
    block_card: bool = Field(description="Whether to block the customer's card")
    risk: int = Field(description='Risk level of query', ge=0, le=10)

model = GeminiModel('gemini-1.5-flash', api_key=os.getenv('GEMINI_KEY'))

support_agent = Agent(  
    model,  
    deps_type=SupportDependencies, # input type
    result_type=SupportResult,  # output type
    system_prompt=(  
        'You are a support agent in our bank, give the '
        'customer support and judge the risk level of their query.'
    ),
)

@support_agent.system_prompt  
async def add_customer_name(ctx: RunContext[SupportDependencies]) -> str:
    customer_name = await ctx.deps.db.customer_name(id=ctx.deps.customer_id)
    return f"The customer's name is {customer_name!r}"

@support_agent.tool  
async def customer_balance(
    ctx: RunContext[SupportDependencies], include_pending: bool
) -> float:
    """Returns the customer's current account balance."""  
    return await ctx.deps.db.customer_balance(
        id=ctx.deps.customer_id,
        include_pending=include_pending,
    )

def main():
    deps = SupportDependencies(customer_id=123, db=DatabaseConn())
    result = support_agent.run_sync('What is my balance?', deps=deps)
    print(result.data)  
    """
    support_advice='Hello John, your current account balance, including pending transactions, is $123.45.' block_card=False risk=1
    """

    result = support_agent.run_sync('I just lost my card!', deps=deps)
    print(result.data)
    """
    support_advice="I'm sorry to hear that, John. We are temporarily blocking your card to prevent unauthorized transactions." block_card=True risk=8
    """

    result = support_agent.run_sync('Someone knows my card pin!', deps=deps)
    print(result.data)
    """
    support_advice='Someone knowing your card pin is a serious security issue. We have blocked your card as a precaution. Please contact us immediately to discuss further actions.' block_card=True risk=3
    """

if __name__ == '__main__':
    main()