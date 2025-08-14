FROM node:18-alpine

WORKDIR /app

# Copy package files first for caching
COPY package.json package-lock.json ./
RUN npm ci --include=dev  # Keep dev dependencies for HMR

# Copy the rest and start dev server
COPY . .
CMD ["npm", "run", "dev"]