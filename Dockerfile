FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"
RUN pip install --no-cache-dir uv
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project
COPY . .
EXPOSE 8000
HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port","8000"]