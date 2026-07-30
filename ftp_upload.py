#!/usr/bin/env python3

import os
import argparse
from ftplib import FTP_TLS


def argument_parser():

    parser = argparse.ArgumentParser(
        description="FTPS upload/download utility"
    )

    actions = parser.add_mutually_exclusive_group(
        required=True
    )

    actions.add_argument(
        "-l",
        "--list",
        action="store_true",
        help="list remote files"
    )

    actions.add_argument(
        "-u",
        "--upload",
        metavar="FILE",
        help="upload local file"
    )

    actions.add_argument(
        "-d",
        "--download",
        metavar="FILE",
        help="download remote file"
    )

    actions.add_argument(
        "--delete",
        metavar="FILE",
        help="delete remote file"
    )

    parser.add_argument(
        "--remote-name",
        help="remote filename override"
    )

    parser.add_argument(
        "--output",
        help="local output filename for downloads"
    )

    return parser


class FTPClient:

    def __init__(self):

        self.host = os.environ["FIGSHARE_FTP_HOST"]
        self.user = os.environ["FIGSHARE_FTP_USER"]
        self.password = os.environ["FIGSHARE_FTP_PASS"]

        self.ftp = FTP_TLS(self.host)

        self.ftp.login(
            self.user,
            self.password
        )

        # encrypt data channel too
        self.ftp.prot_p()

    def upload(self, local_file, remote_file=None):

        remote_file = remote_file or local_file

        self.ftp.cwd('data/files')
        with open(local_file, "rb") as fh:
            self.ftp.storbinary(
                f"STOR {remote_file}",
                fh
            )

    def delete(self, remote_file):
        self.ftp.delete(remote_file)

    def download(self, remote_file, local_file=None):

        local_file = local_file or remote_file

        with open(local_file, "wb") as fh:
            self.ftp.retrbinary(
                f"RETR {remote_file}",
                fh.write
            )

    def list(self, path="."):

        return self.ftp.nlst(path)

    def walk(self, path="."):

        try:

            for name, facts in self.ftp.mlsd(path):

                if name in (".", ".."):
                    continue

                full_path = (
                    f"{path.rstrip('/')}/{name}"
                    if path != "."
                    else name
                )

                entry_type = facts.get("type", "file")

                yield {
                    "type": entry_type,
                    "path": full_path,
                }

                if entry_type == "dir":
                    yield from self.walk(full_path)

        except Exception:

            for name in self.ftp.nlst(path):
                yield {
                    "type": "unknown",
                    "path": name,
                }

    def close(self):

        self.ftp.quit()


if __name__ == "__main__":

    args = argument_parser().parse_args()

    ftp = FTPClient()

    try:

        if args.list:
            for entry in ftp.walk():
                print(
                    f"{entry['type']:8} "
                    f"{entry['path']}"
                )

        elif args.upload:
            ftp.upload(
                args.upload,
                args.remote_name
            )

        elif args.download:
            ftp.download(
                args.download,
                args.output
            )

        elif args.delete:
            ftp.delete(
                args.delete
            )

    finally:
        ftp.close()