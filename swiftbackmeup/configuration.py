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

import swiftbackmeup.exceptions as exc
import os
import yaml

_FIELDS = ['os_username', 'os_password', 'os_tenant_name', 'os_auth_url',
           'create_container', 'purge_container', 'swift_container',
           'swift_pseudo_folder', 'output_directory', 'clean_local_copy',
           'type',' pg_dump_options', 'user', 'password', 'host', 'port']



def check_configuration_file_existence(conf_file=None):
    """Check if the configuration file is present."""
    not_exist = 'File %s does not exist'
    env_file = os.getenv('SWIFTBACKMEUP_CONFIGURATION')
    etc_file = '/etc/swiftbackmeup.conf'

    if conf_file:
        if not os.path.exists(conf_file):
            raise exc.ConfigurationException(not_exist % conf_file)
        file_path = conf_file
    elif env_file:
        if not os.path.exists(env_file):
            raise exc.ConfigurationException(not_exist % env_file)
        file_path = env_file
    else:
        if not os.path.exists(etc_file):
            raise exc.ConfigurationException(not_exits % etc_file)
        file_path = etc_file

    return file_path


def load_configuration(conf):
    """Load the swiftbackmeup configuration file."""

    file_path = check_configuration_file_existence(conf.get('file_path'))

    try:
        file_path_content = open(file_path, 'r').read()
    except IOError as e:
        raise exc.ConfigurationException(e)

    try:
        conf = yaml.load(file_path_content)
    except yaml.YAMLError as e:
        raise exc.ConfigurationException(e)

    return conf


def expand_configuration(configuration):
    """Fill up backups with defaults."""

    fields = {field: configuration.get(field) for field in _FIELDS}

    for backup in configuration['backups']:
        _fields = fields.copy()
        _fields.update(backup)
        backup.update(_fields)


def verify_mandatory_parameter(conf):
    """Ensure that all mandatory parameters are in the configuration object."""

    # Swift Parameters
    os_username = conf.get('os_username', os.getenv('OS_USERNAME'))
    os_password = conf.get('os_password',os.getenv('OS_PASSWORD'))
    os_tenant_name = conf.get('os_tenant_name', os.getenv('OS_TENANT_NAME'))
    os_auth_url = conf.get('os_auth_url', os.getenv('OS_AUTH_URL'))

    if not (os_username and os_password and os_tenant_name and os_auth_url):
        raise exc.ConfigurationException(
            'One of the following parameter is not configured: os_username, '
            'os_password, os_tenant_name, os_auth_url'
        )

    backups = conf.get('backups')

    if backups is None:
        raise exc.ConfigurationException('No backups field encountered')

    if not len(conf['backups']):
        raise exc.ConfigurationException('Backups has no backup configured')

    all_swift_container = all(['swift_container' in b for b in backups)
    if not all_swift_conatiner and 'swift_container' not in conf:
        raise exc.ConfigurationException(
            'swift_container has not been specified for every backups and '
            'no global setting has been set'
        )

    for backup in conf['backups']:
        if 'database' not in backup:
            raise exc.ConfigurationException(
                'A backup has the database field missing'
            )
