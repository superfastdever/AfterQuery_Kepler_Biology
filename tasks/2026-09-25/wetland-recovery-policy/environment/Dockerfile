# The agent's container. Everything in this image is visible to the agent.
#
# Only the four public study files are copied in. The reference solution, the
# sealed verifier, the generator, its seed, the true hypothesis and every
# precomputed result stay out of this image and out of its layers.
FROM python:3.12-slim-bookworm

# Python packages pinned with ==. scipy is needed for its HiGHS-backed milp.
RUN pip install --no-cache-dir \
        numpy==2.2.6 \
        scipy==1.15.3

# The complete study specification: model, archive, output contract, protocol.
# Vendored into the image so the task never depends on a live web resource.
COPY data/ /app/input/

# The three required artifacts are written here.
RUN mkdir -p /app/output

WORKDIR /app
