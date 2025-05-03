# Use the official Apache httpd image as a base
FROM httpd:2.4

# Install openssl for certificate generation
# Update package list and install openssl, then clean up
RUN apt-get update && \
    apt-get install -y openssl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy custom Apache configuration, website content, cert generation files, and entrypoint script
COPY ./apache/httpd-ssl.conf /usr/local/apache2/conf/extra/httpd-ssl.conf
COPY ./certs/ /usr/local/apache2/conf/certs/
COPY ./html/ /usr/local/apache2/htdocs/
COPY ./entrypoint.sh /usr/local/bin/entrypoint.sh

# Make the entrypoint script executable
RUN chmod +x /usr/local/bin/entrypoint.sh

# --- Apache Configuration Adjustments ---

# 1. Enable necessary modules in httpd.conf
# Uncomment or add LoadModule lines for ssl, socache_shmcb, and vhost_alias (if needed, though ServerName handles it)
# Also ensure the Include for vhosts is uncommented.
# We use sed to modify the main config file non-interactively.
RUN sed -i \
        -e 's/^#\(LoadModule .*mod_ssl\.so\)/\1/' \
        -e 's/^#\(LoadModule .*mod_socache_shmcb\.so\)/\1/' \
        -e 's/^#\(LoadModule .*mod_rewrite\.so\)/\1/' \
        -e 's/^#\(Include .*httpd-ssl\.conf\)/\1/' \
        /usr/local/apache2/conf/httpd.conf

# 2. Create a basic httpd-ssl.conf to include our vhosts config within the SSL context
# Note: The actual SSL vhost definitions are in httpd-vhosts.conf for simplicity here.
# This file mainly ensures SSL is generally configured.
RUN echo "SSLRandomSeed startup file:/dev/urandom 512" >> /usr/local/apache2/conf/extra/httpd-ssl.conf && \
    echo "SSLRandomSeed connect file:/dev/urandom 512" >> /usr/local/apache2/conf/extra/httpd-ssl.conf && \
    echo "SSLSessionCache        \"shmcb:/usr/local/apache2/logs/ssl_scache(512000)\"" >> /usr/local/apache2/conf/extra/httpd-ssl.conf && \
    echo "SSLSessionCacheTimeout 300" >> /usr/local/apache2/conf/extra/httpd-ssl.conf && \
    echo "SSLUseStapling Off" >> /usr/local/apache2/conf/extra/httpd-ssl.conf # Simpler without stapling for self-signed

# Expose ports 80 (HTTP) and 443 (HTTPS)
EXPOSE 80
EXPOSE 443

# Set the entrypoint script to run on container start
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

# Command to run Apache in the foreground (will be called by entrypoint.sh)
CMD ["httpd-foreground"]
