rm -rf docs
sphinx-apidoc -H "Lab ToolSuite" -A "Jithin B."  -F -o docs .
cp conf.py docs/conf.py
cd docs
make html
