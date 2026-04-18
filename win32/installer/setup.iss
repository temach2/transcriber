; Inno Setup Script for Qwen Medical Transcriber
; Auto-generated - configure paths to your local models before building

#define AppName "Qwen Medical Transcriber"
#define AppVersion "2.0.0"
#define AppPublisher "Qwen Medical Team"

[Setup]
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
DefaultDirName={pf}\{#AppName}
DefaultGroupName={#AppName}
AllowNoIcons=yes
LicenseFile=
SetupIconFile=resources\icon.ico
UninstallDisplayIcon={app}\QwenTranscriber.exe
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

[Dirs]
Name: "{app}\models"

[Files]
; Main application files
Source: "dist\QwenTranscriber.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\*.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\*.dll"; DestDir: "{app}"; Flags: ignoreversion

; Models (copy to models directory)
; UNCOMMENT AND MODIFY these paths when you have local models:
; Source: "C:\path\to\models\Qwen3-ASR-1.7B\*"; DestDir: "{app}\models\Qwen3-ASR-1.7B"; Flags: ignoreversion recursesubdirs createallsubdirs
; Source: "C:\path\to\models\Qwen3-ForcedAligner-0.6B\*"; DestDir: "{app}\models\Qwen3-ForcedAligner-0.6B"; Flags: ignoreversion recursesubdirs createallsubdirs
; Source: "C:\path\to\models\pyannote-speaker-diarization-3.1\*"; DestDir: "{app}\models\pyannote-speaker-diarization-3.1"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\QwenTranscriber.exe"
Name: "{group}\{#AppName} (Settings)"; Filename: "{app}\QwenTranscriber.exe"; Parameters: "--settings"
Name: "{group}\Uninstall {#AppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\QwenTranscriber.exe"

[Run]
Filename: "{app}\post_install.exe"; Flags: runhidden

[Code]
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    Exec(ExpandConstant('{app}\post_install.exe'), '', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  end;
end;
