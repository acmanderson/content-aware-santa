FROM lambci/lambda:build

ENV LQR_VERSION 0.4.2
ENV IMAGEMAGICK_VERSION 6.9.7-7
ENV PKG_CONFIG_PATH /usr/lib/pkgconfig/:$PKG_CONFIG_PATH

RUN yum install -y \
    glib2-devel \
    libjpeg-devel \
    libpng-devel \
    wget; yum clean all

WORKDIR /var/task
RUN wget http://liblqr.wdfiles.com/local--files/en:download-page/liblqr-1-${LQR_VERSION}.tar.bz2 && \
    tar -vxjf liblqr-1-${LQR_VERSION}.tar.bz2
WORKDIR /var/task/liblqr-1-${LQR_VERSION}
RUN ./configure && \
    make && \
    make install
WORKDIR /var/task

RUN wget https://www.imagemagick.org/download/ImageMagick-${IMAGEMAGICK_VERSION}.tar.gz && \
    tar xvzf ImageMagick-${IMAGEMAGICK_VERSION}.tar.gz
WORKDIR /var/task/ImageMagick-${IMAGEMAGICK_VERSION}
RUN ./configure --prefix=/var/task/build && \
    make && \
    make install && \
    mkdir /var/task/build/ImageMagick-${IMAGEMAGICK_VERSION} && \
    cp \
        /usr/lib64/libjpeg* \
        /usr/lib/liblqr-1* \
        /usr/lib64/libglib* \
        /usr/lib64/libpng* \
    /var/task/build/lib/
WORKDIR /var/task/

ENV MAGICK_HOME /var/task/build