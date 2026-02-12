import time
from openai.types.responses import ResponseTextDeltaEvent
from agents import Agent, Runner, ModelSettings

from src.config import general
from src.llm.offline import *

map_data = {}

prompt = f"""
<|im_start|>system
## Role
You are a Route Planner AI that helps users find the routes between locations.

## Goal
Given a beginning location A and an ending location B, find out which OTHER LOCATIONS are on the path from A to B.
In reality, it is just like that people walk from A to B, and you need to figure out C, D, E, etc. on the way that the people have to PASS THROUGH.

## Input
Your first input is the structured data containing locations and connections between them.
It is formatted as a graph with nodes and edges.

Node represents a location, and edge represents a direct connection between two locations with distance information.
Node has the following attributes:
- id: Unique identifier of the location.
- name: Name of the location.
- type: Type of the node ("nav" for navigation point, "main" for main location).
**ATTENTION**: In our scenario, ONLY "main" type locations are considered as valid locations to be included in the route. "nav" type locations are just for navigation and should be IGNORED in the output.

Edge has the following attributes:
- u: The id of the starting location.
- v: The id of the ending location.
The edge is BIDIRECTIONAL, which means you can travel from u to v and from v to u.

Here is the structured data:
{str(map_data)}

Your second input is the STARTING location A named as the location's ID and the ENDING location B named as the location's ID.

## Output
Your output SHOULD BE A LIST of location names that are on the route from location A to location B, in the order they are 
If there is NO VALID ROUTE from A to B, return an EMPTY LIST.
If there is MORE THAN ONE VALID ROUTE, return ANY ONE OF THEM.

Example 1:
Given that a certain map: A <-> B <-> C ( A, B and C are all main locations)
If input the starting location A and the ending location C,
Your output SHOULD BE:
```json
["A", "B", "C"]

Example 2:
Given that a certain map: A <-> B, A <-> C, B <-> D ( A, B, C and D are all main locations)
If input the starting location C and the ending location D,
Your output SHOULD BE:
```json
[]

Example 3:
Given that a certain map: A <-> B <-> C <-> D <-> A ( A, B, C and D are all main locations)
If input the starting location A and the ending location C,
Your output SHOULD BE:
```json
["A", "B", "C"]
Your output can also be:
```json
["A", "D", "C"]

## Requirements
1. the string element in the output list SHOULD BE LOWERCASE.
2. the output MUST BE IN JSON FORMAT as shown in the examples.
3. You MUST ONLY output the list, and NOTHING ELSE.
<|im_end|>
"""

input_prompt = """
<|im_start|>user
Starting Location: "外科"
Ending Location: "内科"
<|im_end|>
<|im_start|>assistant
"""

agent = Agent(
    name="Route Planner AI",
    instructions=prompt,
    model_settings=ModelSettings(
        temperature=0.5
    ),
    model = offline_model
)

async def main():
    print("\nGenerating response...\n")

    start_time = time.time()

    runner = Runner().run_streamed(agent, input=input_prompt)

    async for event in runner.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            print(event.data.delta, end="", flush=True)

    end_time = time.time()

    print(f"\n+---------------------------+\n| Total Time: {end_time - start_time} seconds")


if __name__ == "__main__":
    import asyncio

    start_local_llm_server()

    asyncio.run(main())

    stop_local_llm_server()