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

## Create necessary CUPS directories
#RUN mkdir -p /run/cups && \
#    mkdir -p /var/log/cups && \
#    mkdir -p /var/spool/cups && \
#    mkdir -p /var/cache/cups && \
#    mkdir -p /usr/share/cups/model && \
#    chmod 755 /run/cups
#
## Set directory permissions for CUPS
#RUN chmod 755 /etc/cups && \
#    chmod 755 /var/log/cups && \
#    chmod -R 755 /var/spool/cups && \
#    chmod -R 755 /var/cache/cups

# Copy CUPS configuration
COPY cupsd.conf /etc/cups/cupsd.conf
RUN chmod 644 /etc/cups/cupsd.conf

# Copy PPD file
COPY dymo-cups-drivers-1.4.0.tar /tmp
RUN tar xf /tmp/dymo-cups-drivers-1.4.0.tar --directory=/tmp

#WORKDIR /tmp/dymo-cups-drivers-1.4.0.5
#RUN configure
#RUN make
#RUN make install
#WORKDIR /

# Copy data for add-on
COPY run.sh /
COPY app.py /

RUN chmod a+x /run.sh

CMD [ "/run.sh" ]