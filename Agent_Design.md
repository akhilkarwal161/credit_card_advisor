Agent Flow and Prompt Design Documentation
This document provides detailed insights into the design and functionality of the LangChain agent powering the Credit Card Advisor application.

1. Overall Architecture
The Credit Card Advisor leverages a Flask backend to serve a web interface and interact with a LangChain agent. This agent acts as the brain of the application, orchestrating calls to various tools to gather information and provide personalized credit card recommendations.

Data Flow Diagram (Conceptual):

User Input (Browser)
       |
       v
Flask Backend (app.py)
       | (POST /chat)
       v
LangChain AgentExecutor (agent.py)
       |
       v
   [ Tools ]
   /       \
  v         v
update_user_data_tool  get_credit_cards_tool
   |          |
   v          v
Internal User Data  Database (database.py)
     &          |
  (recommender.py)
       ^
       | (Structured JSON)
       |
LangChain AgentExecutor
       | (Final Answer: Conversational + Structured JSON)
       v
Flask Backend
       | (JSON response: {response: "...", recommendations: [...]})
       v
Browser (index.html)
       |
       v
User Output (Chat bubble + Card display)

2. Agent Flow
The LangChain agent follows a strict, multi-turn conversational flow to gather all necessary user information before providing recommendations.

2.1. Initialization (agent.py)
The ChatGoogleGenerativeAI model (gemini-2.0-flash) is initialized as the underlying Large Language Model.

Two custom tools are defined:

update_user_data_tool: Manages the collection and storage of user-provided data in a global _temp_user_data_storage dictionary.

get_credit_cards_tool: Fetches and processes credit card recommendations based on user's monthly income, credit score, and preferred benefits. It expects a pure JSON string and extracts parameters after parsing.
Returns a JSON string of a list of recommended cards, each with name, key reasons, and reward simulation.

An AgentExecutor is created with a create_react_agent strategy, enabling the agent to reason and act (ReAct framework).

2.2. Information Gathering Steps (Sequential)
The agent is explicitly prompted to collect information one piece at a time, in a specific order:

Monthly Income (INR): Asks for a numerical value.

Spending Habits: Requests approximate monthly spending in categories like fuel, travel, groceries, and dining (e.g., "category: amount").

Preferred Benefits: Inquires about desired benefits (e.g., cashback, travel points, lounge access) as a comma-separated list. Handles "any" as a special case.

Existing Cards (Optional): Asks if the user has existing cards and expects a list of names or "no".

Approximate Credit Score: Asks for a numerical value (e.g., 750) or allows "unknown."

2.3. Tool Usage
The agent's decision-making process (Thought and Action) is governed by its prompt and the available tools.

update_user_data_tool
Purpose: To store validated pieces of user data (monthly_income, spending_habits, preferred_benefits, existing_cards, credit_score) as they are collected.

Input: Expects a pure JSON string (e.g., {"monthly_income": 50000.0}). It does not use args_schema directly in Tool definition; instead, the update_user_data_tool_func internally parses this string and performs type checking. This makes it robust to minor formatting variations from the LLM.

Output: Returns a simple string message indicating "User data updated successfully."

get_credit_cards_tool
Purpose: To retrieve, process, and rank credit card recommendations once all necessary user data has been collected.

Input: Expects a pure JSON string (e.g., {"user_income": 50000.0, "user_credit_score": 750, "preferred_benefits": "cashback, lounge access"}). Similar to update_user_data_tool, its function get_credit_cards_tool handles internal parsing and extraction from this string.

Output: Returns a JSON string representing a list of recommended card dictionaries, each containing card_name, image_url, key_reasons, reward_simulation, net_benefit, and affiliate_link.

3. Recommendation Logic (recommender.py)
The recommender.py module takes the raw card data (filtered by database.py based on basic eligibility) and the collected user_data to generate personalized recommendations.

get_card_recommendations(raw_cards: list[dict], user_data: dict) -> list[dict]:

Input:

raw_cards: List of dictionaries representing credit cards from the database. Crucially, database.py is configured to return sqlite3.Row objects that behave like dictionaries, ensuring recommender.py receives dictionary-like data.

user_data: The _temp_user_data_storage dictionary containing all collected user information.

Core Logic:

Total Spending Calculation: Sums up monthly spending from user_data['spending_habits'].

