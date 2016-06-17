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
from swiftbackmeup.databases import postgresql

def main():

    conf = {
        'file_path': 'conf.yml'
    }
    backups = configuration.load_configuration(conf)
    backups = configuration.expand_configuration(backups)

    for backup in backups:
        if backup['type'] == 'postgresql':
            cur_backup = postgresql.PostgreSQL(backup)
        cur_backup.run_backup()
        #cur_backup.upload_to_swift()
            
        
