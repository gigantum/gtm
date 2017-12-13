# Copyright (c) 2017 FlashX, LLC
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import re


def dockerize_path(dkrpath: str) -> str:
    """Returns a path that can be mounted as a docker volume on windows
        Docker uses non-standard formats for windows mounts.
        This routine converts C:\\a\\b -> //C/a/b on windows and does
        nothing on posix systems.

    Args:
        dkrpath(str): a python path

    Returns:
        str: path that can be handed to Docker for a volume mount
    """
    # Docker does not take ntpath formatted strings as volume mounts.
    # detect if it's a volume path and rewrite the string.
    if os.path.__name__ == 'ntpath':
        # for windows switch the slashes and then sub the drive letter
        return re.sub('(^[A-Z]):(.*$)', '//\g<1>\g<2>', dkrpath.replace('\\', '/'))
    else:
        return dkrpath 


