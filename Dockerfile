FROM registry.gitlab.com/chariot-h2020/chariot_base:latest

VOLUME ["/usr/src/app"]
WORKDIR /usr/src/app

# Bundle app source
COPY . .

EXPOSE 8033

RUN pip install falcon-jsonify && python setup.py install

ENTRYPOINT ["/usr/local/bin/gunicorn", "--config", "/usr/src/app/gunicorn.py", "chariot_firmware_upload_service.app:app"]
