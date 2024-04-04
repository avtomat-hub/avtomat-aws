from .rules import *

config = {
    "required": required_rule,
    "choice": choice_rule,
    "and": and_rule,
    "at_most_one": at_most_one_rule,
    "at_least_one": at_least_one_rule,
    "logging": logging_rule,
    "date_yymmdd": date_yymmdd_rule,
    "cloudtrail": cloudtrail_rule,
}
