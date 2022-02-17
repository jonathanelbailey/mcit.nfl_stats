# 3.10 doesn't work
FROM public.ecr.aws/j1r0q0g6/notebooks/notebook-servers/jupyter-scipy:v1.4

USER root

# install ms odbc driver
RUN curl https://packages.microsoft.com/keys/microsoft.asc > mskey.txt && apt-key add mskey.txt && \
    curl https://packages.microsoft.com/config/ubuntu/21.04/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt update -y && ACCEPT_EULA=Y apt-get install -y msodbcsql17 --no-install-recommends && \
    apt install unixodbc-dev build-essential unixodbc libsnappy-dev -y --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# copy over odbc dsn and driver configs
COPY odbc*.ini /etc/

USER jovyan

WORKDIR /app

# copy python package dependencies and install them
COPY *.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy modules
COPY *.py .

# set env vars
ENV DB_SERVER='' \
    DB_NAME='' \
    DB_USER='' \
    DB_PW='' \
    PYTHONUNBUFFERED=1

WORKDIR "${HOME}"

# for compatibility with development
#CMD ["python"]