"""
For functions regarding the use of regular expressions in this project.
"""


def create_regex_from_list(strings: [str], capture_keyword: str = None) -> str:
    """
    Join a list of strings into a regex with a group name. When matched, this group can be accessed by calling
    .group(capture_keyword) on the resulting match object, as long as capture_keyword is not None. If capture_keyword is
     None, this group will be made non-capturing.

    :param strings: the list of strings to join together
    :param capture_keyword: the group name to be used when accessing this group from a match, if None this group
    will be made non capturing
    :return: the regex created from the list of strings formatted as such: '\s*(?P<capture_keyword>word_1|word_2)'
    """
    if capture_keyword is None:
        return f'\s*(?:{"|".join(strings)})'
    return f'\s*(?P<{capture_keyword}>{"|".join(strings)})'
