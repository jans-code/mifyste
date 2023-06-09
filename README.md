![logo](mifyste.png)

This tool minimizes your steam library grid.

## Installation:
1. Install Python (from [python.org](www.python.org))
2. Download/clone this repository
3. Open terminal in project root
4. run `pip install -r requirements.txt`
5. run `py mifyste.py`
6. (optional) on windows you can rename `mifyste.py` to `mifyste.pyw` to run the program by just double-clicking on it.

---

## Troubleshooting:

##### Error on step 4

Try `py -m pip install -r requirements.txt`

Instead of `py` try `python` or `python3`.

If all of this fail run `py -m ensurepip` and try again.

As a last step try reinstalling python.

##### Error on step 5

Instead of `py` try `python` or `python3`.

If mifyste cannot find your steam directory use the folder picker to locate your steam root manually.

Then refresh users list and you can generate your steam grid files.

#### I want to get rid of the mifyste look

Delete the folder steam/userdata/YOURID/config/grid

### Other problems?

Please post them [here](https://github.com/jans-code/jansagdakernel/issues).

---

## ToDo/Ideas

- No-GUI mode
- Implement measuring the size of current library assets
- ... and project size after using mifyste
- Overwrite files check-box
- Clean up steam library cache check-box
- Allow more customization (currently images can be swapped in resource folder)
- ... and preview elements
- Implement some other fonts (nothing fancy, resulting image-size is smallest with simple fonts with lots of straight edges)