# Dockerfile
FROM python:3.9.5

# Set the working directory
WORKDIR /app

# Install system dependencies required for rembg
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Create .u2net directory and download the model
RUN mkdir -p /root/.u2net
RUN wget https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2net.onnx -O /root/.u2net/u2net.onnx

# Copy the requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Create necessary directories
RUN mkdir -p uploads processed

# Expose port
EXPOSE 5000

# Command to run the application
CMD ["python", "app.py"]