# Timekeeper<!-- omit in toc --> 
 
- [Project](#project)
- [Installation](#installation)
  - [Dependencies](#dependencies)
- [Usage](#usage)
  - [First Run](#first-run)
  - [Options](#options)

## Project

This is a simple tool to keep track of the duration of regular activities, such as your workshift. It was built using mainly Python 3 and Pandas and has a quite simple usage.

## Installation

At least for now, the tool does not have an executable version that handles all the needed installations. So, you'll need to fullfill the dependencies manually.

### Dependencies

- Python 3
- Python 3 libs:
    - Pandas
    - Numpy
    - Dateutil
    - Tabulate

After making sure the dependencies are satisfied, download the `timekeeper.py` file.

## Usage

### First Run

To run Timekeeper, it is recommended to create a separate folder for the tool:

```bash
mkdir timekeeper
```

After that, run the following command to create a .csv file that will store your activities logs:

```bash
python timekeeper.py --create 
```

Now, you can record the beginning of your first activity:

```bash
python timekeeper.py --begin 
```

### Options

Timekeeper has some options to be executed with.

#### Action Options

These options define the action the tool will execute and are mutually excludent. If none of those is passed, the script will prompt the user for input, allowing for `--begin` or `--end` behaviors.

`--create`: Creates a new .csv file for registering logs.

❗Attention: this will overwrite the `timekeeper.csv` file, if it exists. A backup is recommended.

`--begin`, `-b`: Adds a new line to the log with the current time as begin time. If the previous entry has no end time, a warning will be shown, asking for confirmation to proceed with the creation.

`--end`, `-e`: Edits the last line of the log with the current time as end time. If the previous entry already has an end time, a warning will be shown, asking for confirmation to proceed with the overwriting.

`--stats`, `-s`: Displays stats for a specific period and for all the entries. By default, the period is the current calendar month and this can be changed using the modifier `--period`.

`--table`, `-t`: Displays the full table for a specific period and for all the entries. By default, the period is the current calendar month and this can be changed using the modifier `--period`.

#### Modifier options

These options aren't required and modify an action option.

`--comment`, `-c`: Can be used with `--begin` or `--end`. Adds a comment to the current entry. If the entry already has a comment, the new one is appended. Example:

```bash
python timekeeper.py -b -c Just some comment here
```

`--period`, `-p`: Can be used with `--stats` or `--table`. Defines the period (inclusive on both ends) from which to extract the stats. If only one date is passed, the end of the period will be set as the current date. It accepts multiple date formats, but will consider month before day whenever ambiguous.

```bash
python timekeeper.py -s -p 2020-11-19 2020-12-03
```