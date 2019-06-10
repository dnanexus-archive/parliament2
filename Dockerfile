# Set the base image to Ubuntu 14.04
FROM ubuntu:14.04

# File Author / Maintainer
MAINTAINER Samantha Zarate

# System packages 
RUN apt-get update && apt-get install -y curl wget

# Install miniconda to /miniconda
RUN curl -LO http://repo.continuum.io/miniconda/Miniconda-latest-Linux-x86_64.sh && bash Miniconda-latest-Linux-x86_64.sh -p /miniconda -b && rm Miniconda-latest-Linux-x86_64.sh
ENV PATH=/miniconda/bin:${PATH}
# RUN conda update -y conda

RUN /bin/bash -c "echo 'deb http://dnanexus-apt-prod.s3.amazonaws.com/ubuntu trusty/amd64/' > /etc/apt/sources.list.d/dnanexus.list"
RUN /bin/bash -c "echo 'deb http://dnanexus-apt-prod.s3.amazonaws.com/ubuntu trusty/all/' >> /etc/apt/sources.list.d/dnanexus.list"
RUN wget https://wiki.dnanexus.com/images/files/ubuntu-signing-key.gpg
RUN apt-key add ubuntu-signing-key.gpg

RUN apt-get update -y && apt-get upgrade -y && apt-get install -y --force-yes \
    autoconf \
    bedtools \
    bsdtar \
    build-essential \
    cmake \
    dx-toolkit \
    g++ \
    gcc \
    gettext \
    gfortran \
    git \
    gzip \
    inkscape \
    libc6 \
    libcurl4-openssl-dev \
    libfontconfig \
    libfreetype6-dev \
    libgsl0-dev \
    libgtkmm-3.0-dev \
    libhdf5-serial-dev  \
    liblzma-dev \
    liblzo2-dev \
    libpangomm-1.4-dev \
    libpng-dev \
    libpopt-dev \
    libpthread-stubs0-dev \
    librsvg2-bin \
    librsvg2-dev \
    libsqlite3-dev \
    libstdc++6 \
    libx11-dev \
    libxext-dev \
    libxft-dev \
    libxpm-dev \
    libxslt1-dev \
    python-pip \
    sqlite3 \
    wget \
    wkhtmltopdf \
    xvfb \
    zlib1g-dev
RUN apt-get update

RUN conda config --add channels conda-forge
RUN conda config --add channels bioconda
RUN conda config --add channels defaults
RUN conda install -c bioconda samtools
RUN conda install -c bioconda sambamba -y
RUN conda install -c bioconda bcftools -y
RUN conda install -c bcbio bx-python -y
RUN conda install -c defaults networkx -y
RUN conda install -c bioconda samblaster -y
RUN conda install gcc_linux-64 -y
RUN conda install -c bioconda manta
RUN conda update -y pyopenssl

WORKDIR /
ADD resources.tar.gz /
RUN cp -a /resources/* / && rm -rf /resources/

RUN conda install -c defaults -y numpy
RUN pip install https://github.com/bioinform/breakseq2/archive/2.2.tar.gz
RUN pip install pycparser
RUN pip install asn1crypto
RUN pip install idna
RUN pip install ipaddress

RUN pip install dxpy
    
WORKDIR /root
RUN mkdir -p /home/dnanexus/in /home/dnanexus/out

WORKDIR /home/dnanexus
COPY parliament2.py .
COPY parliament2.sh .
COPY svtyper_env.yml .

RUN conda create -y --name svviz_env svviz
# We have to use a slightly different method for 
# svtyper as it installs software directly from git 
RUN conda env create --name svtyper_env --file svtyper_env.yml

RUN /bin/bash -c "source /etc/profile.d/dnanexus.environment.sh"

ENV PATH=${PATH}:/home/dnanexus/
ENV PATH=${PATH}:/opt/conda/bin/
ENV PATH=${PATH}:/usr/bin/
ENV PYTHONPATH=${PYTHONPATH}:/opt/conda/bin/
ENV ROOTSYS=/home/dnanexus/root
ENV LD_LIBRARY_PATH=/usr/lib/root/lib
ENV LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/home/dnanexus/root/lib
ENV DYLD_LIBRARY_PATH=/usr/lib/root/lib
ENV HTSLIB_LIBRARY_DIR=/usr/local/lib
ENV HTSLIB_INCLUDE_DIR=/usr/local/include

WORKDIR /home/dnanexus
RUN ["chmod", "+x", "parliament2.py"]
RUN ["chmod", "+x", "parliament2.sh"]

ENTRYPOINT ["python","/home/dnanexus/parliament2.py"]
