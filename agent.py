# agent.py
import os
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import Tool
from langchain_core.prompts import PromptTemplate
from langchain.agents import AgentExecutor, create_react_agent
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ValidationError  # Import ValidationError

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

# --- Pydantic Models for Tool Inputs ---


class UserUpdateInput(BaseModel):
    """Input for updating user data."""
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


def get_credit_cards_tool(
    user_income: float,
    user_credit_score: int,
    preferred_benefits: str = "",
) -> str:
    """
    Fetches and processes credit card recommendations based on user's monthly income, credit score,
    and preferred benefits. It will use the _temp_user_data_storage for full user context.
    Returns a JSON string of a list of recommended cards, each with name, key reasons, and reward simulation.
    """
    print(
        f"get_credit_cards_tool: Received user_income={user_income}, user_credit_score={user_credit_score}, preferred_benefits={preferred_benefits}")

    global _temp_user_data_storage  # Access the global storage for full context

    benefits_list = [b.strip().lower() for b in preferred_benefits.split(',')
                     ] if preferred_benefits else []

    if 'any' in benefits_list:  # Handle "any" as a special case for benefits
        raw_cards = get_cards_by_criteria(user_income, user_credit_score, [])
    else:
        raw_cards = get_cards_by_criteria(
            user_income, user_credit_score, benefits_list)

    # Use the recommender to get the final, ranked recommendations
    # Pass the global _temp_user_data_storage for comprehensive recommendation logic
    final_recommendations = get_card_recommendations(
        raw_cards, _temp_user_data_storage)

    # Return the recommendations as a JSON string
    return json.dumps(final_recommendations)


# Expects a single string argument
def update_user_data_tool_func(data_json_string: str) -> str:
    """
    Updates the global user data dictionary with provided information.
    It expects a pure JSON string and validates with Pydantic after parsing.
    """
    global _temp_user_data_storage

    print(
        f"update_user_data_tool_func: Received raw string input: '{data_json_string}'")

    try:
        # Aggressively strip any surrounding characters including markdown backticks and whitespace
        cleaned_json_string = data_json_string.strip().strip('`').strip()

        # Ensure it's not empty after cleaning
        if not cleaned_json_string:
            raise ValueError("Input string is empty after cleaning.")

        parsed_input_dict = json.loads(cleaned_json_string)
        print(
            f"update_user_data_tool_func: Parsed JSON string: {parsed_input_dict}")

        # Validate the parsed input using the Pydantic model
        user_input = UserUpdateInput(**parsed_input_dict)
        print(
            f"update_user_data_tool_func: Validated Pydantic object: {user_input.dict()}")

        # Direct assignment after validation by Pydantic
        if user_input.monthly_income is not None:
            _temp_user_data_storage['monthly_income'] = user_input.monthly_income
        if user_input.spending_habits is not None:
            _temp_user_data_storage['spending_habits'] = user_input.spending_habits
        if user_input.preferred_benefits is not None:
            _temp_user_data_storage['preferred_benefits'] = user_input.preferred_benefits
        if user_input.existing_cards is not None:
            _temp_user_data_storage['existing_cards'] = user_input.existing_cards
        if user_input.credit_score is not None:
            _temp_user_data_storage['credit_score'] = user_input.credit_score

        print(
            f"update_user_data_tool_func: Current _temp_user_data_storage after merge: {_temp_user_data_storage}")
        return "User data updated successfully."
    except json.JSONDecodeError as e:
        print(f"update_user_data_tool_func: JSONDecodeError: {e}")
        return f"Error: Invalid JSON format for data update. Please ensure your Action Input is a pure JSON object string: {e}"
    except ValidationError as e:
        print(
            f"update_user_data_tool_func: Pydantic Validation Error: {e.errors()}")
        return f"Error updating user data: Invalid data format according to schema: {e.errors()}"
    except Exception as e:
        print(f"update_user_data_tool_func: General Error during update: {e}")
        return f"Error updating user data: {e}"


# List of tools available to the LangChain agent.
tools = [
    Tool(
        name="get_credit_cards_tool",
        func=get_credit_cards_tool,
        description="Useful for fetching and processing credit card recommendations. Requires 'user_income' (float), 'user_credit_score' (int), and 'preferred_benefits' (optional, comma-separated string)."
    ),
    Tool(
        name="update_user_data_tool",
        func=update_user_data_tool_func,
        # IMPORTANT: No args_schema here, as the function expects a single raw string.
        # The internal function handles JSON parsing and Pydantic validation.
        description="Call this tool to update the user's collected data. The Action Input MUST be a pure JSON string (e.g., '{\"monthly_income\": 50000.0}'). Do NOT include any markdown formatting like triple backticks (`). Fields: 'monthly_income' (float), 'spending_habits' (dict), 'preferred_benefits' (list of strings), 'existing_cards' (list of strings), or 'credit_score' (int)."
    ),
]

