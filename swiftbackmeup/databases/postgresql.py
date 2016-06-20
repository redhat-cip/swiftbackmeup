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

from swiftbackmeup import databases


class PostgreSQL(databases.Database):

    def __init__(self, conf):
        super(PostgreSQL, self).__init__(conf)
        self.pg_dump_options = conf.get('pg_dump_options')
        self.command = self.build_command()

    def build_command(self):
        command = 'pg_dump'

        if self.pg_dump_options:
            command += ' %s' % self.pg_dump_options

        if self.user:
            command += ' -U %s' % self.user

        if self.host:
            command += ' -h %s' % self.host
        
        if self.database:
            command += ' %s' % self.database

        if self.password:
            self.env['PGPASSWORD'] = self.password

        return command
