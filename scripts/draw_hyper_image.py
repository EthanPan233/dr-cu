import numpy as np
from PIL import Image
import sys
from pathlib import Path

PATH = Path(sys.argv[1])

for dir in PATH.glob("**"):
	designName = str(dir).split("/")[-1]
	print(designName)