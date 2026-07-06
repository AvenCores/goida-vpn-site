@echo off
set GOOS=linux
set GOARCH=amd64
go build -o ../loader/goida-builder .
set GOOS=windows
set GOARCH=amd64
go build -o ../loader/goida-builder.exe .
echo Built successfully into ../loader/
