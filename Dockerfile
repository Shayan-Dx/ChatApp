# Use the official Python image.
FROM python:3.11

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container.
WORKDIR /code

# Copy the requirements file into the container.
COPY requirements.txt . 

# Upgrade pip and setuptools before installing dependencies
RUN pip install --upgrade pip setuptools

# Install the dependencies.
RUN pip install --no-cache-dir -r requirements.txt


# Copy the entire project into the container.
COPY . /code/

# Collect static files (if you have any).
RUN python manage.py collectstatic --noinput

# Expose the port that Daphne will run on.
EXPOSE 8000

# Command to run the Daphne server.
CMD ["daphne", "-p", "8000", "ChatApp.asgi:application"]
