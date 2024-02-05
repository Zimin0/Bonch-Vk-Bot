#!/bin/sh
black -l 79 ./cyberbot/* ./games/* ./teams/* ./tournaments/* ./users/*
isort -l 79 ./cyberbot/* ./games/* ./teams/* ./tournaments/* ./users/*
pylint ./cyberbot/* ./games/* ./teams/* ./tournaments/* ./users/*