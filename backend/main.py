import os

import uvicorn

from .app import app


def main():
    host = os.environ.get('HOST', '127.0.0.1')
    port = int(os.environ.get('PORT', 8000))
    uvicorn.run(app, port=port, host=host)


if __name__ == '__main__':
    main()
