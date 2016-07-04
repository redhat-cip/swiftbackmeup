# swiftbackmeup

An utility that allows one to create items backups and upload them to
OpenStack Swift (Object Store).

## TODO

 - [ ] Add the possibility to encrypt data
 - [ ] Add support for Amazon S3

## Goal

The goal of `swiftbackmeup` is to be able to backup items and upload
those backups to Swift (OpenStack Object Store).

`swiftbackmeup` is configuration driven. Every item that needs to be
backed up are described in the configuration file.


## How to run it

`swiftbackmeup` has various operation modes:

  * `backup`: Allow one to backup items
  * `restore`: Allow one to restore backups from object store
  * `purge`: Allow one to purge backups from object store


`swiftbackmeup` is configuration driven. The configuration file
is (by order of priority):

  1. The one specified on the command line (`swiftbackmeup --conf /path/to/conf.yml`)
  2. The one specified in the environment variable `$SWIFTBACKMEUP_CONFIGURATION`
  3. The `/etc/swiftbackmeup.conf`


### backup

This mode allows a user to backup items listed in the backups array in the configuration
file.

#### `--items`

This option allows one to limit for which backups item the script will be run.
If the backups array has serveral items; ie. `mydb_prod`, `mydb_preprod`, `mydb_test`

`swiftbackmeup backup` would backup all three of them

`swiftbackmeup backup --items mydb_prod` would only backup `mydb_prod`

**Note**: this command is valid in combination with any other command such as `--list` and `--list-items


#### `--list`

This option allows one to list the remote backups for the items listed in the configuration
file. It will by default list all the backups of every items. Items can be limited by using
the `--items` parameter.

```
#> swiftbackmeup backup --list
+---------------+-----------------------------------------------------+----------------------------+
|      Item     |                     Backup file                     |       Last Modified        |
+---------------+-----------------------------------------------------+----------------------------+
|      db1      |           db1/db1_20160624054028.dump.sql           | 2016-06-24T09:40:29.719150 |
| swiftbackmeup | swiftbackmeup/swiftbackmeup_20160624054028.dump.sql | 2016-06-24T09:40:30.377840 |
+---------------+-----------------------------------------------------+----------------------------+
```

```
#> swiftbackmeup backup --list --items db1
+---------------+-----------------------------------------------------+----------------------------+
|      Item     |                     Backup file                     |       Last Modified        |
+---------------+-----------------------------------------------------+----------------------------+
|      db1      |           db1/db1_20160624054028.dump.sql           | 2016-06-24T09:40:29.719150 |
+---------------+-----------------------------------------------------+----------------------------+
```


#### `--list-items`

This option allows one to list the items in the backups array listed in the configuration file.
Items can be limited by using the `--items` parameter.

```
#> swiftbackmeup backup --list-items
+---------------+----------------------+-----------+-----------------+---------------------+-----------------------------+
|      Item     |          Type        |    Host   | Swift Container | Swift Pseudo-Folder |        Subscriptions        |
+---------------+----------------------+-----------+-----------------+---------------------+-----------------------------+
|      db1      |  databases/mariadb   | 127.0.0.1 |      backup     |         db1         | daily, now, monthly, weekly |
| swiftbackmeup | databases/postgresql |   local   |      backup     |    swiftbackmeup    | daily, now, monthly, weekly |
+---------------+----------------------+-----------+-----------------+---------------------+-----------------------------+
```

```
#> swiftbackmeup backup --list-items --items db1
+---------------+----------------------+-----------+-----------------+---------------------+-----------------------------+
|      Item     |          Type        |    Host   | Swift Container | Swift Pseudo-Folder |        Subscriptions        |
+---------------+----------------------+-----------+-----------------+---------------------+-----------------------------+
|      db1      |  databases/mariadb   | 127.0.0.1 |      backup     |         db1         | daily, now, monthly, weekly |
+---------------+----------------------+-----------+-----------------+---------------------+-----------------------------+
```


### purge

This mode allows a user to purge items on the remote object store.

The purge logic is based on the mode `retention` and `unit` parameters.

```
modes:
  daily:
    retention: 7
    unit: day
  now:
    retention: 1
    unit: item

backups:
  - name: db1
    database: db1
    subscriptions:
      - daily
      - now
