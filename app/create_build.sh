
#!/bin/bash
set -e

echo "🔄 Subiendo nueva imagen a GitHub Container Registry..."

echo  docker login ghcr.io -u TU_USUARIO --password-stdin

docker buildx create --use
docker buildx build \
  --platform linux/amd64,linux/arm/v7 \
  -t ghcr.io/hernandezpalo83/porfolio_django:latest \
  --push .

echo "✅ ¡Actualización completada!"

