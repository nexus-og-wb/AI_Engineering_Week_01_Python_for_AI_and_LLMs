import asyncio
import os
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

class ChatService:
    
    def __init__(self):
        api_key = os.environ["OPENROUTER_API_KEY"]

        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1"
        )

    async def stream(self, question: str):
        response = await self.client.chat.completions.create(
            model="nvidia/nemotron-3.5-lightning:free",
            messages=[
                {
                    "role": "user",
                    "content": question
                }
            ], 
            stream=True,
            stream_options={
                "include_usage": True,
            },
        )

        async for chunk in response:

            if chunk.choices:
                delta = chunk.choices[0].delta

                if delta.content:
                    yield {
                        "type": "content",
                        "content": delta.content,
                    }
            if chunk.usage:
                yield {
                    "type": "usage",
                    "usage": {
                        "prompt_tokens": chunk.usage.prompt_tokens,
                        "completion_tokens": chunk.usage.completion_tokens,
                        "total_tokens": chunk.usage.total_tokens,
                    },
                }


async def main():
    chat_service = ChatService()

    query = input("Query:")

    print ("Assistant: ", end="", flush=True)
    async for chunk in chat_service.stream(query):
        if chunk["type"] == "content":
            print(chunk["content"], end="", flush=True)
        elif chunk["type"] == "usage":
            print("\n\nUsage Information:")
            print(f"Prompt Tokens: {chunk['usage']['prompt_tokens']}")
            print(f"Completion Tokens: {chunk['usage']['completion_tokens']}")
            print(f"Total Tokens: {chunk['usage']['total_tokens']}")

    print("\n\nDone.")

if __name__ == "__main__":
    asyncio.run(main())