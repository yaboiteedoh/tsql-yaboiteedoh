<h1>TSQL</h1>

A Python Environment Database Module Generator

<h2>Installation</h2>
to install, use the command:
```
$ pip install tsql-yaboiteedoh
```
in bash

<h2>Usage</h2>
the bash command:
```
$ tsql
```
Runs the application in the current directory, allowing you to search it for
valid configuration files or generate a new database where you are

To get the most out of that I have it installed into a toolbox .venv, and have
added this function to my ~/.bashrc script:
```
sql() {
    (
        source '/home/teedoh/devkit/.venv/bin/activate'
        tsql
    )
}
```
Saving the configuration saves to the current directory under 
(database name).tsql
Default behavior is to not override previous saves, to enable easier version
control

Exporting the configuration folder dumps a python module named after the database
into the current directory, which you can reach with
```
from {database name} import Database
```
once instantiated, you can reach into the database with the associated functions
on the table objects

db = Database()
table_entries = db.{table name}.read_all()

<h4>Functionality</h4>

*0.1.8*
- support for datatypes
    - TEXT
    - INT
    - BOOL
- Groups
    - search multiple columns for the same value
- Filters
    - return based on a combination of column and group values
- parameters
    - NOT NULL
    - PRIMARY KEY
    - AUTOINCREMENT
- Column Types
    - functions with dataclass object returns for unique column values
    - functions with list of dataclass object returns for shared column values
    - any column not labeled 'returns' is considered passive
        - these will exist on the dataclass object but not have an associated query function
- Column references
    - these will update dynamically as you alter your table config

*0.2.0 (planned)*
- expanded data types and parameters
- More robust and customizable version control system
- Hidden columns which will not appear on the dataclass object

*0.3.0 (planned)*
- Join tables

