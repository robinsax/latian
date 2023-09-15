'''
Command line argument parser.
'''
import sys
from typing import Any

class CLIArgs:
    arguments: list[str]
    schema: dict[str, tuple]

    def __init__(self, arguments: list[str], schema: dict[str, tuple]):
        self.arguments = arguments
        self.schema = schema

        self._prevalidate()

    def _prevalidate(self):
        in_value = False
        for argument in self.arguments:
            match = False
            for key in self.schema:
                if argument in self.schema[key][0]:
                    match = True
                    break

            if match:
                in_value = True
            elif in_value:
                in_value = False
            else:
                self._abort('unknown argument: %s'%argument)
    
    def _abort(self, message: str):
        print('invalid arguments: %s'%message, file=sys.stderr)
        sys.exit(1)

    def _abort_invalid_value(self, name: str):
        switches, _, config = self.schema[name]
        value_rule = config.get('value')

        detail = str()
        if isinstance(value_rule, list):
            detail = ', must be one of: %s'%', '.join(value_rule) 

        self._abort('%s has invalid value%s'%(switches[0], detail))

    def get(self, name: str) -> Any:
        switches, _, config = self.schema[name]
        value_rule = config.get('value')
        default_value = config.get('default')
        if callable(default_value):
            default_value = default_value(self)

        value = None
        for k, argument in enumerate(self.arguments):
            if argument in switches:
                if value_rule is None:
                    value = True
                    break
                
                if k + 1 >= len(self.arguments):
                    self._abort('%s missing a value'%switches[0])
                value = self.arguments[k + 1]
                break

        if not value:
            if value_rule and not default_value:
                self._abort('%s is required'%switches[0])
            value = default_value

        if isinstance(value_rule, list) and value not in value_rule:
            self._abort_invalid_value(name)
        elif value_rule is int:
            try:
                value = int(value)
            except ValueError:
                self._abort_invalid_value(name)

        return value

    def show_help(self):
        print('usage:')

        for key in sorted(self.schema.keys()):
            switches, help, config = self.schema[key]
            value_rule = config.get('value')
            default_value = config.get('default')

            option_format = '%s %s'%(
                ', '.join(switches),
                '<val>' if value_rule else str()
            )
            details = list()
            if isinstance(value_rule, list):
                details.append('where <val> is one of: %s'%', '.join(value_rule))
            if default_value and not callable(default_value):
                details.append('defaults to: %s'%default_value)

            print('%s%s%s%s'%(
                option_format,
                ' '*(30 - len(option_format)),
                help,
                ('\n%s'%(' '*34)).join((str(), *details))
            ))
