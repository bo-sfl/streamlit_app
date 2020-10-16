FROM python:3.8.6-slim

RUN pip install streamlit==0.69.1 \
    plotly==4.11.0

ENV STREAMLIT_SERVER_PORT=8081
ENV GIT_PYTHON_REFRESH=quiet
EXPOSE 8081

COPY . /src

WORKDIR src

ENTRYPOINT [ "run.sh" ]