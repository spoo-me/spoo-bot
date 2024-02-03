import os
from dotenv import load_dotenv
import re
import requests
from py_spoo_url import Shortener, Statistics
from typing import Literal
import geopandas as gpd
from mpl_toolkits.axes_grid1 import make_axes_locatable
from typing import Literal
import matplotlib.pyplot as plt
import matplotlib
import discord
import random
import datetime
import random

load_dotenv()

TOKEN = os.environ["TOKEN"]
