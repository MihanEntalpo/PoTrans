FILE="$(basename "$(test -L "$0" && readlink "$0" || echo "$0")")"
DIR=`dirname $FILE`
cd $DIR
rm ./dist/*.gz
rm ./dist/*.whl
python3 ./setup.py sdist
python3 ./setup.py bdist_wheel
twine upload dist/*