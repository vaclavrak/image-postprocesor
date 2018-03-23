#!/bin/bash 

set -e 

base_dir=$(realpath $(dirname $0))
version="0.0.2"
rm -rf $base_dir/build/imgppr-$version
rm -rf $base_dir/image-postprocesor-master
cd $base_dir/build/


echo "Downlad and infate new content" 
wget https://github.com/vaclavrak/image_postprocesor/archive/master.zip  -O master_$version.zip
unzip master_$version.zip
rm -f master_$version.zip
mv image-postprocesor-master imgppr-$version


echo "Make new archive"
tar -czvf imgppr-$version.tar.gz imgppr-$version
cd imgppr-$version

dh_make -e rak@webeye.services -f ../imgppr-$version.tar.gz -s -y

#ln -fs $base_dir/packages/debian $base_dir/build/imgppr-$version/

debuild -us -uc


cd $base_dir
