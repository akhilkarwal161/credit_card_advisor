# agent.py
import os
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import Tool
from langchain_core.prompts import PromptTemplate
from langchain.agents import AgentExecutor, create_react_agent
from typing import Optional, List, Dict, Any
# Keep for internal type checking if needed later
from pydantic import BaseModel, Field, ValidationError

# Import database functions and recommender logic
from database import get_cards_by_criteria
from recommender import get_card_recommendations  # Import recommender function

# IMPORTANT: No need to explicitly set GOOGLE_API_KEY for Canvas environments.
# However, if running locally, you would typically set it as an environment variable or directly:
# Your API Key
os.environ["GOOGLE_API_KEY"] = "AIzaSyDQkuKR0W6XyhOmUKcfNYnb-6KOv8yj0Ew"

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)

# Global placeholder for user data - the agent will update this
_temp_user_data_storage = {
    'monthly_income': None,
    'spending_habits': {},
    'preferred_benefits': [],
    'existing_cards': [],
    'credit_score': None
}

# --- Pydantic Models for Internal Type Checking (not directly for tool input schema) ---
class UserUpdateInput(BaseModel):
    """Internal model for validating updated user data fields."""
    monthly_income: Optional[float] = Field(
        None, description="The user's monthly income in INR.")
    spending_habits: Optional[Dict[str, float]] = Field(
        None, description="Approximate monthly spending on categories like fuel, travel, groceries, and dining. Format as a dictionary, e.g., {'fuel': 2000, 'groceries': 5000}.")
    preferred_benefits: Optional[List[str]] = Field(
        None, description="List of preferred benefits, e.g., ['cashback', 'lounge access']. If user says 'any', provide ['any'].")
    existing_cards: Optional[List[str]] = Field(
        None, description="List of existing credit card names, or an empty list if none.")
    credit_score: Optional[int] = Field(
        None, description="The user's approximate credit score (numerical value) or None if unknown.")


# --- Tool Functions ---


def get_credit_cards_tool(data_json_string: str) -> str:
    """
    Fetches and processes credit card recommendations based on user's monthly income, credit score,
    and preferred benefits. It expects a pure JSON string and extracts parameters after parsing.
    Returns a JSON string of a list of recommended cards, each with name, key reasons, and reward simulation.
    """
    print(
        f"get_credit_cards_tool: Received raw string input: '{data_json_string}'")

    global _temp_user_data_storage  # Access the global storage for full context

    try:
        # Aggressively strip any surrounding characters including markdown backticks and whitespace
        cleaned_json_string = data_json_string.strip().strip('`').strip()

        if not cleaned_json_string:
            raise ValueError("Input string is empty after cleaning.")

        parsed_input_dict = json.loads(cleaned_json_string)
        print(
            f"get_credit_cards_tool: Parsed JSON string: {parsed_input_dict}")

        user_income = parsed_input_dict.get('user_income')
        user_credit_score = parsed_input_dict.get('user_credit_score')
        preferred_benefits_str = parsed_input_dict.get(
            'preferred_benefits', "")

        # Basic type checking and error handling for extracted values
        if not isinstance(user_income, (int, float)):
            raise ValueError(
                f"Invalid type for user_income: {type(user_income)}")
        if not isinstance(user_credit_score, int):
            raise ValueError(
                f"Invalid type for user_credit_score: {type(user_credit_score)}")
        if not isinstance(preferred_benefits_str, str):
            raise ValueError(
                f"Invalid type for preferred_benefits: {type(preferred_benefits_str)}")


        benefits_list = [b.strip().lower() for b in preferred_benefits_str.split(',')
                         ] if preferred_benefits_str else []

        if 'any' in benefits_list:  # Handle "any" as a special case for benefits
            raw_cards = get_cards_by_criteria(
                user_income, user_credit_score, [])
        else:
            raw_cards = get_cards_by_criteria(
                user_income, user_credit_score, benefits_list)

        # Use the recommender to get the final, ranked recommendations
        final_recommendations = get_card_recommendations(
            raw_cards, _temp_user_data_storage)

        # Return the recommendations as a JSON string
        return json.dumps(final_recommendations)

    except json.JSONDecodeError as e:
        print(f"get_credit_cards_tool: JSONDecodeError: {e}")
        return f"Error: Invalid JSON format for get_credit_cards_tool. Please ensure your Action Input is a pure JSON object string: {e}"
    except ValueError as e:
        print(f"get_credit_cards_tool: ValueError: {e}")
        return f"Error: Missing or invalid data types for get_credit_cards_tool: {e}"
    except Exception as e:
        print(f"get_credit_cards_tool: General Error: {e}")
        return f"Error fetching credit card recommendations: {e}"


