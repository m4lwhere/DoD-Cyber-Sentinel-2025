# north-torbia-robots-ctf/Dockerfile
FROM debian:bookworm-slim

# 1. Minimal Nginx install
RUN apt-get update \
 && apt-get install -y --no-install-recommends nginx \
 && rm -rf /var/lib/apt/lists/*

# 2. Put Nginx into foreground mode (required inside a container)
RUN printf '\n# run in foreground\ndaemon off;\n' >> /etc/nginx/nginx.conf

# 3. Copy the static site
COPY site/ /var/www/html

EXPOSE 80

CMD ["nginx"]
