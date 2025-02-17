# Use Python 3.9 base image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the application file into the container
COPY app.py /app/

# Upgrade pip and install dependencies
RUN python -m pip install --upgrade pip && \
    python -m pip install Flask prometheus_client

# Expose the port your app will run on
EXPOSE 5000

# Run the Flask app
CMD ["python", "app.py"]
