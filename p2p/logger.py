#!-*- coding:utf-8 -*-
import logging
import os

PATH = os.path.abspath(os.path.dirname(__file__))
log_filename = 'log/p2p.log'
logging.basicConfig(
    filename=os.path.join(PATH, log_filename),
    format='[%(levelname)s %(asctime)s] %(message)s',
    level=logging.INFO,
)
logger = logging.getLogger(__name__)
