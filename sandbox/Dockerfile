FROM alpine:3.19

# Install Clang 17, LLVM tools, musl development headers, and build essentials
RUN apk add --no-cache \
    clang17 \
    llvm17 \
    musl-dev \
    gcc \
    make

# Create unprivileged runner user
RUN addgroup -S compilerx && adduser -S compilerx -G compilerx

WORKDIR /sandbox

# Copy and compile high-resolution measurement harness
COPY runner.c /sandbox/runner.c
RUN gcc -O2 -Wall -Wextra /sandbox/runner.c -o /usr/local/bin/compilerx-runner \
    && rm /sandbox/runner.c \
    && chmod 755 /usr/local/bin/compilerx-runner

USER compilerx
ENTRYPOINT ["/usr/local/bin/compilerx-runner"]

