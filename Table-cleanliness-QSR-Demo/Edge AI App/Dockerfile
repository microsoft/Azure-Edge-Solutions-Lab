FROM nvcr.io/nvidia/deepstream:6.2-triton

RUN apt update
RUN apt install -y ffmpeg

RUN apt-get install -y --no-install-recommends \
    libavformat58 \
    libavcodec58 \
    libavresample4 \
    libavutil56 

#COPY ./scripts/prepare_classification_test_video.sh /opt/nvidia/deepstream/deepstream-6.2/samples/
#COPY ./scripts/prepare_ds_triton_model_repo.sh /opt/nvidia/deepstream/deepstream-6.2/samples/

WORKDIR /opt/nvidia/deepstream/deepstream-6.2
RUN chmod -R 777 /opt/nvidia/deepstream/deepstream-6.2/user_additional_install.sh && \
    /opt/nvidia/deepstream/deepstream-6.2/user_additional_install.sh

#RUN chmod -R 777 /opt/nvidia/deepstream/deepstream-6.2/user_deepstream_python_apps_install.sh && \
#    /opt/nvidia/deepstream/deepstream-6.2/user_deepstream_python_apps_install.sh

WORKDIR /opt/nvidia/deepstream/deepstream-6.2/samples/ 

RUN chmod -R 777 /opt/nvidia/deepstream/deepstream-6.2/samples/models/
RUN chmod -R 777 /opt/nvidia/deepstream/deepstream-6.2/samples/configs/
RUN chmod -R 777 /opt/nvidia/deepstream/deepstream-6.2/samples/streams/
RUN chmod -R 777 /opt/nvidia/deepstream/deepstream-6.2/samples/triton_model_repo/
RUN chmod -R 777 /opt/nvidia/deepstream/deepstream-6.2/samples/trtis_model_repo/

RUN chmod +x /opt/nvidia/deepstream/deepstream-6.2/samples/prepare_classification_test_video.sh && \
    /opt/nvidia/deepstream/deepstream-6.2/samples/prepare_classification_test_video.sh 

#WORKDIR /opt/nvidia/deepstream/deepstream-6.2/samples/  
#RUN chmod +x /opt/nvidia/deepstream/deepstream-6.2/samples/prepare_ds_triton_model_repo.sh && \
#    /opt/nvidia/deepstream/deepstream-6.2/samples/prepare_ds_triton_model_repo.sh


RUN apt update
RUN apt install -y python3-gi python3-dev python3-gst-1.0 python3-numpy python3-opencv

# Compile Python bindings
RUN apt install python3-gi python3-dev python3-gst-1.0 python-gi-dev git python-dev \
    python3 python3-pip python3.8-dev cmake g++ build-essential libglib2.0-dev \
    libglib2.0-dev-bin libgstreamer1.0-dev libtool m4 autoconf automake libgirepository1.0-dev libcairo2-dev -y
RUN cd /opt/nvidia/deepstream/deepstream/sources/ \
    && git clone https://github.com/NVIDIA-AI-IOT/deepstream_python_apps.git \
    && cd deepstream_python_apps \
    && git submodule update --init \
    && apt-get install -y apt-transport-https ca-certificates -y \
    && update-ca-certificates \
    && cd 3rdparty/gst-python/ \
    && ./autogen.sh \
    && make \
    && make install \
    && cd ../../bindings \
    && mkdir build \
    && cd build \
    && cmake .. \
    && make \
    && pip3 install ./pyds-*.whl

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir datetime && \
    pip install --no-cache-dir requests


WORKDIR /opt/nvidia/deepstream/deepstream-6.2/samples/  


COPY . /app
# RUN cp /app/prepare_ds_triton_model_repo.sh /opt/nvidia/deepstream/deepstream-6.2/samples/
RUN chmod +x /opt/nvidia/deepstream/deepstream-6.2/samples/prepare_ds_triton_model_repo.sh 

ENTRYPOINT ["/opt/nvidia/deepstream/deepstream-6.2/samples/prepare_ds_triton_model_repo.sh"]
