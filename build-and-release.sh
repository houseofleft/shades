rm -r dist shades.egg-info
python3 -m build
python3 -m twine upload dist/*
