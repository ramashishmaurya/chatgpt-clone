FROM node:20-alpine

# Set working directory
WORKDIR /app

# Copy package.json to install dependencies first
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the frontend code
COPY . .

# Expose the default Vite port
EXPOSE 5173

# Start the Vite development server and expose it to all network interfaces
CMD ["npm", "run", "dev", "--", "--host"]
