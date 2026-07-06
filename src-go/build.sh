#!/bin/bash
GOOS=linux GOARCH=amd64 go build -o ../loader/goida-builder .
GOOS=windows GOARCH=amd64 go build -o ../loader/goida-builder.exe .
echo "Built successfully into ../loader/"

