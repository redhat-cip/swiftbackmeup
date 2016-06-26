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

from swiftbackmeup.items import databases

import subprocess

class MariaDB(databases.Database):

    def __init__(self, conf):
        super(MariaDB, self).__init__(conf)


    def type(self):
        return 'databases/mariadb'


    def run(self):
        super(MariaDB, self).run(with_intermediate_file=True)


    def restore(self, backup_filename):
        super(MariaDB, self).restore(backup_filename,
                                     with_intermediate_file=True)


    def build_restore_command(self, backup_filename):
        command = 'mysql'

        if self.user:
            command += ' -u%s' % self.user

        if self.host:
            command += ' -h%s' % self.host

        if self.password:
            command += ' -p%s' % self.password

        return command


    def build_dump_command(self):

        command = 'mysqldump'

        if self.dump_options:
            command += ' %s' % self.dump_options

        if self.user:
            command += ' -u%s' % self.user

        if self.host:
            command += ' -h%s' % self.host

        if self.password:
            command += ' -p%s' % self.password

        if self.database == 'all':
            command += ' --all-databases'
        else:
            command += ' --databases %s' % self.database

        return command
