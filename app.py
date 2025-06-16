# app.py
from flask import Flask, render_template, request, jsonify
import json
import re  # Import the regex module

# Import only what's necessary from agent.py: the agent executor object and the clear function
from agent import get_agent_executor, clear_temp_user_data_storage, get_temp_user_data_storage
from database import init_db, populate_initial_data, clear_duplicate_cards

app = Flask(__name__)

# Initialize the LangChain agent executor once when the app starts
agent_executor = get_agent_executor()

# --- Session Management for Chat History ---
user_sessions = {}  # This will manage chat history per session.


@app.route('/')
def index():
    """Renders the main HTML page for the chat interface."""
    return render_template('index.html')


@app.route('/chat', methods=['POST'])
def chat():
    """
    Handles chat messages from the frontend, feeding them to the LangChain agent
    for dynamic conversation and recommendations.
    """
    if not request.is_json:
        print("Warning: Incoming request is not JSON or has incorrect Content-Type.")
        return jsonify({"response": "Invalid request: Expected JSON content.", "recommendations": []}), 400

    request_data = request.json
    user_message = request_data.get('message', '') if request_data else ''
    session_id = request_data.get(
        'session_id', 'default_session') if request_data else 'default_session'

    # Initialize session data if it does not exist
    if session_id not in user_sessions:
        user_sessions[session_id] = {
            'chat_history': [],  # Stores messages for the LangChain agent's context
        }
        # For simplicity in this demo, we'll clear the global temp storage on a new "session".
        # In a multi-user app, you'd manage per-session state more robustly (e.g., in a database).
        clear_temp_user_data_storage()

    session_data = user_sessions[session_id]
    chat_history = session_data['chat_history']

    response_text = ""
    # This will be populated if the agent's output contains structured recommendations
    recommendations = []

    # Retrieve the current state of user data to pass to the agent (for agent's internal awareness)
    current_user_data = get_temp_user_data_storage()

    # Prepare input for the agent
    agent_input = {
        "input": user_message,
        "chat_history": chat_history,
        # Pass as JSON string
        "current_user_data": json.dumps(current_user_data)
    }

    try:
        # Invoke the LangChain agent to get a response
        agent_response = agent_executor.invoke(agent_input)
        raw_agent_output = agent_response.get(
            'output', "I'm sorry, I couldn't process that.")

        # Default conversational response if no structured recommendations are found/extracted
        response_text = raw_agent_output

        # --- Extract structured recommendations from agent's response if available ---
        # Use regex to find a JSON array pattern (starting with '[' and ending with ']')
        json_match = re.search(r'\[.*\]', raw_agent_output, re.DOTALL)

        if json_match:
            json_str = json_match.group(0)  # Get the matched JSON string
            try:
                parsed_recommendations = json.loads(json_str)
                if isinstance(parsed_recommendations, list):
                    recommendations = parsed_recommendations

                    # Set a generic conversational intro for the chat window
                    response_text = "Here are some credit card recommendations based on your preferences:"

                    # Optionally, you could also remove the JSON part from raw_agent_output
                    # if you wanted to display any non-JSON text the agent provided.
                    # For now, we prioritize the clean intro + structured recommendations.

            except json.JSONDecodeError:
                print(
                    f"Warning: Regex found potential JSON, but JSONDecodeError occurred: {json_str[:100]}...")
                # If parsing fails, the original raw_agent_output remains in response_text
            except Exception as parse_e:
                print(
                    f"Warning: General error parsing potential JSON from agent's recommendations: {parse_e}")
                # If any other parsing error occurs, keep the original response_text

    except Exception as e:
        print(f"Error invoking agent: {e}")
        response_text = "I apologize, I encountered an internal error. Could you please rephrase or try again?"
        # Clear recommendations on agent invocation error
        recommendations = []

    # Update chat history with the user's message and agent's response
    # The 'response_text' here should only be the conversational part
    chat_history.append({"role": "user", "content": user_message})
    chat_history.append({"role": "assistant", "content": response_text})

    return jsonify({"response": response_text, "recommendations": recommendations})


if __name__ == '__main__':
    # Initialize the SQLite database (creates the file and table if they don't exist).
    init_db()

    # Clear any duplicate entries before populating
    clear_duplicate_cards()

    # Populate the database with initial dummy data
    populate_initial_data()

    # Run the Flask application in debug mode for development.
    app.run(debug=True)