```

If a user executes `swiftbackmeup purge` only the last 1 item of the db1 backups
on the remote store will be kept, the other will be purged (ie. --mode now is the
default)


If a user executs `swiftbackmeup purge --mode daily` the backups of the item older
than 7 days will be purged.

#### `--noop`

This option allows one to list the items that would be purged if run without the `--noop` item.

```
#> swiftbackmeup backup --list
+---------------+-----------------------------------------------------+----------------------------+
|      Item     |                     Backup file                     |       Last Modified        |
+---------------+-----------------------------------------------------+----------------------------+
|      db1      |           db1/db1_20160624054028.dump.sql           | 2016-06-24T09:40:29.719150 |
|      db1      |           db1/db1_20160624063610.dump.sql           | 2016-06-24T10:36:12.295490 |
|      db1      |           db1/db1_20160624063613.dump.sql           | 2016-06-24T10:36:14.780210 |
|      db1      |           db1/db1_20160624063615.dump.sql           | 2016-06-24T10:36:17.117850 |
| swiftbackmeup | swiftbackmeup/swiftbackmeup_20160624054028.dump.sql | 2016-06-24T09:40:30.377840 |
| swiftbackmeup | swiftbackmeup/swiftbackmeup_20160624063611.dump.sql | 2016-06-24T10:36:13.216240 |
| swiftbackmeup | swiftbackmeup/swiftbackmeup_20160624063614.dump.sql | 2016-06-24T10:36:15.799500 |
| swiftbackmeup | swiftbackmeup/swiftbackmeup_20160624063616.dump.sql | 2016-06-24T10:36:17.923470 |
+---------------+-----------------------------------------------------+----------------------------+
#> swiftbackmeup purge --noop --force
+---------------+-----------------------------------------------------+----------------------------+---------------+
|     Item      |                     Backup file                     |       Last Modified        |     Status    |
+---------------+-----------------------------------------------------+----------------------------+---------------+
|      db1      |           db1/db1_20160624054028.dump.sql           | 2016-06-24T09:40:29.719150 | Purged (noop) |
|      db1      |           db1/db1_20160624063610.dump.sql           | 2016-06-24T10:36:12.295490 | Purged (noop) |
|      db1      |           db1/db1_20160624063613.dump.sql           | 2016-06-24T10:36:14.780210 | Purged (noop) |
| swiftbackmeup | swiftbackmeup/swiftbackmeup_20160624054028.dump.sql | 2016-06-24T09:40:30.377840 | Purged (noop) |
| swiftbackmeup | swiftbackmeup/swiftbackmeup_20160624063611.dump.sql | 2016-06-24T10:36:13.216240 | Purged (noop) |
| swiftbackmeup | swiftbackmeup/swiftbackmeup_20160624063614.dump.sql | 2016-06-24T10:36:15.799500 | Purged (noop) |
+---------------+-----------------------------------------------------+----------------------------+---------------+
```
#### `--force`

This options allows one not to have to answer the security question: "Are you sure you want to purge the backups?"

```
#> swiftbackmeup backup --list                                                                                                                 
+---------------+-----------------------------------------------------+----------------------------+
|     Item      |                     Backup file                     |       Last Modified        |
+---------------+-----------------------------------------------------+----------------------------+
|      db1      |           db1/db1_20160624054028.dump.sql           | 2016-06-24T09:40:29.719150 |
|      db1      |           db1/db1_20160624063610.dump.sql           | 2016-06-24T10:36:12.295490 |
|      db1      |           db1/db1_20160624063613.dump.sql           | 2016-06-24T10:36:14.780210 |
|      db1      |           db1/db1_20160624063615.dump.sql           | 2016-06-24T10:36:17.117850 |
| swiftbackmeup | swiftbackmeup/swiftbackmeup_20160624054028.dump.sql | 2016-06-24T09:40:30.377840 |
| swiftbackmeup | swiftbackmeup/swiftbackmeup_20160624063611.dump.sql | 2016-06-24T10:36:13.216240 |
| swiftbackmeup | swiftbackmeup/swiftbackmeup_20160624063614.dump.sql | 2016-06-24T10:36:15.799500 |
| swiftbackmeup | swiftbackmeup/swiftbackmeup_20160624063616.dump.sql | 2016-06-24T10:36:17.923470 |
+---------------+-----------------------------------------------------+----------------------------+
#> swiftbackmeup purge --force
+---------------+-----------------------------------------------------+----------------------------+--------+
|     Item      |                     Backup file                     |       Last Modified        | Status |
+---------------+-----------------------------------------------------+----------------------------+--------+
|      db1      |           db1/db1_20160624054028.dump.sql           | 2016-06-24T09:40:29.719150 | Purged |
|      db1      |           db1/db1_20160624063610.dump.sql           | 2016-06-24T10:36:12.295490 | Purged |
|      db1      |           db1/db1_20160624063613.dump.sql           | 2016-06-24T10:36:14.780210 | Purged |
| swiftbackmeup | swiftbackmeup/swiftbackmeup_20160624054028.dump.sql | 2016-06-24T09:40:30.377840 | Purged |
| swiftbackmeup | swiftbackmeup/swiftbackmeup_20160624063611.dump.sql | 2016-06-24T10:36:13.216240 | Purged |
| swiftbackmeup | swiftbackmeup/swiftbackmeup_20160624063614.dump.sql | 2016-06-24T10:36:15.799500 | Purged |
+---------------+-----------------------------------------------------+----------------------------+--------+
#> swiftbackmeup backup --list
+---------------+-----------------------------------------------------+----------------------------+
|     Item      |                     Backup file                     |       Last Modified        |
+---------------+-----------------------------------------------------+----------------------------+
|      db1      |           db1/db1_20160624063615.dump.sql           | 2016-06-24T10:36:17.117850 |
| swiftbackmeup | swiftbackmeup/swiftbackmeup_20160624063616.dump.sql | 2016-06-24T10:36:17.923470 |
+---------------+-----------------------------------------------------+----------------------------+
```


### restore

This mode allows a user to restore items from the remote object store.

To work, it needs the name of the item to restore and the version from which to restore it from

```
#> swiftbackmeup backup --list
+---------------+-----------------------------------------------------+----------------------------+
|      Item     |                     Backup file                     |       Last Modified        |
+---------------+-----------------------------------------------------+----------------------------+
|      db1      |           db1/db1_20160624063615.dump.sql           | 2016-06-24T10:36:17.117850 |
| swiftbackmeup | swiftbackmeup/swiftbackmeup_20160624063616.dump.sql | 2016-06-24T10:36:17.923470 |
+---------------+-----------------------------------------------------+----------------------------+
#> swiftbackmeup restore --items db1 --version db1/db1_20160624063615.dump.sql
```

The previous example will restore the database `db1` to the dump remotely stored as `db1/db1_20160624063615.dump.sql`

#### `--force`

This options allows one not to have to answer the security question: "Are you sure you want to restore the backup?"


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

  * `retention`: Number of unit a backup should be kept, else purged.
  * `unit`: The unit the retention represent. Possible value: `day`, `item`. Default `day`.
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
  - name: mydatabase
    database: mydatabase
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
  - name: mydatabase
    database: mydatabase
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
| store_type          | global, backup | None    | The store type to upload backup to (available: swift)             |
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
| data_only        | backup (the all db) | None    | Should --data-only be passed to pg_dumpall        |
| globals_only     | backup (the all db) | None    | Should --globals-only be passed to pg_dumpall     |
| roles_only       | backup (the all db) | None    | Should --roles-only be passed to pg_dumpall       |
| schema_only      | backup (the all db) | None    | Should --schema-only be passed to pg_dumpall      |
| tablespaces_only | backup (the all db) | None    | Should --tablespaces-only be passed to pg_dumpall |


### Configuration file example

```
---
os_username: os_username
os_password:  os_password
os_tenant_name: os_tenant_name
os_auth_url: os_auth_url

