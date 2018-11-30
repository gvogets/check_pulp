# check_pulp

Nagios Monitoring Plugin for testing the repository synchronisation status on a Pulp Repository. For more information about pulp visit pulpproject.org.

## Usage

```
-bash$ ./check_pulp.py -h
usage: check_pulp.py [-h] [-H HOSTNAME] [-u USERNAME] [-p PASSWORD]
                     [-c CONFIG] [-s SECTION] [--verbose]

Nagios Monitoring Plugin for testing the repository synchronisation status on
a Pulp Repository (see pulpproject.org for more information about Pulp)

optional arguments:
  -h, --help            show this help message and exit
  -H HOSTNAME, --hostname HOSTNAME
                        Hostname of the Pulp API server
  -u USERNAME, --username USERNAME
                        Username for Pulp API authentication (default: admin)
  -p PASSWORD, --password PASSWORD
                        Password for Pulp API authentication (default: admin)
  -c CONFIG, --config CONFIG
                        Path to the optional configuration file
  -s SECTION, --section SECTION
                        Section in the config file
  --verbose, -v         Display repos in shiny state too
```

## Example output

```
-bash$ ./check_pulp.py -H pulp01.example.com
[CRITICAL] gitlab-ce-el7 Malformed repository: metadata is specified for different set of packages in filelists.xml and in other.xml

-bash$ ./check_pulp.py -H pulp01.example.com -u admin -p password -v
[CRITICAL] gitlab-ce-el7 Malformed repository: metadata is specified for different set of packages in filelists.xml and in other.xml
[OK] gitlab-runner-el7 is shiny and in sync
[OK] puppet-v6-el7 is shiny and in sync
[OK] chef-stable-el7 is shiny and in sync
[OK] confluent-dist-v5 is shiny and in sync
```

## Config file

Not yet implemented.

## TODOs

- Thresholds for last sync date
- Improve error handling

## Dependencies

- python-requests
