#Note - no need to change version before runnning -> change after

rm dist/*

python setup.py sdist bdist_wheel

twine upload dist/*
pause
