ARG BUILD_FROM
FROM $BUILD_FROM

RUN apk update
RUN apk add build-base
RUN apk add cups-dev
RUN apk add cups
RUN apk add cups-libs cups
RUN apk add boost-dev
RUN apk add autoconf
RUN apk add automake
RUN apk add libtool
RUN apk add git
RUN apk add eudev-dev
RUN apk add openrc
RUN apk add usbutils
RUN apk add cups-filters
RUN apk add python3
RUN apk add py3-flask
RUN apk add py3-pillow
RUN apk add ttf-dejavu
RUN apk add py3-reportlab
RUN apk add libusb libusb-compat

# Copy CUPS configuration
COPY cupsd.conf /etc/cups/cupsd.conf
RUN chmod 644 /etc/cups/cupsd.conf

# Copy PPD file
COPY dymo_drivers.zip /tmp
WORKDIR tmp
RUN unzip -q dymo_drivers.zip
WORKDIR dymo_drivers
RUN ./build.sh
RUN make install
WORKDIR /

# Copy data for add-on
COPY run.sh /
COPY app.py /

RUN chmod a+x /run.sh

CMD [ "/run.sh" ]