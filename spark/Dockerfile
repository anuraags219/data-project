FROM apache/spark:3.5.8-java17-python3

USER root

# create gluten directory
RUN mkdir -p /opt/gluten

# copy gluten jar into image
COPY ../gluten/ /opt/gluten/

# fix permissions (important for spark user)
RUN chown -R spark:spark /opt/gluten

USER spark