# Use the official Nginx image
FROM nginx:latest

# Copy the custom Nginx config
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port 80 (so the container can receive traffic)
EXPOSE 8080

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]