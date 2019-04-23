import io
import os
import logging

import ftplib


class FirmwareUploader():
    def __init__(self, options):
        self.storage_path = options['storage_path']

    def do(self, file, options):
        url = options['hostname']
        username = options['username']
        password = options['password']
        path = os.path.join(self.storage_path, file)
        
        ftp = ftplib.FTP(url)
        
        ftp.login()
        ftp.storbinary("STOR " + file, open(path, "rb"), 1024)
        ftp.quit()

class FirmwareStore():

    _CHUNK_SIZE_BYTES = 4096

    def __init__(self, storage_path, fopen=io.open):
        self._storage_path = storage_path
        self._fopen = fopen

    def save(self, fileStorage, version):
        logging.debug('Saving file...')
        firmware_stream = fileStorage.file
        filename, file_extension = os.path.splitext(fileStorage.filename)
        
        try:
            name = '{filename}{ext}'.format(filename=filename, version=version, ext=file_extension)
            logging.info('Saving at {name}...'.format(name=name))
            firmware_path = os.path.join(self._storage_path, name)

            with self._fopen(firmware_path, 'wb') as firmware_file:
                while True:
                    chunk = firmware_stream.read(self._CHUNK_SIZE_BYTES)
                    if not chunk:
                        break
                    firmware_file.write(chunk)

            return name
        except Exception as ex:
            logging.debug(ex)