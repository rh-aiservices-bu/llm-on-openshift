FROM registry.access.redhat.com/ubi9/python-311

WORKDIR /opt/app-root/src

USER 1001

COPY --chown=1001:0 requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt && \
    rm -f requirements.txt && \
    # Fix permissions to support pip in Openshift environments \
    chmod -R g+w /opt/app-root/lib/python3.11/site-packages && \
    fix-permissions /opt/app-root -P

COPY --chown=1001:0 app.py ./
COPY --chown=1001:0 assets/ ./assets/

EXPOSE 7860

CMD ["python", "app.py"]

