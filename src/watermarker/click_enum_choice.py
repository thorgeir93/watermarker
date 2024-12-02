"""
** NOTE **
This file is temporary because Click release 8.1.8 or 8.2.0,
the click.EnumChoice will be available.
    - Implementation: https://github.com/pallets/click/pull/2272
    - Release plan: https://github.com/pallets/click/issues/2789
"""
import click


class EnumChoice(click.Choice):
    """Custom click.Choice that converts the string input
    directly into the corresponding enum value.
    """

    def __init__(self, enum_type):
        self.enum_type = enum_type
        super().__init__([e.value for e in enum_type], case_sensitive=False)

    def convert(self, value, param, ctx):
        # Convert the string to the corresponding enum
        value = super().convert(value, param, ctx)  # Validates the choice
        return self.enum_type(value)  # Convert string to enum
