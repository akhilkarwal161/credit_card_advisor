Credit Card Advisor
Project Overview
This Credit Card Advisor is an AI-powered conversational agent designed to help users find the best-fit credit cards based on their financial profile and spending habits. Built with Flask for the backend and a LangChain agent, it guides users through a series of questions to collect necessary information (monthly income, spending habits, preferred benefits, existing cards, and credit score), and then recommends suitable credit cards from a simulated database.

Features
Interactive Chat Interface: Users can converse naturally with the AI advisor.

Personalized Recommendations: Provides credit card suggestions tailored to individual financial data.

Detailed Card Information: For each recommended card, it displays the name, an image, key reasons for the recommendation, and a simulated annual reward/saving.

Structured Data Collection: The agent intelligently collects user data step-by-step.

Extensible Backend: Built on Flask and LangChain, allowing for easy expansion of features and integration with more complex tools or external APIs (e.g., real-time credit card data APIs).

Demo
Experience the live Credit Card Advisor here: https://credit-card-advisor-xvhbgr5zoq-ul.a.run.app

 <https://www.youtube.com/watch?v=pu-LUZE8nW8>

Setup Instructions
Follow these steps to get the Credit Card Advisor up and running on your local machine.

Prerequisites
Python 3.9+

pip (Python package installer)

git (for cloning the repository)

Installation
Clone the Repository:

git clone https://github.com/akhilkarwal161/credit_card_advisor.git
cd credit_card_advisor

Create and Activate a Virtual Environment:
It's recommended to use a virtual environment to manage project dependencies.

python3 -m venv venv
source venv/bin/activate # On macOS/Linux
# For Windows: .\venv\Scripts\activate

Install Python Dependencies:
Install all required libraries using pip and the requirements.txt file.

pip install -r requirements.txt

Database Initialization and Population:
The application uses a SQLite database. This command will create the credit_cards.db file and populate it with initial dummy data.

python -c "from database import init_db, populate_initial_data; init_db(); populate_initial_data()"

(Note: This command clears and repopulates the database. If you have custom data, adjust accordingly.)

Set up Google Gemini API Key:
The LangChain agent uses the Google Gemini API.
You need to set your Google API Key as an environment variable.

export GOOGLE_API_KEY="YOUR_GEMINI_API_KEY" # On macOS/Linux
# For Windows: set GOOGLE_API_KEY="YOUR_GEMINI_API_KEY"

(Replace YOUR_GEMINI_API_KEY with your actual API key obtained from Google Cloud Console or AI Studio. Ensure this environment variable is active in the terminal where you run app.py.)

Running the Application
Start the Flask Backend:

python app.py

The Flask application will start, typically running on http://127.0.0.1:5000/.

Open in Browser:
Open your web browser and navigate to the address provided by Flask (e.g., http://127.0.0.1:5000/).

You can now interact with the Credit Card Advisor!

Technologies Used
Backend: Flask (Python web framework)

AI Agent: LangChain (for building LLM applications)

LLM: Google Gemini 2.0 Flash

Database: SQLite3

Frontend: HTML, JavaScript, Tailwind CSS (for styling)

Dependency Management: pip, requirements.txt