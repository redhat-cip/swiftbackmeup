# swiftbackmeup

An utility that allows one to create database backups and upload them to
OpenStack Swift

## Objective

The goal of `swiftbackmeup` is to be able to backup databases and upload
those backup to Swift.

`swiftbackmeup` is configuration driven. Every database that needs to be
backed up are described in the configuration file


## How to run it

The most simple way to run `swiftbackmeup`:

```
#> swiftbackmeup
```

This is equivalent to `swiftbackmeup --mode now`, it will look at the
configuration file located at `/etc/swiftbackmeup.conf`.


If one wants to trigger another mode:

```
#> swiftbackmeup --mode daily
#>
#> swiftbackmeup --mode monthly
```

## Configuration

The below section aims to explain every parameter of the configuration file

### Swift Parameters

| Parameter          | Scope          | Default | Description                                                       |
|--------------------|----------------|---------|-------------------------------------------------------------------|
| os_username        | global         | None    | OpenStack Username                                                |
| os_password        | global         | None    | OpenStack Password                                                |
| os_tenant_name     | global         | None    | OpenStack Tenant Name                                             |
| os_auth_url        | global         | None    | OpenStack Authentication URL                                      |
| create_container   | global, backup | True    | If the container does not exist, should it be created             |
| purge_container    | global, backup | False   | Should the remote objects be purged                               |
| swift_container    | global, backup | backup  | Name of the swift container on which to store the database backup |
| swift_pseudofolder | global, backup | None    | If wanted, name of the pseudo folder                              |


### Filesystem Parameters

| Parameter              | Scope          | Default  | Description                                                                                 |
|------------------------|----------------|----------|---------------------------------------------------------------------------------------------|
| ouput_directory        | global, backup | /var/tmp | Directory where to store the database backup                                                |
| clean_local_copy       | global, backup | True     | Should the local copy be removed once uploaded to Swift                                     |
| backup_filename        | backup         | None     | Name the backup file (will override any mode pattern)                                       |
| backup_filename_prefix | backup         | None     | Prefix of the backup file name (mode pattern and backup_filename_suffix will be appended)   |
| backup_filename_suffix | backup         | None     | Suffix of the backup file name (backup_filename_prefix and mode pattern will be prepended ) |


### Database Parameters

| Parameter       | Scope          | Default    | Description                                                     |
|-----------------|----------------|------------|-----------------------------------------------------------------|
| type            | global, backup | postgresql | Database type (available: postgres)                             |
| pg_dump_options | global, backup | -Z9 -Fc    | Parameters to pass to the pg_dump command (PostgreSQL specific) |
| database        | backup         | None       | Name of the database to backup                                  |
| user            | global, backup | None       | User to connect to the database system                          |
| password        | global, backup | None       | Password to connect to the database system                      |
| host            | global, backup | None       | Host to connect to the database system                          |
| port            | global, backup | None       | Port to connect to the database system                          |
| subscriptions   | backup         | None       | Mode that this database is backed up when activated             |


### Configuration file example

```
---
os_username: username
os_password: password
os_tenant_name: tenant_name
os_auth_url: auth_url
create_container: True
purge_container: False
swift_container: backup
swift_pseudofolder: example

mode:
  daily:
    retention: 7
    pattern: "%Y%m%d"
  weekly:
    retention: 4
    pattern: "%Y%m%d-%U"
  monthly:
    retention: 6
    pattern: "%Y%m"
  now:
    retention: 10
    pattern: "%Y%m%d%H%M%S"

type: postgresql
pg_dump_options: -Z9 -Fc
output_directory: /var/tmp
clean_local_copy: True

backups:
  - database: swiftbackmeup
    user: jdoe
    password: apassword
    host: 127.0.0.1
    backup_filename_prefix: 'this_is_a_prefix'
    backup_filename_suffix: '.dump.gz'
    subscriptions:
      - daily
      - now
      - monthly
      - weekly

  - database: wordpress
    user: wordpress
    password: wordpresspassword
    host: 127.0.0.1
    backup_filename_prefix: 'wordpress_'
    backup_filename_suffix: '.dump.gz'
    subscriptions:
      - daily
      - now
```
