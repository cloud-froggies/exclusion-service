FROM node:14

WORKDIR /usr/src/app

COPY app .

RUN npm i

EXPOSE 8080

CMD ["node","server.js"]