# Expects a single string argument
def update_user_data_tool_func(data_json_string: str) -> str:
    """
    Updates the global user data dictionary with provided information.
    It expects a pure JSON string and updates the storage after parsing.
    """
    global _temp_user_data_storage

    print(
        f"update_user_data_tool_func: Received raw string input: '{data_json_string}'")

    try:
        # Aggressively strip any surrounding characters including markdown backticks and whitespace
        cleaned_json_string = data_json_string.strip().strip('`').strip()

        if not cleaned_json_string:
            raise ValueError("Input string is empty after cleaning.")

        parsed_input_dict = json.loads(cleaned_json_string)
        print(
            f"update_user_data_tool_func: Parsed JSON string: {parsed_input_dict}")

        # Manually update _temp_user_data_storage with type checking, no explicit conversions unless necessary
        if 'monthly_income' in parsed_input_dict and isinstance(parsed_input_dict['monthly_income'], (int, float)):
            _temp_user_data_storage['monthly_income'] = parsed_input_dict['monthly_income']
        elif 'monthly_income' in parsed_input_dict and parsed_input_dict['monthly_income'] is not None:
            # If it's a string, try converting to float, otherwise warn
            try:
                _temp_user_data_storage['monthly_income'] = float(
                    parsed_input_dict['monthly_income'])
            except ValueError:
                print(
                    f"Warning: Could not convert monthly_income to float: {parsed_input_dict['monthly_income']}")
                # Reset or handle appropriately
                _temp_user_data_storage['monthly_income'] = None

        if 'spending_habits' in parsed_input_dict and isinstance(parsed_input_dict['spending_habits'], dict):
            _temp_user_data_storage['spending_habits'] = parsed_input_dict['spending_habits']
        elif 'spending_habits' in parsed_input_dict:
            print(
                f"Warning: Invalid type for spending_habits: {parsed_input_dict['spending_habits']}")

        if 'preferred_benefits' in parsed_input_dict and isinstance(parsed_input_dict['preferred_benefits'], list):
            _temp_user_data_storage['preferred_benefits'] = parsed_input_dict['preferred_benefits']
        elif 'preferred_benefits' in parsed_input_dict:
            print(
                f"Warning: Invalid type for preferred_benefits: {parsed_input_dict['preferred_benefits']}")

        if 'existing_cards' in parsed_input_dict and isinstance(parsed_input_dict['existing_cards'], list):
            _temp_user_data_storage['existing_cards'] = parsed_input_dict['existing_cards']
        elif 'existing_cards' in parsed_input_dict:
            print(
                f"Warning: Invalid type for existing_cards: {parsed_input_dict['existing_cards']}")

        if 'credit_score' in parsed_input_dict and isinstance(parsed_input_dict['credit_score'], int):
            _temp_user_data_storage['credit_score'] = parsed_input_dict['credit_score']
        elif 'credit_score' in parsed_input_dict and parsed_input_dict['credit_score'] is not None:
            # If it's a float, try converting to int, otherwise warn
            try:
                _temp_user_data_storage['credit_score'] = int(
                    parsed_input_dict['credit_score'])
            except ValueError:
                print(
                    f"Warning: Could not convert credit_score to int: {parsed_input_dict['credit_score']}")
                # Reset or handle appropriately
                _temp_user_data_storage['credit_score'] = None

        print(
            f"update_user_data_tool_func: Current _temp_user_data_storage after merge: {_temp_user_data_storage}")
        return "User data updated successfully."
    except json.JSONDecodeError as e:
        print(f"update_user_data_tool_func: JSONDecodeError: {e}")
        return f"Error: Invalid JSON format for data update. Please ensure your Action Input is a pure JSON object string: {e}"
    except Exception as e:
        print(f"update_user_data_tool_func: General Error during update: {e}")
        return f"Error updating user data: {e}"


