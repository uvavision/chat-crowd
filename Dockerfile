# Start with a Linux micro-container to keep the image tiny
FROM python:3.6

# Set the working directory to /app
WORKDIR ./main

# Copy the current directory contents into the container at /app
ADD . /main

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Make port 80 and 7004 available to the world outside this container
EXPOSE 80:8080

# Run app.py when the container launches
CMD ["python", "run.py"]
