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
import RPi.GPIO as GPIO

__author__ = 'pdassier@free.fr (Patrick Dassier)'

class DmxRelay:

  CONFIG_FILE = '.dmx_relay.conf'

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
    self._dmxValue = 0

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
        self.logger.info(f'Using ARnet universe n°{universe}')

    configFile = Path.joinpath(Path.home(), self.CONFIG_FILE)
    config = configparser.ConfigParser()
    config.read_file(open(configFile, 'r'))
    self.dmxChannel = int(config['DEFAULT']['channel'])
    self.logger.info(f'Listning on DMX channel n°{self.dmxChannel}')
    self._pin = int(config['DEFAULT']['pin'])
    self.logger.info(f'Actuator is plugged on pin n°{self._pin}')
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(self._pin, GPIO.OUT, initial=GPIO.HIGH)

    wrapper = ClientWrapper()
    client = wrapper.Client()
    client.RegisterUniverse(universe, client.REGISTER, self.NewData)
    wrapper.Run()

  def NewData(self, data):
    command = int(data[self.dmxChannel-1])
    if (command != self._dmxValue):
      self._dmxValue = command
      self.logger.info(f'Channel n°{self.dmxChannel} receives value {self._dmxValue}')
      if (self._dmxValue > 128):
        self.logger.info('Open the door...')
        GPIO.output(self._pin, GPIO.LOW)
      else:
        self.logger.info('Stop action')
        GPIO.output(self._pin, GPIO.HIGH)


  def Usage(self):
    print(textwrap.dedent("""
    Usage: dmx-relay.py --universe <universe>

    -h, --help                Display this help message and exit.
    -u, --universe <universe> Universe number."""))

if __name__ == "__main__":
  sys.path.insert(0, '/usr/local/lib/python3.9/site-packages')
  app = DmxRelay(sys.argv[1:])
