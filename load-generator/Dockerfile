# load-generator/Dockerfile
FROM alpine
RUN apk add --no-cache curl

# Perintah ini akan berjalan selamanya, mengirim request ke API Anda
CMD ["sh", "-c", "while true; do curl http://uas/loadtest; done"]