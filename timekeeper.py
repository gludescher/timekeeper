import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta
from dateutil import parser
import select
import sys
import os
from pandas.core.frame import DataFrame
from tabulate import tabulate
from timedataframe import TimeDataframe

#region globals
CREATE = 0 
BEGIN = 1
END = 2
STATS = 3
TABLE = 4
CURRENT_DIR = os.path.dirname(os.path.realpath(sys.argv[0]))

actions = {
    '--create': CREATE,
    '--begin': BEGIN,
    '-b': BEGIN,
    '--end': END,
    '-e': END,
    '--stats': STATS,
    '-s': STATS,
    '--table': TABLE,
    '-t': TABLE,
}
#endregion

#region begin action
def start_the_count(data, begin_time, comment=None):
    date =  begin_time.strftime('%Y-%m-%d')
    end_time = None

    if not previous_row_complete(data) and not begin_warning(data.read(data.last_entry_id())['begin_time']):
        print('Entry not created.')
        return

    data.add(date, begin_time, end_time, comment)

    print('Added a new entry with begin time {}'.format(begin_time.strftime('%Y-%m-%d-%H:%M:%S')))
    return

def previous_row_complete(data):
    if data.length() == 0:
        return True
    previous_entry_id = data.last_entry_id()
    return not pd.isnull(data.read(previous_entry_id)['end_time'])

def begin_warning(start_time):
    print('WARNING: Last entry, with begin time {}, has no end time. This will create a new entry and leave the end time for the previous one empty until manually edited.'.format(start_time.strftime('%Y-%m-%d-%H:%M:%S')))
    return wish_to_proceed()
#endregion

#region end action
def stop_the_count(data, end_time, comment=None):
    id = data.last_entry_id(end_time)
    entry = data.read(id)
    date = entry['date']
    begin_time = entry['begin_time']
    previous_end_time = entry['end_time']
    old_comment = entry['comments']

    if not pd.isnull(previous_end_time):
        if not end_warning(begin_time, end_time):
            print('Entry not overriden.')
            return

    new_comment = old_comment
    if comment is not None:
         new_comment = comment if pd.isnull(old_comment) else old_comment + '; ' + comment 
    
    data.update(id, date, begin_time, end_time, new_comment)

    print('Edited entry with period {} => {}'.format(begin_time.strftime('%Y-%m-%d-%H:%M:%S'), end_time.strftime('%Y-%m-%d-%H:%M:%S')))
    return

def end_warning(start_time, stop_time):    
    print('WARNING: Overriding end time for period: {} => {}'.format(start_time.strftime('%Y-%m-%d-%H:%M:%S'), stop_time.strftime('%Y-%m-%d-%H:%M:%S')))
    return wish_to_proceed()
#endregion

#region stats action
def get_period_sum(df):
    period_sum = df['time_spent'].sum()
    return period_sum

def get_period_avg(df):
    day_count = df['date'].nunique()
    period_sum = get_period_sum(df)
    return period_sum/day_count, day_count

def get_period_workday_avg(df, start_date, end_date):
    workdays_count = np.busday_count(start_date.date(), end_date.date())
    period_sum = get_period_sum(df)
    return period_sum/workdays_count, workdays_count

def calculate_periods(df, row=None):
    df['time_spent'] = df['end_time'] - df['begin_time']
    df['time_spent'] = (df['time_spent'].dt.seconds/3600).round(4)
    return df

def tabulate_stats(stats):
    stats_df = pd.DataFrame(columns=['Period', 'Total Hours', 'Days Worked', 'Daily Average', 'Workdays', 'Average by Workday'])
    stats_df.loc[0] = [stats['period'], stats['period_sum'], stats['period_day_count'], stats['period_avg'], stats['period_workday_count'], stats['period_avg_by_workday']]
    stats_df.loc[1] = [stats['total'], stats['total_sum'], stats['total_day_count'], stats['total_avg'], stats['total_workday_count'], stats['total_avg_by_workday']]
    return tabulate(stats_df, headers='keys', tablefmt="fancy_grid", showindex=False)

def calculate_stats(df, period=True):
    period_str = 'period' if period else 'total'

    stats = {}
    stats[period_str] = min(df['date']).strftime('%d/%m/%Y') + ' - ' + max(df['date']).strftime('%d/%m/%Y')
    stats[period_str+'_sum'] = get_period_sum(df)
    stats[period_str+'_avg'], stats[period_str+'_day_count'] = get_period_avg(df)
    stats[period_str+'_avg_by_workday'], stats[period_str+'_workday_count'] = get_period_workday_avg(df, start_date, end_date)
    return stats

