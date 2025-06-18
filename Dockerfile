# Use the official Python image as a base
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application code into the container
COPY . .

# Initialize the database and populate data during container build
# This ensures the database file is present when the app starts
RUN python -c "from database import init_db, populate_initial_data; init_db(); populate_initial_data()"

# Expose the port your Flask app will listen on
# Cloud Run sets the PORT environment variable dynamically
ENV PORT=8080
EXPOSE $PORT

# Run the Flask application when the container starts
# Use gunicorn or similar for production, for simplicity, using Flask's built-in server
CMD ["python", "app.py"]
