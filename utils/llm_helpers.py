from anthropic import Anthropic


class Conversation:
    def __init__(self, tools=[]):
        self.tools = tools
        self.messages = []
        self.client = Anthropic()
        self.tool_call_map = {}

    def add_message(self, message):
        print(f"[USER]: {message}")
        self.messages.append(
            {
                "role": "user",
                "content": message,
            }
        )
        return self.call_model()

    def call_model(self):
        res = self.client.messages.create(
            tools=self.tools,
            max_tokens=1024,
            messages=self.messages,
            model="claude-sonnet-4-20250514",
        )
        tool_calls = []
        for block in res.content:
            if block.type == "tool_use":
                tool_calls.append(block)
                # This is just used for logging
                self.tool_call_map[block.id] = block.name
                print(f"[TOOL:CALL]: {block.name}")
            elif block.type == "text":
                print(f"[ASSISTANT]: {block.text}")
        self.messages.append(
            {
                "role": "assistant",
                "content": serialize_content_from_api(res.content),
            }
        )

        if len(tool_calls) > 1:
            raise ValueError("Only one tool call is supported")

        return {
            "tool_call": tool_calls[0] if tool_calls else None,
            "last_message": self.messages[-1],
        }

    def add_tool_result(self, tool_use_id, content):
        print(f"[TOOL:RESULT]: {self.tool_call_map[tool_use_id]}")
        self.messages.append(
            {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_use_id,
                        "content": content,
                    }
                ],
            }
        )
        return self.call_model()

    def get_messages(self):
        return self.messages


def serialize_content_from_api(content):
    return [block.to_dict() for block in content]
