# Note: uncomment below to run this with arguments -docpath "<srcpath>" -htmlpath "<destpath>" but that's a pain.
# param([string]$docpath,[string]$htmlpath = $docpath)

Write-Host "Did you close Word? You have 15 seconds."
Start-Sleep -s 15

Add-Type -AssemblyName Microsoft.Office.Interop.Word

$docpath = "D:\Dropbox\Stories\Iraedria\"

# TODO: don't really want directory here anymore, BUT folder must contain ONLY html chapters for updater.py!!
$htmlpath = "C:\Users\Asus\Documents\GitHub\My-HardDrive-Is-Breaking\Iraedria\static\text\"

$parserpath = "C:\Users\Asus\Documents\GitHub\My-HardDrive-Is-Breaking\Iraedria\parser.py"
$updaterpath = "C:\Users\Asus\Documents\GitHub\My-HardDrive-Is-Breaking\Iraedria\updater.py"

$pempath = "C:\Users\Asus\Desktop\IRAEDRIA.PEM"
$dbpath = "C:/Users/Asus/Documents/GitHub/My-HardDrive-Is-Breaking/Iraedria/data.sqlite"
$basehtmlpath = "C:/Users/Asus/Documents/GitHub/My-HardDrive-Is-Breaking/Iraedria/templates/base.html"

$srcfiles = Get-ChildItem $docPath -filter "*.doc" -Recurse
$saveFormat = [Enum]::Parse([Microsoft.Office.Interop.Word.WdSaveFormat], "wdFormatFilteredHTML");

$word = New-Object -ComObject Word.Application
$word.Visible = $False
		
function saveas-filteredhtml
	{
		Write-Host "Converting" $doc.FullName "to" $newPath;
		$opendoc = $word.documents.open($doc.FullName);
		$opendoc.saveas([ref]$newPath, [ref]$saveFormat);
		$opendoc.close();
		python $parserpath $newPath
	}
	

# first!!! copy the db from the server to local so that the precious likes are not overwritten.
scp -i $pempath ubuntu@iraedria.ksadwin.com:/var/www/iraedriapp/Iraedria/data.sqlite $dbpath

ForEach ($doc in $srcfiles)
	{
		if (-not $doc.BaseName.StartsWith("draft")) {
			$newPathDir = $htmlpath + ([System.IO.Path]::GetDirectoryName($doc.FullName)).TrimStart($docpath) + "\";
			$newPath = $newPathDir + $doc.BaseName + ".html";
			# if the html file does not exist, or the doc has a later time than the html
			if ((-not (Test-Path $newPath)) -or ($doc.LastWriteTime -gt (Get-Item $newPath).LastWriteTime)) {
				New-Item -ItemType Directory -Force -Path $newPathDir;
				saveas-filteredhtml
			} else {Write-Host "Did not convert unchanged file" $doc.FullName}
		} else {Write-Host "Did not convert draft file" $doc.FullName}
		$doc = $null
	}

$word.quit();

python $updaterpath
scp -i $pempath $basehtmlpath ubuntu@iraedria.ksadwin.com:/var/www/iraedriapp/Iraedria/templates/
scp -i $pempath $dbpath ubuntu@iraedria.ksadwin.com:/var/www/iraedriapp/Iraedria/
Write-Host "Attempting to connect and restart server"
ssh -i $pempath ubuntu@iraedria.ksadwin.com "sudo service apache2 restart"