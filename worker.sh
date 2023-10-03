#!/bin/bash

set -o errexit
set -o nounset

celery -A watsapp_backend worker -l INFO 