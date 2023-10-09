FROM mcr.microsoft.com/openjdk/jdk:17-ubuntu
WORKDIR /app
RUN addgroup --system --gid 1001 javauser \
    && adduser --system --uid 1001 javauser
COPY --chown=javauser:javauser artifact/example.smallest-?.?.?*-SNAPSHOT.war /app/app.war
USER javauser
EXPOSE 9092
ENTRYPOINT ["java", "-jar", "/app/app.war"]
