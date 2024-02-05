#!/bin/sh
black -l 79 ./app/*
isort -l 79 ./app/*
pylint ./app/*