import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta
from dateutil import parser
import select
import sys
import os
from tabulate import tabulate

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
def start_the_count(df, begin_time=None, comment=None):
    if not begin_time:
        begin_time = datetime.now()
    date =  begin_time.strftime('%Y-%m-%d')
    end_time = None
    time_spent = None
    new_row = df.shape[0]

    if not previous_row_complete(df):
        previous_row = new_row - 1
        previous_begin_time = df.loc[previous_row]['begin_time']
        if not begin_warning(previous_begin_time):
            print('Entry not created.')
            return

    df.loc[new_row] = [date, begin_time, end_time, time_spent, comment]

    print('Added a new entry with begin time {}'.format(begin_time.strftime('%Y-%m-%d-%H:%M:%S')))
    return

def previous_row_complete(df):
    if df.shape[0] == 0:
        return True
    previous_row = df.shape[0] - 1
    previous_begin_time = df.loc[previous_row]['end_time']
    return not pd.isnull(previous_begin_time)

def begin_warning(start_time):
    print('WARNING: Last entry, with begin time {}, has no end time. This will create a new entry and leave the end time for the previous one empty until manually edited.'.format(start_time.strftime('%Y-%m-%d-%H:%M:%S')))
    return wish_to_proceed()
#endregion

#region end action
def stop_the_count(df, end_time=None, comment=None):
    row = find_end_row(df, end_time)
    begin_time = df.loc[row]['begin_time']
    previous_end_time = df.loc[row]['end_time']
    old_comment = df.loc[row]['comments']

    if not pd.isnull(previous_end_time):
        if not end_warning(begin_time, end_time):
            print('Entry not overriden.')
            return

    df.loc[row, 'end_time'] = end_time

    td = end_time - begin_time
    df.loc[row, 'time_spent'] = round(td.seconds/3600, 4)

    if comment is not None:
        df.loc[row, 'comments'] = comment if pd.isnull(old_comment) else old_comment + '; ' + comment 

    print('Edited entry with period {} => {}'.format(begin_time.strftime('%Y-%m-%d-%H:%M:%S'), end_time.strftime('%Y-%m-%d-%H:%M:%S')))
    return

def find_end_row(df, end_time=None):
    print(end_time)
    if end_time:
        row = df[(pd.isnull(df['end_time'])) & (df['begin_time'] < end_time)].tail(1).index[0]
    else: 
        row = df.tail(1).index[0]
    return row

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

def get_stats(df, start_date, end_date):
    df = calculate_periods(df)
    period_df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]

    period_stats = calculate_stats(period_df, True)
    total_stats = calculate_stats(df, False)
    stats = {**total_stats, **period_stats}
    
    print(tabulate_stats(stats))
    return
#endregion

#region table action
def get_table(df, start_date, end_date):
    period_df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
    table = tabulate(period_df, headers='keys', tablefmt="fancy_grid", showindex=False)
    print(table)
    return
#endregion

#region file handling
def create_dataframe():    
    df = pd.DataFrame(columns=['date', 'begin_time', 'end_time', 'time_spent', 'comments'])
    return df

def open_dataframe(path=CURRENT_DIR, file_name='timekeeper.csv'):
    if os.path.exists(path+'/'+file_name):
        df = pd.read_csv(path+'/'+file_name, parse_dates=['date', 'begin_time', 'end_time'])
    else:
        df = create_dataframe()
    return df

def save_dataframe(df, path=CURRENT_DIR, file_name='timekeeper.csv'):
    df.sort_values(by='date').to_csv(path+'/'+file_name, index=False)
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
        date_time = None
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

def wish_to_proceed(time_to_proceed=10):
    accepted_inputs = ['y', 'yes', '1', 's', 'sim', 'n', 'no', 'nao', '0', 'time_for_input_ended']
    positive_inputs = ['y', 'yes', '1', 's', 'sim']
    negative_inputs = ['n', 'no', 'nao', '0']
    received = ''

    print('Proceeding automatically in {} seconds... Do you wish to proceed? [Y/N]'.format(time_to_proceed))
    while(received not in accepted_inputs):
        i, o, e = select.select([sys.stdin], [], [], time_to_proceed)
        received = sys.stdin.readline().strip().lower() if i else 'time_for_input_ended'

    return received not in negative_inputs

opts = [opt for opt in sys.argv[1:] if opt.startswith("-")]
args = [arg for arg in sys.argv[1:] if not arg.startswith("-")]
#endregion

action = get_action()
comment = get_comment()
include_stats = with_stats()

if action == CREATE:
    df = create_dataframe()
else:
    df = open_dataframe()
    if action == BEGIN:    
        begin_time = get_date()     
        start_the_count(df, begin_time=begin_time, comment=comment)
    elif action == END: 
        end_time = get_date()
        stop_the_count(df, end_time=end_time, comment=comment)
    elif action == STATS:
        start_date, end_date = get_period()
        get_stats(df, start_date, end_date)
    elif action == TABLE:
        start_date, end_date = get_period()
        get_table(df, start_date, end_date)

save_dataframe(df)
