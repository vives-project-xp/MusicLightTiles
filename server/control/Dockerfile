FROM python:3.12.0
# Set the working directory to /code
WORKDIR /code
# Set the environment variables
ENV MQTT_HOST=$MQTT_HOST
ENV MQTT_PORT=$MQTT_PORT
ENV MQTT_USER=$MQTT_USER
ENV MQTT_PASSWORD=$MQTT_PASSWORD
# COPY all the files to the container
COPY . .
# Install the dependencies
RUN pip install -r requirements.txt
# EXPOSE port 3000 for websocket connection
EXPOSE 3000
# Run main.py when the container launches
CMD ["python", "main.py"]
