#!/usr/bin/env python
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

import getopt
import textwrap
import sys
import configparser
import logging
import logging.handlers
from pathlib import Path
from ola.ClientWrapper import ClientWrapper

__author__ = 'pdassier@free.fr (Patrick Dassier)'

class DmxRelay:

  CONFIG_FILE = '.dmx_relay.conf'

  def __init__(self, argv):
    self.logger = logging.getLogger('dmxrelay')
    self.logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
      '%(asctime)s - %(filename)s [%(levelname)s] %(message)s'
    )
    streamhandler = logging.StreamHandler(sys.stdout)
    streamhandler.setFormatter(formatter)
    self.logger.addHandler(streamhandler)


    try:
        opts, args = getopt.getopt(argv, "hu:", ['help', 'universe='])
    except getopt.GetoptError as err:
      print(str(err))
      Usage()
      sys.exit(2)

    universe = 1
    for o, a in opts:
      if o in ("-h", "--help"):
        Usage()
        sys.exit()
      elif o in ("-u", "--universe"):
        universe = int(a)
        self.logger.info(f'Using ARnet universe n°{universe}')

    configFile = Path.joinpath(Path.home(), self.CONFIG_FILE)
    config = configparser.ConfigParser()
    config.read_file(open(configFile, 'r'))
    self.dmxChannel = config['DEFAULT']['channel']
    self.logger.info('Listning on DMX channel n°' + self.dmxChannel)

    wrapper = ClientWrapper()
    client = wrapper.Client()
    client.RegisterUniverse(universe, client.REGISTER, NewData)
    wrapper.Run()

  def NewData(data):
    print(data)


  def Usage():
    print(textwrap.dedent("""
    Usage: dmx-relay.py --universe <universe>

    -h, --help                Display this help message and exit.
    -u, --universe <universe> Universe number."""))

if __name__ == "__main__":
  app = DmxRelay(sys.argv[1:])