Base Reward Calculation: Estimates annual rewards based on card['reward_type'] (e.g., cashback, travel points, rewards, co-branded, fuel). It applies different multipliers or specific logic for each type.

Special Perks Matching: Iterates through card['special_perks'] and user_data['preferred_benefits'] to identify additional reasons for recommendation (e.g., lounge access, dining benefits).

Reason Generation: Constructs key_reasons strings based on the calculations and perk matches. Reasons are deduplicated.

Net Annual Benefit: Calculates estimated_annual_rewards - (joining_fee + annual_fee).

Filtering: Only cards with a positive net benefit or low fees (<= Rs. 750) are considered.

Deduplication & Ranking: Unique cards are maintained (highest net_benefit for duplicates), and the top 5 are sorted by net_benefit in descending order.

Output: A list of dictionaries, each formatted with card_name, image_url, key_reasons, reward_simulation, net_benefit, and affiliate_link. This structured output is critical for the frontend display.

4. Prompt Design (_prompt_template_string in agent.py)
The prompt is meticulously crafted to guide the LLM's behavior and ensure consistent output, especially for tool usage and final recommendations. It has been significantly enhanced to foster a super friendly and incredibly helpful conversational tone.

Persona & Goal: Clearly defines the agent as "a super friendly and incredibly helpful credit card advisor!" whose main goal is to "make finding the perfect credit card an absolute breeze for users, all through a warm, clear, and genuinely empathetic conversation." This sets a strong expectation for the LLM's friendly tone.

Sequential Information Collection (Friendly Flow):

Emphasizes collecting information "step-by-step, one question at a time," making it "nice and easy."

Explicitly states, "I'll always acknowledge your input with a friendly remark before moving on to the next exciting detail!"

Each information point (Income, Spending Habits, Preferred Benefits, Existing Cards, Credit Score) now includes a "How to ask" section with suggestions for varied, inviting, and empathetic phrasing (e.g., "What's that figure looking like for you?," "This helps us understand your lifestyle better!").

Includes friendly emojis (e.g., "😊") in expected input descriptions.

CRITICAL BEHAVIOR GUIDELINES (Friendly Advisor Tone):

A. Information Gathering is a Breeze: Reassures the user that the agent "promise[s] to go through our list and ask for only one piece of information at a time."

B. Data Storage is My Secret Power: Describes data storage as "lovingly understand[ing]" and "securely stor[ing]" information, with an emphasis on "pure JSON object string" for tool inputs, framed as being a "stickler for clean data!"

C. Your Conversational Experience Matters: Reinforces the commitment to clear Final Answer blocks with thoughtful Thought: prefixes.

D. I Keep Track for You: Explains current_user_data as a "handy little notepad" that the agent "always peek[s] at" for a smooth flow.

Tool Usage Format: Provides a precise Thought, Action, Action Input, Observation structure, with the Thought: now including phrases like "My thoughtful internal reasoning for what to do next... I'll always be thinking about making your experience great!"

Final Recommendation Format:

The Thought: before calling get_credit_cards_tool is more enthusiastic: "Now, it's time to gather the perfect recommendations! I'll thoughtfully extract the necessary data..."

The Final Answer is highly welcoming and positive: "Great news! Based on the wonderful information you've shared with me, here are some top credit card recommendations that might be an absolutely perfect fit for you! I'm thrilled to help you explore these options:"

Follow-up/Acknowledgement Format: Explicitly guides the LLM to provide "polite, warm, and interactive question[s] or acknowledgement[s]."

Iterative Refinement of Prompt and Tool Handling
The current prompt and tool handling strategy (especially for update_user_data_tool and get_credit_cards_tool accepting a raw JSON string) is a result of iterative refinement to address common challenges with LLM-tool interaction, such as:

Markdown Wrapping: LLMs often wrap JSON in triple backticks, which needs to be stripped.

Inconsistent JSON Formatting: Variations in whitespace or minor malformations.

LLM Hallucinating Arguments: Ensuring the LLM provides arguments in the expected single JSON string format.

Preventing Multi-Question Turns: The "strictly one by one" instruction helps enforce this.

By clearly defining the expected input and output formats at both the tool definition and prompt level, and by heavily emphasizing a friendly tone and interactive conversational patterns, we aim to minimize parsing errors and ensure a delightful user experience.