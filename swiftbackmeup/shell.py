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

from swiftbackmeup import configuration
from swiftbackmeup import parser
from swiftbackmeup import utils
from swiftbackmeup import lists
from swiftbackmeup.databases import mariadb
from swiftbackmeup.databases import postgresql


_CONF = {
    'clean_local_copy': True,
    'create_container': True,
    'purge_backup': False,
}

_METHODS = ['list', 'list_databases']

def main():

    options = parser.parse()

    if options.conf:
        _CONF['file_path'] = options.conf

    global_configuration = configuration.load_configuration(_CONF)

    configuration.verify_mandatory_parameter(global_configuration)
    backups = configuration.expand_configuration(global_configuration)
    backups = utils.filter_databases(options.databases, backups)
    modes = global_configuration.get('mode')

    # swiftbackmeup restore ...
    if 'version' in options:
        for backup in backups:
            if backup['type'] == 'postgresql':
                cur_backup = postgresql.PostgreSQL(backup)
            elif backup['type'] == 'mariadb':
                cur_backup = mariadb.MariaDB(backup)
            if options.force:
                cur_backup.restore(options.version)
            elif utils.query_yes_no('Are you sure you want to restore the database?',
                                  default='no'):
                cur_backup.restore(options.version)
            else:
                print 'Exiting without restoring the database'

    # swiftbackmeup purge ...
    elif 'noop' in options:
        purge = False
        purged_backups = []

        if options.force:
            purge = True
        elif not options.force and utils.query_yes_no('Are you sure you want to purge the backups?',
                                                    default='no'):
            purge = True
        else:
            print 'Exiting without purging the backups'
        if purge:
            for backup in backups:
                if backup['type'] == 'postgresql':
                    cur_backup = postgresql.PostgreSQL(backup)
                elif backup['type'] == 'mariadb':
                    cur_backup = mariadb.MariaDB(backup)
                purged_backups += cur_backup.purge(modes[options.mode], options.noop)
            lists.list_purged_backups(purged_backups, options.noop)

    # swiftbackmeup backup ...
    else:
        # If a --list-* options has been specified, call the proper method
        # and exit
        #
        for method in _METHODS:
            if getattr(options, method):
                if method == 'list_databases':
                    lists.list_databases(backups, options)
                elif method == 'list':
                    lists.list_remote_backups(backups, options, modes)
                return
 

        for backup in backups:
            if options.mode in backup['subscriptions']:
                backup['filename'] = utils.build_filename(backup,
                                                          modes[options.mode])
                if backup['type'] == 'postgresql':
                    cur_backup = postgresql.PostgreSQL(backup)
                elif backup['type'] == 'mariadb':
                    cur_backup = mariadb.MariaDB(backup)
                cur_backup.run()
                cur_backup.upload()
