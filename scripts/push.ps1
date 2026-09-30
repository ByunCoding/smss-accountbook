# GitHub Desktop이 저장한 토큰으로 push 한다 (CLI git은 이 토큰을 못 찾는다)
# 토큰은 Windows 자격 증명 관리자에서 메모리로만 읽고, 디스크나 git 설정에 남기지 않는다.
# 사용: powershell -ExecutionPolicy Bypass -File scripts\push.ps1

$src = @'
using System; using System.Runtime.InteropServices; using System.Text;
public class GhDesktopCred {
  [StructLayout(LayoutKind.Sequential, CharSet=CharSet.Unicode)]
  public struct CREDENTIAL { public int Flags; public int Type; public string TargetName; public string Comment; public long LastWritten; public int CredentialBlobSize; public IntPtr CredentialBlob; public int Persist; public int AttributeCount; public IntPtr Attributes; public string TargetAlias; public string UserName; }
  [DllImport("advapi32.dll", CharSet=CharSet.Unicode, SetLastError=true)] static extern bool CredRead(string t, int type, int f, out IntPtr c);
  [DllImport("advapi32.dll")] static extern void CredFree(IntPtr c);
  public static string Get(string t) {
    IntPtr p; if (!CredRead(t, 1, 0, out p)) return null;
    var c = (CREDENTIAL)Marshal.PtrToStructure(p, typeof(CREDENTIAL));
    var b = new byte[c.CredentialBlobSize]; Marshal.Copy(c.CredentialBlob, b, 0, b.Length);
    CredFree(p);
    return Encoding.UTF8.GetString(b);  // UTF-8로 저장돼 있다 (UTF-16으로 읽으면 절반 길이의 깨진 값)
  }
}
'@
Add-Type $src

$tok = [GhDesktopCred]::Get("GitHub - https://api.github.com/ByunCoding")
if ($null -eq $tok) { Write-Error "GitHub Desktop 자격 증명을 찾지 못했습니다. GitHub Desktop에 로그인돼 있는지 확인하세요."; exit 1 }

$git = (Get-ChildItem "$env:LOCALAPPDATA\GitHubDesktop\app-*" | Sort-Object { [version]($_.Name -replace '^app-', '') } -Descending | Select-Object -First 1).FullName + "\resources\app\git\cmd\git.exe"
$env:GIT_TERMINAL_PROMPT = "0"
$env:GH_TOK = $tok
& $git -c credential.helper= -c "credential.helper=!f() { echo username=x-access-token; echo password=`$GH_TOK; }; f" push origin master
$code = $LASTEXITCODE
$env:GH_TOK = $null
exit $code
