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

import os
import subprocess
import swiftclient

class Database(object):


    def __init__(self, conf):
        print conf
        self.host = conf.get('host')
        self.user = conf.get('user')
        self.password = conf.get('password')
        self.database = conf.get('database')

        # Local backup file related
        self.backup_file = conf.get('filename')
        self.output_directory = conf.get('output_directory')

        # Swift related
        self.os_username = conf.get('os_username')
        self.os_password = conf.get('os_password')
        self.os_tenant_name = conf.get('os_tenant_name')
        self.os_auth_url = conf.get('os_auth_url')
        self.swift_container = conf.get('swift_container')
        self.swift_pseudo_folder = conf.get('swift_pseudo_folder')


    def run_backup(self):
        try:
            backup_file_f = open('%s/%s' % (self.output_directory, self.backup_file), 'w')
        except IOError as exc:
            raise

        p = subprocess.Popen(self.command.split(), stdout=backup_file_f)
        p.wait()
        backup_file_f.flush()

    def clean_local_copy(self):
        try:
            os.remove('%s/%s' % (self.output_directory, self.backup_file))
        except OSError:
            raise

    def upload_to_swift(self):
        swift = swiftclient.client.Connection(auth_version='2',
                                              user=self.os_username,
                                              key=self.os_password,
                                              tenant_name=self.os_tenant_name,
                                              authurl=self.os_auth_url)

        try:
            swift.head_container(self.swift_container)
        except swiftclient.exceptions.ClientException as exc:
            if exc.http_reason == 'Not Found':
                swift.put_container(self.swift_container)
                
        backup_file_content = open('%s/%s' % (self.output_directory,
                                              self.backup_file), 'r').read()

        swift.put_object(self.swift_container,
                         '%s/%s' % (self.swift_pseudo_folder, self.backup_file),
                         backup_file_content)
