{{- define "todo-list-manager.name" -}}
{{- .Chart.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "todo-list-manager.fullname" -}}
{{- printf "%s" (include "todo-list-manager.name" .) -}}
{{- end -}}
