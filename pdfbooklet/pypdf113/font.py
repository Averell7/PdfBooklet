"""
A python port of the ruby pdf-reader library (http://github.com/yob/pdf-reader).
The liscense for that code copied below.
"""

################################################################################
#
# Copyright (C) 2008 James Healy (jimmy@deefa.com)
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
################################################################################

__author__ = "Ben Huffine"
__author_email__ = "ben.huffine@thisismedium.com"

import re
from encoding import Encoding

import utils

class UnsupportedFontEncodingException(utils.PdfReadError):
    pass

class Font(object):
    def __init__(self, *args, **kwargs):
        font = kwargs.get('font')
        if font == 'Symbol':
            self.encoding = Encoding('SymbolEncoding')
        elif font == 'ZapfDingbats':
            self.encoding = Encoding('ZapfDingbatsEncoding')
        else:
            self.encoding = None

        self.basefont = font
        self.tounicode = None

    def to_utf8(self, params):
        if isinstance(self.encoding, basestring):
            raise self.UnsupportedFontEncodingException

        if isinstance(params, basestring):
            #   translate the bytestream into a UTF-8 string
            #   If an encoding hasn't been specified, assume the text using this
            #   font is in Adobe Standard Encoding.
            enc = self.encoding and self.encoding or Encoding('StandardEncoding')
            return enc.to_utf8(params, self.tounicode)
        elif isinstance(params, (list, tuple)):
            return map(lambda param: self.to_utf8(param), params)
        else:
            return params


def glyphnames():
    """
        Returns a hash that maps glyph names to unicode codepoints.  The mapping is based on a text file supplied by Adobe at:
        http://www.adobe.com/devnet/opentype/archives/glyphlist.txt
    """
    glyphs = {}

    glyph_re = re.compile(r'/([0-9A-Za-z]+);([0-9A-F]{4})/')

    import os.path
    dir_name = os.path.dirname(__file__)
    f = open("%s/glyphlist.txt" % dir_name, "r")
    try:
        for line in f:
            m = glyph_re.match(line)
            if m:
                name, code = m.groups()
                glyphs[name] = int(code, 16)
    finally:
        f.close()

    return glyphs

