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

from swiftbackmeup import exceptions

import os
import yaml

_SWIFT_AUTH_FIELDS = (
    "os_username",
    "os_password",
    "os_region_name",
    "os_identity_api_version",
    "os_auth_url",
    "os_tenant_name",
    "os_tenant_id",
    "os_project_name",
    "os_project_id",
    "os_project_domain_name",
    "os_project_domain_id",
    "os_user_domain_name",
    "os_user_domain_id",
)

_FIELDS = (
    "create_container",
    "purge_container",
    "swift_container",
    "swift_pseudo_folder",
    "output_directory",
    "clean_local_copy",
    "type",
    "user",
    "password",
    "host",
    "port",
    "store_type",
)


def check_configuration_file_existence(configuration_file_path=None):
    """Check if the configuration file is present."""

    if configuration_file_path:
        if not os.path.exists(configuration_file_path):
            raise exceptions.ConfigurationExceptions(
                "File %s does not exist" % configuration_file_path
            )
        file_path = configuration_file_path
    elif os.getenv("SWIFTBACKMEUP_CONFIGURATION"):
        if not os.path.exists(os.getenv("SWIFTBACKMEUP_CONFIGURATION")):
            raise exceptions.ConfigurationExceptions(
                "File %s does not exist" % os.getenv("SWIFTBACKMEUP_CONFIGURATION")
            )
        file_path = os.getenv("SWIFTBACKMEUP_CONFIGURATION")
    else:
        if not os.path.exists("/etc/swiftbackmeup.conf"):
            raise exceptions.ConfigurationExceptions(
                "File /etc/swiftbackmeup.conf does not exist "
                "(you could specify an alternate location using --conf)"
            )
        file_path = "/etc/swiftbackmeup.conf"

    return file_path


def load_swift_auth_conf_from_env(conf):
    for var in _SWIFT_AUTH_FIELDS:
        if not conf.get(var):
            conf[var] = os.getenv(var.upper())


def load_configuration(conf):
    """Load the swiftbackmeup configuration file."""

    file_path = check_configuration_file_existence(conf.get("file_path"))

    try:
        with open(file_path, "r") as fd:
            conf = yaml.load(fd, Loader=yaml.BasicLoader)
    except IOError as exc:
        raise exceptions.ConfigurationExceptions(exc)
    except yaml.YAMLError as exc:
        raise exceptions.ConfigurationExceptions(exc)

    load_swift_auth_conf_from_env(conf)

    verify_mandatory_parameter(conf)

    return conf


def expand_configuration(configuration):
    """Fill up backups with defaults."""

    for backup in configuration["backups"]:
        for field in _FIELDS + _SWIFT_AUTH_FIELDS:
            if field not in backup or backup[field] is None:
                if field not in configuration:
                    backup[field] = None
                else:
                    backup[field] = configuration[field]

    return configuration["backups"]


def verify_params_swift_auth(conf):
    """Validate mandatory parameters specific to Swift store auth"""
    if not conf["os_identity_api_version"]:
        if "/v2.0" in conf["os_auth_url"]:
            conf["os_identity_api_version"] = 2
        elif "/v3" in conf["os_auth_url"]:
            conf["os_identity_api_version"] = 3
        else:
            raise exceptions.ConfigurationException(
                "Could not determine the Identity API version to use from "
                "OS_IDENTITY_VERSION or OS_AUTH_URL."
            )

    if conf["os_identity_api_version"] == 2:
        v2_mandatory = (
            "os_username",
            "os_password",
            "os_tenant_name",
            "os_auth_url",
            "os_region_name",
        )
        if not all((conf[var] for var in v2_mandatory)):
            raise exceptions.ConfigurationExceptions(
                "One of the following parameter is not configured: %s"
                % ", ".join(v2_mandatory)
            )
    elif conf["os_identity_api_version"] == 3:
        v3_mandatory = (
            "os_username",
            "os_password",
            "os_project_name",
            "os_auth_url",
            "os_region_name",
        )
        if not all((conf[var] for var in v3_mandatory)):
            raise exceptions.ConfigurationExceptions(
                "One of the following parameter is not configured: %s"
                % ", ".join(v3_mandatory)
            )


def verify_mandatory_parameter(configuration):
    """Ensure that all mandatory parameters are in the configuration object."""

    verify_params_swift_auth(configuration)

    if (
        len([1 for backup in configuration["backups"] if "swift_container" in backup])
        != len(configuration["backups"])
    ) and "swift_container" not in configuration:
        raise exceptions.ConfigurationExceptions(
            "swift_container has not been specified for every backups and no global setting has been set"
        )

    # Backup Parameters
    if "backups" not in configuration:
        raise exceptions.ConfigurationExceptions("No backups field encountered")

    if len(configuration["backups"]) == 0:
        raise exceptions.ConfigurationExceptions("Backups has no backup configured")

    for backup in configuration["backups"]:
        if "name" not in backup:
            raise exceptions.ConfigurationExceptions(
                "A backup has the name field missing"
            )
