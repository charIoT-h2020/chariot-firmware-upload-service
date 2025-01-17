import io
import os
import logging

import ftplib


class FirmwareUploader():
    def __init__(self, options):
        self.storage_path = options['storage_path']

    def do(self, filename, options):
        url = options['hostname']
        username = options['username'] or ''
        password = options['password'] or ''
        upload_path = options['upload_path']

        path = os.path.join(self.storage_path, filename)
        remotefile = os.path.join(upload_path, filename)

        try:
            with ftplib.FTP(url) as ftp:
                ftp.login(username, password)

                with open(path, 'rb') as f:
                    try:
                        ftp.storbinary('STOR ' + remotefile, f, 1024)
                        return True, None
                    except ftplib.all_errors as e:
                        if e.args[0][:3] == '550':
                            logging.debug('Remote file not exist error caught: ' + remotefile)
                            ftp.mkd(upload_path)
                            self.do(filename, options)
                        else:
                            logging.error(e)
                            return False, e
        except ftplib.all_errors as e:
            logging.debug('%s, %s, %s' % (url, username, password))
            logging.error(e)
            return False, e

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
            firmware_path = os.path.join(self._storage_path, name)
            logging.info('Saving at {name}...'.format(name=firmware_path))

            with self._fopen(firmware_path, 'wb') as firmware_file:
                while True:
                    chunk = firmware_stream.read(self._CHUNK_SIZE_BYTES)
                    if not chunk:
                        break
                    firmware_file.write(chunk)

            return name
        except Exception as ex:
            logging.info(ex)
            return None