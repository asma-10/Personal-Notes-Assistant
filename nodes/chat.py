from graphs.states import State
from config.llm import llm


def chat(state: State):
    user_message = state["user_message"]
    memories = state["matched_memory"]

    memory_text = "\n".join(str(m) for m in memories) if memories else "No known facts yet."

    message = [
        {'role': 'system', 'content': f"You are a helpful and nice assistant. Here are known facts about the user:\n{memory_text}"},
        {'role': 'user', 'content': user_message}
    ]

    response = llm.invoke(message)
    return {'answer': response.content}