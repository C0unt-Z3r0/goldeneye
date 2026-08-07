# Goldeneye - Security Assessment Assistant
FROM python:3.11-slim

LABEL maintainer="C0unt-Z3r0"
LABEL description="Goldeneye - Security Assessment Assistant"

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    nmap \
    hydra \
    sqlmap \
    git \
    wget \
    curl \
    golang-go \
    dirb \
    && rm -rf /var/lib/apt/lists/*

# Instalar Nuclei
RUN go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest \
    && cp ~/go/bin/nuclei /usr/local/bin/

# Instalar Httpx e Subfinder
RUN go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest \
    && go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest \
    && cp ~/go/bin/httpx /usr/local/bin/ \
    && cp ~/go/bin/subfinder /usr/local/bin/

WORKDIR /app
COPY . /app/

RUN pip install --no-cache-dir -e . \
    && pip install --no-cache-dir ollama requests python-docx weasyprint matplotlib

RUN mkdir -p /app/projects /app/assets /app/logs

CMD ["goldeneye"]
