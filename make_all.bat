rm dist/*
pause
python setup.py sdist bdist_wheel
pause
twine upload dist/*
pause
