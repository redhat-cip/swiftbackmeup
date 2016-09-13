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

from swiftbackmeup.items import databases

import time
import requests

class Elasticsearch(databases.Database):

    def __init__(self, conf):
        super(Elasticsearch, self).__init__(conf)
        self.repository = conf.get('repository')
        self.repository_path = conf.get('repository_path')


    def type(self):
        return 'databases/elasticsearch'


    def run(self):
        super(Elasticsearch, self).run(cwd=self.repository_path, shell=True)


    def restore(self, backup_filename):
        super(Elasticsearch, self).restore(backup_filename,
                                           cwd=self.repository_path,
                                           shell=True)
        url = ''

        if self.ssl:
            url += 'https://'
        else:
            url += 'http://'

        url = '%s%s:%s/_snapshot/%s/%s/_restore' % (url, self.host, self.port,
                                                    self.repository, backup_filename)
        requests.post(url)


    def build_restore_command(self, backup_filename):
        command = 'tar -xzvf %s/%s' % (self.output_directory,
                                       backup_filename)

        return command



    def build_dump_command(self):

        url = ''

        if self.ssl:
            url += 'https://'
        else:
            url += 'http://'

        url = '%s%s:%s/_snapshot/%s/%s' % (url, self.host, self.port,
                                           self.repository, self.backup_file)
        requests.post(url)
        time.sleep(2)

        command = 'tar -czvf %s/%s indices meta-*.dat snap-*.dat' % (self.output_directory,
                                                                     self.backup_file)

        return command
