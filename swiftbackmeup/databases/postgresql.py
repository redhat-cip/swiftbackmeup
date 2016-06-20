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
from swiftbackmeup import exceptions


_PARAMS = {
  'data_only': '-a',
  'globals_only': '-g',
  'roles_only': '-r',
  'schema_only': '-s',
  'tablespaces_only': '-t'
}

class PostgreSQL(databases.Database):

    def __init__(self, conf):
        super(PostgreSQL, self).__init__(conf)
        self.pg_dump_options = conf.get('pg_dump_options')
        # pg_dumpall parameter
        self.data_only = conf.get('data_only')
        self.globals_only = conf.get('globals_only')
        self.roles_only = conf.get('roles_only')
        self.schema_only = conf.get('schema_only')
        self.tablespaces_only = conf.get('tablespaces_only')

        self.command = self.build_command()

    def build_command(self):

        if self.database == 'all':
            command = 'pg_dumpall'
        else:
            command = 'pg_dump'

        # pg_dumpall *-only options management
        if self.globals_only and self.roles_only:
            raise exceptions.ConfigurationExceptions('%s: options globals_only and roles_only cannot be used together' % self.database)
        elif self.globals_only and self.tablespaces_only:
            raise  exceptions.ConfigurationExceptions('%s: options globals_only and tablespaces_only cannot be used together' % self.database)
        elif self.tablespaces_only and self.roles_only:
            raise  exceptions.ConfigurationExceptions('%s: options tablespaces_only and roles_only cannot be used together' % self.database)

        for param in _PARAMS.keys():
            if getattr(self, param, None):
                command += ' %s' %  _PARAMS[param]

        if self.pg_dump_options and not self.database == 'all':
            command += ' %s' % self.pg_dump_options

        if self.user:
            command += ' -U %s' % self.user

        if self.host:
            command += ' -h %s' % self.host
        
        if self.database and not self.database == 'all':
            command += ' %s' % self.database

        if self.password:
            self.env['PGPASSWORD'] = self.password

        return command
