FROM 3.11-bookworm

LABEL maintainer="xLasercut"

ARG WRK_DIR=/home/edge_booking

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y curl bash bash-completion firefox && \
    mkdir ${WRK_DIR}

WORKDIR ${WRK_DIR}

RUN pip install pipenv

COPY Pipfile ${WRK_DIR}/Pipfile
COPY Pipfile.lock ${WRK_DIR}/Pipfile.lock

RUN pipenv install --deploy --system

COPY src/. ${WRK_DIR}/src/
COPY main.py ${WRK_DIR}/main.py
COPY config.ini ${WRK_DIR}/config.ini

CMD ["python", "main.py"]