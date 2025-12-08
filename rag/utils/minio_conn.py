#
#  Copyright 2025 The InfiniFlow Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

import logging
import time
from urllib.parse import urlparse
from minio import Minio
from minio.error import S3Error
from io import BytesIO
from rag import settings
from rag.utils import singleton


@singleton
class RAGFlowMinio:
    def __init__(self):
        self.conn = None
        self.__open__()

    def __open__(self):
        try:
            if self.conn:
                self.__close__()
        except Exception:
            pass

        try:
            # Internal client: unchanged internal IO endpoint
            self.conn = Minio(settings.MINIO["host"],
                              access_key=settings.MINIO["user"],
                              secret_key=settings.MINIO["password"],
                              secure=False
                              )
        except Exception:
            logging.exception(
                "Fail to connect %s " % settings.MINIO["host"])

    def __close__(self):
        del self.conn
        self.conn = None

    def health(self):
        bucket, fnm, binary = "txtxtxtxt1", "txtxtxtxt1", b"_t@@@1"
        if not self.conn.bucket_exists(bucket):
            self.conn.make_bucket(bucket)
        r = self.conn.put_object(bucket, fnm,
                                 BytesIO(binary),
                                 len(binary)
                                 )
        return r

    def put(self, bucket, fnm, binary):
        for _ in range(3):
            try:
                if not self.conn.bucket_exists(bucket):
                    self.conn.make_bucket(bucket)

                r = self.conn.put_object(bucket, fnm,
                                         BytesIO(binary),
                                         len(binary)
                                         )
                return r
            except Exception:
                logging.exception(f"Fail to put {bucket}/{fnm}:")
                self.__open__()
                time.sleep(1)

    def rm(self, bucket, fnm):
        try:
            self.conn.remove_object(bucket, fnm)
        except Exception:
            logging.exception(f"Fail to remove {bucket}/{fnm}:")

    def get(self, bucket, filename):
        for _ in range(1):
            try:
                r = self.conn.get_object(bucket, filename)
                return r.read()
            except Exception:
                logging.exception(f"Fail to get {bucket}/{filename}")
                self.__open__()
                time.sleep(1)
        return

    def obj_exist(self, bucket, filename):
        try:
            if not self.conn.bucket_exists(bucket):
                return False
            if self.conn.stat_object(bucket, filename):
                return True
            else:
                return False
        except S3Error as e:
            if e.code in ["NoSuchKey", "NoSuchBucket", "ResourceNotFound"]:
                return False
        except Exception:
            logging.exception(f"obj_exist {bucket}/{filename} got exception")
            return False

    def get_presigned_url(self, bucket, fnm, expires):
        """Generate a presigned URL that is consumable at the public /storage path.

        Internal IO stays on the internal endpoint. We only shape the returned URL
        so that the visible host comes from public_base_url and the path includes
        the configured public_path_prefix. The canonical path remains /bucket/object
        when MinIO verifies the signature (proxy strips the prefix).
        """
        for _ in range(10):
            try:
                logging.warning(f"minio_conn.get_presigned_url: bucket={bucket} key={fnm} expires={expires}")
                public_base = (settings.MINIO.get("public_base_url") or "").strip()
                public_prefix = (settings.MINIO.get("public_path_prefix") or "").strip()

                # Always presign with the internal client (host minio:9000)
                url = self.conn.get_presigned_url("GET", bucket, fnm, expires)
                logging.warning(f"minio_conn.get_presigned_url: internal_url={url}")

                if public_base:
                    if public_base.endswith('/'):
                        public_base = public_base[:-1]
                    if public_prefix and not public_prefix.startswith('/'):
                        public_prefix = '/' + public_prefix
                    scheme_sep = url.find('://')
                    if scheme_sep != -1:
                        path_start = url.find('/', scheme_sep + 3)
                        if path_start != -1:
                            path_and_query = url[path_start:]
                            url = f"{public_base}{public_prefix}{path_and_query}"
                logging.warning(f"minio_conn.get_presigned_url: final_url={url}")
                return url
            except Exception:
                logging.exception(f"Fail to get_presigned {bucket}/{fnm}:")
                self.__open__()
                time.sleep(1)
        return

