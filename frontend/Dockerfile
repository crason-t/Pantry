# Pantry web image.
#
# Not used by local environments (scripts/pantry-env runs Vite's dev server so
# HMR keeps working). This exists so a hosted environment is a deploy of
# config rather than a rewrite.
#
# Vite inlines VITE_* values at build time, so the API URL and environment
# name are build arguments -- one image per environment, not one image
# configured at boot:
#
#   docker build --build-arg VITE_API_BASE_URL=https://api.example.com \
#                --build-arg VITE_ENV_NAME=silver -t pantry-web:silver .

FROM node:22-alpine AS build

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

ARG VITE_API_BASE_URL
ARG VITE_ENV_NAME
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL \
    VITE_ENV_NAME=$VITE_ENV_NAME

RUN npm run build

FROM nginx:alpine AS serve

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
