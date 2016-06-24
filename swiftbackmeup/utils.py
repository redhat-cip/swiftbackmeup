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

import datetime
import subprocess
import sys

def build_filename(backup, mode):

    if 'backup_filename' in backup:
        backup_path = backup['backup_filename']
    else:
        backup_path = backup.get('backup_filename_prefix', backup['name'])
        backup_path += datetime.datetime.now().strftime(mode['pattern'])
        if 'backup_filename_suffix' in backup:
            backup_path += '%s' % backup['backup_filename_suffix']

    return backup_path


def output_informations(data):

    x = PrettyTable()
    for column in data:
        x.add_column(column[0], column[1])
    print x


def filter_databases(databases, backups):
    if isinstance(databases, list):
        tmp_backups = []
        for backup in backups:
            if backup['name'] in databases:
                tmp_backups.append(backup)
        backups = tmp_backups
    return backups


def get_file_type(path):
    p = subprocess.Popen(['file', path], stdout=subprocess.PIPE)
    return p.communicate()[0]


def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")
