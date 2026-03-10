FROM ubuntu:24.04

# Install packages
RUN apt-get update && apt-get install -y \
    git \
    curl \
    wget \
    vim \
    openssh-client \
    ca-certificates \
    jq \
    tree \
    htop \
    ncdu \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# Create dev user FIRST (before installing user-specific tools)
# User ID and Group ID are configurable via build arguments to match host user
ARG USER_ID=1000
ARG GROUP_ID=1000

# Check if group with GID ${GROUP_ID} exists, if so rename it to 'dev'
RUN if getent group ${GROUP_ID} > /dev/null; then \
        EXISTING_GROUP=$(getent group ${GROUP_ID} | cut -d: -f1); \
        if [ "${EXISTING_GROUP}" != "dev" ]; then \
            groupmod -n dev ${EXISTING_GROUP}; \
        fi; \
    else \
        groupadd -g ${GROUP_ID} dev; \
    fi

# Check if user with UID ${USER_ID} exists, if so rename it to 'dev'
RUN if getent passwd ${USER_ID} > /dev/null; then \
        EXISTING_USER=$(getent passwd ${USER_ID} | cut -d: -f1); \
        if [ "${EXISTING_USER}" != "dev" ]; then \
            usermod -l dev -d /home/dev -m ${EXISTING_USER}; \
            usermod -g dev dev; \
        fi; \
    else \
        useradd -m -u ${USER_ID} -g dev -s /bin/bash dev; \
    fi

# Create home directory structure
RUN mkdir -p /home/dev/.local \
    && mkdir -p /home/dev/.config/opencode \
    && mkdir -p /home/dev/.local/share/opencode \
    && chown -R dev:dev /home/dev

# Install Node.js 24 via NodeSource (system-wide)
RUN curl -fsSL https://deb.nodesource.com/setup_24.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Set up bash aliases for dev user
RUN echo "alias ll='ls -la'" >> /home/dev/.bashrc \
    && echo "alias ..='cd ..'" >> /home/dev/.bashrc \
    && echo "alias grep='grep --color=auto'" >> /home/dev/.bashrc

# Switch to dev user for installations
USER dev
WORKDIR /home/dev

# Install OpenCode as dev user
RUN curl -fsSL https://opencode.ai/install | bash

# Set up environment (already set above, but ensure it's in final PATH)
ENV PATH="/home/dev/.opencode/bin:/home/dev/.local/bin:${PATH}"

WORKDIR /home/dev/workspace

# Verify installations
RUN node --version && npm --version