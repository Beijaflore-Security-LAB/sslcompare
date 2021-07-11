# wget https://www.python.org/ftp/python/3.9.5/Python-3.9.5.tgz
# tar xzvf Python-3.9.5.tgz
# cd Python-3.9.5
# ./configure LDFLAGS="-static" --disable-shared --enable-optimizations
# make LDFLAGS="-static" LINKFORSHARED=" "
# sudo cp libpython3.9.a /usr/lib
# cd ..
# export LDFLAGS="-static -l:libpython3.9.a"
# poetry run python -m nuitka --onefile --static-libpython=yes sslcompare_standalone.py --include-package-data=sslcompare --linux-onefile-icon=/home/aja/Pictures/icon.png
poetry run python -m nuitka --onefile sslcompare_standalone.py --include-package-data=sslcompare --linux-onefile-icon=/home/aja/Pictures/icon.png
