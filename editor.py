print('Please make your selection:')
print('1. Edit a Site')
print('2. Edit a Dictionary')
print('3. Translate a Story')
print('')

while True:
    choice = raw_input()
    try:
        choice = int(choice)
    except ValueError:
        pass
    if choice == 1:
        from cwsmeagol.editor.editor import Editor
        break
    elif choice == 2:
        from cwsmeagol.editor.dictionary_editor import DictionaryEditor as Editor
        break
    elif choice == 3:
        from cwsmeagol.editor.story_editor import StoryEditor as Editor
        break
Editor().mainloop()
