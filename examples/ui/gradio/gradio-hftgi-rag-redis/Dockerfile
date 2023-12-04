FROM registry.access.redhat.com/ubi9/python-311

WORKDIR /opt/app-root/src

USER root

COPY rpms/ ./rpms/

RUN cd rpms && rpm -i --nodeps *.rpm

RUN yum install -y wget libXrender libXext fontconfig  && \
    wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-3/wkhtmltox-0.12.6.1-3.almalinux9.x86_64.rpm && \
    yum install -y ./wkhtmltox-0.12.6.1-3.almalinux9.x86_64.rpm && \
    rm ./wkhtmltox-0.12.6.1-3.almalinux9.x86_64.rpm

WORKDIR /opt/app-root/src

RUN rm -rf rpms

USER 1001

COPY --chown=1001:0 requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt && \
    rm -f requirements.txt && \
    chmod -R g+w /opt/app-root/lib/python3.11/site-packages && \
    fix-permissions /opt/app-root -P   

COPY --chown=1001:0 app.py ./
COPY --chown=1001:0 assets/ ./assets/ 

EXPOSE 7860

EXPOSE 8000

CMD ["python", "app.py"]

