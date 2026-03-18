package aegis.authz

import future.keywords.if
import future.keywords.contains

default allow := true

deny contains reason if {
  input.tool == "run_shell_command"
  patterns := ["rm -rf", "sudo", "chmod 777", "dd if="]
  pattern := patterns[_]
  contains(input.args.command, pattern)
  reason := sprintf("Blocked: '%v'", [pattern])
}

deny contains reason if {
  input.tool == "read_file"
  sensitive := ["/etc/passwd", "/etc/shadow", "/.ssh", "/.aws"]
  path := sensitive[_]
  startswith(input.args.path, path)
  reason := sprintf("Blocked path: '%v'", [path])
}