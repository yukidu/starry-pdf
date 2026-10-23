FROM node:22-alpine AS build
WORKDIR /web
COPY app-web/package*.json ./
RUN npm install --no-audit --no-fund
COPY app-web/ ./
RUN npm run build

# Official nginx non-root image: listens on 8080 and writes temporary files only to /tmp.
FROM nginxinc/nginx-unprivileged:1.31-alpine
COPY --from=build /web/dist/ /usr/share/nginx/html/
COPY app-web/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 8080
