# Use an image with Python and Playwright browsers installed
FROM mcr.microsoft.com/playwright/python:v1.62.0-noble

# Set the working directory inside the container
WORKDIR /app

# Copy the Python dependencies list
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY abh_monitor.py .

# Start the appointment monitor
CMD ["python", "-u", "abh_monitor.py"]