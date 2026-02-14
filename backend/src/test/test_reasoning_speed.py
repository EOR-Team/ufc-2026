import time
from src.llm.offline.reason import offline_reasoning_model

result = offline_reasoning_model.create_chat_completion(
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Use your REASONING and THINKING skills to answer the following question: What is 2 + 2? You MUST ONLY output the final answer, without any other words or explanations."},
    ],
    stream=True,
    response_format={"type": "text"},
)

all_output = ""

start_time = time.time()

for chunk in result:
    delta = chunk["choices"][0]["delta"]
    if "role" in delta:
        print(delta["role"], end=":", flush=True)
        all_output += delta["role"] + ":"
    if "content" in delta:
        print(delta["content"], end="", flush=True)
        all_output += delta["content"]

end_time = time.time()

print(f"\nTime taken: {end_time - start_time:.2f} seconds")
print(f"Word count: {len(all_output.split())}")
