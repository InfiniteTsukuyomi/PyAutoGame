import ctypes
import logging
import os
import sys
import time

LOG_LEVEL = logging.DEBUG
OPEN_CONSOLE_LOG = True
OPEN_FILE_LOG = True
LOG_FILE_PATH = os.getcwd() + '/log'
LOG_NAME = 'null'

###############################################################################################################
# 仅限windows平台
# Windows CMD命令行 字体颜色定义 text colors  
FOREGROUND_BLACK            = 0x00                                  # black.  
FOREGROUND_DARKBLUE         = 0x01                                  # dark blue.  
FOREGROUND_DARKGREEN        = 0x02                                  # dark green.  
FOREGROUND_DARKSKYBLUE      = 0x03                                  # dark skyblue.  
FOREGROUND_DARKRED          = 0x04                                  # dark red.  
FOREGROUND_DARKPINK         = 0x05                                  # dark pink.  
FOREGROUND_DARKYELLOW       = 0x06                                  # dark yellow.  
FOREGROUND_DARKWHITE        = 0x07                                  # dark white.  
FOREGROUND_DARKGRAY         = 0x08                                  # dark gray.  
FOREGROUND_BLUE             = 0x09                                  # blue.  
FOREGROUND_GREEN            = 0x0a                                  # green.  
FOREGROUND_SKYBLUE          = 0x0b                                  # skyblue.  
FOREGROUND_RED              = 0x0c                                  # red.  
FOREGROUND_PINK             = 0x0d                                  # pink.  
FOREGROUND_YELLOW           = 0x0e                                  # yellow.  
FOREGROUND_WHITE            = 0x0f                                  # white.  

LOG_COLOR_DEFAULT = FOREGROUND_DARKGRAY
STD_OUTPUT_HANDLE = -11
std_out_handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE) 
def set_log_color(color=LOG_COLOR_DEFAULT):
    ctypes.windll.kernel32.SetConsoleTextAttribute(std_out_handle, color)
    return
###############################################################################################################

# 初始化日志
def create_logger(level=LOG_LEVEL, open_console=OPEN_CONSOLE_LOG, open_file=OPEN_FILE_LOG, path=LOG_FILE_PATH):
    logger = logging.getLogger("chao")
    logger.setLevel(level)
    formatter = logging.Formatter('[%(asctime)s][%(levelname)s]: %(message)s')
    if open_console:
        hterm =  logging.StreamHandler()
        hterm.setLevel(level)
        hterm.setFormatter(formatter)
        logger.addHandler(hterm)
    if open_file:
        if not os.path.exists(path):
            os.mkdir(path)
        hfile = logging.FileHandler(path + '/' + time.strftime("%Y-%m-%d", time.localtime()) + ".log")
        hfile.setLevel(level)
        hfile.setFormatter(formatter)
        logger.addHandler(hfile)
    return logger

logger = create_logger()

def d(msg, color=FOREGROUND_DARKGREEN):
    try:
        msg = '[{}][{}][{}] {}'.format(os.path.basename(sys._getframe(1).f_code.co_filename), sys._getframe(1).f_code.co_name, sys._getframe(1).f_lineno, msg)
    except:
        pass
    set_log_color(color)
    logger.debug(msg)
    set_log_color(FOREGROUND_DARKWHITE)
    return

def i(msg, color=FOREGROUND_DARKYELLOW):
    try:
        msg = '[{}][{}][{}] {}'.format(os.path.basename(sys._getframe(1).f_code.co_filename), sys._getframe(1).f_code.co_name, sys._getframe(1).f_lineno, msg)
    except:
        pass
    set_log_color(color)
    logger.info(msg)
    set_log_color(FOREGROUND_DARKWHITE)
    return

def e(msg, color=FOREGROUND_DARKRED):
    try:
        msg = '[{}][{}][{}] {}'.format(os.path.basename(sys._getframe(1).f_code.co_filename), sys._getframe(1).f_code.co_name, sys._getframe(1).f_lineno, msg)
    except:
        pass
    set_log_color(color)
    logger.error(msg)
    set_log_color(FOREGROUND_DARKWHITE)
    return    
