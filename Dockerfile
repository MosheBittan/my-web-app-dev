# Step 1: Use an official lightweight Python runtime as a parent image
FROM python:3.11-slim

# Step 2: Set the working directory inside the container
WORKDIR /app

# Step 3: Copy the requirements file into the container
COPY requirements.txt .

# Step 4: Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Step 5: Copy the rest of the application code into the container
COPY app.py .

# Step 6: Inform Docker that the container listens on port 8080
EXPOSE 8080

# Step 7: Run the application when the container starts
CMD ["python", "app.py"]