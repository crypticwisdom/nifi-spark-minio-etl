FROM apache/spark:3.4.0

USER root

# Set working directory
WORKDIR /opt/spark/work-dir
# WORKDIR /batch-pipeline

RUN chmod g+w /opt/spark/work-dir

RUN chmod a+x /opt/decom.sh
# Copy local JARs to Spark's default jars directory
COPY ./jars/*.jar /opt/spark/jars/

# Copy Spark scripts
COPY ./spark-scripts /opt/spark/work-dir

# Install Python dependencies
COPY ./requirements.txt /opt/spark/work-dir/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

ARG spark_uid=185

USER ${spark_uid}
