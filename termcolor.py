# -*- coding: utf-8 -*-
"""
Created on Fri Sep  6 19:33:10 2019

@author: levy.he
"""
import sys,os
from ctypes import windll

COLOR_LIST = ["black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"]
STYLE_LIST = ["reset", "bold","faint","italic","underline","blink", "rapidblink", "reverse", "conceal"]

COLOR_RESET = '\033[0m'

class Color(object):

    _colors = dict(map(lambda x: (x[1], x[0]), enumerate(COLOR_LIST)))
    _styles = dict(map(lambda x: (x[1], x[0]), enumerate(STYLE_LIST)))

    def __init__(self):
        
        self.TERM = os.getenv("TERM")
        self.kernel32 = windll.kernel32
        if self.TERM is None:
            self.term_color_on()

    def term_color_on(self):
        self.kernel32.SetConsoleMode(self.kernel32.GetStdHandle(-11), 7)

    def color256(self, N):
        return (5, N)

    def colorRGB(self, R, G, B):
        return (2, R, G, B)

    def format(self, *text, fg=None, bg=None, attrs=None, sep=' '):
        fg_str = self._get_color_fm(fg, fg_bg='3')
        bg_str = self._get_color_fm(bg, fg_bg='4')
        if isinstance(attrs, (list, tuple)):
            style_str = ";".join([self._get_style_fm(attr) for attr in attrs])
        else:
            style_str = self._get_style_fm(attrs)
        fm_list = [x for x in [fg_str, style_str, bg_str] if x != '']
        fm_str = ';'.join(fm_list)
        text_str = sep.join([str(x)for x in text])
        if fm_str != '':
            fm_str = '\033[' + fm_str + 'm' + text_str + COLOR_RESET
        else:
            fm_str = text_str
        return fm_str


    def cprint(self, *text, fg=None, bg=None, attrs=None, **kwargs):
        sep = kwargs.get('sep',' ')
        print(self.format(*text, fg=fg, bg=bg, attrs=attrs, sep=sep), **kwargs)

    def _get_color_fm(self, color, fg_bg='3'):
        color_str = ''
        if isinstance(color, (list, tuple)):
            if (color[0] == 2 and len(color) == 4) or (color[0] == 5 and len(color) == 2):
                color_str = fg_bg +'8;' + ';'.join([str(int(x) & 0xFF) for x in color])
        elif isinstance(color, (int, float)):
            if int(color) in self._colors.values():
                color_str = fg_bg + str(int(color))
        elif isinstance(color, str) and color in self._colors:
            color_str = fg_bg+ str(self._colors[color])
        return color_str

    def _get_style_fm(self, style):
        style_str = ''
        if isinstance(style, (int, float)):
            if int(style) in self._styles.values():
                style_str = str(int(style))
        elif isinstance(style, str) and style in self._styles:
            style_str = str(self._styles[style])
        return style_str

    @property
    def BLACK(self):
        return self._colors['black']

    @property
    def RED(self):
        return self._colors['red']

    @property
    def GREEN(self):
        return self._colors['green']

    @property
    def YELLOW(self):
        return self._colors['yellow']

    @property
    def BLUE(self):
        return self._colors['blue']

    @property
    def MAGENTA(self):
        return self._colors['magenta']

    @property
    def CYAN(self):
        return self._colors['cyan']

    @property
    def WHITE(self):
        return self._colors['white']

    @property
    def RESET(self):
        return self._styles['reset']

    @property
    def BOLD(self):
        return self._styles['bold']

    @property
    def FAINT(self):
        return self._styles['faint']

    @property
    def ITALIC(self):
        return self._styles['italic']

    @property
    def UNDERLINE(self):
        return self._styles['underline']

    @property
    def BLINK(self):
        return self._styles['blink']

    @property
    def RAPIDBLINK(self):
        return self._styles['rapidblink']

    @property
    def REVERSE(self):
        return self._styles['reverse']

    @property
    def CONCEAL(self):
        return self._styles['conceal']

class Cursor(object):
    '''
    Function Up, Down, Left, Right:
        Moves the cursor n cells in the given direction. 
        If the cursor is already at the edge of the screen, this has no effect.
    Function Position
        Moves the cursor to row n, column m. 
    Function Clear
        Clears part of the screen.
        If n is 0 (or missing), clear from cursor to end of screen. 
        If n is 1, clear from cursor to beginning of the screen. 
        If n is 2, clear entire screen (and moves cursor to upper left on DOS ANSI.SYS). 
        If n is 3, clear entire screen and delete all lines saved in the scrollback buffer
    Function ClearInLine
        Erases part of the line.
        If n is 0 (or missing), clear from cursor to the end of the line. 
        If n is 1, clear from cursor to beginning of the line. 
        If n is 2, clear entire line. Cursor position does not change.
    '''
    def __init__(self):
        pass

    def up(self, n):
        return '\033[%dA'%(n)

    def down(self, n):
        return '\033[%dB' % (n)

    def right(self, n):
        return '\033[%dC' % (n)
    
    def left(self, n):
        return '\033[%dD' % (n)

    def position(self, n, m):
        return '\033[%d;%dH' % (n,m)

    def clear(self, n):
        return '\033[%dJ' % (n)

    def clearinline(self, n):
        return '\033[%dK' % (n)

color = Color()
cursor = Cursor()
cprint = color.cprint
if __name__ == "__main__":
    print('Current terminal type: %s' % os.getenv('TERM'))
    cprint('Test basic colors:')
    cprint('Black','color',fg='black',attrs='bold')
    cprint('Red color', fg='red', attrs='bold')
    cprint('Green color', fg='green', attrs='bold')
    cprint('Yellow color', fg='yellow', attrs='bold')
    cprint('Blue color', fg='blue', attrs='bold')
    cprint('Magenta color', fg='magenta', attrs='bold')
    cprint('Cyan color', fg='cyan', attrs='bold')
    cprint('White color', fg='white', attrs='bold')
