FROM registry.access.redhat.com/ubi9/python-311:9.5

USER 0

RUN dnf -y update --setopt=tsflags=nodocs && \
    dnf clean all && \
    mkdir -p /opt/app-root/bin && \
    chown -R 1001:0 /opt/app-root

ENV PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=UTF-8 \
    LC_ALL=en_US.UTF-8 \
    LANG=en_US.UTF-8 \
    PIP_NO_CACHE_DIR=1 \
    HOME=/opt/app-root/src \
    PATH=/opt/app-root/src:$PATH

USER 1001

WORKDIR /opt/app-root/bin

COPY --chown=1001:0 . .

RUN pip3 install --no-cache-dir -r requirements.txt

WORKDIR /opt/app-root/src

EXPOSE 8888

CMD ["python3", "-m", "uvicorn", "--app-dir", "/opt/app-root/bin", "docling_serve.app:create_app", "--factory", "--host", "0.0.0.0", "--port", "8888"]