store_type: swift
swift_container: backup
swift_pseudo_folder: example

create_container: True
purge_container: False

output_directory: /var/tmp
clean_local_copy: True

modes:
  daily:
    retention: 7
    unit: day
    pattern: "%Y%m%d"
  weekly:
    retention: 28
    unit: day
    pattern: "%Y%m%d-%U"
  monthly:
    retention: 31
    unit: day
    pattern: "%Y%m"
  now:
    retention: 10
    unit: items
    pattern: "%Y%m%d%H%M%S"


backups:

  - name: mytestfile
    type: file
    path: /tmp/file
    backup_filename_prefix: 'mytestfile_'
    backup_filename_suffix: '.bk'
    subscriptions:
      - now
      - daily
      - monthly

  - name: mygitrepo
    type: git
    path: /srv/git/mygitrepo
    branches: all
    backup_filename_prefix: 'mygitrepo_'
    backup_filename_suffix: '.bundle'
    subscriptions:
      - now
      - daily
      - monthly

  - name: swiftbackmeup_mariadb
    type: mariadb
    database: swiftbackmeup
    host: 127.0.0.1
    user: root
    password: passpass
    backup_filename_prefix: 'swiftbackmeup_mariadb_'
    backup_filename_suffix: '.dump.sql'
    swift_pseudo_folder: swiftbackmeup_mariadb
    subscriptions:
      - now
      - daily
      - monthly

  - name: swiftbackmeup_postgresql
    type: postgresql
    database: swiftbackmeup
    backup_filename_prefix: 'swiftbackmeup_postgresql_'
    dump_options: -Z9 -Fc
    backup_filename_suffix: '.dump'
    swift_pseudo_folder: swiftbackmeup_postgresql
    subscriptions:
      - now
      - daily
      - monthly
```

