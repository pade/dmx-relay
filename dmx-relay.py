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
import subprocess
import smbus

__author__ = 'pdassier@free.fr (Patrick Dassier)'

class DmxRelay:

  CONFIG_FILE = '.dmx_relay.conf'
  DEVICE_BUS = 1
  DEVICE_ADDR = 0x10

  def __init__(self, argv):
    from ola.ClientWrapper import ClientWrapper
    self.logger = logging.getLogger('dmxrelay')
    self.logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
      '%(asctime)s - %(filename)s [%(levelname)s] %(message)s'
    )
    streamhandler = logging.StreamHandler(sys.stdout)
    streamhandler.setFormatter(formatter)
    self.logger.addHandler(streamhandler)
    sysloghandler = logging.handlers.SysLogHandler()
    sysloghandler.setFormatter(formatter)
    self.logger.addHandler(sysloghandler)
    self._cmdValue = 0


    try:
        opts, args = getopt.getopt(argv, "hu:", ['help', 'universe='])
    except getopt.GetoptError as err:
      print(str(err))
      self.Usage()
      sys.exit(2)

    universe = 1
    for o, a in opts:
      if o in ("-h", "--help"):
        self.Usage()
        sys.exit()
      elif o in ("-u", "--universe"):
        universe = int(a)
        self.logger.info(f'Using ARNet universe n°{universe}')

    self._bus = smbus.SMBus(self.DEVICE_BUS)
    configFile = Path.joinpath(Path.home(), self.CONFIG_FILE)
    config = configparser.ConfigParser()
    config.read_file(open(configFile, 'r'))
    self.dmxChannel = int(config['DMX']['channel'])
    self._relayNb = int(config['RELAY']['number'])

    self.logger.info(f'Base DMX channel: {self.dmxChannel}')
    self.logger.info(f'Actuator is plugged on relay n°{self._relayNb}')

    wrapper = ClientWrapper()
    client = wrapper.Client()
    client.RegisterUniverse(universe, client.REGISTER, self.NewData)
    wrapper.Run()

  def NewData(self, data):
    command = self._dataOfChannel(self.dmxChannel, data)
    shutdown = self._dataOfChannel(self.dmxChannel+1, data)
    if (command != self._cmdValue):
      self._cmdValue = command
      if (self._cmdValue > 128):
        self.logger.info('Open the door...')
        self._bus.write_byte_data(self.DEVICE_ADDR, self._relayNb, 0xFF)
      else:
        self.logger.info('Stop opening the door')
        self._bus.write_byte_data(self.DEVICE_ADDR, self._relayNb, 0x00)
    if (shutdown > 128):
      self.logger.info('Ask for shutdown')
      subprocess.call(['sudo', 'shutdown', '-h', 'now'], shell=False)

  def _dataOfChannel(self, ch, data):
    return int(data[ch-1])

  def Usage(self):
    print(textwrap.dedent("""
    Usage: dmx-relay.py --universe <universe>

    -h, --help                Display this help message and exit.
    -u, --universe <universe> Universe number."""))

if __name__ == "__main__":
  sys.path.insert(0, '/usr/local/lib/python3.9/site-packages')
  app = DmxRelay(sys.argv[1:])