# List of tools available to the LangChain agent.
tools = [
    Tool(
        name="get_credit_cards_tool",
        func=get_credit_cards_tool,
        # Removed args_schema for get_credit_cards_tool to manually parse input
        description="Useful for fetching and processing credit card recommendations. The Action Input MUST be a pure JSON string (e.g., '{\"user_income\": 50000.0, \"user_credit_score\": 750, \"preferred_benefits\": \"cashback\"}'). Do NOT include any markdown formatting like triple backticks (`). Fields: 'user_income' (float), 'user_credit_score' (int), and 'preferred_benefits' (optional, comma-separated string)."
    ),
    Tool(
        name="update_user_data_tool",
        func=update_user_data_tool_func,
        # args_schema is removed here, as the function now expects a single raw string
        description="Call this tool to update the user's collected data. The Action Input MUST be a pure JSON string (e.g., '{\"monthly_income\": 50000.0}'). Do NOT include any markdown formatting like triple backticks (`). Fields: 'monthly_income' (float), 'spending_habits' (dict), 'preferred_benefits' (list of strings), 'existing_cards' (list of strings), or 'credit_score' (int)."
    ),
]

# Prompt template string - DEFINED HERE (moved for correct order)
_prompt_template_string = """
You are a super friendly and incredibly helpful credit card advisor! Your main goal is to make finding the perfect credit card an absolute breeze for users, all through a warm, clear, and genuinely empathetic conversation. Let's make this a delightful experience!

To help users find their ideal card, we need a little bit of information from them. We'll go through it **step-by-step, one question at a time**, so it's nice and easy. And don't worry, I'll always acknowledge your input with a friendly remark before moving on to the next exciting detail!

Here's the essential info we'll gather, in a friendly flow:

1.  **Your Monthly Income (in INR):**
    * **How to ask:** Let's start with your approximate monthly income in Indian Rupees. What's that figure looking like for you? Feel free to ask this in a few different, inviting ways!
    * **Expected input:** Just a numerical value, please! 😊

2.  **Your Spending Habits:**
    * **How to ask:** Wonderful! With your income noted, let's explore your monthly spending a bit. Could you share your approximate monthly spends on categories like fuel, travel, groceries, and dining? A simple "category: amount" format works perfectly (e.g., 'fuel: 2000, groceries: 5000'). This helps us understand your lifestyle better!
    * **Expected input:** A lovely list of categories and their approximate amounts.

3.  **Your Preferred Benefits:**
    * **How to ask:** Fantastic, almost there! Now, what kind of benefits really excite you in a credit card? Are you dreaming of cashback, accumulating travel points, enjoying lounge access, or something else? Just let me know your top preferences, separated by commas! If you're open to anything, simply say 'any'!
    * **Expected input:** A comma-separated list of benefits, or the word 'any'.

4.  **Your Existing Cards (Optional):**
    * **How to ask:** Just one more quick question about your current cards, if any! Do you happen to hold any existing credit cards right now? If not, no worries at all, just say 'no'!
    * **Expected input:** A list of card names, or 'no'.

5.  **Your Approximate Credit Score:**
    * **How to ask:** Last but not least, your approximate credit score! This helps us find cards you're more likely to qualify for. What's that number looking like for you (e.g., 750)? If you're unsure, it's totally fine to say 'unknown'!
    * **Expected input:** A numerical value or 'unknown'.

**✨ CRITICAL BEHAVIOR GUIDELINES FOR ME (Your Friendly Advisor)! ✨**

* **A. Information Gathering is a Breeze:** I *promise* to go through our list and ask for only **one piece of information at a time**. No overwhelming you with multiple questions at once! My tone will always be super polite and helpful.
* **B. Data Storage is My Secret Power:** As soon as I lovingly understand each piece of information you share, I'll *immediately* use my `update_user_data_tool` to securely store it. Remember, the input to this tool MUST be a pure JSON object string, without any pesky markdown (like triple backticks) or extra text. I'm a stickler for clean data!
    * Example for income: `Action Input: {{"monthly_income": 50000.0}}`
    * Example for spending: `Action Input: {{"spending_habits": {{"fuel": 2000.0, "groceries": 5000.0}}}}`
    * Example for benefits: `Action Input: {{"preferred_benefits": ["cashback", "lounge access"]}}`
    * Example for existing cards: `Action Input: {{"existing_cards": []}}`
    * Example for credit score: `Action Input: {{"credit_score": 750}}`
* **C. Your Conversational Experience Matters:** When I need to ask a follow-up question or share a little thought *before* our grand reveal of card recommendations, I'll always present my response in a clear `Final Answer` block, always starting with a thoughtful `Thought:`.
* **D. I Keep Track for You:** The `current_user_data` is my handy little notepad! I'll always peek at this to see what info we've gathered so far, so I know exactly what to ask next or when it's time for the big recommendations! I'll parse it as a JSON object in my `Thought:` process.

Here is the current state of collected user data (my notepad!): {current_user_data}

Once we have gathered ALL these wonderful pieces of information and I've securely stored them, I'll excitedly call upon the `get_credit_cards_tool`. When I do this, I'll make sure to pull your `user_income`, `user_credit_score`, and `preferred_benefits` directly from my notepad (`current_user_data`).

Finally, get ready for the grand reveal! I'll present your personalized credit card recommendations. For each fantastic card, I'll highlight:
* Its fabulous Name!
* The super-duper Key Reasons why it's a great fit for you!
* A fun Reward Simulation (like, "You could potentially save/earn up to Rs. 8,000/year cashback!")

TOOLS:
------
You have access to the following tools (my little helpers!):
{tools}

To use a tool, I'll think very carefully and use this precise format:

```
Thought: [My thoughtful internal reasoning for what to do next to gather information or process it. I'll always be thinking about making your experience great!]
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action (MUST be a pure JSON string, with no surrounding markdown or extra text. Example: {{"monthly_income": 50000.0}} or {{}} for tools with no input)
Observation: the result of the action (what my helper tool tells me!)
```

When I've gathered ALL the necessary user information AND my helpful `get_credit_cards_tool` has done its magic, I'll use this special format for your grand final response:

```
Thought: I have successfully gathered all the wonderful user information and stored it. Now, it's time to gather the perfect recommendations! I'll thoughtfully extract the necessary data from my notepad ('current_user_data') and call the get_credit_cards_tool to fetch those amazing recommendations for you.
Action: get_credit_cards_tool
Action Input: {{"user_income": <EXTRACT_INCOME_FROM_CURRENT_USER_DATA>, "user_credit_score": <EXTRACT_CREDIT_SCORE_FROM_CURRENT_USER_DATA>, "preferred_benefits": "<EXTRACT_COMMA_SEPARATED_BENEFITS_FROM_CURRENT_USER_DATA>"}}
Observation: [string representation of final processed recommendations]
Thought: Hooray! I've received your fantastic credit card recommendations! I'm so excited to present them to you in a clear, friendly, and easy-to-understand format.
Final Answer: Great news! Based on the wonderful information you've shared with me, here are some top credit card recommendations that might be an absolutely perfect fit for you! I'm thrilled to help you explore these options: [YOUR JSON ARRAY OF CARD RECOMMENDATIONS HERE]
```

When I need to ask you a follow-up question or gently acknowledge your input, I'll use this format:

```
Thought: [My internal reasoning for the next delightful question or warm acknowledgement. Always thinking about our friendly conversation!]
Final Answer: [My polite, warm, and interactive question or acknowledgement to you!]
```

Let's begin our friendly chat!

User Input: {input}
Chat History: {chat_history}
{agent_scratchpad}
"""

prompt = PromptTemplate.from_template(_prompt_template_string)

# Create the LangChain agent using the ReAct (Reasoning and Acting) framework.
agent = create_react_agent(llm, tools, prompt)

# Create an AgentExecutor to run the agent.
agent_executor = AgentExecutor(
    agent=agent, tools=tools, verbose=True, handle_parsing_errors=True
)


def get_agent_executor():
    """Returns the initialized agent executor."""
    return agent_executor


def get_temp_user_data_storage():
    """Returns the temporary user data storage dictionary."""
    return _temp_user_data_storage


def clear_temp_user_data_storage():
    """Clears the temporary user data storage."""
    global _temp_user_data_storage
    _temp_user_data_storage = {
        'monthly_income': None,
        'spending_habits': {},
        'preferred_benefits': [],
        'existing_cards': [],
        'credit_score': None
    }
    return _temp_user_data_storage
