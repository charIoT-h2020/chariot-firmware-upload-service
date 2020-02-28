import logging

import falcon
import falcon_jsonify
from falcon_multipart.middleware import MultipartMiddleware

from chariot_base.utilities import Tracer
from chariot_base.utilities import open_config_file
from chariot_firmware_upload_service import __service_name__
from chariot_firmware_upload_service.resources import FirmwareResource
from chariot_firmware_upload_service.store import FirmwareStore, FirmwareUploader

from wsgiref import simple_server

# falcon.API instances are callable WSGI apps
app = falcon.API(middleware=[
    MultipartMiddleware(),
    # falcon_jsonify.Middleware(help_messages=True),
])


opts = open_config_file()

options_tracer = opts.tracer

# Resources are represented by long-lived class instances
store = FirmwareStore('upload')
uploader = FirmwareUploader({
    'storage_path': 'upload'
})

firmware = FirmwareResource(store, uploader)

if options_tracer['enabled'] is True:
    options_tracer['service'] = __service_name__
    logging.info(f'Enabling tracing for service "{__service_name__}"')
    tracer = Tracer(options_tracer)
    tracer.init_tracer()
    firmware.inject_tracer(tracer)

app.add_route('/firmware', firmware)

if __name__ == '__main__':
    httpd = simple_server.make_server('127.0.0.1', 9000, app)
    httpd.serve_forever()