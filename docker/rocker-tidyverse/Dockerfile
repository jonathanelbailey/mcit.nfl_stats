FROM rocker/rstudio:4.1.0

ENV ACCEPT_EULA Y

USER root

RUN apt-get update -y && apt-get install -y --no-install-recommends \
    curl \
    gnupg \
    ca-certificates \
    unixodbc \
    libsnappy-dev \
    libxml2-dev \
    libcairo2-dev \
    libsqlite-dev \
    libmariadbd-dev \
    libmariadbclient-dev \
    libpq-dev \
    libssh2-1-dev \
    unixodbc-dev \
    libsasl2-dev \
    git \
    nuget \
    libcurl4-openssl-dev \
    libssl-dev \
    libxml2-dev \
    apt-transport-https \
    software-properties-common

RUN nuget update -self \
    && apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 3FA7E0328081BFF6A14DA29AA6A19B38D3D831EF \
    && echo "deb https://download.mono-project.com/repo/ubuntu stable-focal main" | tee /etc/apt/sources.list.d/mono-official-stable.list \
    && wget -q https://packages.microsoft.com/config/ubuntu/20.04/packages-microsoft-prod.deb -O packages-microsoft-prod.deb \
    && dpkg -i packages-microsoft-prod.deb && add-apt-repository universe \
    && curl https://packages.microsoft.com/keys/microsoft.asc > mskey.txt && apt-key add mskey.txt && \
    curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update -y && apt-get install -y  --no-install-recommends \
    mono-complete \
    dotnet-sdk-3.1 \
    msodbcsql17

RUN install2.r --error --skipinstalled --ncpus -1 --deps TRUE \
    tidyverse \
    dplyr \
    devtools \
    formatR \
    remotes \
    selectr \
    caTools \
    future \
    future.apply \
    doFuture \
    xgboost \
    nflfastR \
    nflseedR  \
    nfl4th \
    fastrmodels \
    && Rscript -e "require(devtools); install_github('Open-Systems-Pharmacology/rClr'); install_github('agstudy/rsqlserver');install_github('nflverse/nflreadr'); install_github('nflverse/nflplotR'); "


#USER root

RUN apt-get update && apt-get install -y --no-install-recommends openssh-server && rm -rf /var/lib/apt/lists/*
# copy over odbc dsn and driver configs
COPY odbc*.ini /etc/

RUN mkdir /var/run/sshd
RUN echo 'root:rstudio' | chpasswd
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config
RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd

EXPOSE 22

CMD ["/usr/sbin/sshd", "-D"]