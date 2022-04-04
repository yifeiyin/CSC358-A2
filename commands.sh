function ss() {
  c/host.py start &
}

function s() {
  c/host.py "$@"
}

function ssend() {
  c/host.py send "$@"
}

function sbr() {
  c/host.py broadcast
}
