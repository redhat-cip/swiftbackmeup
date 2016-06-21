# swiftbackmeup

An utility that allows one to create database backups and upload them to
OpenStack Swift

## TODO

 - [ ] Implement purge/retention feature
 - [ ] Implement Swift as a plugin, and create an S3 alternative for the reference
 - [ ] Implement a function to list all available backups
 - [ ] Implement a function to restore a backup

## Goal

The goal of `swiftbackmeup` is to be able to backup databases and upload
those backups to Swift (OpenStack Object Store).

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

One can specify an alternative configuration file:

```
#> swiftbackmeup --conf /path/to/conf.yml
```

One can list the configured backups in the configuration file:

```
#> swiftbackmeup --list-backups
```

One can limit the databases that will be backedup :

```
#> swiftbackmeup --databases db1,mydb
```

## Modes

Modes are equivalent to tag the backup needs to be subscribed to.

So within the configuration file, backups are 'subscribed' to tags;

```
backups:
  - database: mydatabasenumberone
    subscriptions:
      - daily
      - monthly
      - now
      - tag1
      - mydatabasenumberone
```

This means that this backup will run only if `swiftbackmeup` is run with one
of the tags lists in subscriptions

Modes are defined in the configuration file, by default 4 modes come predefined.

  * `daily`: If one wants to backup the database on a daily basis, with a default of 7 day of retention
  * `weekly`: If one wants to backup the database on a weekly basis, with a default of 4 weeks of retention
  * `monthly`: If one wants to backup the database on a monthly basis, with a default of 6 months of retention
  * `now`: If one wants to backup the database at the moment t, with a default of 10 backup having the same name pattern.


Modes understand for now only two parameters:

  * `retention`: Number of days a backup should be kept, else purged.
  * `pattern`: Pattern that will be used in datetime.format later.


## Naming configuration

There are various way the filename of the backup can be specified.

  1. The backup is part of a tag with a matching pattern.


By default the name will be the pattern. But one can specify 2 parameters
`backup_filename_prefix` and `backup_filename_suffix` to actually have a
meaningfull name.

So name would be the equivalent of:

```
'%s%s%s' % (backup_filename_prefix, modes.pattern, backup_filename_suffix)
```

Example:

```
backups:
  - database: mydatabase
    subscriptions:
      - daily
    backup_filename_prefix: 'mydatabase_'
    backup_filename_suffix: '.dump.gz'
```

  2. The backup is part of a tag with a matching pattern (or not)


Whether the backup is part of a tag or not, one can override the final backup
filename by specifying `backup_filename`

```
backups:
  - database: mydatabase
    subscriptions:
      - daily
    backup_filename: 'mydatabase_backup.dump.gz'
```

## Configuration

The below section aims to explain every parameter of the configuration file

### Swift Parameters

| Parameter           | Scope          | Default | Description                                                       |
|---------------------|----------------|---------|-------------------------------------------------------------------|
| os_username         | global         | None    | OpenStack Username                                                |
| os_password         | global         | None    | OpenStack Password                                                |
| os_tenant_name      | global         | None    | OpenStack Tenant Name                                             |
| os_auth_url         | global         | None    | OpenStack Authentication URL                                      |
| create_container    | global, backup | True    | If the container does not exist, should it be created             |
| purge_container     | global, backup | False   | Should the remote objects be purged                               |
| swift_container     | global, backup | backup  | Name of the swift container on which to store the database backup |
| swift_pseudo_folder | global, backup | None    | If wanted, name of the pseudo folder                              |


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
| type            | global, backup | postgresql | Database type (available: postgres, mariadb)                    |
| dump_options    | global, backup | None       | Parameters to pass to the dump command                          |
| database        | backup         | None       | Name of the database to backup                                  |
| user            | global, backup | None       | User to connect to the database system                          |
| password        | global, backup | None       | Password to connect to the database system                      |
| host            | global, backup | None       | Host to connect to the database system                          |
| port            | global, backup | None       | Port to connect to the database system                          |
| subscriptions   | backup         | None       | Mode that this database is backed up when activated             |


#### PostgreSQL Specifics

When backuping PostgreSQL databases there are two modes of working:

  * `database: all`: This will make `swiftbackmeup` rely on the `pg_dumpall` program. It hence allows access to options like (`roles_only`, `globals_only`, etc...)
  * `database: mydatabase`: This will make `swiftbackmeup` rely on the `pg_dump` program.

| Parameter        | Scope               | Default | Description                                       |
|------------------|---------------------|---------|---------------------------------------------------|
| pg_dump_options  | global, backup      | -Z9 -Fc | Parameters to pass to the pg_dump command         |
| data_only        | backup (the all db) | None    | Should --data-only be passed to pg_dumpall        |
| globals_only     | backup (the all db) | None    | Should --globals-only be passed to pg_dumpall     |
| roles_only       | backup (the all db) | None    | Should --roles-only be passed to pg_dumpall       |
| schema_only      | backup (the all db) | None    | Should --schema-only be passed to pg_dumpall      |
| tablespaces_only | backup (the all db) | None    | Should --tablespaces-only be passed to pg_dumpall |


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

  - database: all
    user: jdoe
    password: apassword
    host: 127.0.0.1
    globals_only: True
    schema_only: True
    backup_filename_prefix: 'globals_schema_only'
    backup_filename_suffix: '.dump.gz'
    subscriptions:
      - daily

  - database: wordpress
    user: wordpress
    password: wordpresspassword
    host: 127.0.0.1
    type: mariadb
    backup_filename_prefix: 'wordpress_'
    backup_filename_suffix: '.dump.gz'
    subscriptions:
      - daily
      - now
```
