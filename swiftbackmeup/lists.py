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

from prettytable import PrettyTable
from swiftbackmeup import utils
from swiftbackmeup.items.databases import postgresql, mariadb
from swiftbackmeup.items.filesystems import file, git

_FULL_TYPE = {
    'mariadb': 'databases/mariadb',
    'postgresql': 'databases/postgres',
    'file': 'filesystem/file',
    'git': 'filesystem/git',
}

# If --list-items has been specified, list the backups items configured
# in the configuration file
#
def list_items(backups, options):
    result = [['Item', []],
              ['Type', []],
              ['Host', []],
              ['Swift Container', []],
              ['Swift Pseudo-Folder', []],
              ['Subscriptions', []]]
    for backup in backups:
        if options.mode in backup['subscriptions']:
            result[0][1].append(backup['name'])
            result[1][1].append(_FULL_TYPE[backup['type']])
            result[2][1].append(backup['host'])
            result[3][1].append(backup['swift_container'])
            result[4][1].append(backup['swift_pseudo_folder'])
            result[5][1].append(', '.join(backup['subscriptions']))
    utils.output_informations(result)


# If --list has been specified, list the backups available
# on the specified store
#
def list_remote_backups(backups, options, modes):
    result = [['Item', []],
              ['Type', []],
              ['Backup file', []],
              ['Last Modified', []]]
    for backup in backups:
        if options.mode in backup['subscriptions']:
            backup['filename'] = utils.build_filename(backup,
                                                      modes[options.mode])
            if backup['type'] == 'postgresql':
                cur_backup = postgresql.PostgreSQL(backup)
            elif backup['type'] == 'mariadb':
                cur_backup = mariadb.MariaDB(backup)
            elif backup['type'] == 'file':
                cur_backup = file.File(backup)
            elif backup['type'] == 'git':
                cur_backup = git.Git(backup)
            
            for backup_item in cur_backup.list():
                result[0][1].append(backup_item['item'])
                result[1][1].append(backup_item['type'])
                result[2][1].append(backup_item['filename'])
                result[3][1].append(backup_item['last-modified'])
    utils.output_informations(result)


def list_purged_backups(backups, noop):
    result = [['Item', []],
              ['Backup file', []],
              ['Last Modified', []],
              ['Status', []]]

    status = 'Purged'
    if noop:
        status += ' (noop)'

    for backup in backups:
        result[0][1].append(backup['item'])
        result[1][1].append(backup['filename'])
        result[2][1].append(backup['last-modified'])
        result[3][1].append(status)
    utils.output_informations(result)
