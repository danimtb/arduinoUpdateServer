FROM %%BASE_IMAGE%%

ENV LANG C.UTF-8

# Setup
RUN apk add --no-cache python3 python3-dev gcc linux-headers \
    && pip3 install --no-cache --upgrade pip
COPY requirements.txt /tmp/
RUN pip3 install --requirement /tmp/requirements.txt

# Copy data for add-on
COPY arwiupser.py /

CMD ["python3", "arwiupser.py"]
