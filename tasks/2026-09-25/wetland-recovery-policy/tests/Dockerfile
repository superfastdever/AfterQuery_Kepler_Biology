# Verifier image. The agent never sees this container.
#
# Everything the verifier needs is installed here; test.sh installs nothing at
# verify time.
FROM python:3.12-slim-bookworm

# Python packages pinned with ==. The pytest and CTRF versions are the ones the
# submit form's required layout specifies.
RUN pip install --no-cache-dir \
        pytest==8.4.1 \
        pytest-json-ctrf==0.3.5 \
        numpy==2.2.6

# Bake the tests and the sealed reference arrays in; harbor does not upload
# tests/ at verify time.
COPY . /tests/

# Pre-create the parent directory of every declared artifact, or harbor's
# upload fails with "Could not find the file /app/output in container".
RUN mkdir -p /app/output
