# Step 1: Secure a Node environment and build the static distribution
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Step 2: Serve the compiled static bundle using a high-performance Nginx engine
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 7860
RUN sed -i 's/listen\.5/listen 7860;/g' /etc/nginx/conf.d/default.conf || true
CMD ["nginx", "-g", "daemon off;"]