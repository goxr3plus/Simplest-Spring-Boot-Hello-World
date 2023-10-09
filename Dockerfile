FROM openjdk:8-jre
WORKDIR /app
RUN addgroup --system --gid 1001 javauser \
    && adduser --system --uid 1001 javauser
COPY --chown=javauser:javauser artifact/example.smallest-?.?.?*-SNAPSHOT.war /app/app.war
COPY --chown=javauser:javauser artifact/application.properties /app/application.properties
USER javauser
EXPOSE 80
ENTRYPOINT ["java", "-jar", "/app/app.war"]
