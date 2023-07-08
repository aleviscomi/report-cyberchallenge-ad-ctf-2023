FROM node:14-slim as build
COPY ./frontend /frontend
WORKDIR /frontend
RUN npm install
RUN npm run build

FROM nginx:1.19.2
RUN apt update && apt install -y ssl-cert
RUN openssl dhparam -out /etc/nginx/ssl-dhparams.pem 2048
COPY ./nginx.conf /etc/nginx/nginx.conf
COPY --from=build /frontend/dist/ /var/www/html/

