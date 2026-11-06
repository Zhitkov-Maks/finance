# syntax=docker/dockerfile:1

# ============================================================
#  BUILD STAGE — собираем Vite/SPA
# ============================================================
FROM node:18-alpine AS build

WORKDIR /app

# package.json / lock-файл отдельно — чтобы слой npm ci кешировался
# и не инвалидировался при каждой правке исходников
COPY package*.json ./
RUN npm ci --no-audit --no-fund

# Исходники и сборка
COPY . .
RUN npm run build

# ============================================================
#  RUNTIME STAGE — nginx раздаёт статику
# ============================================================
FROM nginx:1.25-alpine

# Свой конфиг вместо дефолтного
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Собранное приложение
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]