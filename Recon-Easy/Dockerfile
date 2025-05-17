# Use the official Apache httpd image as a base
FROM nginx:stable-alpine

# Copy certs and config
COPY ./nginx/multi-site.conf /etc/nginx/nginx.conf
COPY ./certs/selfsigned.crt /etc/ssl/certs/selfsigned.crt
COPY ./certs/selfsigned.key /etc/ssl/private/selfsigned.key
COPY ./html/ /usr/share/nginx/html/
# COPY ./entrypoint.sh /usr/local/bin/entrypoint.sh

# # Make the entrypoint script executable
# RUN chmod +x /usr/local/bin/entrypoint.sh


# Expose ports 80 (HTTP) and 443 (HTTPS)
EXPOSE 80
EXPOSE 443

# # Set the entrypoint script to run on container start
# ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

# Command to run Apache in the foreground (will be called by entrypoint.sh)
CMD ["nginx", "-g", "daemon off;"]
