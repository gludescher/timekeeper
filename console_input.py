import sys
import os
from datetime import datetime
from dateutil import parser

#region globals
CREATE = 0 
BEGIN = 1
END = 2
STATS = 3
TABLE = 4
COMMENT = 5
DATE = 6
PERIOD = 7
#endregion

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

run_options = {
    '--create': CREATE,
    '--begin': BEGIN,
    '-b': BEGIN,
    '--end': END,
    '-e': END,
    '--stats': STATS,
    '-s': STATS,
    '--table': TABLE,
    '-t': TABLE,
    '--comment': COMMENT,
    '-c': COMMENT,
    '--date': DATE, 
    '-d': DATE,
    '--period': PERIOD,
    '-p': PERIOD,
}

class ConsoleInput(object):
    def __init__(self):
        self.__console_input = sys.argv[1:]
        self.__opts = [opt for opt in self.__console_input if opt.startswith("-")]
        self.__args = [arg for arg in self.__console_input if not arg.startswith("-")]
        self.__options_args = self.__get_options_args()

    def get_action(self):
        action = next((actions[a] for a in actions if a in self.__opts), None)
        if action is None:
            i = self.__valid_input("Are you registering the beginning or end of period? [B/E]", ['b', 'begin', 'e', 'end'])
            action = BEGIN if i in ['b', 'begin'] else END
        return action

    def get_comment(self):
        comment = None
        if COMMENT in self.__options_args:
            comment = ' '.join(self.__options_args[COMMENT])
        return comment

    def get_period(self):
        if PERIOD in self.__options_args:
            dates = self.__options_args[PERIOD]
            date_1 = parser.parse(dates[0])
            date_2 = parser.parse(dates[1]) if len(dates) > 1 else datetime.today()
            start_date = min(date_1, date_2)
            end_date = max(date_1, date_2)
        else: 
            today = datetime.today()
            start_date = datetime(today.year, today.month, 1)
            end_date = today
        return start_date, end_date

    def get_date(self):
        if DATE in self.__options_args:
            date = ' '.join(self.__options_args[DATE])
            date_time = parser.parse(date)
        else:
            date_time = datetime.now()
        return date_time

    def include_stats(self):
        return STATS in self.__options_args

    def wish_to_proceed(self):
        positive_inputs = ['y', 'yes', '1', 's', 'sim']
        negative_inputs = ['n', 'no', 'nao', '0']
        i = self.__valid_input("Do you wish to proceed? [Y/N]", positive_inputs+negative_inputs)        
        return i in positive_inputs

    def __valid_input(self, message, accepted_inputs):
        text = None
        while (text not in accepted_inputs):
            print(message)
            text = input().lower()
        return text

    def __get_options_args(self):
        options_args = {}
        for opt in self.__opts:
            opt_index = self.__console_input.index(opt)
            options_args[run_options[opt]] = []
            for i in self.__console_input[opt_index+1:]:
                if i.startswith('-'):
                    break
                options_args[run_options[opt]].append(i)
        return options_args
