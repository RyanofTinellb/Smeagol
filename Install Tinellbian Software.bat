cd c:\users\ryan\documents\tinellbianlanguages\creation
pyinstaller --windowed --onefile EditDictionary.py --name "Edit Dictionary"
copy "c:\users\ryan\documents\tinellbianlanguages\creation\dist\Edit Dictionary.exe" "c:\users\ryan\documents\tinellbianlanguages\creation\Edit Dictionary.exe"
del "Edit Dictionary.spec"
cd c:\users\ryan\documents\tinellbianlanguages\creation
pyinstaller --windowed --onefile EditGrammarStory.py --name "Edit Grammar and Story"
copy "c:\users\ryan\documents\tinellbianlanguages\creation\dist\Edit Grammar and Story.exe" "c:\users\ryan\documents\tinellbianlanguages\creation\Edit Grammar and Story.exe"
del "Edit Grammar and Story.spec"
cd c:\users\ryan\documents\tinellbianlanguages\creation
pyinstaller --windowed --onefile TranslateStory.py --name "Translate Story"
copy "c:\users\ryan\documents\tinellbianlanguages\creation\dist\Translate Story.exe" "c:\users\ryan\documents\tinellbianlanguages\creation\Translate Story.exe"
del "Translate Story.spec"
rmdir build /s /q
rmdir dist /s /q