#usr/bin/bash

echo "start running tests"

test_dirs=$(find . -type d -name "Tests")

for dir in $test_dirs; do
  echo "starting battery for directory $dir"
  python -m unittest discover -s $dir -p "test_*.py" -v
  echo "finished battery for directory $dir"
done

echo "finished running tests"