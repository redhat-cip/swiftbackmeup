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

#from swiftbackmeup import exceptions

import os
import yaml

_FIELDS = ['user', 'host', 'password', 'type', 'pg_dump_options',
           'swift_container', 'swift_pseudofolder', 'subscribe',
           'output_directory']

def check_configuration_file_existence(configuration_file_path=None):
    """Check if the configuration file is present."""

    if configuration_file_path:
        if not os.path.exists(configuration_file_path):
#            raise exceptions.ConfigurationExceptions()
             pass
        file_path = configuration_file_path
    elif os.getenv('SWIFTBACKMEUP_CONFIGURATION'):
        if not os.path.exists(os.getenv('SWIFTBACKMEUP_CONFIGURATION')):
            #raise exceptions.ConfigurationExceptions()
            pass
        file_path = os.getenv('SWIFTBACKMEUP_CONFIGURATION')
    else:
        if not os.path.exists('/etc/swiftbackmeup.conf'):
            #raise exceptions.ConfigurationExceptions()
            pass
        file_path = '/etc/swiftbackmeup.conf'

    return file_path
   

def load_configuration(conf):
    """Load the swiftbackmeup configuration file."""

    file_path = check_configuration_file_existence(conf['file_path'])

    try:
        file_path_content = open(file_path, 'r').read()
    except IOError as exc:
        #raise exceptions.ConfigurationExceptions(exc)
        pass

    try:
        conf = yaml.load(file_path_content)
    except yaml.YAMLError as exc:
        #raise exceptions.ConfigurationExceptions(exc)
        pass

    return conf


def expand_configuration(configuration):
    """Fill up backups with defaults."""

    for backup in configuration['backups']:
        for field in _FIELDS:
            if field not in backup:
                if field not in configuration:
                    backup[field] = None
                else:
                    backup[field] = configuration[field]

    return configuration['backups']
