# Verifier image. The agent never sees this container.
#
# Everything the verifier needs must be installed HERE. test.sh must never
# apt-get, curl or pip install at verify time.
FROM python:3.13-slim-bookworm

# Install only what the verifier actually uses. If you do need apt packages,
# never version-pin them, and clean up in the same layer:
#
#   RUN apt-get update \
#       && apt-get install -y --no-install-recommends <pkg> \
#       && rm -rf /var/lib/apt/lists/*

# Python packages must be pinned with ==. These two versions are mandated.
RUN pip install --no-cache-dir pytest==8.4.1 pytest-json-ctrf==0.3.5

# Bake the tests and ground truth into the image; harbor does NOT upload tests/
# at verify time.
COPY . /tests/

# Pre-create the parent directory of every declared artifact, or harbor's
# upload fails with "Could not find the file /app in container".
RUN mkdir -p /app
