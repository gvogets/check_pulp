#!/usr/bin/env python

"""check_pulp.py: Nagios Monitoring Plugin for testing the repository synchronisation status on a Pulp Repository. For more information about pulp visit pulpproject.org."""

__author__ = "Simon Lauger"
__copyright__ = "Copyright 2018, IT Consulting Simon Lauger"
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Simon Lauger"
__email__ = "simon@lauger.de"

import os
import sys
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import argparse
#from ConfigParser import SafeConfigParser

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class check_pulp:
  exitcodes = {
    'OK':       0,
    'WARNING':  1,
    'CRITICAL': 2,
    'UNKOWN':   3,
  }

  def __init__(self, hostname=None, username=None, password=None, ignore=[]):
    # parameters for constructor
    self.hostname = hostname
    self.username = username
    self.password = password

    # set default values for this class
    self.exitcode = self.exitcodes['OK']
    self.messages = []
    self.debug    = False
  
  def set_hostname(self, hostname):
    self.hostname = hostname
  
  def set_username(self, username):
    self.username = username
  
  def set_password(self, password):
    self.password = password

  def get_repos(self):
    result = requests.get('https://' + self.hostname + '/pulp/api/v2/repositories/',
      headers={'Accept': 'application/json'},
      params={'details': 'true'},
      auth=(self.username, self.password),
      verify=False,
    )
    repos = result.json()

    self.repos    = {}
    self.repolist = []

    for item in repos:
      self.repolist.append(item['id'])
      self.repos[item['id']] = item 
    return self.repolist
  
  def check_repo(self, repository):
    # check if repository has a feed
    if not 'importers' in self.repos[repository]:
      self.add_message('OK', repository + ' has no feed')
      return
    else:
      if not 'feed' in self.repos[repository]['importers'][0]['config']:
        self.add_message('OK', repository + ' has no feed')
        return

    result = requests.get('https://' + self.hostname + '/pulp/api/v2/repositories/' + repository + '/history/sync/',
      headers={'Accept': 'application/json'},
      auth=(self.username, self.password),
      verify=False,
    )
    if result.json():
      latest = result.json()[0]
      if latest['exception']:
        self.add_message('CRITICAL', repository + " " + latest['error_message'])
      elif False:
        self.add_message('WARNING', repository + " this should not happen. go home, you are drunk")
      else:
        self.add_message('OK', repository + " is shiny and in sync")
    else:
      self.add_message('CRITICAL', repository + ' has no sync history')
      
  def check_all(self):
    for repository in self.repolist:
      self.check_repo(repository)

  def debugmode(self, mode = True):
    self.debug = mode
    return
  
  def add_message(self, exitcode, message):
    self.set_exitcode(exitcode)
    if exitcode != 'OK':
      self.messages.append('[' + exitcode + '] ' + message)
      return
    if exitcode == 'OK' and self.debug:
      self.messages.append('[' + exitcode + '] ' + message)
      return
    return

  def set_exitcode(self, exitcode):
    if not exitcode in self.exitcodes:
      raise Exception('unkown exitcode ' + exitcode + ' for method set_exitcode')
    if self.exitcodes[exitcode] > self.exitcode:
      self.exitcode = self.exitcodes[exitcode]

  def exit(self):
    # handle empty messages list
    if not len(self.messages):
      if self.exitcodes['OK'] == self.exitcode:
        print('[OK] all repos are shiny and in sync')
        sys.exit(self.exitcodes['OK'])
      else:
        print('[UNKOWN] no repositories found')
        sys.exit(self.exitcodes['UNKOWN'])

    # print out messages
    for item in self.messages:
      print(item)
    sys.exit(self.exitcode)

add_args = (
  {
    '--hostname': {
      'alias': '-H',
      'help': 'Hostname of the Pulp API server',
      'type': str,
      'default': 'admin',
      'required': True,
    }
  },
  {
    '--username': {
      'alias': '-u',
      'help': 'Username for Pulp API authentication (default: admin)',
      'type': str,
      'default': 'admin',
      'required': False,
    }
  },
  {
    '--password': {
      'alias': '-p',
      'help': 'Password for Pulp API authentication (default: admin)',
      'type': str,
      'default': 'admin',
      'required': False,
    }
  },
  {
    '--config': {
      'alias': '-c',
      'help': 'Path to the optional configuration file',
      'type': str,
      'default': None,
      'required': False,
    }
  },
  {
    '--section': {
      'alias': '-s',
      'help': 'Section in the config file',
      'type': str,
      'default': None,
      'required': False,
    }
  },
)

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Nagios Monitoring Plugin for testing the repository synchronisation status on a Pulp Repository. For more information about pulp visit pulpproject.org.')
  for item in add_args:
    arg    = item.keys()[0]
    params = item.values()[0]
    parser.add_argument(
      params['alias'], arg,
      type=params['type'],
      help=params['help'],
      default=params['default'],
      required=params['required'],
    )
  parser.add_argument('--verbose', '-v', action='store_true', help='Display repos in shiny state too')

  args = parser.parse_args()

#  if args.config:
#    cfgfile = os.path.expanduser(args.config)
#
#    if os.path.isfile(cfgfile):
#      config = SafeConfigParser()
    
  nagios_plugin = check_pulp()
  
  nagios_plugin.set_hostname(args.hostname)
  nagios_plugin.set_username(args.username)
  nagios_plugin.set_password(args.password)

  nagios_plugin.debugmode(args.verbose)

  nagios_plugin.get_repos()
  nagios_plugin.check_all()
  nagios_plugin.exit()
