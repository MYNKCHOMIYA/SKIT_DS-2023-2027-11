# ── Stage 1: Dependency Install ───────────────────────────────────────────────
FROM node:20-alpine AS deps

WORKDIR /app

# Copy package files and install dependencies
# Using --frozen-lockfile to guarantee reproducible installs
COPY package.json package-lock.json ./
RUN npm ci --frozen-lockfile

# ── Stage 2: Builder ──────────────────────────────────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /app

COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Set the API URL that Next.js will call at runtime
ARG NEXT_PUBLIC_API_URL=http://backend:8000
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

# Build the production Next.js bundle
RUN npm run build

# ── Stage 3: Runtime ──────────────────────────────────────────────────────────
FROM node:20-alpine AS runtime

WORKDIR /app

ENV NODE_ENV=production
ENV PORT=3000

# Copy only what is needed to run Next.js in production
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public

EXPOSE 3000

# Use the standalone Next.js server for minimal image size
CMD ["node", "server.js"]
