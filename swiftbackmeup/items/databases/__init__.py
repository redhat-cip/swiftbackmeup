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

from swiftbackmeup import items


class Database(items.Item):


    def __init__(self, conf):
        super(Database, self).__init__(conf)
        self.host = conf.get('host')
        self.user = conf.get('user')
        self.password = conf.get('password')
        self.database = conf.get('database')
        self.dump_options = conf.get('dump_options')

