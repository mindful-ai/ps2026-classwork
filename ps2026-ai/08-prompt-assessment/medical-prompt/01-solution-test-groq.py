from openai import OpenAI
import json
from myprompts import MEDICAL_PROMPT

from groq import Groq

# Read API key from file

f = open(r"C:\Users\mindf\OneDrive\Projects\mindful-learning-academy\sapient-ai\classwork\ps2026-ai\key-vault\groq\api.key")
groq_api_key = f.read()
f.close()

# Initialize Groq client
client = Groq(api_key=groq_api_key)

# Select model
MODEL = "openai/gpt-oss-20b"


def build_prompt(user_query):

    # Prompt injection using formatted template
    prompt = f"""

"""
    
    # Use a named replacement to match templates that expect '{user_query}'
    prompt2 = MEDICAL_PROMPT.format(user_query=user_query, context=open("diabetes_context.txt").read() if open("diabetes_context.txt", "r") else "")

    return prompt2


def chat():

    print("\nMedical Assistant Powered by Groq")
    print("-" * 80)

    while True:

        # Get user input
        user_input = input("\nYou: ")

        # Exit condition
        if user_input.lower() in ["quit", "exit", "end"]:
            print("Goodbye!")
            break

        # Build the injected prompt
        final_prompt = build_prompt(user_input)

        # Show generated prompt (for debugging / learning)
        print("\n================ BUILT PROMPT ================\n")
        print(final_prompt)
        print("\n==============================================\n")

        try:

            # LLM call using Responses API
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "user", "content": final_prompt}
                ],
                max_tokens=1000,
            )

            # Extract model output
            ai_reply = response.choices[0].message.content

            # Pretty print JSON if possible
            try:
                parsed_json = json.loads(ai_reply)

                print("AI Response:\n")
                print(json.dumps(parsed_json, indent=4))

            except Exception:
                print("AI:", ai_reply)

        except Exception as e:
            print("Inference failed with error:", e)


# Run app
if __name__ == "__main__":
    chat()