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

from swiftbackmeup.items import filesystems

import shutil

class Git(filesystems.Filesystem):


    def __init__(self, conf):
        super(Git, self).__init__(conf)
        self.branches = conf.get('branches', '--all')


    def type(self):
        return 'filesystems/git'

    
    def run(self):
        super(Git, self).run(cwd=self.path)


    def build_dump_command(self):
        if self.branches == 'all': 
            self.branches = '--all'

        command = 'git bundle create %s/%s %s' % (self.output_directory,
                                                  self.backup_file,
                                                  self.branches)
        return command

    def build_restore_command(self, backup_filename):
        try:
            shutil.rmtree(self.path)
        except OSError:
            pass
 
        command = 'git clone %s/%s -b master %s' % (self.output_directory,
                                                    backup_filename,
                                                    self.path)

        return command
