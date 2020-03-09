# Copyright 2016 Yanis Guenane <yguenane@redhat.com>
# Author: Yanis Guenane <yguenane@redhat.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from swiftbackmeup import stores
from swiftbackmeup import exceptions

import os
import re
import swiftclient


class Swift(stores.Store):
    def __init__(self, conf):
        if conf["os_identity_api_version"] == 2:
            self.connection = self.get_connection_v2(conf)
        elif conf["os_identity_api_version"] == 3:
            self.connection = self.get_connection_v3(conf)

    def get_connection_v2(self, conf):
        return swiftclient.client.Connection(
            auth_version="2",
            user=conf["os_username"],
            key=conf["os_password"],
            tenant_name=conf["os_tenant_name"],
            os_options={"os_region_name": conf["os_region_name"]},
            authurl=conf["os_auth_url"],
        )

    def get_connection_v3(self, conf):
        return swiftclient.client.Connection(
            auth_version="3",
            user=conf["os_username"],
            key=conf["os_password"],
            os_options={
                k: conf[k]
                for k in (
                    "os_region_name",
                    "os_project_id",
                    "os_project_name",
                    "os_user_domain_name",
                    "os_user_domain_id",
                    "os_project_domain_name",
                    "os_project_domain_id",
                )
                if conf[k]
            },
            authurl=conf["os_auth_url"],
        )

    def delete(self, container, filename):
        try:
            self.connection.delete_object(container, filename)
        except swiftclient.exceptions.ClientException:
            raise exceptions.StoreExceptions(
                "An error occured while deleting %s" % filename
            )

    def get(self, container, filename, output_directory):
        try:
            resp_headers, obj_contents = self.connection.get_object(container, filename)
        except swiftclient.exceptions.ClientException as exc:
            if exc.http_reason == "Not Found":
                raise exceptions.StoreExceptions(
                    "%s: File not found in store" % filename
                )

        backup_directory = os.path.dirname("%s/%s" % (output_directory, filename))
        if not os.path.exists(backup_directory):
            os.makedirs(backup_directory)

        with open("%s/%s" % (output_directory, filename), "w") as backup:
            backup.write(obj_contents)

    def list(
        self,
        item,
        item_type,
        container,
        filename=None,
        pseudo_folder=None,
        filename_prefix=None,
        filename_suffix=None,
    ):

        if pseudo_folder:
            if filename:
                backup_name_pattern = "%s/%s" % (pseudo_folder, filename)
            else:
                backup_name_pattern = pseudo_folder or ""
                if filename_prefix and filename_suffix:
                    backup_name_pattern += "/%s.*%s" % (
                        filename_prefix,
                        filename_suffix,
                    )
                elif filename_prefix and not filename_suffix:
                    backup_name_pattern += "/%s.*" % filename_prefix
                elif not filename_prefix and filename_suffix:
                    backup_name_pattern += "/.*%s" % filename_suffix

        else:
            if filename:
                backup_name_pattern = filename
            else:
                backup_name_pattern = ""
                if filename_prefix and filename_suffix:
                    backup_name_pattern += "%s.*%s" % (filename_prefix, filename_suffix)
                elif filename_prefix and not filename_suffix:
                    backup_name_pattern += "%s.*" % filename_prefix
                elif not filename_prefix and filename_suffix:
                    backup_name_pattern += ".*%s" % filename_suffix

        resp, data = self.connection.get_container(container)

        result = []
        for backup in data:
            m = re.search(backup_name_pattern, backup["name"])
            if m:
                result.append(
                    {
                        "item": item,
                        "type": item_type,
                        "filename": m.group(0),
                        "last-modified": backup["last_modified"],
                    }
                )
        return result

    def upload(self, container, file_path, pseudo_folder=None, create_container=True):
        try:
            self.connection.head_container(container)
        except swiftclient.exceptions.ClientException as exc:
            if exc.http_reason == "Not Found" and create_container:
                self.connection.put_container(container)

        if pseudo_folder:
            swift_path = "%s/%s" % (pseudo_folder, os.path.basename(file_path))
        else:
            swift_path = os.path.basename(file_path)

        with open(file_path, "rb") as fd:
            self.connection.put_object(container, swift_path, contents=fd)