# Prompt template string
_prompt_template_string = """
You are a helpful credit card advisor. Your goal is to recommend the best-fit credit cards to users.
To do this, you need to gather specific information from the user through a guided conversation.

Here's the information you need to collect in order, strictly one by one:
1.  **Monthly income (in INR):** You must ask for a numerical value.
2.  **Spending habits:** You must ask for approximate monthly spending on categories like fuel, travel, groceries, and dining. Users should provide this in a "category: amount" format (e.g., 'fuel: 2000, groceries: 5000').
3.  **Preferred benefits:** You must ask what kind of benefits they prefer (e.g., cashback, travel points, lounge access). Users should provide this as a comma-separated list. If they say 'any' or similar, you MUST use '["any"]' for the list value.
4.  **Existing cards (optional):** You must ask if they have any existing credit cards. They can list names or say 'no'. If they say 'no', use '[]' for the list value.
5.  **Approximate credit score:** You must ask for a numerical value (e.g., 750) or allow 'unknown'. If 'unknown', use 'None' or omit the field.

**CRITICAL STEPS:**
* **A. Information Gathering:** You must go through the above list, asking for one piece of information at a time. Do NOT ask for multiple pieces of information in one turn.
* **B. Data Storage:** AFTER you receive and understand EACH piece of information from the user, you MUST immediately use the `update_user_data_tool` to store it. The input to `update_user_data_tool` MUST be a pure JSON object string, without any surrounding markdown (like triple backticks) or extra text.
    * Example for income: `Action Input: {"monthly_income": 50000.0}`
    * Example for spending: `Action Input: {"spending_habits": {"fuel": 2000.0, "groceries": 5000.0}}`
    * Example for benefits: `Action Input: {"preferred_benefits": ["cashback", "lounge access"]}`
    * Example for existing cards: `Action Input: {"existing_cards": ["Card A", "Card B"]}` or `Action Input: {"existing_cards": []}`
    * Example for credit score: `Action Input: {"credit_score": 750}` or `Action Input: {"credit_score": None}`
* **C. Conversational Output:** When you need to ask a follow-up question or provide a direct response *before* making final recommendations, you must put your response in the `Final Answer` block. Do not just output text without a `Thought:` and `Final Answer:`.
* **D. Data Awareness:** The `current_user_data` variable is provided in the prompt. You must use this string to understand the current state of collected information and decide what to ask next or when to make recommendations. Parse this string as a JSON object in your Thought process to inspect the fields.

Here is the current state of collected user data: {current_user_data}

Once you have gathered ALL of the above information and successfully stored it using the `update_user_data_tool`, you will then call the `get_credit_cards_tool`. When calling `get_credit_cards_tool`, you MUST extract the `user_income`, `user_credit_score`, and `preferred_benefits` from the `current_user_data` string.

Finally, present the recommended cards to the user. For each recommendation, include:
* Card Name
* Key reasons for the recommendation
* A reward simulation (e.g., "You could earn Rs. 8,000/year cashback")

TOOLS:
------
You have access to the following tools:
{tools}

To use a tool, please use the following format:

```
Thought: You should always think about what to do next to gather information or process it.
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action (MUST be a pure JSON string, with no surrounding markdown or extra text. Example: {"monthly_income": 50000.0} or {} for tools with no input)
Observation: the result of the action
```

When you have gathered ALL necessary user information AND have called `get_credit_cards_tool`, use the following format for your final response:

```
Thought: I have successfully gathered all user information and stored it. Now I will extract the necessary data from 'current_user_data' and call the get_credit_cards_tool to fetch recommendations.
Action: get_credit_cards_tool
Action Input: {{"user_income": <EXTRACT_INCOME_FROM_CURRENT_USER_DATA>, "user_credit_score": <EXTRACT_CREDIT_SCORE_FROM_CURRENT_USER_DATA>, "preferred_benefits": "<EXTRACT_COMMA_SEPARATED_BENEFITS_FROM_CURRENT_USER_DATA>"}}
Observation: [string representation of final processed recommendations]
Thought: I have received the credit card recommendations. Now I will present them to the user.
Final Answer: [Your final answer, which includes the recommended cards with their name, key reasons, and reward simulation, clearly presented.]
```

When you need to ask a follow-up question, use this format:
```
Thought: I need more information. I will ask the user the next question.
Final Answer: [Your question to the user]
```

Begin!

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
