# Stage 1: Build the Flutter web application
FROM ubuntu:22.04 AS build

# Prevent prompts from apt
ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    unzip \
    xz-utils \
    zip \
    libglu1-mesa \
    && rm -rf /var/lib/apt/lists/*

# Install Flutter
ENV FLUTTER_HOME=/opt/flutter
RUN git clone https://github.com/flutter/flutter.git -b stable ${FLUTTER_HOME}
ENV PATH="${PATH}:${FLUTTER_HOME}/bin"

# Run flutter doctor to verify installation
RUN flutter doctor -v

# Copy the app source code
COPY . /app
WORKDIR /app

# Download dependencies
RUN flutter pub get

# Build the web application
ARG API_URL=https://ai-agent-uqxt.onrender.com
RUN flutter build web --release --dart-define=API_URL=${API_URL}

# Stage 2: Serve with nginx
FROM nginx:alpine AS production

# Copy the built web app to nginx
COPY --from=build /app/build/web /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
