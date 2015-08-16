cp ../experiment.py .
cp -R ../widgets .
cp ../custom_widgets.py .
cp ../achan.py .
cp ../digital_channel.py .
cp ../interface.py .
cp ../packet_handler.py .
cp ../SPI_class.py .
cp ../I2C_class.py .
cp ../NRF24L01_class.py .
cp ../MCP4728_class.py .

cp -R ../Apps/*.py Apps/

rm -rf docs
sphinx-apidoc -H "Lab ToolSuite" -A "Jithin B."  -F -e -o docs .
cp conf.py docs/conf.py
cp custom.css docs/_static/custom.css
cp index.rst docs/index.rst
cp Apps.rst docs/Apps.rst
cd docs

rm achan.rst
rm commands_proto.rst
rm conf.rst
rm custom_widgets.rst
rm digital_channel.rst
rm experiment.rst
rm packet_handler.rst
rm template_exp.rst
rm widgets.*
rm MCP4728_class.rst

make html
mkdir _build/html/videos
cp ../videos/bandpass.avi _build/html/videos
cp ../videos/lissajous.ogv _build/html/videos
cp -R ../js _build/html/
