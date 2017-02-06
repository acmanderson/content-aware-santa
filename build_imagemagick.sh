#!/usr/bin/env bash

mkdir -p build
docker run -i -v `pwd`/build:/build lambci/lambda:build bash <<'EOF'
    #!/usr/bin/env bash

    LQR_VERSION=0.4.2
    IMAGE_MAGICK_VERSION=7.0.4-7

    yum install -y \
        wget \
        glib2-devel \
        libpng-devel \
        libjpeg-devel

    wget http://liblqr.wdfiles.com/local--files/en:download-page/liblqr-1-${LQR_VERSION}.tar.bz2
    tar -vxjf liblqr-1-${LQR_VERSION}.tar.bz2
    cd liblqr-1-${LQR_VERSION}
    ./configure && make && make install
    export PKG_CONFIG_PATH=/usr/lib/pkgconfig/
    cd ..

    wget https://www.imagemagick.org/download/ImageMagick.tar.gz
    tar xvzf ImageMagick.tar.gz
    cd ImageMagick-${IMAGE_MAGICK_VERSION}
    ./configure --prefix=/build && make && make install

    mkdir /build/ImageMagick-${IMAGE_MAGICK_VERSION}
    cp \
        /usr/lib64/libjpeg* \
        /usr/lib/liblqr-1* \
        /usr/lib64/libglib* \
        /usr/lib64/libpng* \
        /usr/local/lib64/node-v4.3.x/lib/libgomp* \
        /usr/local/lib64/node-v4.3.x/lib/libgcc* \
    /build/lib/
EOF