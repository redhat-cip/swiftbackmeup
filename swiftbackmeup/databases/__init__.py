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

from swiftbackmeup import utils
from swiftbackmeup.stores import swift


import datetime
import exceptions
import os
import subprocess

class Database(object):


    def __init__(self, conf):
        self.host = conf.get('host')
        self.user = conf.get('user')
        self.password = conf.get('password')
        self.database = conf.get('database')
        self.env = os.environ
        self.dump_options = conf.get('dump_options')

        # Local backup file related
        self.backup_file = conf.get('filename')
        self.backup_filename = conf.get('backup_filename')
        self.backup_filename_prefix = conf.get('backup_filename_prefix')
        self.backup_filename_suffix = conf.get('backup_filename_suffix')
        self.output_directory = conf.get('output_directory')
        self.clean_local_copy = conf.get('clean_local_copy')

        self.store_type = conf.get('store_type')
        self.store = self.get_store(conf)

        # Swift related
        self.swift_container = conf.get('swift_container')
        self.swift_pseudo_folder = conf.get('swift_pseudo_folder')


    def get_store(self, conf):
        if self.store_type == 'swift':
            store = swift.Swift(conf)
        else:
            raise Exception('Unknown store_type: %s' % self.store_type)

        return store


    def run(self):
        try:
            backup_file_f = open('%s/%s' % (self.output_directory, self.backup_file), 'w')
        except IOError as exc:
            raise

        p = subprocess.Popen(self.command.split(), stdout=backup_file_f, env=self.env)
        p.wait()
        backup_file_f.flush()


    def restore(self, backup_filename):
        self.store.get(self.swift_container, backup_filename, self.output_directory)


    def purge(self, mode, noop):
        backups = self.store.list(self.database, self.swift_container,
                                  self.backup_filename,
                                  self.swift_pseudo_folder,
                                  self.backup_filename_prefix,
                                  self.backup_filename_suffix)

        if mode['unit'] == 'item':
            if len(backups) > mode['retention']:
                backups = backups[:-mode['retention']]
            else:
                backups = []
        else:
            tmp_backup = []
            for backup in backups:
                if (datetime.datetime.now() - datetime.datetime.strptime(backup['last-modified'], '%Y-%m-%dT%H:%M:%S.%f')).days >= mode['retention']:
                    tmp_backup.append(backup)
            backups = tmp_backup

        if not noop:
            for backup in backups:
                self.store.delete(self.swift_container, backup['filename'])

        return backups


    def _clean_local_copy(self, backup_file=None):

        if not backup_file:
            self.backup_file

        try:
            os.remove('%s/%s' % (self.output_directory, backup_file))
        except OSError:
            raise


    def list(self):
        return self.store.list(self.database, self.swift_container,
                               self.backup_filename, self.swift_pseudo_folder,
                               self.backup_filename_prefix,
                               self.backup_filename_suffix)


    def upload(self):
       self.store.upload(self.swift_container,
                         '%s/%s' % (self.output_directory, self.backup_file),
                         self.swift_pseudo_folder, True) #create_container
       if self.clean_local_copy:
           self._clean_local_copy(self.backup_file)



    def build_restore_command(self, backup_filename):
        pass


    def build_dump_command(self):
        pass
