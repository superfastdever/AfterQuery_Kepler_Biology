# The agent's container. This is the agent's entire world.
#
# CRITICAL: everything in this image is visible to the agent. Never COPY in
# ground truth, expected outputs, or anything from tests/ or solution/.
# Referencing those paths from here fails validation.
#
# No `FROM --platform=` pins.
FROM ubuntu:24.04

# apt packages are never version-pinned. Update first, clean up after.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        python3 \
        python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Python packages must be pinned with ==.
# RUN pip3 install --no-cache-dir --break-system-packages \
#         numpy==2.3.4

# Vendor input data into the image rather than fetching it at run time -- a
# live web resource can change or disappear and will make the task flaky.
# COPY data/ /app/data/

WORKDIR /app
