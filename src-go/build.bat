@echo off
set GOOS=linux
set GOARCH=amd64
go build -o ../loader/goida-builder main.go
set GOOS=windows
set GOARCH=amd64
go build -o ../loader/goida-builder.exe main.go
echo Built successfully into ../loader/
