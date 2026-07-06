#!/bin/bash
export GOOS=linux
export GOARCH=amd64
go build -o ../loader/goida-builder main.go
export GOOS=windows
export GOARCH=amd64
go build -o ../loader/goida-builder.exe main.go
echo "Built successfully into ../loader/"
