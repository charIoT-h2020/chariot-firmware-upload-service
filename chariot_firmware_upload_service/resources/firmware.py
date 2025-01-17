import io
import os
import uuid
import json
import falcon
import logging
import mimetypes

from chariot_base.utilities import Traceable


class FirmwareResource(Traceable):

    def __init__(self, firmware_store, uploader):
        super(Traceable, self).__init__()
        self.tracer = None
        self._firmware_store = firmware_store
        self._uploader = uploader

    def on_post(self, req, resp):
        span = self.start_span_from_request('upload_firmware', req)
        try:
            fileStorage = req.get_param('file')
            version = req.get_param('version')
            hostname = req.get_param('hostname')
            username = req.get_param('username')
            password = req.get_param('password')
            upload_path = req.get_param('upload_path')
        
            name = self._firmware_store.save(fileStorage, version)
            logging.info('File is saved')
        
            status, ex = self._uploader.do(name, {
                'hostname': hostname,
                'username': username,
                'password': password,
                'upload_path': upload_path
            })
            logging.info('File is uploaded')

            if status is True:
                resp.status = falcon.HTTP_201
            else:
                resp.status = falcon.HTTP_500

            resp.body = json.dumps({'status': status, 'message': str(ex)}, ensure_ascii=False)
            resp.content_type = falcon.MEDIA_JSON

            self.close_span(span)
        except Exception as ex:
            logging.error(ex)
            self.set_tag(span, 'is_ok', False)
            self.error(span, ex, False)
            self.close_span(span)
