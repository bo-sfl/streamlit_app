FROM python:3.8.6-slim as base

FROM base as builder
COPY requirements.txt /requirements.txt
RUN pip install --prefix=/install \
    --no-warn-script-location \
    # --no-dependencies \
    -r /requirements.txt

FROM base
COPY --from=builder /install /usr/local

ENV STREAMLIT_SERVER_PORT=8081
ENV GIT_PYTHON_REFRESH=quiet
EXPOSE 8081

COPY . /src
WORKDIR /src
ENTRYPOINT [ "./run.sh" ]