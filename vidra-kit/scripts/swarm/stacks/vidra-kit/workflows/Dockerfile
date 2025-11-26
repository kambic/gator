FROM python:3.13
# FROM python:3.13-slim

# Set environment variables to avoid Python buffering and ensure UTF-8
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100


# Set your Devpi server URL (replace with yours)
ARG DEVPI_URL=https://pypi-paytv.telekom.si/rkambic/stable

# Optionally, credentials can be passed as build arguments (not secure if pushed to logs)
ARG DEVPI_USER
ARG DEVPI_PASS

# Create .pip/pip.conf with Devpi URL and credentials (basic auth)
# RUN mkdir -p /root/.pip 

# Copy your code and install dependencies
WORKDIR /app
RUN pip3 install "https://pypi-paytv.telekom.si/rkambic/stable/+f/89b/172a817e09c41/vidra_kit-0.1.0-py3-none-any.whl#sha256=89b172a817e09c418b4b667444bc2515c5efdc6f977c9c2080f5853182c3eacf"
COPY worker.py .
# RUN pip install vidra-kit

# Copy rest of app

CMD ["python", "worker.py"]
# CMD ["vidra-kit", "ingest", "worker"]