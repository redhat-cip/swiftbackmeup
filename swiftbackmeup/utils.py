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

import datetime

def build_filename(backup, mode):

    backup_path = '%s/' % backup['output_directory'] 

    if 'backup_filename' in backup:
        backup_path += '/%s' % backup['backup_filename']
    else:
        backup_path += backup.get('backup_filename_prefix', backup['database'])
        backup_path += datetime.datetime.now().strftime(mode['pattern'])
        if 'backup_filename_suffix' in backup:
            backup_path += '%s' % backup['backup_filename_suffix']

    return backup_path
