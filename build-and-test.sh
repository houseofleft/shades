pip uninstall -y shades
rm -r dist shades.egg-info

python3 -m build
pip install $(ls dist/*.whl)
pip install -r requirements.txt

cd tests
python3 -m unittest
