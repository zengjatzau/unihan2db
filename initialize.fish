mkdir -p data/source
mkdir -p data/derived
wget -nc -O data/source/Unihan.zip https://www.unicode.org/Public/UCD/latest/ucd/Unihan.zip
unzip data/source/Unihan.zip -d data/source
