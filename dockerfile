FROM python:3.13-slim

# Set work directory
WORKDIR /opt/app-root

# Copy Python Project Files (Container context must be the `python` directory)
COPY . /opt/app-root

USER root

# Install system build dependencies and UV package manager
RUN apt-get update && apt-get install -y gcc g++ \
 && pip install uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_NO_CACHE=1

# Install the project
RUN uv sync --frozen --no-install-project --no-dev

# Allow non-root user to access the everything in app-root
RUN chgrp -R root /opt/app-root/ && chmod -R g+rwx /opt/app-root/

# Expose default port (change if needed)
EXPOSE 10020

USER 1001

# Run the agent
CMD uv run main.py --host 0.0.0.0