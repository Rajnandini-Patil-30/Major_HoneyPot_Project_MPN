# Stage 1: Build React app
FROM node:18-bullseye-slim AS build

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY public/ public/
COPY src/ src/

ENV REACT_APP_API_URL=""
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
COPY public/ public/
COPY src/ src/

# Build with API URL pointing to relative path (nginx will proxy)
ENV REACT_APP_API_URL=""
RUN npm run build

# Stage 2: Serve with nginx
FROM nginx:alpine

# Copy built assets
COPY --from=build /app/build /usr/share/nginx/html

# Custom nginx config to proxy /api to backend
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
