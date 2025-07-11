FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY services/dashboard/package*.json ./
RUN npm ci --only=production

# Copy source code
COPY services/dashboard/ ./

# Build the application
RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]
