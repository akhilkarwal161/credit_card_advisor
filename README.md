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

### Set up Google Gemini API Key
The LangChain agent uses the Google Gemini API. To protect your key, you should not hard-code it. Instead, use an environment file.

1.  **Create a `.env` file:** In the root directory of the project, create a new file named `.env` by copying the example file.
    ```bash
    cp .env.example .env
    ```

2.  **Add your API key:** Open the new `.env` file and replace `YOUR_GOOGLE_API_KEY_HERE` with your actual API key obtained from Google.

    ```
    # .env
    GOOGLE_API_KEY="your_actual_api_key_from_google"
    ```

The `.gitignore` file is already configured to ignore `.env`, so you won't accidentally commit your secret key.

### Deployment Note
When deploying to a service like Google Cloud Run, do not upload your `.env` file. Instead, configure the `GOOGLE_API_KEY` as a secret or environment variable directly in the cloud service's configuration settings. The application is set up to read this variable automatically.

Running the Application
Start the Flask Backend:

python app.py

The Flask application will start, typically running on http://127.0.0.1:5000/.

Open in Browser:
Open your web browser and navigate to the address provided by Flask (e.g., http://127.0.0.1:5000/).

You can now interact with the Credit Card Advisor!

## Technologies Used
Backend: Flask (Python web framework)

AI Agent: LangChain (for building LLM applications)

LLM: Google Gemini 2.0 Flash

Database: SQLite3

Frontend: HTML, JavaScript, Tailwind CSS (for styling)

Dependency Management: pip, requirements.txt