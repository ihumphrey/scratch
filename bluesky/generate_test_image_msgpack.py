# Resources
# ---------
# https://github.com/bluesky/databroker/blob/master/examples/generate_msgpack_data.py
# https://github.com/NSLS-II-CSX/xf23id1_profiles/blob/master/profile_collection/startup/csx1/plans/xpcs.py
# https://nsls-ii.github.io/bluesky/
import logging
import tempfile
from functools import partial

import numpy as np
from PIL import Image

import bluesky.preprocessors as bpp
from bluesky import RunEngine
from bluesky.plans import count, scan
from bluesky.simulators import summarize_plan
from bluesky.utils import ProgressBarManager
from ophyd.sim import det4, det5, motor, SynSignal #direct_img
from suitcase.msgpack import Serializer


def image_array(img_file, rgb=False) -> np.array:
    """
    Opens an image file and returns an unsigned 8-bit np.array.

    Parameters
    ----------
    img_file:
        Full path to the image to open.
    rgb:
        Flag to return rgb vs. 1-channel (default False).

    Returns
    -------
    If `rgb` is True, returns an 3-channel unsigned 8-bit np.array;
    otherwise, returns a 1-channel unsigned 8-bit np.array.
    """
    try:
        with Image.open(img_file) as im:
            # Convert from RGB to single-channel
            im = im.convert("L")
            return np.array(im)
    except FileNotFoundError as e:
        raise IOError(f"Can't open image {img_file}.") from e

def plan(detectors, num):
    """
    Defines a callable that can be passed into RE.

    Parameters
    ----------
    detectors:
        List of detectors to run this plan on.
    num:
        Number of plans to run for each detector (~ number of events).

    Returns
    -------
    Document generator.
    """
    yield from count(detectors, num)


def add_noise(image: np.array):
    # Applies random 0 or 1 noise to the image
    return np.random.rand(*image.shape).round() + image


test_file = '../assets/clyde.jpg'
im = image_array(test_file)
direct_img = SynSignal(func=partial(add_noise, im),
                       name='img', labels={'detectors'})

DETECTORS = [direct_img]
NUM = 10
RE = RunEngine()

# Create a temporary /tmp directory to store our msgpack
directory = tempfile.TemporaryDirectory().name

# Define metadata for the plan
md = {'detectors': [det.name for det in DETECTORS],
      'num_steps': NUM,
      'plan_args': {'detectors': list(map(repr, DETECTORS)), 'num': NUM},
      'plan_name': 'test_count'}

with Serializer(directory) as serializer:
    # Serializer all documents; print only 'event' documents
    cbs = {'all': [serializer], 'event': [print]}
    RE(plan(detectors=DETECTORS, num=NUM), cbs, md=md)

#RE.waiting_hook = ProgressBarManager()

logger = logging.getLogger('databroker')
logger.setLevel('DEBUG')
handler = logging.StreamHandler()
handler.setLevel('DEBUG')
logger.addHandler(handler)

from databroker._drivers.msgpack import BlueskyMsgpackCatalog
cat = BlueskyMsgpackCatalog(f'{directory}/*.msgpack')
print(f"\nCreated msgpack:\n\t{directory}/{list(cat)[-1]}.msgpack")
#logger.log(logging.INFO, f"Created catalog {cat} at {directory}.")

