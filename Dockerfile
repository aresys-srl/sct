FROM python:3.11.7-bookworm

# insert your GitHub token here
ARG token=

USER root
RUN apt-get update -y && apt-get upgrade -y && apt-get install libgfortran5 && pip install --upgrade pip

WORKDIR /home/sw_dev

RUN git clone "https://${token}@github.com/aresys-srl/arepyextras-quality.git" && \
    git clone "https://${token}@github.com/aresys-srl/arepyextras-eo_products.git" && \
    git clone "https://${token}@github.com/aresys-srl/arepyextras-perturbations.git" && \
    git clone "https://${token}@github.com/aresys-srl/arepyextras-iers_solid_tides.git" && \
    git clone "https://${token}@github.com/aresys-srl/arepytools.git" && \
    git clone "https://${token}@github.com/aresys-srl/sct.git"

RUN cd arepytools && pip install -e. && cd ..
RUN cd arepyextras-iers_solid_tides && pip install -e . && cd ..
RUN cd arepyextras-eo_products && pip install -e . && cd ..
RUN cd arepyextras-perturbations && pip install -e . && cd ..
RUN cd arepyextras-quality && pip install -e . && cd ..
RUN cd sct && pip install -e .[cli] && cd .. && cd ..

WORKDIR /home

CMD /bin/bash