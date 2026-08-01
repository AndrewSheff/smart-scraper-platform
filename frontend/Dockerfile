# ─── Сборка фронтенда Smart Scraper Platform ───
# Мультистейдж: node собирает бандл, nginx раздает статику.
# Финальный образ получается совсем легким — только nginx + html/js/css

# --- стадия сборки ---
FROM node:20-alpine AS build

WORKDIR /opt/frontend

# сначала копируем только package-файлы — кэш npm ci не будет сбрасываться
COPY package.json package-lock.json* ./

# ci вместо install — строгая установка по lock-файлу
RUN npm ci --silent

# теперь копируем остальной код и собираем
COPY . .
RUN npm run build

# --- стадия продакшена ---
FROM nginx:alpine AS production

# выкидываем дефолтный конфиг nginx, свой подсунем через docker-compose
RUN rm -rf /usr/share/nginx/html/*

# забираем собранный бандл из стадии build
# стандартный путь для vite — dist/, для CRA — build/
COPY --from=build /opt/frontend/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
