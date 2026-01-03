# Use Python 3.11 slim image as base
FROM python:3.11-slim

RUN useradd -m -u 1000 user

USER user

ENV PATH="/home/user/.local/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy requirements file
COPY --chown=user requirements.txt requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=user blog_summarizer.py blog_summarizer.py

COPY --chown=user app.py app.py

# Expose port (if applicable, e.g., for a web app)
EXPOSE 7777

# Run the application
CMD ["python", "app.py"]