FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Copy the requirements file from the root context
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend code into the container
# (Since context is root, we copy from backend/ to /app/)
COPY backend/ .

# Expose the port FastAPI runs on
EXPOSE 8000

# Start the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]


