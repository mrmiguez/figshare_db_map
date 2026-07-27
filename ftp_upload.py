#!/usr/bin/env python3

import os
from ftplib import FTP


class FTPClient:

    def __init__(self):

        self.host = os.environ["FIGSHARE_FTP_HOST"]
        self.user = os.environ["FIGSHARE_FTP_USER"]
        self.password = os.environ["FIGSHARE_FTP_PASS"]

        self.ftp = FTP(self.host)
        self.ftp.login(self.user, self.password)

    def upload(self, local_file, remote_file=None):

        remote_file = remote_file or local_file

        with open(local_file, "rb") as fh:
            self.ftp.storbinary(
                f"STOR {remote_file}",
                fh
            )

    def download(self, remote_file, local_file=None):

        local_file = local_file or remote_file

        with open(local_file, "wb") as fh:
            self.ftp.retrbinary(
                f"RETR {remote_file}",
                fh.write
            )

    def list(self, path="."):

        return self.ftp.nlst(path)

    def close(self):

        self.ftp.quit()


if __name__ == "__main__":

    ftp = FTPClient()

    print(ftp.list())

    ftp.close()