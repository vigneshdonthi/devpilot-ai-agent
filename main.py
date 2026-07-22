from agent import agent
from langchain_core.messages import AIMessage


config = {
    "configurable": {
        "thread_id": "devpilot-session-1"
    }
}


print("DevPilot started. Type 'exit' to stop.\n")


while True:

    user_input = input("You: ")
    if not user_input:
        continue

    if user_input.lower() == "exit":
        break

    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": user_input
                }
            ]
        },
        config=config
    )

    print("\nTools used:")

    tool_found = False

    for message in result["messages"]:

        if isinstance(message, AIMessage) and message.tool_calls:

            for tool_call in message.tool_calls:

                tool_found = True

                print(
                    f"  -> {tool_call['name']} "
                    f"{tool_call['args']}"
                )

    if not tool_found:
        print("  No tools used")

    print("\nDevPilot:")
    print(result["messages"][-1].content)
    print()