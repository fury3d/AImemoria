Set WinScriptHost = CreateObject("WScript.Shell")
Set fs = CreateObject("Scripting.FileSystemObject")

' Pega o diretorio onde este script vbs está salvo
scriptFolder = fs.GetParentFolderName(WScript.ScriptFullName)

' Caminho para o script python dentro da mesma pasta
scriptPath = fs.BuildPath(scriptFolder, "memoria_delta_gui.py")

' Roda pythonw (sem terminal) passando o script
WinScriptHost.Run "pythonw " & chr(34) & scriptPath & chr(34), 0, False
