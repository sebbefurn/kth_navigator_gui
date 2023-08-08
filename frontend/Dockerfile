FROM node:20-alpine

COPY ./src /app/
COPY index.html /app/
COPY package.json /app/
COPY package-lock.json /app/
COPY vite.config.js /app/

WORKDIR /app

RUN npm install

EXPOSE 5173

CMD ["npm", "run", "dev"]