def get_stats(data, start_date, end_date):
    df = calculate_periods(data.get_all())
    period_df = calculate_periods(data.get_entries_between(start_date, end_date))

    period_stats = calculate_stats(period_df, True)
    total_stats = calculate_stats(df, False)
    stats = {**total_stats, **period_stats}
    
    print(tabulate_stats(stats))
    return
#endregion

#region table action
def get_table(data, start_date, end_date):
    period = data.get_entries_between(start_date, end_date)
    table = tabulate(period, headers='keys', tablefmt="fancy_grid", showindex=False)
    print(table)
    return
#endregion

#region input handling
def get_action():
    action = next((actions[a] for a in actions if a in opts), None)
    if action is None:
        i = valid_input("Are you registering the beginning or end of period? [B/E]", ['b', 'begin', 'e', 'end'])
        action = BEGIN if i in ['b', 'begin'] else END
    return action

def get_comment():
    comment = None
    if '-c' in opts or '--comment' in opts:
        comment = get_following_args(['-c', '--comment'])
    return comment

def get_period():
    if '-p' in opts or '--period' in opts:
        dates = get_following_args(['-p', '--period'], join=False)
        date_1 = parser.parse(dates[0])
        date_2 = parser.parse(dates[1]) if len(dates) > 1 else datetime.today()
        start_date = min(date_1, date_2)
        end_date = max(date_1, date_2)
    else:
        today = datetime.today()
        start_date = datetime(today.year, today.month, 1)
        end_date = today
    return start_date, end_date

def get_date():
    if '-d' in opts or '--date' in opts:
        date = get_following_args(['-d', '--d'], join=True)
        date_time = parser.parse(date)
    else:
        date_time = datetime.now()
    return date_time

def with_stats():
    return '-s' in opts or '--sum' in opts 

def valid_input(message, accepted_inputs):
    text = None
    while (text not in accepted_inputs):
        print(message)
        text = input().lower()
    return text

def get_following_args(options, join=True):
    option_arg = []
    for option in options:
        try:
            opt_index = sys.argv[1:].index(option)
            for arg in sys.argv[opt_index+2:]:
                if arg.startswith('-'):
                    break
                option_arg.append(arg)
            break
        except:
            continue

    return ' '.join(option_arg) if join else option_arg

def wish_to_proceed():
    accepted_inputs = ['y', 'yes', '1', 's', 'sim', 'n', 'no', 'nao', '0', 'time_for_input_ended']
    _positive_inputs = ['y', 'yes', '1', 's', 'sim']
    negative_inputs = ['n', 'no', 'nao', '0']
    received = ''

    print('Do you wish to proceed? [Y/N]')
    while(received not in accepted_inputs):
        received = input()
        
    return received not in negative_inputs

# not in use
def timed_wish_to_proceed(time_to_proceed=10):
    accepted_inputs = ['y', 'yes', '1', 's', 'sim', 'n', 'no', 'nao', '0', 'time_for_input_ended']
    _positive_inputs = ['y', 'yes', '1', 's', 'sim']
    negative_inputs = ['n', 'no', 'nao', '0']
    received = ''

    print('Proceeding automatically in {} seconds... Do you wish to proceed? [Y/N]'.format(time_to_proceed))
    while(received not in accepted_inputs):
        i, _o, _e = select.select([sys.stdin], [], [], time_to_proceed)
        received = sys.stdin.readline().strip().lower() if i else 'time_for_input_ended'

    return received not in negative_inputs

opts = [opt for opt in sys.argv[1:] if opt.startswith("-")]
args = [arg for arg in sys.argv[1:] if not arg.startswith("-")]
#endregion

action = get_action()
comment = get_comment()
include_stats = with_stats()
data = TimeDataframe()

if action == CREATE:
    data.open(force_create_new = True)
else:
    data.open()
    if action == BEGIN:    
        begin_time = get_date()     
        start_the_count(data, begin_time, comment=comment)
    elif action == END: 
        end_time = get_date()
        stop_the_count(data, end_time=end_time, comment=comment)
    elif action == STATS:
        start_date, end_date = get_period()
        get_stats(data, start_date, end_date)
    elif action == TABLE:
        start_date, end_date = get_period()
        get_table(data, start_date, end_date)

data.close()
