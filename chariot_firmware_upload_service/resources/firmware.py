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
        fileStorage = req.get_param('file')
        version = req.get_param('version')
        hostname = req.get_param('hostname')
        username = req.get_param('username')
        password = req.get_param('password')
        upload_path = req.get_param('upload_path')

        name = self._firmware_store.save(fileStorage, version)
        self._uploader.do(name, {
            'hostname': hostname,
            'username': username,
            'password': password,
            'upload_path': upload_path
        })
        resp.status = falcon.HTTP_201

        self.close_span(span)
