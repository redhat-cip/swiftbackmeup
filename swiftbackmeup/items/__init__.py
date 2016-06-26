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

from swiftbackmeup.stores import swift

import datetime
import exceptions
import os
import subprocess


class Item(object):


    def __init__(self, conf):
        self.name = conf.get('name')
        self.env = os.environ

        self.backup_file = conf.get('filename')
        self.backup_filename = conf.get('backup_filename')
        self.backup_filename_prefix = conf.get('backup_filename_prefix')
        self.backup_filename_suffix = conf.get('backup_filename_suffix')
        self.output_directory = conf.get('output_directory')
        self.clean_local_copy = conf.get('clean_local_copy')

        self.store_type = conf.get('store_type')
        self.store = self.get_store(conf)

        self.create_container = conf.get('create_container')
        self.purge_container = conf.get('purge_container')

        # store_type: swift
        self.swift_container = conf.get('swift_container')
        self.swift_pseudo_folder = conf.get('swift_pseudo_folder')


    def get_store(self, conf):
        """Method to retrieve a connection to the remote store."""

        if self.store_type == 'swift':
            store = swift.Swift(conf)
        else:
            raise Exception('Unknown store_type: %s' % self.store_type)

        return store


    def type(self):
        """Method to retrieve the type object the backup was made from."""
        pass


    def run(self, with_intermediate_file=False, cwd=None):
        """Method to run the backup command where it applies."""

        command = self.build_dump_command()

        if with_intermediate_file:
            try:
                backup_file_f = open('%s/%s' % (self.output_directory,
                                                self.backup_file), 'w')
            except IOError as exc:
                raise

            p = subprocess.Popen(command.split(), stdout=backup_file_f,
                                 env=self.env, cwd=cwd)
            p.wait()
            backup_file_f.flush()
        else:
            FNULL = open(os.devnull, 'w')
            p = subprocess.Popen(command.split(), env=self.env, cwd=cwd,
                                 stdout=FNULL, stderr=subprocess.STDOUT)


    def restore(self, backup_filename,with_intermediate_file=False):
        """Method to restore the backup."""

        self.store.get(self.swift_container, backup_filename,
                       self.output_directory)
        command = self.build_restore_command(backup_filename)


        if with_intermediate_file:
            file_path = '%s/%s' % (self.output_directory, backup_filename)
            backup_file_content = open(file_path, 'r').read()

            p = subprocess.Popen(command.split(), stdin=subprocess.PIPE)
            p.communicate(backup_file_content)
        else:
            FNULL = open(os.devnull, 'w')
            p = subprocess.Popen(command.split(), stdout=FNULL,
                                 stderr=subprocess.STDOUT)
            p.wait()

        if self.clean_local_copy:
            self._clean_local_copy(backup_filename)


    def purge(self, mode, noop=False):
        """Method to purge the remote backups."""

        backups = self.store.list(self.name, self.type(),
                                  self.swift_container,
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


    def list(self):
        """Method to list the backups of a given item on the remote store."""

        return self.store.list(self.name, self.type(), self.swift_container,
                               self.backup_filename, self.swift_pseudo_folder,
                               self.backup_filename_prefix,
                               self.backup_filename_suffix)


    def upload(self):
        """Method to upload a backup of a given item on the remote store."""

        self.store.upload(self.swift_container,
                          '%s/%s' % (self.output_directory, self.backup_file),
                          self.swift_pseudo_folder, self.create_container)
        if self.clean_local_copy:
            self._clean_local_copy(self.backup_file)


    def build_restore_command(self, backup_filename):
        """Method to build the restore command that will be run."""
        pass


    def build_dump_command(self):
        """Method to build the dump command that will be run."""
        pass


    def _clean_local_copy(self, backup_file=None):

        if not backup_file:
            self.backup_file

        try:
            os.remove('%s/%s' % (self.output_directory, backup_file))
        except OSError:
            raise
