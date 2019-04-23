# Let's get this party started!
import falcon
import falcon_jsonify

from chariot_base.utilities import open_config_file
from falcon_multipart.middleware import MultipartMiddleware

from chariot_base.utilities import Tracer
from chariot_firmware_upload_service.store import FirmwareStore, FirmwareUploader
from chariot_firmware_upload_service.resources import FirmwareResource
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
    'hostname': '192.168.2.32', 
    'username': '', 
    'password': '',
    'storage_path': 'upload'
})

firmware = FirmwareResource(store, uploader)

if options_tracer['enabled']:
    tracer = Tracer(options_tracer)
    tracer.init_tracer()
    firmware.inject_tracer(tracer)

app.add_route('/firmware', firmware)

if __name__ == '__main__':
    httpd = simple_server.make_server('127.0.0.1', 9000, app)
    httpd.serve_forever()