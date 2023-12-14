FROM nginx:latest
# Copy files to the container
COPY ./web /usr/share/nginx/html
# Expose port 80
EXPOSE 80
# Run nginx when the container launches
CMD ["nginx", "-g", "daemon off;"]