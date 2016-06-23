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

import argparse

def parse():

    parser = argparse.ArgumentParser(description='swiftbackmeup')

    parser.add_argument('--conf',
        help='Path to configuration file')

    
    subparsers = parser.add_subparsers(help='commands')

    restore_parser = subparsers.add_parser('restore', help='restore local database from remote backups')
    restore_parser.add_argument('--version',
        default='latest',
        help='name of the backup to restore')
    restore_parser.add_argument('--databases',
        action='append',
        nargs='*',
        help='Databases list to apply action to')

    backup_parser = subparsers.add_parser('backup', help='backup local database')
    backup_parser.add_argument('--mode',
        default='now',
        help='Mode under which the script will be run')
    backup_parser.add_argument('--list-backups',
        action='store_true',
        help='List all currently configured backups')
    backup_parser.add_argument('--list-backups-remote',
        action='store_true',
        help='List all remote backups')
    backup_parser.add_argument('--databases',
        action='append',
        nargs='*',
        help='Databases list to apply action to')

    options = parser.parse_args()
    normalize_databases_parameter(options)

    return options


def normalize_databases_parameter(options):
    """The databases parameters can have differents form based on how it
       was passed as an input

       swiftbackmeup --databases db1,db2
       swiftbackmeup --databases db1 db2
       swiftbackmeup --databases db1 --databases db2

       This method aims to provide a plain array witch each element being
       a database itself
    """

    if not isinstance(options.databases, list):
        return

    final_dbs = []
    for dbs in options.databases:
        for db in dbs:
            if ',' in db:
                final_dbs += db.split(',')
            else:
                final_dbs.append(db)

    options.databases = final_dbs
